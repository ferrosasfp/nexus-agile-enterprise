# Tracker: quien tiene cada HU

> El tracker del equipo (Jira, Linear, GitHub Issues, una herramienta propia o un archivo) es la autoridad sobre quien tiene una HU. NexusAgil no la decide: la consulta antes de empezar y deja visible que un agente la esta trabajando.
> Por que: en la segunda corrida real, un orquestador implemento entera una HU asignada a otro integrante del equipo, y nadie lo freno. En los estudios de sistemas multiagente, repetir trabajo ya hecho es la falla mas frecuente (15,7 % de 1.600 trazas, MAST 2025), y en el mercado el reclamo de una tarea es su asignacion en el tracker.

## Configuracion (`project-context.md`)

| Campo | Valor |
|-------|-------|
| **tracker** | `jira` / `linear` / `github` / `archivo` / `propio` |
| **tracker_project** | clave o URL del proyecto (ej: `SCRUM`, `owner/repo`) |
| **tracker_user** | como aparece la persona que usa NexusAgil en el tracker (nombre o id) |
| **tracker_write** | `true` / `false` (default `false`). Con `true`, NexusAgil comenta en el ticket al tomarlo y al cerrarlo |

## Cuatro operaciones

| Operacion | Cuando | Que devuelve o hace |
|-----------|--------|---------------------|
| `duenio(HU)` | Antes de F0 | Responsable actual, o nadie |
| `estado(HU)` | Antes de F0 | Estado actual (por hacer, en curso, en revision, cerrada) |
| `reclamar(HU)` | Al empezar, si `tracker_write: true` | Comentario en el ticket: que agente la trabaja, en que rama, desde cuando |
| `cerrar(HU)` | En DONE, si `tracker_write: true` | Comentario con el PR o la rama, el commit aprobado y el costo de la HU |

Mover el ticket de estado no es una de estas operaciones: lo hace la persona.

## Adaptadores

| tracker | duenio y estado | reclamar y cerrar |
|---------|-----------------|-------------------|
| `jira` | `getJiraIssue` del conector de Atlassian (campos assignee y status) | `addOrEditJiraIssueComment` |
| `linear` | La herramienta de lectura de issues del conector de Linear (assignee, delegate y state) | Comentario en el issue |
| `github` | `gh issue view <n> --json assignees,state` | `gh issue comment <n>` |
| `archivo` | La fila de la HU en `$NEXUS_ROOT/doc/sdd/_INDEX.md` (columna Responsable) | La misma fila |
| `propio` | La API o CLI de la herramienta, cuando exista | Idem |

Sin el conector que el tracker necesita, la operacion no se adivina: el orquestador lo dice y escala.

## Gate de propiedad (antes de F0)

1. El orquestador consulta `duenio(HU)` y `estado(HU)` en el tracker, y `mem_search "trabajo/<HU>"` si hay memoria.
2. Clasifica el resultado:
   - **propia**: el responsable es `tracker_user`.
   - **libre**: no tiene responsable y nadie la reclamo en memoria en los ultimos 3 dias.
   - **ajena**: la tiene otra persona, o la reclamo otra sesion hace menos de 3 dias, o esta cerrada o en revision.
3. Con **ajena**, para y escala con lo que encontro. Si la persona decide tomarla igual, el resultado pasa a **autorizada**, con su decision citada. Tambien en AUTO: es una prioridad de negocio, no la decide el orquestador ni el supervisor.
4. Lanza al analista con la linea `PROPIEDAD:` en el prompt, con el resultado y la evidencia: `PROPIEDAD: propia (jira SCRUM-541, asignada a Fernando Rosas, Tareas por hacer)`. El hook no deja lanzar el primer F0/F1 de una HU sin esa linea, ni con `ajena`.
5. Guarda el reclamo en memoria (`trabajo/<HU>`: sesion, rama, worktree, fase, fecha) y, con `tracker_write: true`, comenta en el ticket.

El registro en memoria es un candado con vencimiento, no una segunda autoridad: si contradice al tracker, manda el tracker. Un reclamo sin cambios en mas de 3 dias se trata como abandonado: se pregunta, no se pisa.
