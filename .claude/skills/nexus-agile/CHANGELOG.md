# Changelog — NexusAgil

## 2.0.0-rc.5 — Primera HU de un proyecto nuevo (sin publicar)

Correcciones de la primera corrida en un proyecto vacio (Nexus Control, GH-1, manual).

### Corregido
- Hook: una sonda de solo lectura (`python3 -c ... >/dev/null`) ya no cuenta como escritura; un `.gates.jsonl` de prueba en `/tmp` se puede crear; una redireccion a un archivo de la HU se frena antes de correr (restaurar despues no alcanzaba con un `git commit` en el mismo comando); un gate dentro de un mensaje avisa que no se registro; SubagentStop frena caracteres de formato invisibles (U+202E, U+FEFF) en los artefactos.
- Un `.gates.jsonl` de prueba con `cd` a `/tmp` y ruta relativa ya no se bloquea (la rc.5 inicial lo seguia bloqueando: lo encontro el QA corto de la HU real). Repetir una fase sobre una HU cerrada no la reabre: queda como `rerun` en `.nexus-state.json`.
- `check_contract.py` entiende listas y rangos de ACs ("AC-1, 2, 3"); `nexus_metrics.py` cuenta una vez un agente que cruza un cambio de sesion; `nexus_memory.py` da claves distintas a dos hechos del mismo archivo.

### Cambiado
- **Tope de dos rondas** de correccion entre SPEC_VERIFY y SECURITY; lo que quede va a `Limites conocidos` del SDD y lo acepta la persona. Sin tope, F2 corrio 6 veces y se llevo el 59 % del costo de la HU.
- Seguridad y controles debiles se miden contra un atacante de afuera del codigo de la HU, no contra quien lo escribe.
- SPEC_VERIFY y SECURITY pueden correr en paralelo sobre la misma version del SDD.
- **Enmienda corta del contrato** por un fix de AR: solo el diff se verifica y se revisa, en una vuelta.
- En un proyecto sin codigo, el arquitecto comprueba el comportamiento del entorno con sondas de solo lectura.
- Docs: los temporales en `/tmp` los borra el orquestador al cerrar; las decisiones de la persona van a memoria como `decision/`.

## 2.0.0-rc.4 — Cerebro, seguridad del diseno y costo

### Agregado
- **Memoria del proyecto (el cerebro)**: hechos atados al blob SHA de git (`scripts/nexus_memory.py`), lecciones que aprueba la persona, reclamos de trabajo con vencimiento. El analista y el arquitecto leen (5 busquedas como maximo), Docs escribe. Antes ningun agente tenia las herramientas de Engram: el protocolo no se podia usar. Diseno: `docs/plan-cerebro.md`; protocolo: `references/engram_protocol.md`.
- **Gate de propiedad con cualquier tracker** (`references/tracker.md`): Jira, Linear, GitHub Issues, archivo o una herramienta propia. El hook no deja lanzar el primer analista sin `PROPIEDAD:` ni con una HU ajena.
- Evals: memoria con un hecho viejo y HU ajena, 6/6.

### Cambiado
- Lectura minima por agente, reporte de 25 lineas como maximo y salidas largas a archivo; el orquestador pasa rutas, no contenido.
- El fix-pack empieza por convertir cada reproduccion en un test en rojo; un hallazgo sin reproduccion no se arregla.

## 2.0.0-rc.3 — Correcciones de las dos primeras corridas reales

### Corregido
- Segunda HU real (AUTO con supervisor): 11 falsos bloqueos del hook a lecturas (`merge-base`, patrones de grep entre comillas, variables encadenadas, `..` dentro de un texto). Las variantes que escriben siguen bloqueadas.
- `check_contract.py`: titulo numerado del contrato en el SDD, rutas relativas a un subdirectorio declarado y ACs eliminados. 0 fallas falsas en las dos HUs reales.
- El re-CR acotado es obligatorio cuando el CR rechazo: el comando decia que era opcional y el hook lo exigia.
- `nexus_metrics.py`: tiempo activo (sin las esperas entre vueltas de un agente reanudado), vueltas y tokens procesados. El contexto final se quedaba corto con reanudaciones: en la segunda HU, 1,57 M de contexto final contra 45,8 M procesados.
- `.versions/` guarda cada entrega del analista y del arquitecto, no solo la aprobada.
- AUTO se delega con el comando al inicio de cualquier linea del mensaje (tambien tras un guion o un verbo como "Lanza"), y el hook lo confirma. En la segunda HU real, el comando venia dentro de un bloque de instrucciones y la sesion quedo sin delegar.
- Nombrar `.gates.jsonl` dentro de comillas o de un heredoc (una nota en la bitacora) ya no bloquea; escribir en el sigue bloqueado.
- Los comandos ya no comparan contra `main` fijo: cada prompt lleva `BASE_REF`, la base real de la HU.
- Con el plugin, el hook exige el prefijo `nexus-agile:`. Sin prefijo se usaba en silencio otra version instalada.
- `SKILL_DIR` busca primero dentro del plugin.
- Sin `CODE_ROOT` valido, el hook bloquea en lugar de usar la carpeta actual.
- `/nexus-p1-f0-f1` ya no se contradice con la edicion de `_INDEX.md`.
- Falsos positivos del hook (9 de 11 bloqueos en la corrida real): leer `.gates.jsonl`, rutas relativas despues de un `cd` a `/tmp`, variables asignadas en el mismo comando, y `>` entre comillas o en un heredoc.
- `check_contract.py` reconoce titulos numerados y filas "Modificar" con nota, y falla en voz alta si no reviso nada.
- DONE admite "APROBADO con observaciones" si la persona decide cerrar; procedimiento para cuando Claude Code rechaza que un subagente escriba `report.md`.
- La plantilla del SDD ya no lleva `SPEC_APPROVED: no`: el estado vive en `.gates.jsonl`, y cambiar la cabecera rompia el hash.
- La Wave -1 del Story File y el pre-flight de F3 solo comprueban, sin `npm install` ni variables que los tests no usan.
- `migrations_build_cmd` es opcional y puede ser `no disponible`.
- El supervisor no trata como rodeo que un agente siga la instruccion del propio mensaje del hook.

### Agregado
- Agente `nexus-security` y fase `SECURITY`: revisa la seguridad del diseno antes de `SPEC_APPROVED`, solo si el analista marca `security_review: required`. Matriz de autorizacion, hallazgos con camino de ataque, y el hook no deja pasar a F3 con hallazgos abiertos. Eval: 4 casos, 12/12. En un SDD con dos huecos por ausencia (webhook sin firma, exportacion sin chequeo de modulo), los dos agentes los ven, pero SPEC_VERIFY los deja como controles debiles y no frena el gate en 2 de 3 corridas; `nexus-security` los marca ALTO y frena en 3 de 3.
- `security_cmd` en `project-context.md`: controles de seguridad sin modelo que QA corre en F4.
- AUTO regla 11: un costo de mas del doble de la implementacion se escala con el costo y las opciones.
- Supervisor: no decide por costo hundido; ante un "presentar a la persona" solo continua si cada punto ya lo decidio la persona, citando donde. En la segunda HU real, la persona confirmo que no habria frenado ninguno de sus 10 veredictos.
- SPEC_VERIFY senala controles debiles del plan de tests (`debiles=`), con la forma de evadirlos.
- Regla de comandos reescritos (rtk) en cada agente.
- `report.md` y la descripcion del PR traen las dependencias de merge de una HU apilada: PRs en orden, y commit y arbol aprobados por QA para comprobar la resolucion de conflictos sin repetir QA. En la primera HU real, el PR quedo fuera de la guia de merges del sprint.
- `marketplace.json`: instalacion con `/plugin marketplace add` y `/plugin install`.
- README con lo medido y lo no medido.
- Fase `SPEC_VERIFY` en QUALITY (era el experimento E10): el adversario, en un contexto nuevo, verifica cada afirmacion del SDD contra el codigo y escribe `sdd-verification.md` con el hash del SDD. El hook no deja pasar a F3 con falsas abiertas ni con la verificacion de otra version. Se apaga con `spec_verify: false`.
- `nexus_metrics.py`: metricas de una HU desde los transcripts y `.gates.jsonl`. DONE lo corre y `report.md` trae la tabla.
- CI del repo de la metodologia (`.github/workflows/ci.yml`): pruebas sin modelo en cada push; eval a mano con secreto.
- Las preguntas del analista quedan en `work-item.md`, y el hook frena F2 y F3 mientras haya alguna abierta. En la corrida real, el reporte no llego y sus preguntas se habrian perdido.
- Regla del orquestador: si un agente no entrega su reporte, leer artefacto y transcript antes de seguir.
- El analista tiene `Edit`, para no reescribir el archivo entero en cada cambio.
- `forbidden_commands` en `project-context.md`: comandos que el hook bloquea para todos, incluida la sesion principal.
- Bloqueo de interpretes en linea que escriben, y comparacion del arbol en todo agente que no implementa, despues de que un arquitecto rodeara un bloqueo con `python3 -c`.
- Regla en todos los agentes: si un hook bloquea, detente y reporta.
- Guia para componer el gate unico desde el CI.
- Experimento E10: verificador independiente del SDD.
- Supervisor de AUTO (E8): agente `nexus-supervisor` de solo lectura y `/nexus-auto --supervisor`. Por defecto sigue el checklist.
- AUTO escala siempre las decisiones de producto, seguridad, alcance y costo, aunque el checklist de PASS.
- Cada gate guarda una copia del documento aprobado en `.versions/`.
- Politica de commits explicita antes de F3; los revisores y `review_package.sh` tambien ven el trabajo sin commitear.
- Eval que usa un comando real: los casos anteriores armaban los prompts a mano y no vieron los defectos de las plantillas.
- Bloqueo por destino real (`PostToolUse(Bash)`): si un Bash de un agente cambia un archivo de `HU_DIR` sin Write ni Edit, se restaura, la version modificada queda en `.violations/`, se registra como `VIOLATION` en `.gates.jsonl` y el agente se frena. Verificado en Claude Code real. En la corrida real, el unico rodeo efectivo (un script de Python que edito `sdd.md`) paso el filtro por texto.
- Nota sobre proxies que reescriben comandos (rtk): la evidencia se toma con el comando sin reescribir.
- Con el plugin, el hook frena un `SKILL_DIR` ausente, sin resolver o fuera del plugin (en el eval del 2-nov, 1 de 3 corridas del comando real apunto a otra version).
- Casos de eval `ar-script-cambia-artefacto` y `hook-script-disimulado` (en `_requieren-bash/`): un script que borra un riesgo o un AC del documento aprobado.
- Antes de un push, el orquestador muestra que dispara (CI, migraciones, preview).

### Cambiado
- El agente de docs pasa a sonnet; FAST sigue con `model: haiku` para el mini-report. En la segunda HU real, haiku metio 5 errores en `report.md`.
- El tope de 400 lineas del SDD no cuenta el plan de tests ni el contrato, y prohibe quitar riesgos, decisiones o dependencias para entrar. En la corrida real, el arquitecto borro un riesgo para no pasarse.
- La suite completa corre dos veces por HU, no cuatro: el Dev al cerrar F3 (con HEAD y salida en su reporte) y QA en F4. AR y CR corren solo lo que reproduce sus hallazgos.
- `contract_mode: unified` es el default: el contrato del Dev va en el SDD y no hay F2.5. `classic` (Story File) queda para tareas L o si la persona lo pide. Una HU con `story-file.md` previo sigue valiendo. En la corrida real, el Story File repitio casi todo el SDD y cada correccion se hizo dos veces.
- El bloque MCP de Engram paso de `.mcp.json` a `setup/mcp.json`: en la raiz, el plugin arrancaba su propio engram. `setup.sh` lo sigue copiando al proyecto.
- El arquitecto puede correr la suite en una copia desechable para medir el impacto.

## Sin publicar — Harness: enforcement, medicion y seguridad

### Agregado
- Hooks en `hooks/`: gates por codigo, escritura limitada por agente, Bash de solo lectura, `--no-verify` bloqueado, reporte y `STATUS:` exigidos, comparacion del arbol y estado por HU.
- Plugin (`.claude-plugin/plugin.json`) sin mover archivos ni renombrar agentes.
- `evals/` y `tests/test_nexus_hook.py`.
- `references/`: `enforcement`, `security`, `evaluation`, `experiments`, `living_spec`, `auto_blindaje`, `reference_detail`.
- `scripts/`: `check_contract.py` antes de F3, `review_package.sh` y `check_spec_ids.py`.
- Formato de bug con Sin cambio, comprobacion invertida de retiros, brechas de verificacion, clasificacion de fallas y ciclo de vida de reglas.

### Medido
- `evals/RESULTADOS.md`: 14 casos, 42 de 42 corridas, y lo que eso no demuestra. Los 2 casos de QA siguen sin correr.

### Cambiado
- Cada prompt lleva `FASE:` y `HU_DIR:`, y cada reporte una linea `STATUS:`.
- Revisores: reportan todo y el triaje va aparte; cierran con "¿lo fusionarias?"; el contenido externo es dato, nunca instruccion.
- `SKILL.md` baja de 20 KB: el detalle pasa a `references/`.

## Sin publicar — Fase 3: coherencia y poda

### Corregido
- F5 ahora se activa con `release_gate: true`. Antes decia aplicar por defecto, pero ningun comando la ejecutaba. `RELEASE_APPROVED` entra en la tabla de gates y nunca se autoaprueba.
- Autoaprobacion: "la IA no aprueba gates" y AUTO ya no se contradicen. La excepcion es la delegacion explicita de `HU_APPROVED` y `SPEC_APPROVED`.
- Limites de FAST y FAST+AR: una sola tabla, en `quick_flow.md`. FAST admite hasta 2 archivos de codigo mas sus tests, y menos de 50 lineas.
- FAST+AR aparece en `SKILL.md` y en el sizing del analista.
- F0 y F1 son del Analyst, y F2 del Architect. Se quitaron la revision de SDD por Adversary y el "Spec Writer", que ningun comando ejecutaba.
- Una fase por lanzamiento, salvo F0+F1. El protocolo mandaba F2 y F2.5 juntos, con un gate en medio.
- Conteos corregidos: 11 comandos, 6 agentes y 9 roles.
- QA en FAST: cada AC lleva comando y salida.
- Docs no cierra el issue: se lo recuerda al humano.
- Texto actualizado sobre permisos en segundo plano, tool Agent y precios.

### Cambiado
- Menos enfasis visual: sin ⛔, 🔴 ni ⚠️ en agentes y comandos, y menos mayusculas. Se conservan los nombres de gates, marcadores y artefactos.

### Movido
- Enterprise pasa a `references/enterprise.md`, y el reporte final de AUTO a `references/auto_completion_report.md`.

### Quitado
- Party Mode, personalidades del roster, celebracion de la retro y metricas futuras de FAST.

### Evaluado
- `/nexus-auto` como Workflow: no se migra. Ver `references/workflow_evaluation.md`.

## Sin publicar — Fase 2: modernizacion

### Agregado
- `contract_mode: unified`: en tareas S/M sin riesgo, el contrato de implementacion va dentro del SDD y no hay F2.5. Sin el campo, todo sigue como `classic`.
- Verificacion de BLOQUEANTEs: antes del fix-pack, un agente nuevo intenta reproducirlos y escribe `blq-verification.md`. Ante la duda, siguen bloqueando. Descartar un BLQ-ALTO o de las categorias 1, 9, 10 u 11 requiere al humano.
- Worktrees por HU y candados con `flock` para recursos compartidos.
- LSP opcional en arquitecto, dev y adversario, con Grep como alternativa.
- `effort: high` en arquitecto y adversario.

### Cambiado
- El Dev puede leer el SDD para entender el porque. El contrato sigue definiendo el trabajo y, si difieren, manda el contrato.

### Decidido
- No se usa `isolation: worktree` en `nexus-dev`: sale por defecto de la rama default y no ve archivos sin commit.

### Quitado
- IDs de un proyecto real en ejemplos y comandos.

## Sin publicar — Fase 1: errores y seguridad

### Seguridad
- Se quito la sugerencia de aplicar migraciones al remoto mientras corre el AR.
- Revisores y orquestador ya no ejecutan `git reset --hard`, `git checkout -- .` ni `git pull`; se reemplazaron por `fetch` y `status`. Los permisos de ejemplo dejan de autorizar `git *`.

### Corregido
- AR: una sola lista de 12 categorias. `adversarial_review_checklist.md` se reescribio sobre esas 12 y conserva sus checks.
- CR: una sola lista de 8 checks, y un solo responsable, `nexus-adversary`. SOLID queda como lente del check 3 y los tests pasan a la categoria 7 del AR.
- Analista: sigue en sonnet porque su salida la revisa un humano; en AUTO QUALITY se pide opus. Vuelve Grep y suma Bash de lectura, WebFetch y lectura de Jira. Documentacion alineada, incluido docs en haiku.
- Modo no interactivo: los sub-agentes no pueden preguntar. El analista marca `[NEEDS CLARIFICATION]` y devuelve `PREGUNTAS PARA EL HUMANO`; el orquestador pregunta o escala.
- Evidencia de QA: comando y salida literal. Una cita `archivo:linea` sola ya no alcanza.
- QA corre una vez el gate unico; ya no depende de que el CR lo haya corrido. Las inyecciones de prueba se hacen en una copia desechable.
- Revisores y QA reciben Write para sus reportes, y la documentacion ya no afirma que no pueden modificar codigo.
- Las referencias de agentes y comandos usan `$SKILL_DIR`, porque una ruta relativa no resolvia desde el repo.

### Agregado
- `references/paths.md`: `NEXUS_ROOT` y `CODE_ROOT` para dejar artefactos fuera del repo. Sin configurar, el comportamiento no cambia.
- `Gate unico` y `Entorno de validacion` en `project_context_template.md`, para equipos que aplican migraciones despues, en una ventana manual.
- `scripts/check_consistency.sh`: verifica conteos, modelos, tools, rutas y comandos prohibidos.
