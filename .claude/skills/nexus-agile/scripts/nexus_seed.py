#!/usr/bin/env python3
"""Siembra retroactiva: junta candidatas a leccion de lo que un proyecto ya escribio en doc/sdd/.

Uso:
  nexus_seed.py --sdd NEXUS_ROOT/doc/sdd [--out candidatas.md] [--json candidatas.json]

Lee, de cada carpeta de HU:
  - auto-blindaje.md: cada entrada `### [fecha] ...`, con su "Aplicar en" (la regla) o, si falta, su causa raiz.
  - lecciones.md: cada leccion propuesta por Docs.
  - report.md, done-report.md y cierre.md: los puntos de la seccion "Lecciones".

Solo lee: no escribe en la memoria ni en el repo. Las candidatas son material para que una persona apruebe;
ninguna entra a Engram sin ese visto bueno (references/engram_protocol.md, regla 2). Las que repiten la misma
regla en varias HUs aparecen agrupadas primero: una regla que se volvio a pagar es la mejor candidata.
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

HEADING = re.compile(r"^#{1,6}\s", re.M)
ENTRY = re.compile(r"^#{2,4}\s+\[[^\]]*\d{4}[^\]]*\]\s*(.*)$", re.M)  # "### [2026-10-29 09:55] Wave 1 — ..."
FIELD = re.compile(r"^\s*-\s*\*\*(?P<name>[^*:]+):?\*\*:?\s*(?P<text>.+(?:\n(?![ \t]*(?:-\s|#|\n|$)).+)*)", re.M)
LESSONS_TITLE = re.compile(r"^(#{2,4})\s+(?:\d+\.\s*)?.*\blecci[oó]n(?:es)?\b.*$", re.M | re.I)
ITEM = re.compile(r"^[ \t]*(?:(?:\d+[.)]|[-*])[ \t]+|(?=\*\*))(\S.*(?:\n(?![ \t]*(?:\d+[.)]|[-*])[ \t])(?!#)(?![ \t]*\n).+)*)", re.M)
FENCE = re.compile(r"^ {0,3}(```|~~~).*?^ {0,3}\1[^\n]*$", re.M | re.S)


def plain(text):
    text = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in text if not unicodedata.combining(c))


def line_of(text, offset):
    return text.count("\n", 0, offset) + 1


def clean(text, limit=400):
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def masked(text):
    """Los bloques de codigo, en blanco y con las mismas lineas: un '# comentario' adentro no es un titulo."""
    return FENCE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def from_auto_blindaje(path, hu):
    text = path.read_text(encoding="utf-8", errors="replace")
    view = masked(text)
    for match in ENTRY.finditer(view):
        # La entrada termina en el titulo siguiente, sea otra entrada o no ("Recomendaciones...", "## Resumen").
        nxt = HEADING.search(view, match.end())
        body = text[match.end(): nxt.start() if nxt else len(text)]
        fields = {}
        for f in FIELD.finditer(body):
            fields.setdefault(plain(f.group("name")).strip(), f.group("text"))
        rule = next((v for k, v in fields.items() if k.startswith("aplicar en") or k.startswith("regla")), None)
        cause = next((v for k, v in fields.items() if k.startswith("causa")), None)
        yield {"hu": hu, "source": f"{path.name}:{line_of(text, match.start())}", "kind": "auto-blindaje",
               "title": clean(match.group(1), 160), "rule": clean(rule or cause or ""), "has_rule": rule is not None}


def from_lessons_section(path, hu):
    text = path.read_text(encoding="utf-8", errors="replace")
    view = masked(text)
    titles = list(LESSONS_TITLE.finditer(view))
    spans = []
    for title in titles:
        level = len(title.group(1))
        end = re.compile(rf"^#{{1,{level}}}\s", re.M).search(view, title.end())
        spans.append((title, title.end(), end.start() if end else len(view)))
    for title, start, stop in spans:
        # Una seccion que contiene otro titulo de lecciones ("## Spinoffs / lecciones" > "### Lecciones extraidas")
        # cede a la de adentro: si no, las mismas lecciones salen dos veces y los spinoffs entran como lecciones.
        if any(start < inner < stop for _title, inner, _stop in spans):
            continue
        sub = HEADING.search(view, start, stop)
        section_end = sub.start() if sub else stop
        cut = re.search(r"^---\s*$", view[start:section_end], re.M)
        section_end = start + cut.start() if cut else section_end
        for item in ITEM.finditer(view, start, section_end):
            body = text[item.start(1): item.end(1)]
            bold = re.match(r"\*\*(.+?)\*\*\s*[—:-]?\s*(.*)", body, re.S)
            yield {"hu": hu, "source": f"{path.name}:{line_of(text, item.start(1))}", "kind": "leccion",
                   "title": clean(bold.group(1) if bold else body, 160), "rule": clean(bold.group(2) if bold else body),
                   "has_rule": True}


def collect(sdd):
    found = []
    for hu_dir in sorted(p for p in Path(sdd).iterdir() if p.is_dir() and not p.name.startswith((".", "_"))):
        ab = hu_dir / "auto-blindaje.md"
        if ab.is_file():
            found += from_auto_blindaje(ab, hu_dir.name)
        for name in ("lecciones.md", "report.md", "done-report.md", "cierre.md"):
            path = hu_dir / name
            if path.is_file():
                found += from_lessons_section(path, hu_dir.name)
    lessons = Path(sdd) / "_LECCIONES.md"
    if lessons.is_file():
        found += from_lessons_section(lessons, "_LECCIONES")
    return found


STOP = set("para con sin que una uno los las del por como cuando antes despues desde sobre entre toda todo cada este esta "
           "the and for with not hay ser son fue mas solo debe tiene".split())


def signature(candidate):
    words = [w for w in re.findall(r"[a-z0-9_]{4,}", plain(candidate["title"] + " " + candidate["rule"])) if w not in STOP]
    return set(words)


def group(candidates, threshold=0.5):
    """Agrupa candidatas de HUs distintas que dicen casi lo mismo (Jaccard de palabras). Simple a proposito:
    la agrupacion fina la hace quien cura la lista; esto solo pone arriba lo que se repite."""
    groups = []
    for cand in candidates:
        sig = signature(cand)
        for g in groups:
            union = sig | g["sig"]
            if union and len(sig & g["sig"]) / len(union) >= threshold:
                g["items"].append(cand)
                g["sig"] |= sig
                break
        else:
            groups.append({"sig": sig, "items": [cand]})
    for g in groups:
        g["hus"] = sorted({c["hu"] for c in g["items"]})
    groups.sort(key=lambda g: (-len(g["hus"]), g["items"][0]["hu"]))
    return groups


def render(groups, sdd, total):
    repeated = [g for g in groups if len(g["hus"]) > 1]
    out = [f"# Candidatas a leccion de {sdd}", "",
           f"{total} candidatas en {len({c['hu'] for g in groups for c in g['items']})} HUs; "
           f"{len(repeated)} grupos se repiten en mas de una HU.", "",
           "Nada de esto esta en la memoria. Cada candidata necesita el visto bueno de la persona, con su alcance "
           "(`scope: project` o `scope: global`), antes de guardarse con `mem_save`.", ""]
    for n, g in enumerate(groups, 1):
        first = g["items"][0]
        out.append(f"## C{n:03d}. {first['title']}")
        out.append(f"- HUs: {len(g['hus'])} ({', '.join(g['hus'][:8])}{', …' if len(g['hus']) > 8 else ''})")
        for c in g["items"][:5]:
            out.append(f"- `{c['hu']}/{c['source']}`: {c['rule'] or c['title']}")
        if len(g["items"]) > 5:
            out.append(f"- y {len(g['items']) - 5} mas")
        out.append("")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sdd", required=True, help="carpeta doc/sdd del proyecto")
    parser.add_argument("--out", help="archivo Markdown de salida (por defecto, a pantalla)")
    parser.add_argument("--json", help="tambien en JSON, para curarlas con otro script")
    args = parser.parse_args()
    if not Path(args.sdd).is_dir():
        sys.exit(f"no existe {args.sdd}")
    candidates = collect(args.sdd)
    groups = group(candidates)
    text = render(groups, args.sdd, len(candidates))
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"{len(candidates)} candidatas, {len(groups)} grupos, {sum(len(g['hus']) > 1 for g in groups)} repetidos: {args.out}")
    else:
        print(text)
    if args.json:
        Path(args.json).write_text(json.dumps([{**{k: v for k, v in g.items() if k != "sig"}} for g in groups],
                                              ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
