# Plan: el cerebro de NexusAgil (memoria con Engram)

> Objetivo: una memoria que guarde contexto entre HUs, evite que dos agentes o dos personas hagan la misma tarea, corte las alucinaciones y baje el consumo de tokens. Cada paso dice que resuelve y como se comprueba.

## Lo que tiene que lograr

| Objetivo | Como lo logra | Como se mide |
|----------|---------------|--------------|
| Guardar contexto | Lecciones, trampas y decisiones con su porque, escritas por Docs al cerrar cada HU | Errores conocidos que no se repiten en la HU siguiente |
| No duplicar tareas | Registro `trabajo/<HU>` mas Jira y `_INDEX.md`, comprobado antes de F0 | HUs tomadas por dos personas o sesiones: tiene que ser 0 |
| No alucinar | Hechos atados al sha256 del archivo; lo que viene de la memoria es una hipotesis hasta comprobarlo | Afirmaciones falsas que llegan a SPEC_VERIFY por memoria vieja: tiene que ser 0 |
| Gastar menos | Un hecho vigente evita releer el archivo; topes de busqueda | Tokens procesados por HU con `nexus_metrics.py`, contra las dos HUs sin memoria |

## Estado de partida (medido)

- El protocolo de Engram pedia buscar y guardar en cada fase, pero ningun agente tenia sus herramientas: **nunca se uso** en las HUs reales.
- Probado el 4-nov: un subagente del plugin puede usar Engram si sus herramientas estan en `tools:`; los nombres que no existen en la maquina se ignoran; `tools:` recorta (sin `mem_save`, no escribe).
- Referencia sin memoria: HU-A (2 puntos, manual) 62,2 M tokens procesados; HU-B (1 punto, AUTO) 45,8 M.

## Pasos

| # | Paso | Estado |
|---|------|--------|
| 1 | Diseno: tres trabajos (contexto, registro de trabajo, hechos con hash) y tres reglas (la memoria es hipotesis, escriben pocos con origen, se mide). `references/engram_protocol.md` | Hecho |
| 2 | Permisos por rol: analista y arquitecto leen (`mem_search`, `mem_get_observation`), Docs escribe (`mem_save`, `mem_update`). Las dos variantes de nombre. Topes: 5 busquedas y 3 lecturas completas por agente | Hecho |
| 3 | Registro de trabajo: el orquestador comprueba Jira, `_INDEX.md` y `trabajo/<HU>` antes de F0 y escala si la HU es de otro; lo actualiza en cada gate; Docs lo cierra. El supervisor lo verifica en su primer punto | Hecho: interfaz de tracker (Jira, Linear, GitHub, archivo, propio), gate de propiedad en el hook |
| 4 | Hechos con hash: formato `hecho/<ruta>`, regla de reuso (hash igual: se cita sin releer; distinto: se reverifica). Script `nexus_memory.py` que da el sha y arma la entrada, para que nadie la escriba a mano | Hecho, con el blob SHA de git y pares por archivo; las lecciones las aprueba la persona |
| 5 | Controles: el hook exige `## MEMORIA CONSULTADA` en el work-item, y `cierre.md` trae "Memoria guardada"; check de consistencia | Hecho: `MEMORIA CONSULTADA` exigida |
| 6 | Consumo: `nexus_metrics.py` cuenta las llamadas a la memoria y lo que costaron, para saber si ahorra o suma | Hecho |
| 7 | Evals con un Engram simulado (`mocks/`): un hecho con hash viejo (tiene que reverificarlo y descartarlo), una memoria falsa (no puede entrar al SDD), y una HU registrada por otra sesion (tiene que escalar) | Hecho con el respaldo en archivo: 6/6. Simular Engram en el eval no es viable hoy |
| 8 | Siembra inicial en el primer proyecto real: las trampas y hechos que ya conocemos de HU-A y HU-B (rtk, `vitest.config.ts`, `check_contract.py`) y el registro de las HUs en curso. **Escribe en tu memoria: necesita tu visto bueno** | Hecho en la practica: Limitless y Nexus Control guardaron trampas, hechos, lecciones aprobadas y reclamos desde su primera HU |
| 9 | Prueba real: la HU siguiente a HU-C, con la memoria activa, comparando contra HU-A y HU-B | Hecho como uso, no como experimento: 12 HUs de Nexus Control con memoria activa. Resultado en `docs/medicion-memoria.md` |

## Segunda etapa: el cerebro en todos los proyectos (2.3.0)

> Objetivo: que NexusAgil sea el arnes de todos los proyectos, con Engram como memoria de experiencia. Engram no es la fuente de verdad: la verdad esta en el repo (`project-context.md`, SDDs), la coordinacion en el tracker, y Engram guarda experiencia que se trata como hipotesis.

### Lo que se encontro (21-nov-2026)

| Hallazgo | Evidencia |
|----------|-----------|
| La misma trampa se redescubre en cada proyecto | rtk reescribiendo la salida aparece por separado en 5 proyectos de Engram: limitless-nexus #904, limitless #870 y #891, usuario #809, wasiai-a2a #690 |
| La busqueda falla en silencio y el agente escribe "Ninguna" | GH-12: dos busquedas largas vacias, "Ninguna" falso, lo atrapo el supervisor; `mem_search "nexus-control leccion"` las encontraba. GH-18 y GH-21, igual. Causa medida: `match_mode` por defecto es `all` (todas las palabras deben aparecer) |
| FAST y FAST+AR no consultan la memoria | GH-3, GH-9 y GH-10: "busqueda no ejecutada en esta corrida FAST" |
| Las memorias caen en el proyecto equivocado | Proyectos `usuario`, `fernando`, `system32` en Engram: el proyecto se deduce de la carpeta. `engram init <nombre>` lo fija (probado) |
| `scope: global` no se ve desde otro proyecto con una busqueda normal | Probado en una base aislada: hace falta `all_projects: true` + `scope: global` |
| `engram sync` permite compartir con el equipo por git | Probado: exporta solo el ambito `project`, sin prompts, incremental; `engram sync --import` lo carga. No exporta `global` ni `personal` |

### Pasos

| # | Paso | Como se comprueba |
|---|------|-------------------|
| 10 | **Identidad del proyecto**: `setup.sh` y F0 fijan el proyecto con `engram init <memory_project>` (`.engram/config.json`), para que la memoria no caiga en otro proyecto | Test de `setup.sh` en carpeta temporal; check de consistencia |
| 11 | **Busqueda confiable**: receta fija de consultas cortas con `match_mode: any`; FAST y FAST+AR tambien consultan; el hook lee el transcript del analista y frena si uso Engram sin la receta, si falta la linea `Busquedas:`, o si no busco y no dice "sin Engram" | Tests del hook; check de consistencia |
| 12 | **Ambito global**: las trampas del entorno y de las herramientas (no las del dominio) se guardan con `scope: global` y se leen con `all_projects: true, scope: global`. `lecciones.md` declara `scope: project | global`; lo aprueba la persona como cualquier leccion | Check de consistencia; busqueda real que devuelve las trampas globales |
| 13 | **Siembra global** (escribe en tu Engram, autorizado el 21-nov-2026): una trampa global consolidada de rtk (reune #690, #809, #870, #891, #904) y pasar a global #841 (artefactos por Bash) y #842 (Write/Edit decodifican escapes Unicode) | `mem_search` con `all_projects` + `scope: global` las devuelve |
| 14 | **Equipo**: campo `memory_share: none | git` en `project-context.md`. Con `git`, DONE corre `engram sync --project <memory_project>` y el chunk entra con la proxima HU, como los gates posteriores al cierre; F0 corre `engram sync --import` antes de buscar. Solo repos privados | Check de consistencia; prueba de ida y vuelta documentada |
| 15 | **Sin Engram y setup**: `setup.sh` deja de prometer "MEMORY.md" y busquedas en cada fase; respaldo unico `_LECCIONES.md`; version de Engram probada | Lectura de `setup.sh`; `bash -n` |
| 16 | **Medicion**: `docs/medicion-memoria.md` con lo que la memoria hizo en las 12 HUs de Nexus Control | El documento cita cada work-item |
| 17 | **Release 2.3.0**: CHANGELOG, `plugin.json`, `marketplace.json`, README (tres capas), CI en verde | `unittest`, `check_consistency.sh` |

**Estado (21-nov-2026):** pasos 10 a 17 hechos en la 2.3.0. Siembra global en Engram: #957 (rtk, consolidada), #841 y #842 (pasadas a `global`, siguen en `nexus-control`). Revision adversaria independiente: 4 MAYOR y 6 MENOR, corregidos; queda abierto que una version corregida despues de un bloqueo del hook no se guarda en `.versions/`. Falta correr el eval con modelo (`workflow_dispatch` con `eval`), sobre todo `memoria-hecho-desactualizado`.

### Fuera de esta etapa

- Un modo mas liviano que FAST para prototipos (el costo por HU sigue alto: 45 a 62 M tokens procesados en HUs de 1 y 2 puntos).
- Compartir el ambito global entre personas: `engram sync` no lo exporta; las trampas de la metodologia siguen yendo al repo de NexusAgil.
- Un experimento controlado de tokens con y sin memoria: las HUs reales no son comparables entre si.

## Tercera etapa: un cerebro que aprende solo, en cualquier maquina (2.4 a 2.6)

> Objetivo: cubrir lo que la 2.3.0 no hace. Que aprenda solo sin perder el control, que cubra todos los proyectos, que recuerde el codigo, que no dependa de una maquina, que lo lean los agentes que lo necesitan y que se mida solo. Aprobado por la persona el 21-nov-2026.

### Lo que faltaba (21-nov-2026)

| Hueco | Evidencia |
|-------|-----------|
| Proyectos sin memoria | 8 proyectos propios con NexusAgil sin `memory_project`; el mayor, con 205 carpetas de HU |
| Experiencia escrita que nunca entro a la memoria | El mayor de esos proyectos: 509 entradas de auto-blindaje y 18 reportes con lecciones |
| Las trampas globales no viajan | `engram sync` exporta solo el ambito `project` (probado) |
| Todo vive en una maquina | `~/.engram` sin respaldo |
| Aprende poco | 2 hechos con hash en 12 HUs de Nexus Control; las lecciones dependen de que Docs las proponga |
| Solo el analista y el arquitecto leen | Dev, AR y QA repiten trampas que ya estaban guardadas |
| La medicion es a mano | `docs/medicion-memoria.md` se armo leyendo 12 work-items |

### Lo que no se hace

Guardar lecciones de criterio sin aprobacion humana. Una memoria falsa guardada una vez se vuelve "verdad" para las HUs que siguen (MINJA, 2025: 98 % de insercion). Lo automatico se limita a lo que se puede comprobar con un comando; lo demas se aprueba, con menos friccion.

### Pasos

| # | Etapa | Paso | Como se comprueba | Estado |
|---|-------|------|-------------------|--------|
| 18 | A (2.4.0) | **Conectar los proyectos**: fila `memory_project` y `memory_share: none` en `project-context.md`, y `engram init` | `.engram/config.json` en cada repo; el aviso del paso 19 no sale | Hecho en los 8, local: entra con la proxima HU de cada repo |
| 19 | A | **Aviso al abrir**: el hook avisa en `SessionStart` si falta `memory_project` o `.engram/config.json` | Tests del hook; corrida contra los proyectos reales | Hecho |
| 20 | A | **Trampas globales en el plugin**: `references/trampas_globales.md`, leido por el analista y Dev | Check de consistencia | Hecho, con las 3 globales |
| 21 | A | **Respaldo**: `nexus_brain.py respaldar/restaurar` en un repo git propio; DONE lo corre | Tests con un engram falso; ida y vuelta real en una base aislada | Hecho: `~/nexus-brain` con remoto privado en GitHub |
| 22 | A | **Siembra retroactiva**: `nexus_seed.py` junta candidatas; se curan y la persona las aprueba | Tests; corrida sobre el proyecto mayor | Hecho: 578 candidatas curadas a 25, aprobadas por la persona y guardadas (11 del proyecto, 14 globales; 4 de ellas tambien en `trampas_globales.md`) |
| 23 | B (2.5) | **Candidatas automaticas**: el hook junta, de cada HU, bloqueos del hook, hallazgos del AR, auto-blindaje y violaciones, y arma `candidatas.md`; la persona aprueba en una sola pregunta por HU o por lote | Tests del hook | Pendiente |
| 24 | B | **Automatico lo verificable**: hechos con hash y trampas con `Verify:` se guardan sin preguntar; si el archivo cambia o el `Verify:` deja de fallar, se invalidan solos | Tests; eval `memoria-hecho-desactualizado` | Pendiente |
| 25 | B | **Hechos desde SPEC_VERIFY**: las afirmaciones VERDADERAS con `archivo:linea` pasan a hechos con hash al cerrar | Una HU QUALITY real deja hechos; la siguiente los cita VIGENTE | Pendiente |
| 26 | B | **Renovacion**: una memoria usada y vigente renueva su fecha de revision; la que nadie usa en meses se marca para revisar | Tests | Pendiente |
| 27 | C (2.6) | **Mas agentes leen**: Dev (trampas del entorno), AR y QA (lecciones de tests), con 1 o 2 busquedas | Check de consistencia; hook | Pendiente |
| 28 | C | **Medicion automatica**: un script lee `## MEMORIA CONSULTADA` de cada HU y regenera `docs/medicion-memoria.md` | Tests; corrida sobre Nexus Control da los numeros del 21-nov | Pendiente |
| 29 | C | **Comparar**: despues de 5 HUs con la 2.4, repetir la medicion | La tabla de `docs/medicion-memoria.md`, "Como volver a medir" | Pendiente |

Cada etapa es una version del plugin con su PR, tests y revision adversaria. El eval con modelo se corre solo si la persona lo pide.

## Riesgos y como se cubren

| Riesgo | Cobertura |
|--------|-----------|
| Una memoria falsa se vuelve "verdad" | Regla 1 (hipotesis) y hechos atados al hash; SPEC_VERIFY revisa lo que entra al SDD |
| Memoria vieja | El hash del archivo la invalida sola; un registro de trabajo sin cambios en 3 dias se pregunta |
| Mas tokens en lugar de menos | Topes de busqueda y medicion en el paso 6; si no ahorra, se recorta |
| Datos del cliente | La memoria es local y por proyecto (`memory_project`); nunca se copia a un repo publico |
| El equipo no la ve (Engram es local) | `$NEXUS_ROOT/doc/sdd/_LECCIONES.md` como respaldo versionado; compartir Engram entre personas queda fuera de este plan |

## Lo que no se puede prometer

- Que el consumo quede en un "estandar de mercado": no hay un numero publico confiable de tokens por HU con el que comparar. Lo que si se puede: medir cada HU con el mismo script y fijar un tope por tamano con nuestros propios datos.
- Que la memoria evite todo error repetido: evita los que alguien guardo. Lo que nadie anoto, se vuelve a descubrir.
