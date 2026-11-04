#!/usr/bin/env python3
"""Metricas de una HU de NexusAgil, leidas de los transcripts de Claude Code y de .gates.jsonl.

Uso:
  nexus_metrics.py --hu-dir HU_DIR [--json]            busca todas las sesiones que trabajaron en la HU
  nexus_metrics.py --session <transcript.jsonl | carpeta> [--hu-dir HU_DIR] [--json]

Por cada agente lanzado: fase, HU, tokens, tiempo, herramientas, Bash y bloqueos del hook.
Los tokens son los que reporta el harness al terminar el agente (contexto final); ademas se suman
entrada, cache y salida de cada mensaje, para quien quiera calcular costo con sus precios.
Solo lee: no escribe nada salvo la salida estandar.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


IDLE_SECONDS = 300


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None


def first_prompt(entries):
    for entry in entries:
        message = entry.get("message") or {}
        if entry.get("type") == "user" and message.get("role") == "user":
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return "\n".join(c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text")
    return ""


def field(prompt, name):
    found = re.search(rf"^\s*{name}:\s*(\S.*?)\s*$", prompt, re.M)
    return found.group(1) if found else None


def tool_result_text(block):
    content = block.get("content")
    if isinstance(content, list):
        return "\n".join(c.get("text", "") for c in content if isinstance(c, dict))
    return content if isinstance(content, str) else ""


def hook_blocks_in(entries):
    seen, blocks = set(), []
    for entry in entries:
        message = entry.get("message") or {}
        for block in message.get("content") if isinstance(message.get("content"), list) else []:
            if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("is_error") \
                    and block.get("tool_use_id") not in seen:
                # Solo bloqueos reales: un error de hook. Un reporte que cita un bloqueo anterior no cuenta.
                seen.add(block.get("tool_use_id"))
                found = re.search(r"NEXUS GATE: [^\n]{0,160}", tool_result_text(block))
                if found:
                    blocks.append(found.group(0))
    return blocks


def read_entries(path):
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return entries


def agent_metrics(transcript):
    entries = read_entries(transcript)
    meta_path = transcript.with_suffix(".meta.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    prompt = first_prompt(entries)
    seen, tools, last_usage = set(), {}, None
    totals = {"input": 0, "cache_read": 0, "cache_write": 0, "output": 0}
    blocks_hook, timestamps, models = hook_blocks_in(entries), [], set()
    for entry in entries:
        if entry.get("timestamp"):
            timestamps.append(parse_ts(entry["timestamp"]))
        message = entry.get("message") or {}
        content = message.get("content") if isinstance(message.get("content"), list) else []
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use" and block.get("id") not in seen:
                seen.add(block.get("id"))
                tools[block.get("name")] = tools.get(block.get("name"), 0) + 1
        usage = message.get("usage")
        message_id = message.get("id")
        if usage and message_id and message_id not in seen:
            seen.add(message_id)
            last_usage = usage
            if message.get("model"):
                models.add(message["model"])
            totals["input"] += usage.get("input_tokens", 0)
            totals["cache_read"] += usage.get("cache_read_input_tokens", 0)
            totals["cache_write"] += usage.get("cache_creation_input_tokens", 0)
            totals["output"] += usage.get("output_tokens", 0)
    final_context = 0
    if last_usage:
        final_context = sum(last_usage.get(k, 0) for k in
                            ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens"))
    duration = (max(timestamps) - min(timestamps)).total_seconds() if len(timestamps) > 1 else 0
    # Tiempo activo: un agente reanudado deja huecos de espera entre vueltas. Un hueco de mas de IDLE no cuenta.
    ordered = sorted(timestamps)
    gaps = [(b - a).total_seconds() for a, b in zip(ordered, ordered[1:])]
    active = sum(g for g in gaps if g <= IDLE_SECONDS)
    rounds = 1 + sum(1 for g in gaps if g > IDLE_SECONDS)
    return {
        "agent_id": transcript.stem.replace("agent-", ""),
        "agent": (meta.get("agentType") or "?").split(":")[-1],
        "description": meta.get("description") or "",
        "phase": field(prompt, "FASE") or "-",
        "hu_dir": field(prompt, "HU_DIR"),
        "started": min(timestamps).isoformat() if timestamps else None,
        "tokens": final_context,
        "usage": totals,
        "models": sorted(models),
        "seconds": round(active),
        "span_seconds": round(duration),
        "rounds": rounds,
        # Lo que el modelo proceso en todas sus llamadas: con reanudaciones, el contexto final se queda corto.
        "processed": sum(totals.values()),
        "tool_uses": sum(tools.values()),
        "bash": tools.get("Bash", 0),
        "memory_calls": {name.split("__")[-1]: count for name, count in tools.items() if name and "engram" in name},
        "hook_blocks": blocks_hook,
    }


def gates_summary(hu_dir):
    path = Path(hu_dir) / ".gates.jsonl"
    if not path.exists():
        return None
    entries = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    summary = {}
    for entry in entries:
        summary[entry.get("gate", "?")] = summary.get(entry.get("gate", "?"), 0) + 1
    return {"counts": summary, "violations": [e for e in entries if e.get("gate") == "VIOLATION"],
            "overrides": [e for e in entries if e.get("gate") == "OVERRIDE"]}


def session_folders(session, hu_dir, projects):
    """Una sesion dada, o todas las que lanzaron agentes sobre HU_DIR: una HU puede cruzar varias sesiones."""
    if session:
        session = Path(session).expanduser()
        folder = session.with_suffix("") if session.suffix == ".jsonl" else session
        if not (folder / "subagents").is_dir():
            sys.exit(f"no encuentro {folder / 'subagents'}: pasa el transcript principal o la carpeta de la sesion")
        return [folder]
    if not hu_dir:
        sys.exit("pasa --session, --hu-dir o los dos")
    needle = str(Path(hu_dir).expanduser().resolve()).encode()
    found = {t.parent.parent for t in Path(projects).expanduser().glob("*/*/subagents/agent-*.jsonl") if needle in t.read_bytes()}
    if not found:
        sys.exit(f"ninguna sesion en {projects} lanzo agentes sobre {hu_dir}")
    return sorted(found)


def collect(session, hu_dir=None, projects="~/.claude/projects"):
    folders = session_folders(session, hu_dir, projects)
    agents = [agent_metrics(t) for folder in folders for t in sorted((folder / "subagents").glob("agent-*.jsonl"))]
    agents = [a for a in agents if a["started"]]
    if hu_dir:
        target = str(Path(hu_dir).expanduser().resolve())
        agents = [a for a in agents if a["hu_dir"] and str(Path(a["hu_dir"]).expanduser().resolve()) == target]
    agents.sort(key=lambda a: a["started"])
    phases = {}
    for a in agents:
        p = phases.setdefault(a["phase"], {"launches": 0, "tokens": 0, "processed": 0, "seconds": 0})
        p["launches"] += 1
        p["tokens"] += a["tokens"]
        p["processed"] += a["processed"]
        p["seconds"] += a["seconds"]
    main_blocks = [b for folder in folders if folder.with_suffix(".jsonl").exists()
                   for b in hook_blocks_in(read_entries(folder.with_suffix(".jsonl")))]
    return {
        "session": ", ".join(str(f) for f in folders),
        "orchestrator_hook_blocks": main_blocks,
        "agents": agents,
        "phases": phases,
        "totals": {"launches": len(agents), "tokens": sum(a["tokens"] for a in agents),
                   "processed": sum(a["processed"] for a in agents), "rounds": sum(a["rounds"] for a in agents),
                   "seconds": sum(a["seconds"] for a in agents),
                   "hook_blocks": sum(len(a["hook_blocks"]) for a in agents) + len(main_blocks)},
        "gates": gates_summary(hu_dir) if hu_dir else None,
    }


def number(value):
    return f"{value:,}".replace(",", ".")


def render(data):
    out = [f"# Metricas de la HU", "", f"Sesion: `{data['session']}`", ""]
    out += ["| # | Fase | Agente | Descripcion | Vueltas | Contexto final | Procesados | Tiempo activo | Herramientas | Bash | Bloqueos del hook |",
            "|---|------|--------|-------------|--------:|---------------:|-----------:|--------------:|-------------:|-----:|------------------:|"]
    for i, a in enumerate(data["agents"], 1):
        out.append(f"| {i} | {a['phase']} | {a['agent']} | {a['description'][:50]} | {a['rounds']} | {number(a['tokens'])} | "
                   f"{number(a['processed'])} | {a['seconds']} s | {a['tool_uses']} | {a['bash']} | {len(a['hook_blocks'])} |")
    t = data["totals"]
    out += [f"| | **Total** | | | **{t['rounds']}** | **{number(t['tokens'])}** | **{number(t['processed'])}** | "
            f"**{number(t['seconds'])} s** | | | **{t['hook_blocks']}** |", ""]
    out += ["## Por fase", "", "| Fase | Lanzamientos | Contexto final | Procesados | Tiempo activo |",
            "|------|------------:|---------------:|-----------:|--------------:|"]
    for phase, p in data["phases"].items():
        out.append(f"| {phase} | {p['launches']} | {number(p['tokens'])} | {number(p['processed'])} | {number(p['seconds'])} s |")
    blocks = [(a["phase"], a["agent"], b) for a in data["agents"] for b in a["hook_blocks"]]
    blocks += [("-", "orquestador", b) for b in data["orchestrator_hook_blocks"]]
    if blocks:
        out += ["", "## Bloqueos del hook", ""] + [f"- {phase} / {agent}: `{text}`" for phase, agent, text in blocks]
    memory = {}
    for a in data["agents"]:
        for name, count in a.get("memory_calls", {}).items():
            memory[name] = memory.get(name, 0) + count
    out += ["", "## Memoria", "", ("Llamadas a Engram: " + ", ".join(f"{k} {v}" for k, v in sorted(memory.items()))) if memory
            else "Ningun agente uso la memoria."]
    if data["gates"]:
        g = data["gates"]
        out += ["", "## Gates", "", ", ".join(f"{k}: {v}" for k, v in g["counts"].items())]
        for v in g["violations"]:
            out.append(f"- VIOLATION de {v.get('by')}: {', '.join(Path(f).name for f in v.get('files', []))}")
        for o in g["overrides"]:
            out.append(f"- OVERRIDE: {o.get('reason')}")
    out += ["", "Contexto final: el ultimo contexto de cada agente, igual que la notificacion del harness. Con un agente reanudado se queda corto.",
            "Procesados: entrada, cache y salida sumadas en todas sus llamadas; es la base para calcular costo con tus precios (la cache se cobra distinto).",
            f"Tiempo activo: suma de los tramos entre eventos, sin los huecos de mas de {IDLE_SECONDS} s (esperas entre vueltas).",
            "No incluye la sesion principal ni el tiempo de la persona."]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--session", help="transcript principal o carpeta de la sesion; sin el, busca todas las sesiones de la HU")
    parser.add_argument("--projects", default="~/.claude/projects", help="donde buscar sesiones si no se pasa --session")
    parser.add_argument("--hu-dir")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = collect(args.session, args.hu_dir, args.projects)
    print(json.dumps(data, ensure_ascii=False, indent=2) if args.json else render(data))


if __name__ == "__main__":
    main()
