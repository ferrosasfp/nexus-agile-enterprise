#!/usr/bin/env python3
"""Hechos verificados para la memoria de NexusAgil, atados al hash de git de los archivos de los que salen.

Uso:
  nexus_memory.py hecho --repo CODE_ROOT --file ruta [--file otra] --claim "..." --evidence "archivo:linea" --source "HU, fecha"
      Imprime la entrada lista para mem_save (topic_key y content), con el blob SHA de git de cada archivo.
  nexus_memory.py vigente --repo CODE_ROOT --pair ruta=sha [--pair otra=sha]
      Exit 0 y VIGENTE si todos los archivos tienen hoy el mismo blob SHA; exit 1 y CAMBIO con los que difieren.

El blob SHA es el que calcula `git hash-object`: no depende de rtk ni de la herramienta que lea el archivo,
y es el mismo que git guarda. Un hecho que depende de varios archivos lleva un par por archivo.
Solo lee: no escribe en la memoria ni en el repo.
"""
import argparse
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


def cmd_hecho(args):
    pairs = []
    for path in args.file:
        digest = blob_sha(args.repo, path)
        if digest is None:
            sys.exit(f"no existe {path} en {args.repo}: un hecho no se guarda sobre un archivo que no esta")
        pairs.append((path, digest))
    # Un archivo puede tener varios hechos: la clave lleva un nombre corto del hecho, para que uno no pise al otro.
    slug = args.key or "-".join(re.findall(r"[a-z0-9]+", args.claim.lower())[:5])
    key = "hecho/" + pairs[0][0] + ("" if len(pairs) == 1 else "+" + str(len(pairs) - 1)) + "#" + slug
    lines = [f"topic_key: {key}", "content:", f"  Claim: {args.claim}"]
    lines += [f"  File: {path} @ {digest}" for path, digest in pairs]
    lines += [f"  Evidence: {args.evidence}", f"  Source: {args.source}",
              f"  Verify: nexus_memory.py vigente --repo <CODE_ROOT> " + " ".join(f"--pair {p}={d}" for p, d in pairs)]
    print("\n".join(lines))


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
    vigente = sub.add_parser("vigente")
    vigente.add_argument("--repo", required=True)
    vigente.add_argument("--pair", action="append", required=True)
    args = parser.parse_args()
    if args.cmd == "hecho":
        cmd_hecho(args)
        return 0
    return cmd_vigente(args)


if __name__ == "__main__":
    sys.exit(main())
