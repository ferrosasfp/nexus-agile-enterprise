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
| `PostToolUse(Bash)` | Bloqueo por destino real: compara los archivos de `HU_DIR` antes y despues de cada Bash de un agente. Si cambio alguno que no se escribio con Write o Edit, lo registra como `VIOLATION` en `.gates.jsonl` y frena al agente, sin importar como estaba escrito el comando |
| `SubagentStop` | Frena al agente que tiene una `VIOLATION` propia en esta fase; exige el reporte y su linea `STATUS:`; exige la seccion de preguntas en el work-item; compara el arbol de git de todo agente que no implementa; QA debe haber ejecutado al menos un comando |
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

- **No es una frontera de seguridad.** En una corrida real, un agente bloqueado edito `sdd.md` con un script de Python lanzado por Bash, y el filtro por texto no lo vio. Ahora la comparacion despues de cada Bash lo detecta, pero despues de que paso: el cambio queda hecho y registrado, y lo revierte una persona. Tampoco ve un proceso que siga escribiendo en segundo plano despues de que el comando termina.
- **El filtro previo es por texto.** Resuelve un `cd` inicial a `/tmp`, variables asignadas en el mismo comando, comillas y heredocs. Fuera de eso puede dar falsos positivos: en la prueba real de noviembre, 9 de 11 bloqueos fueron falsos, todos de esos tipos.
- **Herramientas que reescriben comandos.** Un proxy como rtk puede cambiar la salida de `cat`, `grep` o `diff` (en la prueba real devolvio salidas vacias o lineas que no estaban). La evidencia de AR, CR, QA y del supervisor se toma con el comando sin reescribir (`rtk proxy <cmd>` o la ruta absoluta, como `/usr/bin/diff`).
- **`forbidden_commands` compara texto.** Un alias o un script que envuelve el comando no coincide. Reduce errores; no reemplaza quitar las credenciales de produccion del entorno.
- **La fase la declara el orquestador.** Una fase mal declarada pasa como esa fase.
- **La sesion principal no esta limitada.** Un orquestador que implementa por su cuenta no se bloquea.
- **`SubagentStop` insiste una sola vez**, para evitar ciclos.
- **Sin `python3`, el hook falla**, y con `onFailure: block` eso bloquea. Es intencional.
