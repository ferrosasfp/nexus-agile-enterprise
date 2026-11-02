# Changelog — NexusAgil

## Sin publicar — Harness: enforcement, medicion y seguridad

### Agregado
- Hooks en `hooks/`: gates por codigo, escritura limitada por agente, Bash de solo lectura, `--no-verify` bloqueado, reporte y `STATUS:` exigidos, comparacion del arbol y estado por HU.
- Plugin (`.claude-plugin/plugin.json`) sin mover archivos ni renombrar agentes.
- `evals/` y `tests/test_nexus_hook.py`.
- `references/`: `enforcement`, `security`, `evaluation`, `experiments`, `living_spec`, `auto_blindaje`, `reference_detail`.
- `scripts/`: `check_contract.py` antes de F3, `review_package.sh` y `check_spec_ids.py`.
- Formato de bug con Sin cambio, comprobacion invertida de retiros, brechas de verificacion, clasificacion de fallas y ciclo de vida de reglas.

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
