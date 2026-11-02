# Changelog — NexusAgil

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
