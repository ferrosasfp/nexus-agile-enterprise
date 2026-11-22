#!/usr/bin/env python3
"""Hechos verificados para la memoria de NexusAgil, atados al hash de git de los archivos de los que salen.

Uso:
  nexus_memory.py hecho --repo CODE_ROOT --file ruta [--file otra] --claim "..." --evidence "archivo:linea" --source "HU, fecha"
      Imprime la entrada lista para mem_save (topic_key y content), con el blob SHA de git de cada archivo.
  nexus_memory.py vigente --repo CODE_ROOT --pair ruta=sha [--pair otra=sha]
      Exit 0 y VIGENTE si todos los archivos tienen hoy el mismo blob SHA; exit 1 y CAMBIO con los que difieren.
  nexus_memory.py desde-verificacion --repo CODE_ROOT --report sdd-verification.md [--report ...] --base BASE_REF
                  --source "HU, fecha" [--project nombre]
      Lee la seccion "## Hechos para la memoria" de los informes de SPEC_VERIFY y arma una entrada por hecho.
      SPEC_VERIFY corre antes de F3, asi que las lineas citadas son las de BASE_REF. Si el archivo cambio en la HU,
      el hecho se guarda solo si ningun cambio toca las lineas citadas, y la cita pasa a las lineas de hoy; si las
      toca, o el archivo no existia en la base, se descarta. Con varios informes, el ultimo manda.
  nexus_memory.py usadas --file work-item.md [--file otro.md]
      Lee la tabla de "## MEMORIA CONSULTADA" y dice que memorias renovar (VERIFICADA o VIGENTE: la HU las uso
      y siguen siendo ciertas), cuales corregir (DESCARTADA) y cuales no se comprobaron (SIN VERIFICAR).

El blob SHA es el que calcula `git hash-object`: no depende de rtk ni de la herramienta que lea el archivo,
y es el mismo que git guarda. Un hecho que depende de varios archivos lleva un par por archivo.
Solo lee: no escribe en la memoria ni en el repo.
"""
import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path


def blob_sha(repo, path):
    target = Path(repo) / path
    if not target.is_file():
        return None
    out = subprocess.run(["git", "-C", str(repo), "hash-object", "--", path], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def entry(pairs, claim, evidence, source, key=None, project=None):
    # Un archivo puede tener varios hechos: la clave lleva un nombre corto del hecho, para que uno no pise al otro.
    slug = key or "-".join(re.findall(r"[a-z0-9]+", claim.lower())[:5])
    topic = "hecho/" + pairs[0][0] + ("" if len(pairs) == 1 else "+" + str(len(pairs) - 1)) + "#" + slug
    lines = [f"topic_key: {topic}", "content:", f"  Claim: {claim}"]
    lines += [f"  File: {path} @ {digest}" for path, digest in pairs]
    lines += [f"  Evidence: {evidence}", f"  Source: {source}",
              "  Verify: nexus_memory.py vigente --repo <CODE_ROOT> " + " ".join(f"--pair {p}={d}" for p, d in pairs)]
    if project:
        # El titulo lleva la palabra del tipo: la busqueda de los agentes va por el titulo.
        short = claim if len(claim) <= 90 else claim[:87].rstrip() + "..."
        lines.insert(0, f"title: {project} hecho: {short}")
    return "\n".join(lines), topic


def cmd_hecho(args):
    pairs = []
    for path in args.file:
        digest = blob_sha(args.repo, path)
        if digest is None:
            sys.exit(f"no existe {path} en {args.repo}: un hecho no se guarda sobre un archivo que no esta")
        pairs.append((path, digest))
    print(entry(pairs, args.claim, args.evidence, args.source, args.key, args.project)[0])


SECTION = re.compile(r"^#{2,4}\s*(?:\d+\.\s*)?Hechos para la memoria\s*$", re.M | re.I)
MEMORY_SECTION = re.compile(r"^#{2,4}\s*MEMORIA CONSULTADA\s*$", re.M | re.I)
REF = re.compile(r"(?<![\w/.])([A-Za-z0-9_.][\w./-]*):(\d+)(?:-(\d+))?")
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", re.M)
FENCE = re.compile(r"^ {0,3}(```|~~~).*?^ {0,3}\1[^\n]*$", re.M | re.S)
SEPARATOR = re.compile(r"^:?-{2,}:?$")
BASE_SHA = re.compile(r"^BASE_SHA:\s*`?([0-9a-f]{7,40})`?\s*$", re.M)


def section_table(text, heading):
    """Las filas de la primera tabla de una seccion, sin el encabezado. La seccion termina en el proximo titulo y la
    tabla en la primera linea que no es de la tabla: una tabla posterior (despues de un parrafo o de un titulo en
    negrita) no es de la seccion. Un titulo dentro de un bloque de codigo no cuenta. Una barra escapada no corta la celda."""
    view = FENCE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    found = heading.search(view)
    if not found:
        return None
    raw, started = [], False
    for line in view[found.end():].splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if not stripped.startswith("|"):
            if started:
                break
            continue
        started = True
        cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", stripped.strip("|"))]
        raw.append(cells)
    if len(raw) > 1 and all(SEPARATOR.match(c) for c in raw[1] if c):
        raw = raw[:1] + raw[2:]
        raw = raw[1:]  # el encabezado
    return [cells for cells in raw if not all(SEPARATOR.match(c) or not c for c in cells)]


def table_rows(text):
    """Las filas de "Hechos para la memoria": (hecho, celda de archivos, evidencia)."""
    rows = section_table(text, SECTION)
    if rows is None:
        return None
    return [(cells[0].replace("`", "").strip(), cells[1], cells[2] if len(cells) > 2 else cells[1])
            for cells in rows if len(cells) >= 2 and cells[0]]


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "core.quotepath=off", *args], capture_output=True, text=True)


def base_blob(repo, base, path):
    out = git(repo, "rev-parse", "--verify", "--quiet", f"{base}:{path}")
    return out.stdout.strip() if out.returncode == 0 else None


def report_base(repo, text, base):
    """El commit sobre el que corrio SPEC_VERIFY: la linea BASE_SHA del informe o, si falta, el merge-base de
    BASE_REF con HEAD. Contra BASE_REF a secas, un merge posterior en main corria las citas a lineas equivocadas."""
    found = BASE_SHA.search(text)
    if found and git(repo, "rev-parse", "--verify", "--quiet", found.group(1) + "^{commit}").returncode == 0:
        return git(repo, "rev-parse", found.group(1)).stdout.strip(), "BASE_SHA del informe"
    merge = git(repo, "merge-base", base, "HEAD")
    if merge.returncode == 0 and merge.stdout.strip():
        return merge.stdout.strip(), f"merge-base de {base} y HEAD"
    return None, None


def moved_range(repo, base, path, start, end):
    """Las lineas start-end de la base en el archivo de hoy, o None si algun cambio las toca o si el diff no se
    puede leer. Se llama solo cuando el archivo cambio: un diff sin hunks legibles (color, binario, textconv) no
    prueba que las lineas sigan iguales, asi que el hecho se descarta."""
    out = git(repo, "diff", "--no-color", "--no-ext-diff", "--no-textconv", "-U0", base, "--", path)
    hunks = list(HUNK.finditer(out.stdout)) if out.returncode == 0 else []
    if not hunks:
        return None
    shift = 0
    for hunk in hunks:
        old, old_n = int(hunk.group(1)), int(hunk.group(2) or 1)
        new_n = int(hunk.group(4) or 1)
        # Con old_n == 0, git pone en old la linea despues de la cual inserta.
        first, last = (old + 1, old) if old_n == 0 else (old, old + old_n - 1)
        if old_n == 0 and start <= old < end:
            return None
        if old_n and first <= end and last >= start:
            return None
        if last < start:
            shift += new_n - old_n
    return start + shift, end + shift


STATES = (("VERIFICADA", "renovar"), ("VIGENTE", "renovar"), ("DESCARTADA", "corregir"), ("SIN VERIFICAR", "sin_verificar"))


def cmd_usadas(args):
    groups = {"renovar": {}, "corregir": {}, "sin_verificar": {}, "sin_clasificar": {}}
    sections = 0
    for name in args.file:
        rows = section_table(Path(name).read_text(encoding="utf-8", errors="replace"), MEMORY_SECTION)
        if rows is None:
            continue
        sections += 1
        for cells in rows:
            # El id de Engram es #N, en la primera columna; las trampas del plugin (TG-T1) no tienen fecha que renovar.
            ids = re.findall(r"#(\d+)", cells[0])
            if not ids or len(cells) < 2:
                continue
            state = re.sub(r"^[^A-Z]+", "", cells[-1].upper().replace("`", "").replace("*", ""))
            kind = next((k for word, k in STATES if state.startswith(word)), "sin_clasificar")
            for number in ids:
                # En dos archivos: DESCARTADA gana siempre; VERIFICADA en otro lado gana sobre SIN VERIFICAR.
                current = next((k for k, v in groups.items() if number in v), None)
                rank = {"corregir": 3, "renovar": 2, "sin_verificar": 1, "sin_clasificar": 0}
                if current and rank[current] >= rank[kind]:
                    continue
                if current:
                    del groups[current][number]
                groups[kind][number] = Path(name).name
    print(f"MEMORIA CONSULTADA: {sections} seccion(es)")
    labels = {"renovar": "RENOVAR (mem_review mark_reviewed)", "corregir": "CORREGIR (mismo topic_key)",
              "sin_verificar": "SIN VERIFICAR (no se renuevan)", "sin_clasificar": "SIN CLASIFICAR (estado no reconocido: revisarlas)"}
    for kind, label in labels.items():
        ids = sorted(groups[kind], key=int)
        if ids or kind != "sin_clasificar":
            print(f"{label}: {' '.join('#' + i for i in ids) if ids else 'ninguna'}")
    return 0 if sections else 1


def cmd_desde_verificacion(args):
    if git(args.repo, "rev-parse", "--verify", "--quiet", args.base + "^{commit}").returncode != 0:
        sys.exit(f"BASE_REF {args.base} no existe en {args.repo}: sin la base no se sabe si el hecho sigue valiendo")
    facts, skipped, without, bases = {}, [], [], []
    # El ultimo informe manda: se recorren del ultimo al primero y gana la primera aparicion de cada hecho.
    for report in reversed(args.report):
        text = Path(report).read_text(encoding="utf-8", errors="replace")
        rows = table_rows(text)
        if rows is None:
            without.append(report)
            continue
        base, origin = report_base(args.repo, text, args.base)
        if base is None:
            skipped.append(f"{Path(report).name}: no se pudo fijar la base")
            continue
        bases.append(f"{Path(report).name}: {base[:12]} ({origin})")
        for claim, files_cell, evidence in rows:
            refs = [(m.group(1).rstrip(".,;"), *sorted((int(m.group(2)), int(m.group(3) or m.group(2)))))
                    for m in REF.finditer(files_cell)]
            if not refs:
                skipped.append(f"{claim[:70]}: sin archivo:linea")
                continue
            pairs, cites, problem = {}, [], None
            for path, start, end in refs:
                now, before = blob_sha(args.repo, path), base_blob(args.repo, base, path)
                if now is None:
                    problem = f"no existe {path}"
                elif before is None:
                    problem = f"{path} no existia en la base {base[:12]}"
                elif now != before:
                    moved = moved_range(args.repo, base, path, start, end)
                    if moved is None:
                        problem = f"la HU cambio {path}:{start}-{end} (o el diff no se pudo leer): verificarlo de nuevo"
                    else:
                        start, end = moved
                if problem:
                    break
                pairs[path] = now
                cites.append(f"{path}:{start}" + (f"-{end}" if end != start else ""))
            if problem:
                skipped.append(f"{claim[:70]}: {problem}")
                continue
            # La clave lleva un hash corto del hecho: dos hechos que empiezan igual ("cinco intentos por minuto" y
            # "por hora") no se pisan, ni en esta HU ni contra uno guardado por otra.
            words = "-".join(re.findall(r"[a-z0-9]+", claim.lower())[:5])
            key = f"{words}-{hashlib.sha1(claim.strip().lower().encode()).hexdigest()[:6]}"
            text_entry, topic = entry(list(pairs.items()), claim,
                                      f"{', '.join(cites)} (SPEC_VERIFY, {Path(report).name}: {evidence})", args.source,
                                      key=key, project=args.project)
            if topic in facts:
                continue
            facts[topic] = text_entry
    if len(facts) > args.max:
        skipped += [f"{t}: pasa el tope de {args.max} hechos por HU" for t in list(facts)[args.max:]]
        facts = dict(list(facts.items())[:args.max])
    skipped = list(dict.fromkeys(skipped))  # el mismo hecho descartado en dos informes se cuenta una vez
    print(f"HECHOS: {len(facts)} para guardar, {len(skipped)} descartados")
    if bases:
        print("BASE: " + "; ".join(bases))
    for text_entry in facts.values():
        print("---\n" + text_entry)
    if skipped:
        print("---\nDESCARTADOS:\n" + "\n".join(f"  {s}" for s in skipped))
    if without:
        print("---\nSIN SECCION 'Hechos para la memoria': " + ", ".join(without))
    return 0


def cmd_vigente(args):
    changed = []
    for pair in args.pair:
        path, _, expected = pair.partition("=")
        current = blob_sha(args.repo, path)
        if current != expected:
            changed.append(f"{path}: guardado {expected[:12]}, hoy {current[:12] if current else 'no existe'}")
    if changed:
        print("CAMBIO: el hecho no vale sin volver a verificarlo")
        print("\n".join(f"  {c}" for c in changed))
        return 1
    print(f"VIGENTE: {len(args.pair)} archivo(s) con el mismo blob SHA")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    hecho = sub.add_parser("hecho")
    hecho.add_argument("--repo", required=True)
    hecho.add_argument("--file", action="append", required=True)
    hecho.add_argument("--claim", required=True)
    hecho.add_argument("--evidence", required=True)
    hecho.add_argument("--source", required=True)
    hecho.add_argument("--key", help="nombre corto del hecho dentro del archivo; por defecto, las primeras palabras de --claim")
    hecho.add_argument("--project", help="memory_project: agrega la linea title")
    usadas = sub.add_parser("usadas")
    usadas.add_argument("--file", action="append", required=True)
    desde = sub.add_parser("desde-verificacion")
    desde.add_argument("--repo", required=True)
    desde.add_argument("--report", action="append", required=True)
    desde.add_argument("--base", required=True)
    desde.add_argument("--source", required=True)
    desde.add_argument("--project", help="memory_project: agrega la linea title")
    desde.add_argument("--max", type=int, default=10)
    vigente = sub.add_parser("vigente")
    vigente.add_argument("--repo", required=True)
    vigente.add_argument("--pair", action="append", required=True)
    args = parser.parse_args()
    if args.cmd == "hecho":
        cmd_hecho(args)
        return 0
    if args.cmd == "usadas":
        return cmd_usadas(args)
    if args.cmd == "desde-verificacion":
        return cmd_desde_verificacion(args)
    return cmd_vigente(args)


if __name__ == "__main__":
    sys.exit(main())
