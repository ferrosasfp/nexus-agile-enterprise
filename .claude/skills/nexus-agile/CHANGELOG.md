# Changelog — NexusAgil

## Sin publicar — Correcciones de la primera corrida real

### Corregido
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
- Bloqueo por destino real (`PostToolUse(Bash)`): si un Bash de un agente cambia un archivo de `HU_DIR` sin Write ni Edit, queda como `VIOLATION` en `.gates.jsonl` y el agente se frena. En la corrida real, el unico rodeo efectivo (un script de Python que edito `sdd.md`) paso el filtro por texto.
- Nota sobre proxies que reescriben comandos (rtk): la evidencia se toma con el comando sin reescribir.

### Cambiado
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
