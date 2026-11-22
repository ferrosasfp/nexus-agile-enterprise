#!/usr/bin/env python3
"""Respaldo de la memoria de Engram en un repo git propio, para no depender de una maquina.

Uso:
  nexus_brain.py respaldar [--dir DIR] [--push | --sin-push]
      Exporta toda la memoria (`engram export --all`: todos los proyectos y todos los ambitos, global incluido)
      a DIR/memoria.json, normalizada para que git muestre solo lo que cambio, y la commitea si cambio.
      Si DIR no es un repo, lo crea (solo local). Si tiene remoto y gh confirma que es privado, lo empuja; si no
      se puede confirmar, avisa y queda local. --push lo exige (falla si no puede); --sin-push no empuja. Nunca crea un remoto.
  nexus_brain.py restaurar [--dir DIR]
      Importa DIR/memoria.json en la base local (`engram import`). Lo que ya esta se saltea: se puede repetir.

DIR por defecto: $NEXUS_BRAIN_DIR o ~/nexus-brain.

Por que export y no `engram sync`: sync exporta solo el ambito `project`; las trampas globales y lo personal
no viajan (probado con Engram 3.7.2). El export trae todo, y el import no duplica.

La memoria trae lecciones, decisiones, resumenes de sesion y prompts de todos los proyectos, con detalle de
los clientes: el remoto tiene que ser un repo PRIVADO. Este script no lo crea ni lo elige: eso lo decide la persona.
Empuja solo si gh confirma que el remoto de push es un repo de GitHub privado.
Salvaguardas: solo escribe en un repo de respaldo (marca .nexus-brain); no pisa el respaldo si a la base local le
faltan memorias que el respaldo tiene (maquina nueva sin restaurar), salvo --forzar; lo borrado no se respalda.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FILE = "memoria.json"


def brain_dir(arg):
    return Path(os.path.expanduser(arg or os.environ.get("NEXUS_BRAIN_DIR") or "~/nexus-brain"))


def git(repo, *args, check=True):
    result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        sys.exit(f"git {' '.join(args)} fallo: {result.stderr.strip()}")
    return result


MARKER = ".nexus-brain"
OWN_FILES = {FILE, "README.md", MARKER}


def normalize(data):
    """Sin la fecha del export, sin lo borrado y con un orden fijo: dos respaldos de la misma memoria dan el mismo
    archivo, y lo que alguien borro (quiza por sensible) no sigue viajando."""
    data = {k: v for k, v in data.items() if k != "exported_at"}
    if isinstance(data.get("observations"), list):
        data["observations"] = [o for o in data["observations"] if not o.get("deleted_at")]
    for key in ("sessions", "observations", "prompts"):
        if isinstance(data.get(key), list):
            data[key] = sorted(data[key], key=lambda item: (str(item.get("sync_id") or ""), str(item.get("id") or "")))
    return data


def sync_ids(data):
    return {o.get("sync_id") or f"id-{o.get('id')}" for o in data.get("observations") or []}


def check_brain_repo(repo):
    """Solo se escribe en un repo de respaldo: el que creo este script (marca .nexus-brain) o uno que solo tiene
    sus archivos. Un --dir que apunta al repo de un cliente commitearia su trabajo y empujaria la memoria ahi."""
    if not (repo / ".git").exists():
        if any(repo.iterdir()):
            sys.exit(f"{repo} no esta vacio y no es un repo de respaldo: elegi otra carpeta")
        git(repo, "init", "-q")
    elif not (repo / MARKER).is_file():
        tracked = set(git(repo, "ls-files").stdout.split())
        others = {p.name for p in repo.iterdir() if p.name != ".git"} - OWN_FILES
        if not tracked <= OWN_FILES or others:
            sys.exit(f"{repo} es un repo git que no es de respaldo (tiene {sorted((tracked | others) - OWN_FILES)[:5]}). "
                     "No se escribe ahi")
    (repo / MARKER).write_text("Repo de respaldo de la memoria de NexusAgil (nexus_brain.py).\n", encoding="utf-8")
    if not (repo / "README.md").is_file():
        (repo / "README.md").write_text(
            "# Memoria de NexusAgil\n\nRespaldo de Engram (`nexus_brain.py respaldar`). Repo PRIVADO: trae lecciones, "
            "decisiones y resumenes de sesion de todos los proyectos.\n\nPara restaurar en otra maquina: "
            "`nexus_brain.py restaurar --dir <este repo>`.\n", encoding="utf-8")


def remote_problem(url):
    """None solo si gh confirma que el remoto de GitHub es PRIVADO. Si no se puede confirmar (otro host, alias de SSH
    que gh no resuelve, gh sin sesion), no se empuja: la memoria trae datos de clientes."""
    found = re.search(r"[:/]([\w.-]+)/([\w.-]+?)(?:\.git)?/?$", url)
    if not found:
        return f"no se reconoce el repo en {url}"
    if not shutil.which("gh"):
        return "sin gh no se puede confirmar que el remoto sea privado"
    host = re.search(r"^(?:\w+://)?(?:[^@/]+@)?([^:/]+)", url)
    name = f"{found.group(1)}/{found.group(2)}"
    if host and host.group(1) not in ("github.com", "www.github.com"):
        name = f"github.com/{name}" if host.group(1).startswith("github") else None
    if name is None:
        return f"{url} no es de GitHub: no se puede confirmar que sea privado"
    result = subprocess.run(["gh", "repo", "view", name, "--json", "visibility", "-q", ".visibility"],
                            capture_output=True, text=True)
    visibility = result.stdout.strip().upper()
    if result.returncode != 0:
        return f"gh no pudo ver {name} ({result.stderr.strip()[:120]}): no se confirma que sea privado"
    return None if visibility == "PRIVATE" else f"{name} es {visibility or 'de visibilidad desconocida'}, no PRIVATE"


def cmd_respaldar(args):
    if not shutil.which("engram"):
        sys.exit("no hay engram en el PATH: no hay memoria que respaldar")
    repo = brain_dir(args.dir)
    repo.mkdir(parents=True, exist_ok=True)
    check_brain_repo(repo)
    with tempfile.TemporaryDirectory() as tmp:
        raw = Path(tmp) / "export.json"
        result = subprocess.run(["engram", "export", str(raw), "--all"], capture_output=True, text=True)
        if result.returncode != 0 or not raw.is_file():
            sys.exit(f"engram export fallo: {(result.stderr or result.stdout).strip()}")
        data = normalize(json.loads(raw.read_text(encoding="utf-8")))
    # Una maquina nueva (o una base a medias) no pisa el respaldo: lo que ya estaba respaldado tiene que seguir.
    previous = repo / FILE
    if previous.is_file() and not args.forzar:
        missing = sync_ids(normalize(json.loads(previous.read_text(encoding="utf-8")))) - sync_ids(data)
        if missing:
            sys.exit(f"la memoria local no tiene {len(missing)} memorias que el respaldo si tiene: corre primero "
                     f"'nexus_brain.py restaurar --dir {repo}'. Si las borraste a proposito, repeti con --forzar")
    previous.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    git(repo, "add", "--", *sorted(OWN_FILES))
    count = len(data.get("observations") or [])
    if git(repo, "diff", "--cached", "--quiet", check=False).returncode == 0:
        print(f"SIN CAMBIOS: {count} memorias, igual que el ultimo respaldo ({repo})")
    else:
        git(repo, "-c", "user.name=nexus-brain", "-c", "user.email=nexus-brain@localhost",
            "commit", "-qm", f"respaldo de la memoria: {count} memorias")
        print(f"RESPALDADO: {count} memorias en {previous}")
    # Con remoto, se empuja solo (asi DONE no necesita saber si hay uno), pero solo si gh confirma que es privado.
    # --push lo exige: sin remoto o sin confirmar, falla. --sin-push deja el respaldo local.
    remotes = git(repo, "remote", check=False).stdout.split()
    if args.sin_push or (not remotes and not args.push):
        return 0
    if not remotes:
        sys.exit("--push sin remoto: agrega uno PRIVADO con git -C <dir> remote add origin <url>")
    url = git(repo, "remote", "get-url", "--push", remotes[0], check=False).stdout.strip()
    problem = remote_problem(url)
    if problem:
        if args.push:
            sys.exit(f"no se empuja: {problem}")
        print(f"NO EMPUJADO: {problem}. El respaldo quedo local", file=sys.stderr)
        return 0
    pushed = git(repo, "push", "-q", remotes[0], "HEAD", check=args.push)
    if pushed.returncode == 0:
        print(f"EMPUJADO a {remotes[0]}")
    else:
        print(f"NO EMPUJADO: git push fallo ({pushed.stderr.strip()[:160]}). El respaldo quedo local", file=sys.stderr)
    return 0


def cmd_restaurar(args):
    source = brain_dir(args.dir) / FILE
    if not source.is_file():
        sys.exit(f"no existe {source}")
    if not shutil.which("engram"):
        sys.exit("no hay engram en el PATH")
    result = subprocess.run(["engram", "import", str(source)], capture_output=True, text=True)
    print((result.stdout or result.stderr).strip())
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    backup = sub.add_parser("respaldar")
    backup.add_argument("--dir")
    backup.add_argument("--push", action="store_true")
    backup.add_argument("--sin-push", action="store_true", help="no empujar aunque haya remoto")
    backup.add_argument("--forzar", action="store_true", help="respaldar aunque falten memorias que el respaldo tenia")
    restore = sub.add_parser("restaurar")
    restore.add_argument("--dir")
    args = parser.parse_args()
    sys.exit({"respaldar": cmd_respaldar, "restaurar": cmd_restaurar}[args.command](args))


if __name__ == "__main__":
    main()
