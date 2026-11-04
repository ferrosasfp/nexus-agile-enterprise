#!/usr/bin/env python3
"""Antes de F3: contrasta el contrato con los ACs y con el repo. Sin modelo, determinista.

Uso: check_contract.py <HU_DIR> [--code-root DIR]
Exit 0 sin fallas, 1 con fallas, 2 si el uso es incorrecto.
"""
import argparse
import re
import sys
from pathlib import Path

AC_RE = re.compile(r"\bAC[-\s]?(\d+)\b")
PATH_RE = re.compile(r"`([\w./@-]+\.[A-Za-z0-9]+)`")


def contract_text(hu_dir):
    story = hu_dir / "story-file.md"
    if story.is_file():
        return story.read_text(encoding="utf-8"), "story-file.md"
    sdd = hu_dir / "sdd.md"
    if sdd.is_file():
        text = sdd.read_text(encoding="utf-8")
        found = re.search(r"^#+ *(?:\d+[.)]?\s*)?Contrato de implementaci.n.*", text, re.M | re.I)
        if found:
            return text[found.start():], "sdd.md, Contrato de implementacion"
    return None, None


def section(text, title):
    """Seccion por titulo, aunque este numerado ("## 7. Tests"), con sus subsecciones."""
    found = re.search(rf"^(#+) *(?:\d+[.)]?\s*)?{title}[^\n]*$", text, re.M | re.I)
    if not found:
        return None
    level = len(found.group(1))
    end = re.compile(rf"^#{{1,{level}}} ", re.M).search(text, found.end())
    return text[found.end():end.start() if end else len(text)]


def path_bases(contract, root):
    """Rutas relativas a un subdirectorio declarado ("rutas relativas a `apps/web/`"), ademas de la raiz del repo."""
    bases = [root]
    for declared in re.findall(r"(?i)relativas? a `([\w./@-]+)/?`", contract):
        if (root / declared).is_dir() and root / declared not in bases:
            bases.append(root / declared)
    return bases


def resolve(root, path, bases):
    return any((base / path).exists() for base in bases)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("hu_dir")
    parser.add_argument("--code-root", default=".")
    args = parser.parse_args()
    hu_dir, root = Path(args.hu_dir), Path(args.code_root)
    item = hu_dir / "work-item.md"
    if not item.is_file():
        print(f"FALLA  no existe {item}")
        return 1
    contract, name = contract_text(hu_dir)
    if contract is None:
        print("FALLA  no hay contrato: story-file.md ni seccion Contrato de implementacion")
        return 1
    failures = []
    item_text = item.read_text(encoding="utf-8")
    # Un AC que el work-item da de baja ("- AC-5: (eliminado ...)") no tiene que estar en el contrato.
    removed = set(re.findall(r"(?im)^\s*[-*]?\s*\**AC[-\s]?(\d+)\**\s*:\s*\(?\s*(?:eliminad|removed|descartad|~~)", item_text))
    acs = sorted(set(AC_RE.findall(item_text)) - removed, key=int)
    covered = set(AC_RE.findall(contract))
    tests_text = section(contract, "Test")
    tests = set(AC_RE.findall(tests_text or ""))
    for number in acs:
        if number not in covered:
            failures.append(f"AC-{number} no aparece en el contrato")
        elif tests and number not in tests:
            failures.append(f"AC-{number} no tiene test en el contrato")
    if tests_text is None:
        failures.append("no encontre la seccion de tests (titulo que empiece por Test)")
    elif not tests:
        failures.append("la seccion de tests no nombra ningun AC")
    files = section(contract, "Files to Modify")
    if files is None:
        failures.append("no encontre la seccion Files to Modify/Create: no pude revisar rutas")
        files = ""
    checked = 0
    bases = path_bases(contract, root)
    for row in files.splitlines():
        cells = [c.strip() for c in row.split("|")]
        action = next((c for c in cells if re.match(r"(?i)\**\s*(modificar|modify)\b", c)), None)
        paths = PATH_RE.findall(row)
        if action and paths:
            checked += 1
            if not resolve(root, paths[0], bases):
                failures.append(f"se pide modificar {paths[0]}, que no existe (busque desde {', '.join(str(b) for b in bases)})")
    if files and not checked:
        failures.append("la seccion de archivos no tiene filas Modificar con ruta: no revise ninguna")
    for failure in failures:
        print(f"FALLA  {failure}")
    print(f"{name}: {len(acs)} ACs, {checked} rutas revisadas, {len(failures)} falla(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
