# Case Types — Modificadores de Pipeline

> **Principio**: No todas las HUs son iguales. Un cambio de DB no es lo mismo que un cambio de copy.
> Los Case Types son modificadores que agregan checks especificos al pipeline estandar sin cambiar su estructura.

---

## Como funcionan

El Case Type se detecta en **F0 (Triage)** o **F2 (SDD)** y agrega checks obligatorios a fases existentes.
No cambia el pipeline — lo enriquece.

```
Pipeline normal:        F0 → F1 → F2 → F2.5 → F3 → AR → CR → F4 → F5 → DONE
                              ↑         ↑              ↑         ↑    ↑
Case Type modifiers:    [detect]  [extra checks]  [AR extras] [QA extras] [release extras]
```

---

## Case Types Definidos

### DB-MIGRATION

> HU que crea, modifica o elimina tablas/columnas/indices en base de datos.

| Fase | Check adicional |
|------|----------------|
| **F2 (SDD)** | Incluir seccion "Migration Plan": up migration + down migration + datos existentes afectados |
| **F2 (SDD)** | Constraint: REQUIRED — migration reversible (down migration que restaura estado anterior) |
| **F2 (SDD)** | Evaluar: datos existentes se corrompen? Necesita data backfill? |
| **AR** | Verificar: down migration existe y funciona. Verificar: no hay DROP sin backup plan. |
| **F4 (QA)** | Ejecutar migration en entorno limpio. Verificar: migration es idempotente. |
| **F5 (Release)** | Migration aplicada en staging sin errores. Down migration testeada en staging. |

**Nunca FAST**: Una HU con DB-MIGRATION nunca califica como FAST. Auto-upgrade a QUALITY.

**Deteccion en F0**: HU menciona "tabla", "columna", "schema", "migration", "base de datos", o el SDD incluye cambios en schema/prisma/migrations.

---

### CONTRACT-CHANGE

> HU que modifica una API publica, un contrato entre servicios, o una interfaz consumida por terceros.

| Fase | Check adicional |
|------|----------------|
| **F2 (SDD)** | Incluir seccion "Contract Impact": endpoints afectados + consumidores conocidos + estrategia de compatibilidad |
| **F2 (SDD)** | Constraint: REQUIRED — backward compatible o versionado (v1/v2) |
| **F2 (SDD)** | Definir Integration Contract (ver `references/integration_contract_template.md`) |
| **AR** | Verificar: consumidores existentes no se rompen. Verificar: error codes documentados. |
| **F3** | Implementar: contract tests (request/response validation). |
| **F4 (QA)** | Ejecutar contract tests. Verificar: OpenAPI/schema actualizado si existe. |
| **F5 (Release)** | Consumidores notificados. Periodo de deprecation definido si es breaking change. |

**Nunca FAST**: Un cambio de contrato nunca califica como FAST. Auto-upgrade a QUALITY.

**Deteccion en F0**: HU menciona "API", "endpoint", "response", "request", "contrato", "integracion", o el SDD modifica archivos en /api/ con cambios de signature.

---

### INFRA-ENV

> HU que agrega/modifica variables de entorno, secrets, configuracion de CI/CD, o infraestructura.

| Fase | Check adicional |
|------|----------------|
| **F2 (SDD)** | Listar: env vars nuevas/modificadas + valores por entorno (dev/staging/prod) |
| **F2 (SDD)** | Constraint: FORBIDDEN — secrets hardcodeados en codigo. REQUIRED — .env.example actualizado. |
| **AR** | Verificar: no hay secrets en el repo. Verificar: env vars documentadas. |
| **F4 (QA)** | Verificar: app funciona sin las env vars nuevas (graceful degradation o error claro). |
| **F5 (Release)** | Env vars configuradas en TODOS los entornos antes de deploy. Verificar con checklist. |

**Puede ser FAST**: Si es solo agregar una env var existente a un nuevo entorno, puede ser FAST con checklist reducido.

**Deteccion en F0**: HU menciona "env", "variable de entorno", "secret", "config", "CI/CD", o el SDD modifica .env*, CI config, infra files.

---

### SECURITY-INCIDENT

> Respuesta a una vulnerabilidad descubierta (reporte externo, CVE, audit finding, penetration test).

| Fase | Check adicional |
|------|----------------|
| **F0 (Triage)** | Clasificar severidad: CRITICAL (explotable, datos en riesgo) / HIGH (explotable, sin datos) / MEDIUM (teorico) |
| **F0 (Triage)** | CRITICAL: activar Hotfix pipeline inmediato. HIGH/MEDIUM: QUALITY pipeline con prioridad. |
| **F2 (SDD)** | Incluir seccion "Vulnerability Analysis": vector de ataque, impacto, CVSS si aplica |
| **F2 (SDD)** | Constraint: REQUIRED — fix elimina el vector, no solo lo oculta |
| **AR** | AR **obligatorio siempre** (sin excepciones). Adversary verifica que el vector esta cerrado. |
| **AR** | Check adicional: buscar variantes del mismo patron en el codebase (ej: si hay SQL injection en un endpoint, buscar en todos) |
| **F4 (QA)** | Incluir test que reproduce la vulnerabilidad (antes: falla, despues: pasa) |
| **F5 (Release)** | Deploy prioritario. Verificar: no hay otros vectores abiertos del mismo tipo. |
| **DONE** | Documentar: CVE ID (si aplica), timeline de respuesta, root cause, impacto estimado. |

**Nunca FAST**: Un security incident nunca es FAST. Minimo QUALITY (Hotfix si es CRITICAL).

**Deteccion en F0**: Trigger explicito: "security incident", "vulnerabilidad", "CVE", "audit finding".

---

### DATA-BACKFILL

> HU que ejecuta scripts de transformacion o correccion de datos en produccion.

| Fase | Check adicional |
|------|----------------|
| **F2 (SDD)** | Incluir seccion "Data Plan": registros afectados (estimado) + query de verificacion pre/post + plan de rollback de datos |
| **F2 (SDD)** | Constraint: REQUIRED — script idempotente (puede correrse 2x sin corromper datos) |
| **F2 (SDD)** | Constraint: REQUIRED — dry-run mode (correr sin aplicar, solo reportar que cambiaria) |
| **AR** | Verificar: script no borra datos sin backup. Verificar: transacciones con rollback en caso de error. |
| **F4 (QA)** | Ejecutar dry-run en staging. Verificar: registros afectados coinciden con estimado. |
| **F5 (Release)** | Ejecutar dry-run en prod (sin aplicar). Confirmar registros. Aplicar con supervision humana. |

**Nunca FAST**: Data backfill nunca es FAST. Siempre QUALITY.

**Deteccion en F0**: HU menciona "backfill", "migracion de datos", "correccion masiva", "script de datos", o el SDD incluye scripts que modifican datos existentes (no schema).

---

## Matriz de Compatibilidad con Modos

| Case Type | FAST | LAUNCH | QUALITY | Hotfix |
|-----------|------|--------|---------|--------|
| DB-MIGRATION | NUNCA | Si (simplificado) | Si (completo) | Solo si CRITICAL + upgrade |
| CONTRACT-CHANGE | NUNCA | Si (simplificado) | Si (completo) | Solo si CRITICAL + upgrade |
| INFRA-ENV | Solo si trivial | Si | Si (completo) | Si (env var urgente) |
| SECURITY-INCIDENT | NUNCA | NUNCA | Si (completo) | Si (CRITICAL) |
| DATA-BACKFILL | NUNCA | NUNCA | Si (completo) | NUNCA |

---

## Combinaciones

Una HU puede tener multiples Case Types. Ejemplo:
- Feature que agrega tabla + endpoint nuevo = **DB-MIGRATION + CONTRACT-CHANGE**
- Los checks se suman (no se duplican)
- El modo es el mas restrictivo que aplique

---

## Deteccion Automatica

En F0, el Triage Agent detecta Case Types por señales:

```
CASE TYPE DETECTION:
HU text signals:
  "tabla", "columna", "schema", "migration" → DB-MIGRATION
  "API", "endpoint", "contrato", "response" → CONTRACT-CHANGE
  "env", "secret", "config", "variable"     → INFRA-ENV
  "CVE", "vulnerabilidad", "security"       → SECURITY-INCIDENT
  "backfill", "datos existentes", "script"  → DATA-BACKFILL

SDD signals (F2):
  schema.prisma modified                    → DB-MIGRATION
  /api/ routes with signature changes       → CONTRACT-CHANGE
  .env* files modified                      → INFRA-ENV
  Data modification scripts                 → DATA-BACKFILL

If detected mid-pipeline (F2 or F3):
  → Add Case Type checks retroactively
  → Notify TL: "Case Type [X] detected. Adding required checks."
```

---

## Reglas

1. **Case Type nunca simplifica el pipeline** — solo agrega checks. Nunca se salta una fase por tener un Case Type.
2. **Deteccion puede ser tardia** — si se detecta en F2 o F3, agregar los checks a las fases restantes.
3. **TL puede agregar Case Types manualmente** — en SPEC_APPROVED, TL puede escribir: "SPEC_APPROVED + Case Type: DB-MIGRATION".
4. **Case Types se documentan en _INDEX.md** — columna adicional: `| 001 | ... | QUALITY | DB-MIGRATION,CONTRACT-CHANGE | DONE |`
