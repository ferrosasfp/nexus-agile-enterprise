# Enterprise — Equipos y Organizaciones

> NexusAgile fue creado para operadores individuales. Esta seccion extiende la metodologia para equipos de 2+ personas.

### Roles Humanos y Matriz de Autoridad

En equipo, los gates son de **personas, no de bots**. Cada gate tiene un aprobador humano definido.

| Rol | Responsabilidad principal | Gates |
|-----|--------------------------|-------|
| **Product Owner** | Define QUE, prioriza backlog | `HU_APPROVED`, `SPRINT_APPROVED` |
| **Tech Lead** | Define COMO, calidad tecnica | `SPEC_APPROVED` |
| **Developer** | Implementa, revisa PRs de peers | — |
| **QA Lead** | Valida evidencia, drift detection | F4 sign-off |
| **Scrum Master** | Facilita ceremonias, remueve impedimentos | `REVIEW_APPROVED`, `RETRO_APPROVED` |

> Detalle completo, delegacion AI, escalation paths, y configuracion por tamano de equipo: `references/roles_matrix.md`

### Trabajo Concurrente

Multiples devs trabajan en paralelo sin pisarse:

- **1 owner por HU** — asignado en Sprint Planning
- **Feature branches** — `feat/NNN-titulo`, siempre PR → main
- **Branch protection** — nadie pushea directo a main
- **Rebase diario** — prevenir conflictos, no resolverlos
- **Dependency map** — HUs dependientes se secuencian, independientes van en paralelo

> Detalle completo, PR workflow, conflict resolution: `references/concurrent_work_protocol.md`

### Metricas y Dashboard

Lo que no se mide no se mejora:

| Categoria | Metricas clave |
|-----------|---------------|
| Velocidad | Lead time, throughput, carry-over rate, PR merge time |
| Calidad | BLOQUEANTE rate, drift rate, bug escape rate, re-work rate |
| Anti-alucinacion | Imports fantasma, archivos fuera de scope, exemplar miss rate |
| Eficiencia AI | Tokens/HU, costo/HU, context overflow events |

> Templates de dashboard, sprint report, alertas: `references/metrics.md`

### Onboarding

Cada rol tiene un path de lectura especifico. Un dev nuevo puede ejecutar su primera HU en <1 hora.

> Guia completa, cheat sheet, FAQ: `references/onboarding.md`

### Dispatcher Enterprise

| Necesidad | Referencia |
|-----------|-----------|
| Roles y permisos | `references/roles_matrix.md` |
| Branches, PRs, conflictos | `references/concurrent_work_protocol.md` |
| KPIs, dashboard, sprint report | `references/metrics.md` |
| Primer dia, setup, FAQ | `references/onboarding.md` |


### Governance y Protocolos de Excepcion

La realidad interrumpe los procesos. Estos protocolos definen que hacer:

| Situacion | Protocolo | Referencia |
|-----------|----------|-----------|
| PO cambia scope despues de gate | Scope Change Tiers (Trivial/Menor/Mayor) | references/governance.md |
| Dev disputa un BLOQUEANTE del AR | Dispute Resolution (Confirmar/Degradar/Descartar) | references/governance.md |
| Produccion se cae mid-sprint | Incident Protocol (P0/P1/P2) | references/governance.md |
| FAST resulta ser complejo | Escalation FAST->QUALITY | references/governance.md |
| Proyecto nuevo sin codigo | Greenfield Bootstrap | references/greenfield_bootstrap.md |
| 2+ equipos comparten dependencias | Cross-Team Protocol | references/cross_team_protocol.md |
| Componentes se comunican | Integration Contract | references/integration_contract_template.md |
