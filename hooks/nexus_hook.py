#!/usr/bin/env python3
"""Controles de NexusAgil que el modelo no puede ignorar por descuido.

Un solo despachador para todos los eventos, porque los sub-agentes de un plugin
ignoran los hooks declarados en su frontmatter. Solo usa la biblioteca estandar.

Uso: nexus_hook.py <gate|prompt|answer|stop|session>  (recibe JSON por stdin)
Exit 0 permite. Exit 2 bloquea, y stderr es el motivo que lee el modelo.

No es una frontera de seguridad: frena errores honestos y racionalizaciones. Un
agente decidido puede escribir por Bash de formas que el filtro no ve, y por eso
`stop` compara el arbol de git al terminar.
"""
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

GATES = ("HU_APPROVED", "SPEC_APPROVED", "RELEASE_APPROVED")
GATE_DOC = {"HU_APPROVED": "work-item.md", "SPEC_APPROVED": "sdd.md"}
READ_ONLY_BASH = {"nexus-adversary", "nexus-qa", "nexus-analyst", "nexus-architect", "nexus-docs", "nexus-supervisor", "nexus-security"}
INLINE_CMD = re.compile(r"\b(python[0-9.]*\s+-c|node\s+(-e|--eval)|perl\s+-[a-zA-Z]*e|ruby\s+-e)\b")
INLINE_WRITE = re.compile(r"\b(python[0-9.]*\s+-c|node\s+(-e|--eval)|perl\s+-[a-zA-Z]*e|ruby\s+-e)\b.*(open\(|write|unlink|rename|remove|rmtree|copy|move|mkdir)", re.S)
PHASES = ("F0F1", "F1", "F2", "SPEC_VERIFY", "SECURITY", "F2.5", "F3", "AR", "CR", "VERIFY", "F4", "DONE", "SUPERVISION")
VERSIONED = {"F0F1": ("work-item.md",), "F1": ("work-item.md",), "F2": ("sdd.md",), "F2.5": ("story-file.md",)}
PHASE_OUTPUT = {
    "F0F1": "work-item.md", "F1": "work-item.md", "F2": "sdd.md", "F2.5": "story-file.md",
    "AR": "ar-report.md", "CR": "cr-report.md", "VERIFY": "blq-verification.md", "SPEC_VERIFY": "sdd-verification.md", "SECURITY": "security-review.md",
    "F4": "validation.md", "DONE": "cierre.md",
}
WRITE_RULES = {
    "nexus-supervisor": r"(?!)",
    "nexus-security": r"/security-review(-\d+)?\.md$",
    "nexus-adversary": r"/(ar-report(-\d+)?|cr-report(-\d+)?|blq-verification(-\d+)?|sdd-verification(-\d+)?)\.md$",
    "nexus-qa": r"/validation(-\d+)?\.md$",
    "nexus-docs": r"/(cierre\.md|_INDEX\.md|lecciones\.md|_LECCIONES\.md)$",
    "nexus-architect": r"/doc/sdd/[^/]+/[^/]+\.md$",
    "nexus-analyst": r"(/doc/sdd/[^/]+/[^/]+\.md|/doc/sdd/_INDEX\.md|/doc/prd/.+|/(project|product)-context\.md)$",
    # El dev escribe codigo y sus notas; no los documentos aprobados ni los reportes de otros roles.
    "nexus-dev": r"^(?!.*/doc/sdd/[^/]+/(work-item|sdd|story-file|ar-report(-\d+)?|cr-report(-\d+)?|blq-verification(-\d+)?|sdd-verification(-\d+)?|security-review(-\d+)?|validation(-\d+)?|cierre(-\d+)?)\.md$)(?!.*/doc/sdd/[^/]+/\.(versions|violations)/)",
}
GIT_DESTRUCTIVE = re.compile(r"\bgit\b[^|;&]*\s(reset\s+--hard|checkout\s+--|checkout\s+\.|clean\s|restore\s|stash\b(?!\s+(list|show)\b)|pull\b)")
NO_VERIFY = re.compile(r"\bgit\b[^|;&]*\s(commit|push)\b[^|;&]*\s--no-verify\b")
GIT_WRITE = re.compile(r"\bgit\b[^|;&]*\s(commit|push|merge(?!-base)|rebase|apply|add|rm|mv|tag)\b")
FILE_MUTATION = re.compile(r"\btee\b|\b(sed|perl)\b[^|;&]*\s-[a-zA-Z]*i|\b(rm|mv|cp|chmod|chown|truncate|dd)\s")
REDIRECT = re.compile(r"(?<![0-9&<>])>>?\s*([^\s&|;]+)")


def deny(message):
    print(f"NEXUS GATE: {message}", file=sys.stderr)
    sys.exit(2)


def state_dir():
    base = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.expanduser("~/.claude/nexus-state")
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path


def session_file(data):
    name = re.sub(r"[^\w-]", "_", data.get("session_id") or "sin-sesion")
    return state_dir() / f"{name}.json"


def load_session(data):
    path = session_file(data)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"hu_dir": None, "delegated": False, "override": None, "spawns": []}


def save_session(data, session):
    atomic_write(session_file(data), json.dumps(session))


def atomic_write(path, text):
    """Se escribe aparte y se reemplaza de una vez: nadie lee el archivo a medio escribir.
    En la HU-2 de Nexus Control, AR y CR en paralelo dejaron leer el estado vacio y el hook freno un mensaje de la persona."""
    tmp = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else None


def abs_path(value, data):
    path = Path(value).expanduser()
    return path if path.is_absolute() else Path(data.get("cwd") or os.getcwd()) / path


def prompt_field(prompt, name):
    found = re.search(rf"^\s*{name}:\s*(\S.*?)\s*$", prompt, re.M)
    return found.group(1) if found else None


def read_gates(hu_dir):
    path = hu_dir / ".gates.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def save_version(hu_dir, name):
    """Copia de un documento por su hash en .versions/. Idempotente."""
    digest = sha(hu_dir / name)
    if digest is None:
        return None
    versions = hu_dir / ".versions"
    versions.mkdir(exist_ok=True)
    target = versions / f"{Path(name).stem}-{digest[:12]}.md"
    if not target.exists():
        target.write_bytes((hu_dir / name).read_bytes())
    return target


def record_gate(hu_dir, gate, by):
    doc = GATE_DOC.get(gate)
    entry = {"gate": gate, "by": by, "sha256": sha(hu_dir / doc) if doc else None, "ts": int(time.time())}
    if doc and entry["sha256"]:
        # Copia de lo aprobado: para comparar despues sin reconstruirlo desde un transcript.
        entry["copy"] = str(save_version(hu_dir, doc).relative_to(hu_dir))
    with (hu_dir / ".gates.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def write_state(hu_dir, **fields):
    """Estado por HU, para retomar despues de una compactacion o de otra sesion."""
    path = hu_dir / ".nexus-state.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    if state.get("phase") == "DONE" and state.get("status") == "done" and fields.get("phase") not in (None, "DONE"):
        # Repetir una fase sobre una HU cerrada (un QA corto, una verificacion) no la reabre: queda como repeticion.
        state["rerun"] = {"phase": fields.get("phase"), "agent": fields.get("agent"), "status": fields.get("status"),
                          "ts": int(time.time())}
        atomic_write(path, json.dumps(state, indent=1))
        return
    state.update(fields, updated=int(time.time()))
    atomic_write(path, json.dumps(state, indent=1))


def latest(hu_dir, stem):
    """cierre.md o cierre-2.md: el de numero mas alto es el vigente."""
    best, best_n = None, -1
    for path in hu_dir.glob(f"{stem}*.md"):
        found = re.fullmatch(rf"{re.escape(stem)}(?:-(\d+))?\.md", path.name)
        if found and int(found.group(1) or 1) > best_n:
            best, best_n = path, int(found.group(1) or 1)
    return best


def pipeline_of(hu_dir):
    item = hu_dir / "work-item.md"
    text = item.read_text(encoding="utf-8") if item.exists() else ""
    found = re.search(r"pipeline\W{0,6}(FAST\+AR|FAST|LAUNCH|QUALITY)", text, re.I)
    return found.group(1).upper() if found else "QUALITY"


def questions_section(hu_dir):
    item = hu_dir / "work-item.md"
    if not item.is_file():
        return None
    found = re.search(r"^#+ *PREGUNTAS PARA EL HUMANO[^\n]*\n(.*?)(?=^#+ |\Z)", item.read_text(encoding="utf-8"), re.M | re.S)
    return found.group(1) if found else None


def open_questions(hu_dir):
    return len(re.findall(r"^\s*- \[ \]", questions_section(hu_dir) or "", re.M))


def release_required(data, code_root):
    candidates = [abs_path(p, data) for p in (".", ".nexus", "docs")]
    if code_root:
        candidates.append(Path(code_root))
    for base in candidates:
        path = base / "project-context.md"
        if path.exists() and re.search(r"release_gate\W{0,6}true", path.read_text(encoding="utf-8"), re.I):
            return True
    return False


def require_gate(hu_dir, gate, session, phase, consume_override):
    entries = [e for e in read_gates(hu_dir) if e["gate"] == gate]
    if not entries and session.get("delegated") and gate != "RELEASE_APPROVED":
        problem = delegated_review_problem(hu_dir, gate) if session.get("supervised") else None
        if problem:
            consume_override(problem)
            return
        record_gate(hu_dir, gate, "claude-delegated")
        entries = read_gates(hu_dir)
        entries = [e for e in entries if e["gate"] == gate]
    if not entries:
        hint = "" if session.get("delegated") else ". Si era una corrida AUTO, la sesion no quedo delegada: la persona escribe /nexus-agile:nexus-auto al inicio de una linea"
        consume_override(f"{phase} requiere el gate {gate}, escrito por una persona. Registrados en {hu_dir}: {[e['gate'] for e in read_gates(hu_dir)] or 'ninguno'}{hint}")
        return
    doc = GATE_DOC.get(gate)
    current = sha(hu_dir / doc) if doc else None
    if doc and entries[-1].get("sha256") != current:
        consume_override(f"{doc} cambio despues de {gate}. Pidele a la persona que lo revise y vuelva a escribir {gate}")


def delegated_review_problem(hu_dir, gate):
    """Con --supervisor, un gate delegado necesita un veredicto del supervisor sobre la version actual del documento:
    CONTINUAR, o ESCALAR seguido de la respuesta de la persona. Antes, el hook lo registraba sin mirar si hubo revision."""
    doc = hu_dir / GATE_DOC[gate]
    changed = int(doc.stat().st_mtime) if doc.is_file() else 0
    entries = read_gates(hu_dir)
    reviews = [e for e in entries if e.get("gate") == "SUPERVISION" and e.get("ts", 0) >= changed]
    if not reviews:
        return (f"{gate} delegado necesita un veredicto del supervisor sobre la version actual de {doc.name}. "
                f"Consultalo (FASE: SUPERVISION) antes de lanzar la fase")
    last = reviews[-1]
    if last.get("verdict") == "CONTINUAR":
        return None
    if last.get("verdict") == "ESCALAR":
        if any(e.get("gate") == "DECISION" and e.get("ts", 0) >= last.get("ts", 0) for e in entries):
            return None
        return f"el supervisor escalo {gate} y falta la respuesta de la persona. Preguntale con lo que el supervisor dejo listo"
    return f"el ultimo veredicto del supervisor es {last.get('verdict')}: reune lo que pide y consultalo de nuevo"


def pending_escalation(hu_dir):
    """True si el ultimo veredicto del supervisor es ESCALAR y la persona todavia no respondio."""
    entries = read_gates(hu_dir)
    reviews = [e for e in entries if e.get("gate") == "SUPERVISION"]
    if not reviews or reviews[-1].get("verdict") != "ESCALAR":
        return False
    return not any(e.get("gate") == "DECISION" and e.get("ts", 0) >= reviews[-1].get("ts", 0) for e in entries)


def record_decision(hu_dir, answer, via):
    entry = {"gate": "DECISION", "by": "human", "via": via, "answer": answer[:300], "ts": int(time.time())}
    with (hu_dir / ".gates.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def spec_verify_required(data, session):
    """QUALITY verifica el SDD contra el codigo salvo que el proyecto declare spec_verify: false."""
    bases = [session.get("nexus_root"), data.get("cwd"), os.environ.get("NEXUS_ROOT")]
    for base in filter(None, bases):
        for sub in (".nexus", ".", "docs"):
            path = Path(base) / sub / "project-context.md"
            if path.is_file():
                return not re.search(r"spec_verify\W{0,6}false", path.read_text(encoding="utf-8"))
    return True


def spec_verification_problem(hu_dir):
    report = latest(hu_dir, "sdd-verification")
    if report is None:
        return "QUALITY requiere sdd-verification.md (FASE: SPEC_VERIFY) antes de F3"
    text = report.read_text(encoding="utf-8")
    status = re.search(r"^STATUS:\s*(.+)$", text, re.M)
    if status is None:
        return f"{report.name} no tiene la linea STATUS:"
    if re.search(r"falsas=[1-9]", status.group(1)):
        return f"{report.name} tiene afirmaciones falsas sin corregir: {status.group(1)}"
    verified = re.search(r"^SDD_SHA256:\s*([0-9a-f]{64})", text, re.M)
    if verified is None or verified.group(1) != sha(hu_dir / "sdd.md"):
        return f"{report.name} verifico otra version de sdd.md: verifica la aprobada"
    return None


def security_review_required(hu_dir):
    """El analista marca security_review: required cuando la HU toca auth, permisos, datos, pagos, RLS o entradas publicas."""
    item = hu_dir / "work-item.md"
    return item.is_file() and bool(re.search(r"security_review\W{0,6}required", item.read_text(encoding="utf-8")))


def security_review_problem(hu_dir):
    report = latest(hu_dir, "security-review")
    if report is None:
        return "el work-item pide security_review: falta security-review.md (FASE: SECURITY) antes de F3"
    text = report.read_text(encoding="utf-8")
    status = re.search(r"^STATUS:\s*(.+)$", text, re.M)
    if status is None:
        return f"{report.name} no tiene la linea STATUS:"
    if re.search(r"(altos|medios)=[1-9]", status.group(1)):
        return f"{report.name} tiene hallazgos de seguridad abiertos: {status.group(1)}"
    reviewed = re.search(r"^SDD_SHA256:\s*([0-9a-f]{64})", text, re.M)
    if reviewed is None or reviewed.group(1) != sha(hu_dir / "sdd.md"):
        return f"{report.name} reviso otra version de sdd.md: revisa la aprobada"
    return None


def check_skill_dir(prompt):
    """Con el plugin, SKILL_DIR debe apuntar al plugin: en la prueba real apuntaba a la version vieja de ~/.claude."""
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not root:
        return
    expected = f"{root.rstrip('/')}/.claude/skills/nexus-agile"
    found = re.search(r"SKILL_DIR=([^·\n]*?)\s*(?:·|$)", prompt, re.M)
    if not found:
        deny(f"RUTAS: falta SKILL_DIR=. Con el plugin es {expected}")
    value = found.group(1).strip()
    if "CLAUDE_PLUGIN_ROOT" in value:
        return
    if not value or value.startswith("[valor"):
        deny(f"RUTAS: tiene SKILL_DIR sin resolver. Con el plugin es {expected}")
    if value.startswith("["):
        return  # instruccion para el agente, que busca primero en el plugin
    real = os.path.realpath(os.path.expanduser(value))
    if not real.startswith(os.path.realpath(root) + os.sep):
        deny(f"SKILL_DIR={value} esta fuera del plugin y correria otra version. Usa {expected}")


def check_phase(data, session):
    tool_input = data.get("tool_input") or {}
    prompt = tool_input.get("prompt") or ""
    phase = prompt_field(prompt, "FASE")
    hu_value = prompt_field(prompt, "HU_DIR")
    agent = (tool_input.get("subagent_type") or "").split(":")[-1]
    if not phase or not hu_value:
        deny(f"el prompt de {agent} debe traer las lineas FASE: y HU_DIR:")
    if phase not in PHASES:
        deny(f"fase desconocida {phase}. Validas: {', '.join(PHASES)}")
    hu_dir = abs_path(hu_value, data)
    if os.environ.get("CLAUDE_PLUGIN_ROOT") and ":" not in (tool_input.get("subagent_type") or ""):
        deny(f"esta sesion usa el plugin: lanza nexus-agile:{agent}. Sin prefijo correria otra version instalada")
    check_skill_dir(prompt)
    routes = re.search(r"CODE_ROOT=([^\s·]+)", prompt)
    if routes and routes.group(1).startswith("["):
        deny("RUTAS: tiene CODE_ROOT sin resolver. Pasa la ruta real")
    code_root = str(abs_path(routes.group(1), data)) if routes else (data.get("cwd") or os.getcwd())
    if phase not in ("F0F1", "F1", "SUPERVISION") and not is_git_repo(code_root):
        deny(f"{code_root} no es un repo git. Pasa CODE_ROOT= en la linea RUTAS:")
    nexus = re.search(r"NEXUS_ROOT=([^\s·]+)", prompt)
    if nexus and not nexus.group(1).startswith("["):
        session["nexus_root"] = str(abs_path(nexus.group(1), data))

    def blocked(message):
        if session.get("override"):
            record_override(hu_dir, session, message)
            return
        deny(f"{message}. Si es un falso positivo, la persona puede escribir NEXUS_OVERRIDE <motivo>")

    def need(name):
        if not (hu_dir / name).is_file() or not (hu_dir / name).stat().st_size:
            blocked(f"{phase} requiere {hu_dir / name}")

    if phase not in ("F0F1", "F1") and not hu_dir.is_dir():
        blocked(f"no existe HU_DIR {hu_dir}")
    if phase in ("F0F1", "F1") and not (hu_dir / "work-item.md").is_file():
        # Gate de propiedad: antes del primer analista, alguien miro en el tracker quien tiene la HU.
        ownership = prompt_field(prompt, "PROPIEDAD")
        if not ownership or ownership.startswith("["):
            blocked("falta la linea PROPIEDAD: con el resultado del gate de propiedad (references/tracker.md): "
                    "propia, libre, autorizada o ajena, con la evidencia del tracker")
        elif re.match(r"(?i)ajena\b", ownership):
            blocked(f"la HU es de otra persona o sesion ({ownership}). Escala: tomarla lo decide la persona")
        elif not re.match(r"(?i)(propia|libre|autorizada)\b", ownership):
            blocked(f"PROPIEDAD: {ownership} no es propia, libre, autorizada ni ajena")
    pipeline = pipeline_of(hu_dir) if hu_dir.is_dir() else "QUALITY"
    has_spec = pipeline in ("QUALITY",)
    # unified es el default: solo un contract_mode: classic explicito pide Story File.
    classic = hu_dir.is_dir() and any(
        (hu_dir / n).exists() and re.search(r"contract_mode\W{0,6}classic", (hu_dir / n).read_text(encoding="utf-8"))
        for n in ("work-item.md", "sdd.md"))

    if phase in ("F2", "F3") and hu_dir.is_dir():
        pending = open_questions(hu_dir)
        if pending:
            blocked(f"work-item.md tiene {pending} pregunta(s) sin responder en PREGUNTAS PARA EL HUMANO")

    if phase == "F2":
        need("work-item.md")
        require_gate(hu_dir, "HU_APPROVED", session, phase, blocked)
    elif phase in ("SPEC_VERIFY", "SECURITY"):
        need("sdd.md")
        require_gate(hu_dir, "HU_APPROVED", session, phase, blocked)
    elif phase == "F2.5":
        need("sdd.md")
        require_gate(hu_dir, "SPEC_APPROVED", session, phase, blocked)
        if not classic:
            blocked("sin contract_mode: classic no hay F2.5: el contrato va en la seccion Contrato de implementacion de sdd.md")
    elif phase == "F3":
        need("work-item.md")
        require_gate(hu_dir, "HU_APPROVED", session, phase, blocked)
        if has_spec:
            need("sdd.md")
            require_gate(hu_dir, "SPEC_APPROVED", session, phase, blocked)
            if spec_verify_required(data, session):
                problem = spec_verification_problem(hu_dir)
                if problem:
                    blocked(problem)
            if security_review_required(hu_dir):
                problem = security_review_problem(hu_dir)
                if problem:
                    blocked(problem)
            if classic:
                need("story-file.md")
            elif not (hu_dir / "story-file.md").is_file() and "Contrato de implementaci" not in (hu_dir / "sdd.md").read_text(encoding="utf-8"):
                # Una HU anterior a este default puede traer su story-file.md: sigue valiendo.
                blocked("sdd.md no tiene la seccion Contrato de implementacion (contract_mode: unified, el default)")
    elif phase == "F4" and pipeline not in ("FAST", "LAUNCH"):  # LAUNCH no tiene AR ni CR (SKILL.md)
        for stem in ("ar-report", "cr-report"):
            report = latest(hu_dir, stem)
            if report is None:
                blocked(f"F4 requiere {stem}.md")
                continue
            status = re.search(r"^STATUS:\s*(.+)$", report.read_text(encoding="utf-8"), re.M)
            if status is None:
                blocked(f"{report.name} no tiene la linea STATUS:")
            elif "RECHAZADO" in status.group(1) or re.search(r"open_blq=[1-9]", status.group(1)):
                blocked(f"{report.name} tiene BLOQUEANTEs abiertos: {status.group(1)}")
    elif phase == "DONE":
        report = latest(hu_dir, "validation")
        if report is None:
            blocked("DONE requiere validation.md")
        else:
            status = re.search(r"^STATUS:\s*(.+)$", report.read_text(encoding="utf-8"), re.M)
            if status is None or "APROBADO" not in status.group(1):
                blocked(f"{report.name} no tiene STATUS: APROBADO")
        if release_required(data, code_root):
            require_gate(hu_dir, "RELEASE_APPROVED", session, phase, blocked)

    session["hu_dir"] = str(hu_dir)
    session["spawns"].append({"agent": agent, "phase": phase, "hu_dir": str(hu_dir), "code_root": code_root, "tree": tree_hash(code_root),
                              "ts": int(time.time())})
    save_session(data, session)
    if hu_dir.is_dir():
        write_state(hu_dir, phase=phase, agent=agent, pipeline=pipeline, status="running")


def record_override(hu_dir, session, message):
    if hu_dir.is_dir():
        with (hu_dir / ".gates.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"gate": "OVERRIDE", "by": "human", "reason": session["override"], "blocked": message, "ts": int(time.time())}) + "\n")
    session["override"] = None


def disposable(path, data):
    """Una copia en /tmp sirve, salvo que el propio proyecto viva bajo /tmp."""
    cwd = str(data.get("cwd") or os.getcwd())
    return path.startswith("/tmp/") and not path.startswith(cwd.rstrip("/") + "/")


QUOTED = re.compile(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n.*?\n\s*\2\b", re.S)
ASSIGN = re.compile(r"(?:^|[;&|]\s*|\bexport\s+)([A-Za-z_]\w*)=(['\"]?)(/[^\s'\"$`;&|]*)\2(?=\s*(?:$|[;&|]))")


ASSIGN_ANY = re.compile(r"(?:^|[;&|\n][ \t]*|\bexport\s+)([A-Za-z_]\w*)=(['\"]?)([^\s'\";&|`]*)\2(?=[ \t]*(?:$|[;&|\n]))")


def expand_vars(command):
    """Expande $X y ${X} cuando el mismo comando asigna X a una ruta, tambien encadenada (W=$S/copia).
    Lo que viene de otra llamada, se reasigna con otro valor o no queda en una ruta literal, no se adivina."""
    values, seen = {}, {}
    # Una asignacion dentro del cuerpo de un heredoc es texto del archivo que se escribe, no del shell:
    # en la HU-3 de Nexus Control, un S="$S/..." en el script de QA anulo el S del comando y el hook bloqueo $S/mk.py.
    shell_only = HEREDOC.sub(lambda m: m.group(0)[: m.group(0).index("\n")] + "\n", command)
    for name, _, raw in ASSIGN_ANY.findall(shell_only):
        value = re.sub(r"\$\{(\w+)\}|\$(\w+)", lambda m: values.get(m.group(1) or m.group(2), m.group(0)), raw)
        resolved = os.path.normpath(value) if value.startswith("/") and "$" not in value else None
        seen.setdefault(name, set()).add(resolved)
        if resolved:
            values[name] = resolved
    for name, value in values.items():
        if len(seen[name]) != 1:
            continue
        command = re.sub(r"\$\{" + name + r"\}|\$" + name + r"\b", lambda _: value, command)
    return command


def masked(command):
    """El comando con el contenido de comillas y de heredocs tapado, mismas posiciones."""
    text = HEREDOC.sub(lambda m: m.group(0)[: m.group(0).index("\n")] + re.sub(r"[^\n]", "x", m.group(0)[m.group(0).index("\n"):]), command)
    return QUOTED.sub(lambda m: m.group(0)[0] + "x" * (len(m.group(0)) - 2) + m.group(0)[-1], text)


def redirect_targets(command):
    """Destinos de > y >> reales: ignora los que estan dentro de comillas o en el cuerpo de un heredoc."""
    return [t for t, _ in redirect_targets_at(command)]


def redirect_targets_at(command):
    return [(command[m.start(1):m.end(1)].strip("'\""), m.start(1)) for m in REDIRECT.finditer(masked(command))]


CD = re.compile(r"(?:^|[;&|\n]\s*)cd\s+(['\"]?)(/[^'\"\s;&|]+)\1\s*(?=&&|;|\n|$)")


def single_cd(command):
    """(posicion, directorio) del unico `cd /ruta` del comando, este donde este (despues de asignar variables, en otra linea).
    Con mas de un cd, o con pushd, no se adivina: (None, None)."""
    # Un cd dentro de un subshell, `(cd X && ...)`, no cambia el directorio del resto del comando: no cuenta.
    top = re.sub(r"\(\s*cd\b[^()]*\)", lambda m: " " * len(m.group(0)), command)
    found = list(CD.finditer(top))
    if len(found) != 1 or len(re.findall(r"\b(cd|pushd)\b", top)) != 1:
        return None, None
    return found[0].end(), os.path.normpath(found[0].group(2))


def mutation_targets(command, visible, data):
    """Archivos que tocan rm, mv, cp, tee, sed -i y compania, resueltos contra el ultimo cd.
    Las palabras se cortan sobre el texto con las comillas tapadas: un script de sed con espacios es una sola palabra."""
    targets = []
    for match in FILE_MUTATION.finditer(visible):
        end = re.search(r"[;&|\n]", visible[match.end():])
        stop = match.end() + end.start() if end else len(visible)
        tool = match.group(0).split()[0] if match.group(0).split() else ""
        words = [(command[match.end() + m.start():match.end() + m.end()], match.end() + m.start())
                 for m in re.finditer(r"\S+", visible[match.end():stop])]
        if tool in ("sed", "perl"):
            words = [w for w in words if not w[0].startswith("-")][1:]  # el primero es el script
        elif tool == "dd":
            words = [(w[3:], pos + 3) for w, pos in words if w.startswith("of=")]
        elif tool == "cp":
            words = [w for w in words if not w[0].startswith("-")][-1:]  # cp solo escribe el destino; mv tambien borra el origen
        if tool in ("chmod", "chown"):
            words = [w for w in words if not w[0].startswith("-")][1:]  # el primero es el modo o el duenio
        for word, pos in words:
            if word.startswith("-") or word in ("<", ">"):
                continue
            targets.append(resolve_at(command, word.strip("'\""), pos, data))
    return targets


def mutations_disposable(command, visible, data):
    """True si cada archivo que tocan rm, mv, cp, tee, sed -i y compania resuelve a una ruta desechable.
    En la HU-3 de Nexus Control, QA corrio `cd <repo>; rm -rf $S` con S en /tmp, y el cd al repo lo hizo parecer una escritura."""
    targets = mutation_targets(command, visible, data)
    return bool(targets) and all(t == "/dev/null" or disposable(t, data) or t.startswith(("$TMPDIR", "${TMPDIR")) for t in targets)


def leading_cd(command):
    """Directorio del unico cd del comando, si va antes que cualquier escritura. Se mantiene por compatibilidad."""
    return single_cd(command)[1]


def cd_base_at(command, position, default):
    """Directorio vigente en `position`: el del ultimo `cd /ruta` antes de esa posicion, fuera de subshells.
    Si antes hubo un cd que no se puede resolver (`cd ..`, `cd $X` sin asignar, pushd), devuelve None."""
    top = re.sub(r"\(\s*cd\b[^()]*\)", lambda m: " " * len(m.group(0)), command[:position])
    if re.search(r"\bpushd\b", top):
        return None
    literal = {m.start(): m for m in CD.finditer(top)}
    base = default
    for word in re.finditer(r"(?:^|[;&|\n][ \t]*)cd\b", top):
        match = next((m for start, m in literal.items() if start == word.start()), None)
        if match is None:
            return None
        base = os.path.normpath(match.group(2))
    return base


def resolve_at(command, target, position, data):
    """Ruta absoluta de `target`, que aparece en `position`, relativa al ultimo cd anterior (o al cwd)."""
    if target.startswith(("/", "$", "~")):
        return os.path.normpath(os.path.expanduser(target)) if not target.startswith("$") else target
    base = cd_base_at(command, position, str(data.get("cwd") or os.getcwd()))
    if base is None:
        return target  # no se sabe donde esta: queda relativa y no cuenta como desechable
    return os.path.normpath(os.path.join(base, target))


def absolute(target, base):
    if base and not target.startswith(("/", "$", "~")):
        return os.path.normpath(os.path.join(base, target))
    return target


def is_git_repo(path):
    try:
        return subprocess.run(["git", "-C", path, "rev-parse", "--git-dir"], capture_output=True, timeout=20).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def forbidden_pattern(data, session):
    """Comandos que el proyecto prohibe a todos, incluida la sesion principal."""
    bases = [session.get("nexus_root"), data.get("cwd"), os.environ.get("NEXUS_ROOT")]
    for base in filter(None, bases):
        for sub in (".nexus", ".", "docs"):
            path = Path(base) / sub / "project-context.md"
            if path.is_file():
                found = re.search(r"forbidden_commands\W+`([^`]+)`", path.read_text(encoding="utf-8"))
                return found.group(1) if found else None
    return None


def check_forbidden(command, data):
    pattern = forbidden_pattern(data, load_session(data))
    if not pattern:
        return
    try:
        matched = re.search(pattern, command)
    except re.error as error:
        deny(f"forbidden_commands no es una expresion valida: {error}")
    if matched:
        deny(f"el proyecto prohibe este comando ({matched.group(0)}). Detente y preguntale a la persona")


def check_bash(agent, command, data):
    # Solo si el comando escribe en .gates.jsonl. Nombrarlo dentro de comillas o de un heredoc (una nota en la bitacora) no cuenta.
    visible = masked(command)
    expanded = expand_vars(command)
    # Lo que decide es a donde apunta cada mencion de .gates.jsonl, con variables y cd resueltos: un archivo de
    # prueba en /tmp se puede crear, el de una HU no. Se probo con los comandos literales de tres corridas reales.
    mentions = [(m.group(0).strip("'\"();"), m.start()) for m in re.finditer(r"[^\s'\"=]*\.gates\.jsonl", expanded)]
    outside = [t for t, pos in mentions if not disposable(resolve_at(expanded, t, pos, data), data)]
    if outside and (any(t.endswith(".gates.jsonl") for t in redirect_targets(expanded))
                    or FILE_MUTATION.search(masked(expanded)) or INLINE_WRITE.search(command)):
        deny("los gates solo los registra el hook")
    check_forbidden(command, data)
    if NO_VERIFY.search(command):
        deny("no se usa --no-verify: arregla lo que el hook del repo rechaza")
    if agent not in READ_ONLY_BASH:
        return
    if GIT_DESTRUCTIVE.search(visible) or GIT_WRITE.search(visible):
        deny(f"{agent} no modifica el repo con git: {command[:80]}")
    command = expand_vars(command)
    visible = masked(command)
    # El interprete tiene que estar fuera de comillas (un grep que busca "python -c" no es un interprete); lo que escribe va adentro.
    if INLINE_CMD.search(visible) and INLINE_WRITE.search(command) and \
            not any(disposable(w.strip("'\"()"), data) for w in re.split(r"[\s,]+", command)):
        deny(f"{agent} no escribe con un interprete en linea. Si necesita un cambio, usa Write o Edit donde su rol lo permite, o reportalo")
    base = leading_cd(command)
    for target, position in redirect_targets_at(command):
        if not (target == "/dev/null" or disposable(resolve_at(command, target, position, data), data)
                or target.startswith(("$TMPDIR", "${TMPDIR"))):
            hint = ("Un artefacto de la HU se escribe con Write o Edit" if "doc/sdd/" in resolve_at(command, target, position, data)
                    else "Usa una ruta absoluta en /tmp, escrita en el mismo comando")
            deny(f"{agent} no escribe archivos por Bash ({target}). {hint}")
    if base:
        # Dentro de un cd a /tmp, toda ruta absoluta tambien debe ser desechable, y nada sube con "..".
        # El ".." que cuenta es el de una ruta, no el de un texto entre comillas (un import en un sed).
        cut = visible.index("&&") + 2 if "&&" in visible else visible.index(";") + 1
        rest, rest_visible = command[cut:], visible[cut:]
        paths = [w.strip("'\"") for w in rest.split() if w.strip("'\"").startswith("/")]
        safe = disposable(base + "/", data) and ".." not in rest_visible and all(disposable(p, data) or p == "/dev/null" for p in paths)
    else:
        # Laxo a proposito: alcanza con una palabra en /tmp. Endurecerlo frena, en las corridas reales, docker cp,
        # docker rm y carpetas de mktemp; queda pendiente con su propia prueba.
        safe = any(disposable(w, data) or "TMPDIR" in w for w in command.split())
    # Un patron de grep entre comillas ('cp |tee |sed -i') no es una mutacion.
    # Juzgar por archivo solo vale si nada mas escribe: un interprete en linea despues de un cd al repo puede tocarlo.
    inline = (INLINE_CMD.search(visible) and INLINE_WRITE.search(command)) or \
        re.search(r"\b(python[0-9.]*|node|ruby|perl|bash|sh)\s+(-I\s+)?-\s*<<|<<\S*\s*\|\s*(python[0-9.]*|node|ruby|perl|bash|sh)\b", visible)
    if FILE_MUTATION.search(visible) and not safe and (inline or not mutations_disposable(command, visible, data)):
        deny(f"{agent} tiene Bash de solo lectura: {command[:80]}")


def cmd_gate(data):
    tool = data.get("tool_name") or ""
    tool_input = data.get("tool_input") or {}
    agent = (data.get("agent_type") or "").split(":")[-1]
    if tool in ("Agent", "Task"):
        target = (tool_input.get("subagent_type") or "").split(":")[-1]
        if target.startswith("nexus-"):
            check_phase(data, load_session(data))
        return
    if tool in ("Write", "Edit"):
        path = str(abs_path(tool_input.get("file_path") or "", data))
        if path.endswith(".gates.jsonl") and not disposable(path, data):
            deny("los gates solo los registra el hook")
        rule = WRITE_RULES.get(agent)
        if rule and not disposable(path, data) and not re.search(rule, path):
            deny(f"{agent} no puede escribir {path}. Reporta el hallazgo en lugar de modificarlo")
    if tool in ("Write", "Edit") and agent:
        with (state_dir() / "writes.log").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps({"path": path, "ts": time.time()}) + "\n")
    elif tool == "Bash":
        check_bash(agent, tool_input.get("command") or "", data)
        if agent.startswith("nexus-"):
            check_bash_into_hu_dir(agent, tool_input.get("command") or "", data)
        if agent.startswith("nexus-"):
            snapshot_artifacts(data)


def check_bash_into_hu_dir(agent, command, data):
    """Una redireccion a un archivo de HU_DIR se frena antes de correr. Restaurar despues no alcanza:
    en la primera HU de un proyecto nuevo, el mismo comando hizo git commit y la version prohibida quedo en el historial."""
    hu_dir = load_session(data).get("hu_dir")
    if not hu_dir:
        return
    root = os.path.realpath(hu_dir) + os.sep
    expanded = expand_vars(command)
    base = leading_cd(expanded) or str(data.get("cwd") or os.getcwd())
    for target in redirect_targets(expanded):
        if target == "/dev/null" or target.startswith("$"):
            continue
        resolved = os.path.realpath(os.path.join(base, os.path.expanduser(target)))
        if resolved.startswith(root):
            deny(f"{agent} no escribe artefactos de la HU por Bash ({target}). Usa Write o Edit, y el commit en otro comando")
    # Lo mismo con sed -i, tee, cp, mv y rm: en la HU-4 de Nexus Control, el dev corrio un sed -i sobre su
    # auto-blindaje.md y el git commit del mismo comando guardo la version del sed antes de que el hook la revirtiera.
    for target in mutation_targets(expanded, masked(expanded), data):
        if target.startswith("$"):
            continue
        if os.path.realpath(target).startswith(root):
            deny(f"{agent} no modifica artefactos de la HU por Bash ({os.path.basename(target)}). Usa Edit o Write, y el commit en otro comando")


def artifact_hashes(hu_dir):
    return {str(p): sha(p) for p in sorted(Path(hu_dir).glob("*")) if p.is_file() and p.name != ".nexus-state.json"}


def snapshot_file(data):
    return state_dir() / ("bash-" + re.sub(r"[^\w-]", "_", data.get("tool_use_id") or "sin-id") + ".json")


def snapshot_artifacts(data):
    """Antes de cada Bash de un agente: hash de los artefactos de la HU, para ver despues si el comando los cambio."""
    hu_dir = load_session(data).get("hu_dir")
    if hu_dir and Path(hu_dir).is_dir():
        contents = {str(p): base64.b64encode(p.read_bytes()).decode() for p in Path(hu_dir).glob("*")
                    if p.is_file() and p.name not in (".nexus-state.json", ".gates.jsonl") and p.stat().st_size <= 1_000_000}
        atomic_write(snapshot_file(data), json.dumps({"hu_dir": hu_dir, "ts": time.time(), "hashes": artifact_hashes(hu_dir),
                                                     "contents": contents}))
    # Las fotos de un Bash cancelado no las borra nadie, y guardan copias de los artefactos (con datos del cliente).
    for old in state_dir().glob("bash-*.json"):
        try:
            if old.stat().st_mtime < time.time() - 6 * 3600:
                old.unlink()
        except OSError:
            pass


def cmd_after_bash(data):
    """Bloqueo por destino real: si un Bash de un agente cambio un artefacto, no importa como estaba escrito el comando."""
    path = snapshot_file(data)
    if not path.exists():
        return
    before = json.loads(path.read_text(encoding="utf-8"))
    path.unlink()
    since = before["ts"]
    written = set()
    log = state_dir() / "writes.log"
    if log.exists():
        recent = []
        for line in log.read_text(encoding="utf-8").splitlines():
            entry = json.loads(line)
            if entry["ts"] >= since - 1:
                written.add(entry["path"])
            if entry["ts"] >= time.time() - 86400:
                recent.append(line)
        log.write_text("".join(l + "\n" for l in recent), encoding="utf-8")
    after = artifact_hashes(before["hu_dir"])
    changed = sorted(f for f in set(before["hashes"]) | set(after)
                     if before["hashes"].get(f) != after.get(f) and f not in written and not f.endswith(".gates.jsonl"))
    if not changed:
        return
    agent = (data.get("agent_type") or "").split(":")[-1]
    restored = restore(before, changed)
    with (Path(before["hu_dir"]) / ".gates.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps({"gate": "VIOLATION", "by": agent, "files": changed, "restored": restored,
                                 "command": ((data.get("tool_input") or {}).get("command") or "")[:300], "ts": int(time.time())}) + "\n")
    names = ", ".join(Path(f).name for f in changed)
    print(f"NEXUS GATE: este comando Bash cambio {names}. Los artefactos solo se escriben con Write o Edit, y solo los de tu rol. "
          "El hook restauro la version anterior y guardo la modificada en .violations/. Quedo registrado en .gates.jsonl. "
          "Detente y reportalo al orquestador con el comando literal; no vuelvas a intentarlo.", file=sys.stderr)
    sys.exit(2)


def restore(before, changed):
    """Deja el artefacto como estaba antes del Bash. La version modificada queda en .violations/ para la persona."""
    keep = Path(before["hu_dir"]) / ".violations"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    restored = []
    for name in changed:
        path = Path(name)
        if path.is_file():
            keep.mkdir(exist_ok=True)
            shutil.copy2(path, keep / f"{path.name}.{stamp}")
        old = before.get("contents", {}).get(name)
        if old is not None:
            path.write_bytes(base64.b64decode(old))
            restored.append(path.name)
        elif name not in before["hashes"] and path.is_file():
            path.unlink()  # creado por el Bash: queda solo en .violations/
            restored.append(path.name)
    return restored


def find_hu_dir(data, session, reference):
    if reference:
        direct = abs_path(reference, data)
        if direct.is_dir():
            return direct
        roots = [os.environ.get("NEXUS_ROOT"), data.get("cwd"), os.environ.get("CLAUDE_PROJECT_DIR")]
        for root in filter(None, roots):
            found = sorted(Path(root).glob(f"doc/sdd/{reference}*"))
            if found:
                return found[0]
    return Path(session["hu_dir"]) if session.get("hu_dir") else None


def cmd_prompt(data):
    prompt = (data.get("prompt") or "").strip()
    session = load_session(data)
    # El comando al inicio de cualquier linea: en la segunda HU real venia en medio de un bloque de instrucciones
    # y la sesion quedo sin delegar. Se confirma en voz alta para que la persona sepa que delego.
    if re.search(r"^\s*(?:[-*]\s*)?(?:(?:lanza|lanz[aá]|corre|corr[eé]|usa|us[aá]|run)\s+)?/(nexus-agile:)?nexus-auto\b", prompt, re.M | re.I):
        session["delegated"] = True
        session["supervised"] = bool(re.search(r"--supervisor\b", prompt))
        save_session(data, session)
        print("NexusAgil: sesion delegada (AUTO). HU_APPROVED y SPEC_APPROVED los registra Claude tras la revision clinica; "
              "RELEASE_APPROVED sigue siendo humano.")
        return
    override = re.match(r"NEXUS_OVERRIDE\s+(\S.*)$", prompt, re.S)
    if override:
        session["override"] = override.group(1).strip()
        save_session(data, session)
        print("NexusAgil: el proximo bloqueo se deja pasar y queda registrado con este motivo.")
        return
    hu_dir = Path(session["hu_dir"]) if session.get("hu_dir") else None
    if session.get("supervised") and hu_dir and hu_dir.is_dir() and pending_escalation(hu_dir):
        # La respuesta a un escalado puede llegar escrita en el chat, no solo en la ventana de opciones.
        record_decision(hu_dir, prompt, "texto")
    found = re.fullmatch(rf"({'|'.join(GATES)})(?:\s+(\S+))?", prompt)
    if found:
        apply_gate(data, session, found.group(1), found.group(2))
    elif len(prompt) <= 400 and re.search(rf"\b({'|'.join(GATES)})\b", prompt):
        # En la primera HU de un proyecto nuevo, "agregalo al Scope OUT y HU_APPROVED" no registro el gate y nadie lo dijo.
        print("NexusAgil: el gate NO se registro. Un gate cuenta solo si es el mensaje entero (por ejemplo, `HU_APPROVED`), "
              "en un mensaje aparte y despues de que el documento este como lo queres aprobar. Decile esto a la persona.")


def apply_gate(data, session, gate, reference):
    hu_dir = find_hu_dir(data, session, reference)
    if hu_dir is None or not hu_dir.is_dir():
        print(f"NexusAgil: no se pudo ubicar la HU de {gate}. La persona debe escribir: {gate} <NNN o ruta>")
        return
    record_gate(hu_dir, gate, "human")
    session["hu_dir"] = str(hu_dir)
    save_session(data, session)
    print(f"NexusAgil: {gate} registrado para {hu_dir}. Si hay memoria, actualiza el reclamo trabajo/<HU> con la fase nueva.")


def cmd_answer(data):
    """Respuesta a AskUserQuestion: elegir la opcion con el nombre del gate tambien cuenta."""
    text = json.dumps(data.get("tool_response") or "")
    session = load_session(data)
    hu_dir = Path(session["hu_dir"]) if session.get("hu_dir") else None
    if session.get("supervised") and hu_dir and hu_dir.is_dir() and pending_escalation(hu_dir):
        record_decision(hu_dir, json.dumps(data.get("tool_response") or "", ensure_ascii=False), "ventana")
    for gate in GATES:
        if re.search(rf'":\s*\\?"{gate}\\?"', text) or f'"{gate}"' in text:
            apply_gate(data, session, gate, None)


def tree_hash(code_root):
    # Los artefactos pueden vivir dentro del repo y no cuentan como cambio de codigo.
    scope = ["--", ".", ":(exclude)doc/sdd", ":(exclude)doc/prd", ":(exclude)project-context.md", ":(exclude)product-context.md", ":(exclude).nexus"]
    try:
        outputs = [subprocess.run(["git", "-C", code_root, *args], capture_output=True, text=True, timeout=20).stdout
                   for args in (["status", "--porcelain", *scope], ["diff", *scope], ["rev-parse", "HEAD"])]
    except (OSError, subprocess.SubprocessError):
        return None
    return hashlib.sha256("\0".join(outputs).encode()).hexdigest()


VERDICT = re.compile(r"VEREDICTO:\s*(CONTINUAR|PEDIR_EVIDENCIA|ESCALAR)\b")


def record_supervision(hu_dir, transcript):
    """Cada veredicto del supervisor queda en .gates.jsonl, con el punto de parada, para medir AUTO sin leer transcripts.
    En la HU-4 de Nexus Control, la herramienta que los cuenta tuvo que leerlos de los transcripts porque no estaban en ningun archivo."""
    if not transcript or not Path(transcript).is_file():
        return True  # sin transcript no hay de donde leerlo; no es culpa del supervisor
    verdict = None
    with open(transcript, encoding="utf-8", errors="replace") as handle:
        for raw in handle:
            try:
                message = json.loads(raw).get("message") or {}
            except ValueError:
                continue
            if message.get("role") != "assistant":
                continue
            found = VERDICT.findall(json.dumps(message.get("content"), ensure_ascii=False))
            verdict = found[-1] if found else verdict
    point = re.search(r"Punto de parada:\s*([^\n]{1,160})", transcript_prompt(transcript))
    entry = {"gate": "SUPERVISION", "by": "nexus-supervisor", "verdict": verdict,
             "point": point.group(1).strip() if point else None, "ts": int(time.time())}
    with (hu_dir / ".gates.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return verdict is not None


def transcript_prompt(path):
    """El prompt original del sub-agente, para saber que fase corrio en AR+CR paralelos."""
    if not path or not Path(path).is_file():
        return ""
    with open(path, encoding="utf-8") as handle:
        for raw in handle:
            if "FASE:" in raw:
                try:
                    return json.dumps(json.loads(raw), ensure_ascii=False).replace("\\n", "\n")
                except ValueError:
                    return raw
    return ""


def cmd_stop(data):
    if data.get("stop_hook_active"):
        return
    agent = (data.get("agent_type") or "").split(":")[-1]
    if not agent.startswith("nexus-"):
        return
    session = load_session(data)
    mine = [s for s in session["spawns"] if s["agent"] == agent]
    transcript = data.get("agent_transcript_path")
    finished = session.setdefault("finished", [])
    if mine:
        found_phase = re.search(r"FASE:\s*([A-Z0-9.]+)", transcript_prompt(transcript))
        phase_found = found_phase.group(1) if found_phase else None
        spawn = next((s for s in mine if s["phase"] == phase_found), mine[0])
        session["spawns"].remove(spawn)
        spawn["transcript"] = transcript
        finished.append(spawn)
        del finished[:-20]
    else:
        # Un agente retomado con SendMessage vuelve a terminar sin un lanzamiento nuevo, que el hook no ve.
        # En la HU-3 de Nexus Control, dos correcciones del SDD hechas asi no quedaron en .versions/.
        done = [s for s in finished if s["agent"] == agent and (not transcript or s.get("transcript") in (None, transcript))]
        if not done:
            return
        spawn = done[-1]
    previous_ts, previous_tree = spawn.get("ts", 0), spawn.get("tree")
    # La proxima vez que este agente termine, se revisa solo lo que hizo despues de ahora.
    spawn["ts"], spawn["tree"] = int(time.time()), tree_hash(spawn["code_root"]) if spawn.get("tree") else None
    save_session(data, session)
    hu_dir = Path(spawn["hu_dir"])
    # Cada version que entrega un agente, no solo la aprobada: en la segunda HU real se perdio la v1 del work-item.
    for name in VERSIONED.get(spawn["phase"], ()):
        save_version(hu_dir, name)
    problems = []
    if agent == "nexus-supervisor" and hu_dir.is_dir():
        if not record_supervision(hu_dir, transcript):
            problems.append("tu respuesta no empieza con VEREDICTO: CONTINUAR, PEDIR_EVIDENCIA o ESCALAR. Respondé con ese formato")
    if agent in READ_ONLY_BASH and previous_tree and spawn["tree"] != previous_tree:
        problems.append("el arbol de git cambio mientras corrias, y tu rol no modifica codigo. Restauralo y reporta por que")
    violations = [g for g in read_gates(hu_dir) if g.get("gate") == "VIOLATION" and g.get("by") == agent and g.get("ts", 0) >= previous_ts]
    if violations:
        files = sorted({Path(f).name for g in violations for f in g.get("files", [])})
        problems.append(f"cambiaste {', '.join(files)} con Bash. Reportalo al orquestador con el comando literal; no lo corrijas por tu cuenta")
    hidden = invisible_chars(hu_dir, previous_ts)
    if hidden:
        problems.append("hay caracteres invisibles de formato en " + ", ".join(hidden) +
                        ". Quitalos con Edit: invierten o esconden texto y nadie los ve al revisar")
    expected = PHASE_OUTPUT.get(spawn["phase"])
    if expected and spawn["phase"] != "F2.5":
        stem = expected[:-3]
        report = latest(hu_dir, stem)
        if report is None:
            problems.append(f"falta {hu_dir / expected}")
        elif spawn["phase"] in ("AR", "CR", "F4", "SPEC_VERIFY", "SECURITY") and not re.search(r"^STATUS:", report.read_text(encoding="utf-8"), re.M):
            problems.append(f"{report.name} no tiene la linea STATUS:")
    if spawn["phase"] in ("F0F1", "F1") and (hu_dir / "work-item.md").is_file() and questions_section(hu_dir) is None:
        problems.append("work-item.md no tiene la seccion PREGUNTAS PARA EL HUMANO. Agregala, aunque diga Ninguna")
    if spawn["phase"] in ("F0F1", "F1") and (hu_dir / "work-item.md").is_file() and \
            not re.search(r"^#+ *MEMORIA CONSULTADA", (hu_dir / "work-item.md").read_text(encoding="utf-8"), re.M | re.I):
        problems.append("work-item.md no tiene la seccion MEMORIA CONSULTADA. Agregala, aunque diga Ninguna y por que")
    if spawn["phase"] == "F4" and transcript and Path(transcript).is_file():
        if '"name":"Bash"' not in Path(transcript).read_text(encoding="utf-8").replace('": "', '":"'):
            problems.append("QA no ejecuto ningun comando: su evidencia debe ser comando y salida")
    if problems:
        print(json.dumps({"decision": "block", "reason": "NEXUS GATE: " + "; ".join(problems)}))
        return
    if hu_dir.is_dir():
        write_state(hu_dir, phase=spawn["phase"], agent=agent, status="done")


def invisible_chars(hu_dir, since):
    """Caracteres de formato (categoria Cf: U+202E, U+FEFF, U+200B...) en los artefactos escritos desde `since`.
    En la primera HU de un proyecto nuevo entraron U+202E y U+FEFF reales en sdd.md por escapes \\uXXXX en Write."""
    import unicodedata
    found = []
    for path in sorted(Path(hu_dir).glob("*.md")) if Path(hu_dir).is_dir() else []:
        if path.stat().st_mtime < since - 1:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            chars = {f"U+{ord(c):04X}" for c in line if unicodedata.category(c) == "Cf" and c != "\u200d"}
            if chars:
                found.append(f"{path.name}:{number} ({', '.join(sorted(chars))})")
                break
    return found


def cmd_session(data):
    """Despues de compactar o retomar: recordar la HU activa, porque el chat ya no es confiable."""
    session = load_session(data)
    if not session.get("hu_dir"):
        return
    state_path = Path(session["hu_dir"]) / ".nexus-state.json"
    if state_path.exists():
        print(f"NexusAgil: HU activa en {session['hu_dir']}. Estado: {state_path.read_text(encoding='utf-8')}. "
              "Antes de lanzar otra fase, relee .gates.jsonl y los artefactos de esa carpeta.")


COMMANDS = {"gate": cmd_gate, "prompt": cmd_prompt, "answer": cmd_answer, "stop": cmd_stop, "session": cmd_session,
            "after-bash": cmd_after_bash}


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command not in COMMANDS:
        deny(f"subcomando desconocido: {command}")
    data = json.load(sys.stdin)
    # Una ejecucion del hook a la vez: con agentes en paralelo, dos podian leer y escribir el estado al mismo tiempo.
    import fcntl
    with open(state_dir() / ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        COMMANDS[command](data)


if __name__ == "__main__":
    main()
