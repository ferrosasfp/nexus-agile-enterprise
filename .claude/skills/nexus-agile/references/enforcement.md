# Enforcement — lo que se cumple por codigo

> Una regla en texto es una sugerencia: el modelo decide si la sigue. Lo que debe ocurrir siempre va en un hook.

## Que controla cada hook

`hooks/nexus_hook.py` es un solo despachador. Los sub-agentes de un plugin ignoran los hooks de su frontmatter, por eso no se usan ahi.

| Evento | Que hace |
|--------|----------|
| `UserPromptSubmit` | Registra `HU_APPROVED`, `SPEC_APPROVED` y `RELEASE_APPROVED` escritos por una persona, con el hash del documento |
| `PostToolUse(AskUserQuestion)` | Registra el gate si se elige la opcion con su nombre |
| `PreToolUse(Agent)` | Bloquea la fase sin `FASE:`, `HU_DIR:`, artefacto o gate; si el documento cambio despues de aprobarlo; si quedan preguntas sin responder en el work-item (F2 y F3); si `CODE_ROOT` no esta resuelto o no es un repo git; y si la sesion usa el plugin y el agente va sin prefijo |
| `PreToolUse(Write, Edit)` | Cada agente de especificacion o revision escribe solo sus artefactos |
| `PreToolUse(Bash)` | Solo lectura para quienes no implementan, incluidos interpretes en linea que escriben. Nadie usa `--no-verify`. `forbidden_commands` del proyecto vale para todos, incluida la sesion principal |
| `SubagentStop` | Exige el reporte y su linea `STATUS:`; exige la seccion de preguntas en el work-item; compara el arbol de git de todo agente que no implementa; QA debe haber ejecutado al menos un comando |
| `SessionStart(compact, resume)` | Recuerda la HU activa y su estado |

## Archivos que escribe

| Archivo | Contenido |
|---------|-----------|
| `HU_DIR/.gates.jsonl` | Gate, quien lo dio (`human`, `claude-delegated`), hash y fecha. Tambien cada override |
| `HU_DIR/.nexus-state.json` | Fase, agente y estado, para retomar |
| `HU_DIR/.versions/` | Copia de cada documento en el momento en que se aprobo |

## Falsos positivos

La persona escribe `NEXUS_OVERRIDE <motivo>`: pasa el proximo bloqueo y queda registrado. Un agente no puede dar un override.

## Instalacion

- **Como plugin** (`--plugin-dir` o marketplace): los hooks cargan solos.
- **Copia en `.claude/`** (`setup.sh`): copia `hooks/` y agrega el bloque de `hooks/hooks.json` a `settings.json`, cambiando `${CLAUDE_PLUGIN_ROOT}/hooks` por la ruta real. Sin eso, las reglas siguen siendo solo texto.

## Lo que NO garantiza

- **No es una frontera de seguridad.** En una corrida real, un agente bloqueado edito su artefacto con `python3 -c`. Ese camino ya se cierra, pero `python3 script.py` sigue pasando el filtro. La comparacion del arbol lo detecta despues, y no cubre artefactos fuera del repo.
- **`forbidden_commands` compara texto.** Un alias o un script que envuelve el comando no coincide. Reduce errores; no reemplaza quitar las credenciales de produccion del entorno.
- **La fase la declara el orquestador.** Una fase mal declarada pasa como esa fase.
- **La sesion principal no esta limitada.** Un orquestador que implementa por su cuenta no se bloquea.
- **`SubagentStop` insiste una sola vez**, para evitar ciclos.
- **Sin `python3`, el hook falla**, y con `onFailure: block` eso bloquea. Es intencional.
