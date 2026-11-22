#!/usr/bin/env python3
"""Candidatas a leccion de una HU, juntadas de lo que el hook y los agentes ya dejaron escrito.

Uso:
  nexus_candidates.py --hu-dir NEXUS_ROOT/doc/sdd/NNN-titulo [--trampas SKILL_DIR/references/trampas_globales.md]

Lee de la carpeta de la HU:
  - .blocks.jsonl: cada bloqueo del hook (agrupados por mensaje, con cuantas veces y que agentes).
  - .gates.jsonl: las VIOLATION (un agente escribio lo que no debia y el hook lo restauro).
  - ar-report*.md y cr-report*.md: los hallazgos BLQ y MAYOR, lo que llego hasta la revision sin que nadie lo viera.
  - auto-blindaje.md: cada entrada, con su "Aplicar en".
Con --trampas, marca las candidatas que se parecen a una trampa global del plugin: esas van como evidencia de la
trampa, no como leccion nueva.

Imprime Markdown. Solo lee: no escribe en la memoria ni en el repo. Docs usa la salida para escribir lecciones.md
(cada leccion cita sus K-N), y la persona las aprueba en una sola pregunta (references/engram_protocol.md).
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from nexus_seed import clean, from_auto_blindaje, line_of, masked, signature  # noqa: E402

# Un hallazgo lleva su id (BLQ-MED-1, MAY-2, "MAYOR (MAY-1)"); "## BLQ previos" o "Estado de los BLQ" son secciones.
# El adversario pide un id por hallazgo pero no un formato: titulo, vineta en negrita o fila de tabla.
FINDING_ID = r"\b(?:BLQ|MAYOR|MAY)(?:-[A-Z]+)*-\d+\b"
FINDING = re.compile(rf"^(?:#{{2,4}}\s+([^\n]*{FINDING_ID}[^\n]*)"
                     rf"|[ \t]*[-*]\s+(\*\*[^\n]*?{FINDING_ID}[^\n]*)"
                     rf"|[ \t]*\|\s*(\**{FINDING_ID}[^\n]*))$", re.M)
TRAMPA = re.compile(r"^##\s+(T\d+)\.\s+(.+)$", re.M)


def read_jsonl(path):
    if not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def from_blocks(hu_dir):
    groups = {}
    for entry in read_jsonl(hu_dir / ".blocks.jsonl"):
        message = str(entry.get("message", ""))
        # El mismo bloqueo con otra ruta u otro numero es el mismo bloqueo.
        key = re.sub(r"\d+", "N", re.sub(r"(?:/[\w.@~-]+)+", "<ruta>", message.split(". Si es un falso positivo")[0]))
        group = groups.setdefault(key, {"count": 0, "agents": set(), "message": message})
        group["count"] += 1
        group["agents"].add(str(entry.get("agent", "?")))
    for group in sorted(groups.values(), key=lambda g: -g["count"]):
        yield {"kind": "bloqueo del hook", "source": ".blocks.jsonl",
               "title": clean(group["message"], 200),
               "rule": f"{group['count']} vez/veces, {', '.join(sorted(group['agents']))}"}


def from_violations(hu_dir):
    for n, entry in enumerate(read_jsonl(hu_dir / ".gates.jsonl"), 1):
        if entry.get("gate") != "VIOLATION":
            continue
        restored = ", ".join(Path(str(f)).name for f in entry.get("restored") or entry.get("files") or [])
        yield {"kind": "violacion", "source": f".gates.jsonl:{n}",
               "title": f"{entry.get('by', '?')} cambio {restored or 'artefactos'} fuera de lo permitido",
               "rule": clean(str(entry.get("command", "")), 200)}


def report_order(path):
    """ar-report.md, ar-report-2.md, ar-report-3.md...: la primera corrida primero."""
    found = re.search(r"-(\d+)\.md$", path.name)
    return int(found.group(1)) if found else 1


def from_findings(hu_dir):
    for family in ("ar-report", "cr-report"):
        seen = set()
        for path in sorted(hu_dir.glob(f"{family}*.md"), key=report_order):
            text = path.read_text(encoding="utf-8", errors="replace")
            for match in FINDING.finditer(masked(text)):
                group = next(i for i in (1, 2, 3) if match.group(i) is not None)
                title = text[match.start(group):match.end(group)].replace("**", "").strip(" |")
                # Las re-revisiones repiten los hallazgos previos en una tabla de estado ("Resuelto"): cuenta la
                # primera aparicion, que trae la descripcion.
                ids = frozenset(re.findall(FINDING_ID, title))
                if ids & seen:
                    continue
                seen |= ids
                yield {"kind": "hallazgo de revision", "source": f"{path.name}:{line_of(text, match.start())}",
                       "title": clean(re.sub(r"\s*\|\s*", " | ", title), 200), "rule": ""}


def load_trampas(path):
    if not path:
        return []
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    spans = list(TRAMPA.finditer(text))
    out = []
    for i, match in enumerate(spans):
        body = text[match.end(): spans[i + 1].start() if i + 1 < len(spans) else len(text)]
        out.append((match.group(1), match.group(2).strip(), signature({"title": match.group(2), "rule": body})))
    return out


def similar_trampa(candidate, trampas, threshold=0.25, min_words=4):
    """Medido sobre una HU real: la que repetia T2 compartia 6 palabras (0,33); las que no, 3 o menos."""
    sig = signature(candidate)
    best = None
    for tid, title, tsig in trampas:
        if not sig or not tsig:
            continue
        shared = len(sig & tsig)
        score = shared / len(sig)  # que parte de la candidata ya dice la trampa
        if shared >= min_words and score >= threshold and (best is None or score > best[0]):
            best = (score, tid, title)
    return best


def collect(hu_dir):
    found = list(from_blocks(hu_dir)) + list(from_violations(hu_dir)) + list(from_findings(hu_dir))
    ab = hu_dir / "auto-blindaje.md"
    if ab.is_file():
        found += [{**c, "kind": "auto-blindaje"} for c in from_auto_blindaje(ab, hu_dir.name)]
    return found


def render(hu_dir, candidates, trampas):
    out = [f"# Candidatas a leccion de {hu_dir.name}", "",
           f"{len(candidates)} candidatas. Nada de esto esta en la memoria: Docs las cura en lecciones.md (una leccion "
           "puede juntar varias K-N, y muchas no dejan leccion) y la persona aprueba.", ""]
    if not candidates:
        out.append("Ninguna: la HU no dejo bloqueos, violaciones, hallazgos BLQ o MAYOR ni auto-blindaje.")
    for n, cand in enumerate(candidates, 1):
        line = f"- **K-{n}** ({cand['kind']}, `{cand['source']}`): {cand['title']}"
        if cand.get("rule"):
            line += f" — {cand['rule']}"
        match = similar_trampa(cand, trampas)
        if match:
            line += f" — **posible {match[1]}** ({match[2]}): si lo es, va como evidencia de esa trampa"
        out.append(line)
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--hu-dir", required=True)
    parser.add_argument("--trampas", help="references/trampas_globales.md del plugin")
    args = parser.parse_args()
    hu_dir = Path(args.hu_dir).resolve()
    if not hu_dir.is_dir():
        sys.exit(f"no existe {hu_dir}")
    print(render(hu_dir, collect(hu_dir), load_trampas(args.trampas)))


if __name__ == "__main__":
    main()
