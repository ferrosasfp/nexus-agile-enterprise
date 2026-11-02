#!/usr/bin/env python3
"""Despues de fusionar deltas: ningun requisito se pierde en silencio.

Uso: check_spec_ids.py <spec_antes.md> <spec_despues.md> <sdd.md>
Exit 0 sin fallas, 1 con fallas.
"""
import re
import sys
from pathlib import Path

REQ = re.compile(r"^#+ *(REQ-[A-Z0-9-]+)\b", re.M)
DELTA = re.compile(r"^#+ *(ADDED|MODIFIED|REMOVED|RENAMED) +(REQ-[A-Z0-9-]+)(?: *-> *(REQ-[A-Z0-9-]+))?", re.M)


def ids(path):
    return set(REQ.findall(Path(path).read_text(encoding="utf-8")))


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    before, after = ids(sys.argv[1]), ids(sys.argv[2])
    expected = set(before)
    for kind, first, second in DELTA.findall(Path(sys.argv[3]).read_text(encoding="utf-8")):
        if kind == "ADDED":
            expected.add(first)
        elif kind == "REMOVED":
            expected.discard(first)
        elif kind == "RENAMED":
            expected.discard(first)
            expected.add(second)
    failures = [f"falta {i}" for i in sorted(expected - after)] + [f"sobra {i}" for i in sorted(after - expected)]
    for failure in failures:
        print(f"FALLA  {failure}")
    print(f"{len(after)} requisitos, {len(failures)} falla(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
