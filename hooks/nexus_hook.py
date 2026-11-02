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
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

GATES = ("HU_APPROVED", "SPEC_APPROVED", "RELEASE_APPROVED")
GATE_DOC = {"HU_APPROVED": "work-item.md", "SPEC_APPROVED": "sdd.md"}
READ_ONLY_BASH = {"nexus-adversary", "nexus-qa", "nexus-analyst", "nexus-architect", "nexus-docs", "nexus-supervisor"}
INLINE_WRITE = re.compile(r"\b(python[0-9.]*\s+-c|node\s+(-e|--eval)|perl\s+-[a-zA-Z]*e|ruby\s+-e)\b.*(open\(|write|unlink|rename|remove|rmtree|copy|move|mkdir|>)", re.S)
PHASES = ("F0F1", "F1", "F2", "F2.5", "F3", "AR", "CR", "VERIFY", "F4", "DONE", "SUPERVISION")
PHASE_OUTPUT = {
    "F0F1": "work-item.md", "F1": "work-item.md", "F2": "sdd.md", "F2.5": "story-file.md",
    "AR": "ar-report.md", "CR": "cr-report.md", "VERIFY": "blq-verification.md",
    "F4": "validation.md", "DONE": "report.md",
}
WRITE_RULES = {
    "nexus-supervisor": r"(?!)",
    "nexus-adversary": r"/(ar-report(-\d+)?|cr-report(-\d+)?|blq-verification(-\d+)?)\.md$",
    "nexus-qa": r"/validation(-\d+)?\.md$",
    "nexus-docs": r"/(report\.md|_INDEX\.md)$",
    "nexus-architect": r"/doc/sdd/[^/]+/[^/]+\.md$",
    "nexus-analyst": r"(/doc/sdd/[^/]+/[^/]+\.md|/doc/sdd/_INDEX\.md|/doc/prd/.+|/(project|product)-context\.md)$",
}
GIT_DESTRUCTIVE = re.compile(r"\bgit\b[^|;&]*\s(reset\s+--hard|checkout\s+--|checkout\s+\.|clean\s|restore\s|stash\b|pull\b)")
NO_VERIFY = re.compile(r"\bgit\b[^|;&]*\s(commit|push)\b[^|;&]*\s--no-verify\b")
GIT_WRITE = re.compile(r"\bgit\b[^|;&]*\s(commit|push|merge|rebase|apply|add|rm|mv|tag)\b")
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
    session_file(data).write_text(json.dumps(session), encoding="utf-8")


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


def record_gate(hu_dir, gate, by):
    doc = GATE_DOC.get(gate)
    entry = {"gate": gate, "by": by, "sha256": sha(hu_dir / doc) if doc else None, "ts": int(time.time())}
    if doc and entry["sha256"]:
        # Copia de lo aprobado: para comparar despues sin reconstruirlo desde un transcript.
        versions = hu_dir / ".versions"
        versions.mkdir(exist_ok=True)
        target = versions / f"{Path(doc).stem}-{entry['sha256'][:12]}.md"
        if not target.exists():
            target.write_bytes((hu_dir / doc).read_bytes())
        entry["copy"] = str(target.relative_to(hu_dir))
    with (hu_dir / ".gates.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def write_state(hu_dir, **fields):
    """Estado por HU, para retomar despues de una compactacion o de otra sesion."""
    path = hu_dir / ".nexus-state.json"
    state = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    state.update(fields, updated=int(time.time()))
    path.write_text(json.dumps(state, indent=1), encoding="utf-8")


def latest(hu_dir, stem):
    """report.md o report-2.md: el de numero mas alto es el vigente."""
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
        record_gate(hu_dir, gate, "claude-delegated")
        entries = read_gates(hu_dir)
        entries = [e for e in entries if e["gate"] == gate]
    if not entries:
        consume_override(f"{phase} requiere el gate {gate}, escrito por una persona. Registrados en {hu_dir}: {[e['gate'] for e in read_gates(hu_dir)] or 'ninguno'}")
        return
    doc = GATE_DOC.get(gate)
    current = sha(hu_dir / doc) if doc else None
    if doc and entries[-1].get("sha256") != current:
        consume_override(f"{doc} cambio despues de {gate}. Pidele a la persona que lo revise y vuelva a escribir {gate}")


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
    pipeline = pipeline_of(hu_dir) if hu_dir.is_dir() else "QUALITY"
    has_spec = pipeline in ("QUALITY",)
    unified = hu_dir.is_dir() and any(
        (hu_dir / n).exists() and re.search(r"contract_mode\W{0,6}unified", (hu_dir / n).read_text(encoding="utf-8"))
        for n in ("work-item.md", "sdd.md"))

    if phase in ("F2", "F3") and hu_dir.is_dir():
        pending = open_questions(hu_dir)
        if pending:
            blocked(f"work-item.md tiene {pending} pregunta(s) sin responder en PREGUNTAS PARA EL HUMANO")

    if phase == "F2":
        need("work-item.md")
        require_gate(hu_dir, "HU_APPROVED", session, phase, blocked)
    elif phase == "F2.5":
        need("sdd.md")
        require_gate(hu_dir, "SPEC_APPROVED", session, phase, blocked)
        if unified:
            blocked("con contract_mode: unified no hay F2.5: el contrato va en sdd.md")
    elif phase == "F3":
        need("work-item.md")
        require_gate(hu_dir, "HU_APPROVED", session, phase, blocked)
        if has_spec:
            need("sdd.md")
            require_gate(hu_dir, "SPEC_APPROVED", session, phase, blocked)
            if not unified:
                need("story-file.md")
            elif "Contrato de implementaci" not in (hu_dir / "sdd.md").read_text(encoding="utf-8"):
                blocked("sdd.md no tiene la seccion Contrato de implementacion")
    elif phase == "F4" and pipeline != "FAST":
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
    session["spawns"].append({"agent": agent, "phase": phase, "hu_dir": str(hu_dir), "code_root": code_root, "tree": tree_hash(code_root)})
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


def expand_vars(command):
    """Expande $X y ${X} cuando el mismo comando asigna X a una ruta literal. Lo que viene de otra llamada no se adivina."""
    literal = ASSIGN.findall(command)
    values = {name: os.path.normpath(value) for name, _, value in literal}
    for name, value in values.items():
        if len(re.findall(r"\b" + name + r"=", command)) != sum(1 for n, _, _ in literal if n == name) or \
                len({os.path.normpath(v) for n, _, v in literal if n == name}) != 1:
            continue  # se reasigna con otro valor o con algo no literal: no se adivina
        command = re.sub(r"\$\{" + name + r"\}|\$" + name + r"\b", lambda _: value, command)
    return command


def redirect_targets(command):
    """Destinos de > y >> reales: ignora los que estan dentro de comillas o en el cuerpo de un heredoc."""
    masked = HEREDOC.sub(lambda m: m.group(0)[: m.group(0).index("\n")] + re.sub(r"[^\n]", "x", m.group(0)[m.group(0).index("\n"):]), command)
    masked = QUOTED.sub(lambda m: m.group(0)[0] + "x" * (len(m.group(0)) - 2) + m.group(0)[-1], masked)
    return [command[m.start(1):m.end(1)].strip("'\"") for m in REDIRECT.finditer(masked)]


def leading_cd(command):
    """Directorio de un `cd /ruta &&` inicial, si es el unico cd del comando. Sin el, una ruta relativa queda sin resolver."""
    found = re.match(r"\s*cd\s+(['\"]?)(/[^'\"\s;&|]+)\1\s*(&&|;)", command)
    if not found or len(re.findall(r"\b(cd|pushd)\b", command)) != 1:
        return None
    return os.path.normpath(found.group(2))


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
    if ".gates.jsonl" in command and (REDIRECT.search(command) or FILE_MUTATION.search(command) or INLINE_WRITE.search(command)):
        deny("los gates solo los registra el hook")
    check_forbidden(command, data)
    if NO_VERIFY.search(command):
        deny("no se usa --no-verify: arregla lo que el hook del repo rechaza")
    if agent not in READ_ONLY_BASH:
        return
    if GIT_DESTRUCTIVE.search(command) or GIT_WRITE.search(command):
        deny(f"{agent} no modifica el repo con git: {command[:80]}")
    command = expand_vars(command)
    if INLINE_WRITE.search(command) and not any(disposable(w.strip("'\"()"), data) for w in re.split(r"[\s,]+", command)):
        deny(f"{agent} no escribe con un interprete en linea. Si necesita un cambio, usa Write o Edit donde su rol lo permite, o reportalo")
    base = leading_cd(command)
    for target in redirect_targets(command):
        if not (target == "/dev/null" or disposable(absolute(target, base), data) or target.startswith(("$TMPDIR", "${TMPDIR"))):
            deny(f"{agent} no escribe archivos por Bash ({target}). Usa una ruta absoluta en /tmp, escrita en el mismo comando")
    if base:
        # Dentro de un cd a /tmp, toda ruta absoluta tambien debe ser desechable, y nada sube con "..".
        rest = command.split("&&", 1)[-1] if "&&" in command else command.split(";", 1)[-1]
        paths = [w.strip("'\"") for w in rest.split() if w.strip("'\"").startswith("/")]
        safe = disposable(base + "/", data) and ".." not in rest and all(disposable(p, data) or p == "/dev/null" for p in paths)
    else:
        safe = any(disposable(w, data) or "TMPDIR" in w for w in command.split())
    if FILE_MUTATION.search(command) and not safe:
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
        if path.endswith(".gates.jsonl"):
            deny("los gates solo los registra el hook")
        rule = WRITE_RULES.get(agent)
        if rule and not disposable(path, data) and not re.search(rule, path):
            deny(f"{agent} no puede escribir {path}. Reporta el hallazgo en lugar de modificarlo")
    elif tool == "Bash":
        check_bash(agent, tool_input.get("command") or "", data)


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
    if re.match(r"/(nexus-agile:)?nexus-auto\b", prompt):
        session["delegated"] = True
        save_session(data, session)
        return
    override = re.match(r"NEXUS_OVERRIDE\s+(\S.*)$", prompt, re.S)
    if override:
        session["override"] = override.group(1).strip()
        save_session(data, session)
        print("NexusAgil: el proximo bloqueo se deja pasar y queda registrado con este motivo.")
        return
    found = re.fullmatch(rf"({'|'.join(GATES)})(?:\s+(\S+))?", prompt)
    if found:
        apply_gate(data, session, found.group(1), found.group(2))


def apply_gate(data, session, gate, reference):
    hu_dir = find_hu_dir(data, session, reference)
    if hu_dir is None or not hu_dir.is_dir():
        print(f"NexusAgil: no se pudo ubicar la HU de {gate}. La persona debe escribir: {gate} <NNN o ruta>")
        return
    record_gate(hu_dir, gate, "human")
    session["hu_dir"] = str(hu_dir)
    save_session(data, session)
    print(f"NexusAgil: {gate} registrado para {hu_dir}")


def cmd_answer(data):
    """Respuesta a AskUserQuestion: elegir la opcion con el nombre del gate tambien cuenta."""
    text = json.dumps(data.get("tool_response") or "")
    session = load_session(data)
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
    if not mine:
        return
    transcript = data.get("agent_transcript_path")
    found_phase = re.search(r"FASE:\s*([A-Z0-9.]+)", transcript_prompt(transcript))
    phase_found = found_phase.group(1) if found_phase else None
    spawn = next((s for s in mine if s["phase"] == phase_found), mine[0])
    session["spawns"].remove(spawn)
    save_session(data, session)
    hu_dir = Path(spawn["hu_dir"])
    problems = []
    if agent in READ_ONLY_BASH and spawn.get("tree") and tree_hash(spawn["code_root"]) != spawn["tree"]:
        problems.append("el arbol de git cambio mientras corrias, y tu rol no modifica codigo. Restauralo y reporta por que")
    expected = PHASE_OUTPUT.get(spawn["phase"])
    if expected and spawn["phase"] != "F2.5":
        stem = expected[:-3]
        report = latest(hu_dir, stem)
        if report is None:
            problems.append(f"falta {hu_dir / expected}")
        elif spawn["phase"] in ("AR", "CR", "F4") and not re.search(r"^STATUS:", report.read_text(encoding="utf-8"), re.M):
            problems.append(f"{report.name} no tiene la linea STATUS:")
    if spawn["phase"] in ("F0F1", "F1") and (hu_dir / "work-item.md").is_file() and questions_section(hu_dir) is None:
        problems.append("work-item.md no tiene la seccion PREGUNTAS PARA EL HUMANO. Agregala, aunque diga Ninguna")
    if spawn["phase"] == "F4" and transcript and Path(transcript).is_file():
        if '"name":"Bash"' not in Path(transcript).read_text(encoding="utf-8").replace('": "', '":"'):
            problems.append("QA no ejecuto ningun comando: su evidencia debe ser comando y salida")
    if problems:
        print(json.dumps({"decision": "block", "reason": "NEXUS GATE: " + "; ".join(problems)}))
        return
    if hu_dir.is_dir():
        write_state(hu_dir, phase=spawn["phase"], agent=agent, status="done")


def cmd_session(data):
    """Despues de compactar o retomar: recordar la HU activa, porque el chat ya no es confiable."""
    session = load_session(data)
    if not session.get("hu_dir"):
        return
    state_path = Path(session["hu_dir"]) / ".nexus-state.json"
    if state_path.exists():
        print(f"NexusAgil: HU activa en {session['hu_dir']}. Estado: {state_path.read_text(encoding='utf-8')}. "
              "Antes de lanzar otra fase, relee .gates.jsonl y los artefactos de esa carpeta.")


COMMANDS = {"gate": cmd_gate, "prompt": cmd_prompt, "answer": cmd_answer, "stop": cmd_stop, "session": cmd_session}


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command not in COMMANDS:
        deny(f"subcomando desconocido: {command}")
    COMMANDS[command](json.load(sys.stdin))


if __name__ == "__main__":
    main()
