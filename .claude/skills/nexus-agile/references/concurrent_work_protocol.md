# Protocolo de Trabajo Concurrente

> **Principio**: Multiples desarrolladores trabajan en paralelo sin pisarse.
> Cada HU tiene un owner. Cada branch tiene un responsable. Los conflictos se previenen, no se resuelven.

---

## Ownership de HUs

### Asignacion en Sprint Planning

Durante Sprint Planning, el SM facilita la asignacion:

1. PO presenta HUs priorizadas
2. TL propone asignacion basada en: dominio del dev, carga actual, dependencias entre HUs
3. Cada HU queda asignada a exactamente **1 dev owner**
4. El owner es responsable de toda la HU: F3, PR, fixes post-AR, fixes post-CR

### Reglas de ownership

| Regla | Detalle |
|-------|---------|
| **1 owner por HU** | No se comparten HUs entre devs. Si es muy grande, se divide en 2 HUs. |
| **Owner = responsable del PR** | El owner crea el branch, abre el PR, responde a reviews. |
| **Re-asignacion** | Solo el TL puede re-asignar una HU. Se documenta en el sprint tracker. |
| **Bloqueo** | Si el owner esta bloqueado >4h, notifica al SM. SM coordina desbloqueo o re-asignacion. |
| **Ausencia** | Si el owner no esta disponible (enfermedad, emergencia), TL re-asigna. El nuevo owner hereda el branch y PR existentes. |

### Formato de asignacion en Sprint Planning

| HU | Owner | Branch | Dependencias | Status |
|----|-------|--------|-------------|--------|
| 001 — Login con OAuth | @dev-1 | feat/001-login-oauth | ninguna | pending |
| 002 — Dashboard metricas | @dev-2 | feat/002-dashboard | 001 (auth) | blocked-by-001 |
| 003 — Export CSV | @dev-3 | feat/003-export-csv | ninguna | pending |

---

## Branch Strategy

### Modelo: Feature Branches + PR obligatorio

main (protegido — nadie pushea directo)
  feat/NNN-titulo   -> PR -> main (requiere review)
  feat/NNN-titulo   -> PR -> main (otro dev, otra HU)
  hotfix/NNN-titulo -> PR -> main (fast-track review)

### Reglas de branching

| Regla | Detalle |
|-------|---------|
| **Naming** | feat/NNN-titulo-corto o hotfix/NNN-titulo-corto. NNN = numero de HU del _INDEX.md. |
| **Base** | Siempre desde main actualizado. git checkout main, git pull, git checkout -b feat/NNN-titulo. |
| **1 branch = 1 HU** | No mezclar trabajo de multiples HUs en un branch. |
| **Vida corta** | Un branch no deberia vivir mas de 1 sprint. Si pasa, el TL revisa si la HU es demasiado grande. |
| **Rebase before PR** | Antes de abrir PR: git fetch origin main, git rebase origin/main. Resolver conflictos localmente. |
| **Delete after merge** | Branch se borra despues del merge. No acumular branches muertos. |

### Proteccion de main

Configurar en GitHub/GitLab:
- required_reviews: 1 (minimo 1 reviewer humano)
- dismiss_stale_reviews: true (re-review si hay nuevos commits)
- require_status_checks: true (CI debe pasar)
- require_linear_history: true (no merge commits, rebase only)
- restrict_push: true (nadie pushea directo a main)

---

## PR Workflow

### Ciclo de vida de un PR

1. Dev completa F3 (implementacion)
2. AI ejecuta AR (Adversarial Review) — BLOQUEANTEs? Dev corrige, AI re-ejecuta AR
3. AI ejecuta CR (Code Review)
4. Dev abre PR contra main
5. CI corre (typecheck + lint + tests + build) — CI falla? Dev corrige, push, CI re-corre
6. Peer review (otro dev humano) — Cambios pedidos? Dev corrige, push, re-review
7. TL aprueba (approval final)
8. TL o Dev mergea (squash merge)
9. Branch eliminado

### Contenido del PR

El PR debe incluir:
- **HU**: NNN — Titulo de la HU
- **Resumen**: 1-3 oraciones sobre que hace este cambio
- **Tipo**: Feature / Bugfix / Hotfix / Refactor / Tech task
- **Archivos clave**: path/to/file.ts — que hace
- **Testing**: Tests agregados, tests pasan, build limpio
- **Checklist**: Patrones seguidos, sin imports inventados, sin archivos fuera de scope, AR completado, CR completado
- **Evidencia**: Link al validation.md o copiar resumen de F4

### Reglas de review

| Regla | Detalle |
|-------|---------|
| **Reviewer asignado** | TL asigna reviewer en sprint planning o al abrir el PR. No self-review. |
| **Tiempo de review** | Max 24h despues de abrir PR. Si no hay review en 24h, SM escala. |
| **Review scope** | Reviewer verifica: patrones seguidos, no hay code smells, tests cubren lo importante, no hay drift vs SDD. |
| **Approval count** | Equipo chico: 1 approval (TL o peer). Equipo mediano+: 1 peer + 1 TL. |
| **Merge responsibility** | El que da el ultimo approval mergea. O TL si prefiere controlar el timing. |

---

## Prevencion de Conflictos

### Estrategia principal: prevenir, no resolver

| Estrategia | Como |
|-----------|------|
| **Scope disjunto** | En Sprint Planning, TL verifica que las HUs no toquen los mismos archivos. Si 2 HUs tocan el mismo archivo, se secuencian. |
| **Archivo compartido** | Si es inevitable (ej: router principal, schema DB), TL define orden: HU-A primero, HU-B despues. HU-B espera merge de HU-A. |
| **Rebase frecuente** | Devs hacen git fetch origin main, git rebase origin/main al menos 1x al dia. |
| **Archivos de barril** | Exports centralizados (index.ts, routes.ts) son propiedad del TL. Devs agregan su linea, TL resuelve si hay conflicto. |
| **Feature flags** | Para features que tocan flujos criticos, usar feature flags. Merge a main sin activar. Activar despues de validar. |

### Cuando hay conflicto

Dev A y Dev B modificaron el mismo archivo:
1. Dev B (segundo) hace rebase y resuelve conflictos
2. Conflicto trivial? (import agregado, linea nueva en zona distinta) -> Dev B resuelve solo
3. Conflicto no trivial? -> Dev B llama a Dev A, resuelven juntos. TL arbitra si no hay acuerdo.
4. Push + re-run CI
5. Re-request review si los cambios son significativos

---

## Coordinacion de HUs Dependientes

### Tipos de dependencia

| Tipo | Ejemplo | Manejo |
|------|---------|--------|
| **Hard dependency** | HU-002 necesita la tabla que crea HU-001 | HU-002 no empieza F3 hasta que HU-001 esta mergeada |
| **Soft dependency** | HU-002 usa un componente que HU-001 modifica | Pueden correr en paralelo. Dev-002 revisa el PR de HU-001 para anticipar cambios. |
| **Interface dependency** | HU-001 crea un API, HU-002 la consume | Definir Integration Contract en F2. Ambas HUs referencian el mismo contrato. Dev-002 puede mockear mientras Dev-001 implementa. |
| **Sin dependencia** | HU-001 y HU-003 tocan dominios distintos | Paralelo total. Sin coordinacion necesaria. |

### Visualizacion en Sprint Planning

Ejemplo:
- HU-001 (Login OAuth) -> HU-002 (Dashboard) [hard: necesita auth]
- HU-003 (Export CSV) [sin dependencias]
- HU-002 -> HU-004 (Notificaciones) [soft]

Orden de ejecucion:
- W1: HU-001 + HU-003 (paralelo)
- W2: HU-002 (despues de merge HU-001)
- W3: HU-004 (despues de merge HU-002)

---

## Comunicacion del Equipo

### Canales minimos

| Canal | Proposito | Frecuencia |
|-------|----------|-----------|
| #sprint-NNN (Slack/Teams) | Status, bloqueos, preguntas rapidas | Continuo |
| Daily standup (async o sync) | Que hice, que hare, bloqueos | Diario |
| PR comments | Review tecnico | Por PR |
| Sprint Planning | Asignacion y estimacion | Inicio de sprint |
| Sprint Status | Mid-sprint check | Mitad de sprint |
| Retrospectiva | Mejora continua | Fin de sprint |

---

## Reglas Globales de Concurrencia

1. **No pushear a main** — Todo va por PR. Sin excepciones.
2. **1 dev = 1 HU activa** — Un dev no trabaja en 2 HUs simultaneamente. Si esta bloqueado, puede tomar otra HU con permiso del TL.
3. **Rebase diario** — Minimo 1 rebase contra main por dia de trabajo.
4. **PR chicos** — Si un PR tiene >500 lineas cambiadas, probablemente la HU era muy grande. Dividir en futuro.
5. **Merge rapido** — PRs aprobados se mergean el mismo dia. No acumular PRs aprobados sin mergear.
6. **CI obligatorio** — Ningun PR se mergea con CI rojo. Sin excepciones.
7. **Feature flags para riesgo** — Si una feature puede romper el flujo principal, usar feature flag. Merge desactivado, activar despues de validar.
8. **Comunicar bloqueos inmediatamente** — No esperar al daily. Slack/Teams en el momento.
