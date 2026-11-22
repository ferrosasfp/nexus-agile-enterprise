# Memoria del proyecto (Engram)

> La memoria guarda la **experiencia** del proyecto entre HUs: lecciones, trampas del entorno, decisiones y su porqué. No guarda la verdad sobre el código: eso está en el repo y se comprueba cada vez.
> Motor de referencia: [Engram](https://github.com/Gentleman-Programming/engram), un proyecto open source aparte (MIT). NexusAgil lo integra, no lo incluye. Sin Engram, el respaldo es `doc/sdd/_LECCIONES.md`.

## Por que

En las dos primeras HUs reales, lo que se repitio no lo podia evitar ningun gate:

- El arquitecto escribio dos veces la misma afirmacion falsa sobre `vitest.config.ts`, porque el entorno (rtk) le escondio la linea las dos veces.
- Los mismos falsos positivos de un script y del hook, redescubiertos por cada orquestador.

Hasta la version 2.0.0-rc.3, este protocolo pedia buscar y guardar en cada fase, pero ningun agente tenia las herramientas de Engram en su lista: nadie podia usarlo.

## Tres trabajos del cerebro

| Trabajo | Pieza | Donde |
|---------|-------|-------|
| **Guardar contexto** | Lecciones, trampas y decisiones con su porque | Engram, `topic_key: leccion/…`, `trampa/…`, `decision/…` |
| **Que nadie haga dos veces la misma tarea** | Gate de propiedad contra el tracker, mas un reclamo con vencimiento | El tracker manda (`references/tracker.md`); el reclamo va en Engram, `topic_key: trabajo/<HU>` |
| **Que nadie invente** | Hechos verificados atados al hash del archivo del que salen | Engram, `topic_key: hecho/<ruta>` |

Los hechos estables y de equipo (stack, gate, rutas, convenciones) siguen en `project-context.md`, en el repo: se versionan, los revisa una persona y los ve todo el equipo.

## Tres capas: quien manda en que

| Capa | Que guarda | Autoridad |
|------|------------|-----------|
| Repo (`project-context.md`, `product-context.md`, SDDs, `_INDEX.md`) | Stack, convenciones, decisiones de equipo, estado de cada HU | **Verdad**: versionada y revisada por una persona |
| Tracker (Jira, Linear, GitHub, archivo) | Quien hace que | **Coordinacion** (`references/tracker.md`) |
| Engram | Lecciones, trampas, hechos atados al hash, reclamos | **Experiencia**: hipotesis hasta comprobarla en el codigo |

Si dos capas se contradicen, manda la de arriba. Engram nunca corrige al repo: una memoria que contradice al codigo se descarta.

## Proyecto y ambito

**Proyecto.** Cada repo declara `memory_project` en `project-context.md` y lo fija con `engram init <memory_project>` en la raiz del repo (crea `.engram/config.json`, que se commitea; lo hace `setup.sh`, y F0 si falta). Si `.engram/config.json` y `memory_project` no coinciden, el orquestador escala. Sin eso, Engram deduce el proyecto de la carpeta y las memorias caen en otro lado: en la maquina de referencia hay memorias de proyectos reales guardadas como `usuario`, `fernando` y `system32`. Toda llamada lleva `project: <memory_project>` explicito.

**Ambito.** Cada memoria tiene uno:

| Ambito | Para que | Ejemplos |
|--------|----------|----------|
| `project` (por defecto) | Lo que vale solo en este repo | `hecho/…`, `trabajo/<HU>`, lecciones del dominio, decisiones del producto |
| `global` | Trampas del entorno y de las herramientas, que valen en cualquier proyecto | rtk reescribe la salida de `cat`/`grep`/`diff`; Write/Edit decodifican escapes Unicode; el hook bloquea artefactos escritos por Bash |

La trampa de rtk se redescubrio por separado en cinco proyectos antes de que existiera el ambito global. Una memoria global conserva su proyecto de origen (es su procedencia) y se lee desde cualquier otro con `all_projects: true, scope: "global"`: una busqueda normal por proyecto **no** la trae. Una leccion es global solo si no nombra nada propio del repo (rutas, tablas, modulos, reglas del negocio); si duda, es `project`.

**Trampas globales en el plugin.** `engram sync` no exporta el ambito `global`, asi que una trampa global guardada en una maquina no llega a otra. Las aprobadas pasan tambien a `references/trampas_globales.md` por PR, sin nombres de clientes ni rutas personales, y viajan con el plugin a cualquier maquina, con o sin Engram. El analista las lee en F0 junto con la busqueda global, y Dev antes de F3. Si una trampa esta en los dos lados, la busqueda trae la evidencia nueva y el archivo es la referencia revisada.

## Receta de busqueda

En Engram, `mem_search` exige por defecto que aparezcan todas las palabras (`match_mode: all`). Una consulta larga ("escalados supervisor GH-11 lecciones L1 L2") no encuentra nada y el agente escribe "Ninguna" aunque haya lecciones: paso en GH-12, GH-18 y GH-21 de Nexus Control. Por eso la busqueda es fija, con consultas de una o dos palabras y `match_mode: "any"`:

| # | Consulta | Para que |
|---|----------|----------|
| 1 | `mem_search(query: "leccion", project: <memory_project>, match_mode: "any")` | Lecciones aprobadas del proyecto |
| 2 | `mem_search(query: "trampa", project: <memory_project>, match_mode: "any")` | Trampas del proyecto |
| 3 | `mem_search(query: "trampa leccion", all_projects: true, scope: "global", match_mode: "any")` | Trampas y lecciones globales de todos los proyectos (las lecciones de criterio que no nombran nada del repo tambien son globales) |
| 4 | `mem_search(query: "decision", project: <memory_project>, match_mode: "any")` | Decisiones de la persona: lo que ya se pregunto no se vuelve a preguntar |
| 5 | `mem_search(query: "<archivo o modulo>", project: <memory_project>, match_mode: "any")` | `hecho/` y lecciones de lo que se va a tocar (`reader.py`, `conftest`) |

Las cuatro primeras son obligatorias en todos los pipelines, FAST incluido: cuestan poco y son las que traen las lecciones y las decisiones. El hook lee el transcript del analista: si uso Engram y faltan "leccion", "trampa" (cortas o con `match_mode: any`) o la global, frena. El tope sigue en 5 busquedas y 3 lecturas completas por agente. Por eso los titulos llevan la palabra del tipo (`[proyecto] trampa: …`, `[proyecto] leccion: …`): la busqueda va por el titulo y el contenido, no por el `topic_key`.

`## MEMORIA CONSULTADA` lleva siempre una linea `Busquedas:` con cada consulta y cuantos resultados dio (`Busquedas: "leccion" 4, "trampa" 0, global "trampa" 2, "reader.py" 1`). Un "Ninguna" sin esa linea no vale: el hook lo frena. Sin Engram, la seccion dice "sin Engram" y se consulta `_LECCIONES.md`.

## Equipo

Engram es local: cada persona tiene su base. Para compartir la memoria del proyecto, `project-context.md` declara `memory_share`:

| Valor | Que pasa |
|-------|----------|
| `none` (por defecto) | La memoria queda en la maquina de cada persona. El equipo ve `_LECCIONES.md` y `cierre.md` |
| `git` | Al cerrar la HU, despues de guardar hechos, lecciones y reclamo, el orquestador corre `engram sync --project <memory_project>`: escribe un chunk comprimido en `.engram/chunks/` que entra en el primer commit de la proxima HU, en su rama y su PR (la misma regla que los gates posteriores al cierre). En F1 (y F0), antes de buscar, el analista corre `engram sync --import` |

Lo que viaja: solo el ambito `project`, sin los prompts (probado con Engram 3.7.2); ni `global` ni `personal`. Incluye los resumenes de sesion del proyecto, que pueden tener detalle del cliente: `git` solo en repos privados, y quien aprueba el PR revisa que el chunk no lleve nada que no deba. Lo que entra a git queda en el historial aunque despues se borre. El reclamo `trabajo/<HU>` viaja recien con el commit: para coordinar en vivo manda el tracker.

## Respaldo: no depender de una maquina

Engram vive en `~/.engram` de una sola maquina. `memory_share: git` comparte el ambito `project` de un repo, pero no las globales ni los repos de terceros, donde nada de la memoria puede ir al repo del cliente. Para eso esta el respaldo personal:

```
python3 $SKILL_DIR/scripts/nexus_brain.py respaldar            # ~/nexus-brain o $NEXUS_BRAIN_DIR
python3 $SKILL_DIR/scripts/nexus_brain.py respaldar --push     # exige empujarlo (falla si no puede)
python3 $SKILL_DIR/scripts/nexus_brain.py restaurar            # en la maquina nueva
```

Exporta toda la memoria (`engram export --all`: todos los proyectos y ambitos, global incluido) a `memoria.json` en un repo git propio, normalizada para que cada commit muestre solo lo que cambio. El import no duplica: restaurar dos veces no hace dano. El remoto lo agrega la persona y tiene que ser **privado** (la memoria trae detalle de los clientes); el script no crea ninguno, y empuja solo si `gh` confirma que el remoto de push es un repo de GitHub **privado** (otro host, un alias que gh no resuelve o gh sin sesion: queda local y avisa; con `--push`, falla). Salvaguardas: solo escribe en un repo de respaldo (lo marca con `.nexus-brain`; un repo de otra cosa se rechaza), no pisa el respaldo si a la base local le faltan memorias que el respaldo tiene (una maquina nueva sin restaurar; `--forzar` para un borrado a proposito), y lo borrado no se respalda. DONE lo corre al final si el repo de respaldo existe.

## Siembra retroactiva

Un proyecto que ya tenia HUs antes de conectar la memoria tiene su experiencia escrita en `doc/sdd/` (auto-blindaje, lecciones de los reportes), pero no en Engram. Para traerla:

```
python3 $SKILL_DIR/scripts/nexus_seed.py --sdd $NEXUS_ROOT/doc/sdd --out candidatas.md --json candidatas.json
```

Junta cada entrada de `auto-blindaje.md` (con su "Aplicar en") y cada punto de las secciones "Lecciones", con `HU/archivo:linea`, y agrupa las casi identicas. Solo lee. Las candidatas se curan (se agrupan por significado, se descartan las de una sola vez, las que ya estan en `project-context.md` y las que ya son globales) y la persona aprueba la lista, con el `scope` de cada una, antes de guardarlas: es la regla 2, igual que en DONE. En un proyecto de 122 HUs dio 578 candidatas, que la curacion dejo en 25.

### Registro de trabajo

Es coordinacion, no memoria: el gate de propiedad de `references/tracker.md` consulta al tracker antes de F0, y el tracker es la autoridad. El reclamo `trabajo/<HU>` en Engram es un candado con vencimiento para lo que el tracker no ve (otra sesion de Claude en la misma maquina, una HU sin ticket). Lo guarda el orquestador al empezar, lo actualiza en cada gate, lo cierra en DONE con el estado final y el commit aprobado, y lo actualiza una vez mas despues del merge (PR, commit del merge, issue cerrado): si no, queda diciendo "PR en borrador" y la proxima sesion cree que la HU sigue abierta. Sin cambios en mas de 3 dias, se trata como abandonado: se pregunta, no se pisa. Si contradice al tracker, manda el tracker.

### Hechos verificados

Cada vez que un agente comprueba algo del codigo que otra HU puede volver a necesitar (que incluye una configuracion, que firma tiene una funcion, como se chequea un permiso), Docs lo guarda al cerrar. La entrada la arma el script, para que nadie copie un hash a mano:

```
python3 $SKILL_DIR/scripts/nexus_memory.py hecho --repo $CODE_ROOT --file vitest.config.ts \
  --claim "vitest incluye tests/**" --evidence "vitest.config.ts:30" --source "HU-12, 2026-11-03"
```

Devuelve el `topic_key` y el `content` con el **blob SHA de git** de cada archivo (`git hash-object`: el mismo hash que guarda git, sin depender de rtk). Un hecho que depende de varios archivos lleva un par por archivo.

Para usarlo, el agente corre la linea `Verify:` que trae la entrada (`nexus_memory.py vigente ...`). **VIGENTE**: puede citar el hecho sin volver a leer el archivo. **CAMBIO**: el hecho no vale; lo vuelve a verificar y Docs lo actualiza. Un hecho nunca se usa sin esa comprobacion. Ningun producto revisado ata hechos al hash del archivo; lo mas parecido es GitHub Copilot, que verifica las citas de cada memoria contra el codigo antes de usarla (A/B del vendor: 90 % de PRs mergeados con memoria, 83 % sin). Esto evita a la vez la alucinacion (nada se afirma sin una verificacion atada al estado actual del archivo) y el trabajo repetido (lo ya verificado no se vuelve a investigar mientras el archivo no cambie).

**Hechos desde SPEC_VERIFY.** La verificacion del SDD ya comprueba, con `archivo:linea`, muchas afirmaciones sobre el codigo que existe. La adversaria marca las que otra HU puede necesitar en la seccion `## Hechos para la memoria` de `sdd-verification.md` (hasta 10), y Docs las guarda al cerrar con `nexus_memory.py desde-verificacion`. Las lineas citadas son las del commit sobre el que corrio SPEC_VERIFY (la linea `BASE_SHA:` del informe; si falta, el merge-base de `BASE_REF` con `HEAD`), porque corre antes de F3. Si hay varios informes, el ultimo manda y sus hechos entran primero al tope de 10. Cada hecho lleva en su `topic_key` un hash corto de la frase, para que dos hechos que empiezan igual no se pisen. Un diff que no se puede leer (color, archivo binario) descarta el hecho en lugar de darlo por intacto. Si la HU cambio el archivo, el script guarda el hecho solo si ningun cambio toca las lineas citadas, y pasa la cita a las lineas de hoy; si las toca, lo descarta. En una HU real, los dos hechos de prueba citaban archivos que la propia HU modifico: con la regla "el archivo no cambio" se habrian perdido los dos. Se guardan sin preguntar porque son verificables: la linea `Verify:` los invalida sola si el archivo cambia. La HU siguiente los cita como VIGENTE en `## MEMORIA CONSULTADA`.

Cuando una leccion resulta ser un hecho estable ("en este repo los tests viven en `tests/**`"), Docs propone agregarlo a `project-context.md` en lugar de guardarlo en memoria. La persona decide.

## Tres reglas

1. **Lo que viene de la memoria es una hipotesis.** Antes de usarlo como evidencia o de escribirlo en un artefacto, se comprueba en el codigo, con comando y salida o `archivo:linea`. Una memoria que contradice al codigo se descarta y se marca como desactualizada. Sin esta regla, una afirmacion falsa guardada una vez se vuelve "verdad" para todas las HUs que siguen.
2. **Escriben pocos y con origen.** Docs guarda al cerrar la HU los hechos y el cierre del reclamo. **Las lecciones las aprueba la persona**: Docs las propone en `lecciones.md` y se guardan despues de su visto bueno, porque no se pueden comprobar con un hash y son lo mas expuesto a quedar falso (en ataques medidos, una memoria envenenada se inserta el 98 % de las veces: MINJA, 2025). Cada memoria lleva la HU, la fecha, la evidencia y como volver a comprobarla. El analista y el arquitecto solo leen; los demas agentes no usan la memoria.
3. **Se mide.** El work-item registra que memoria se consulto y que paso con cada una, y `cierre.md` dice si alguna evito un error conocido.

## Por fase

### Antes de F0 — Orquestador

Registro de trabajo: comprueba que nadie mas tenga la HU y guarda `trabajo/<HU>`. Ver arriba.

### F0 + F1 — Analista (lee)

Corre la receta de busqueda (las cuatro consultas fijas y una por los archivos o modulos que va a tocar), en todos los pipelines, FAST y FAST+AR incluidos. Con `memory_share: git`, antes corre `engram sync --import`. En `work-item.md`, seccion `## MEMORIA CONSULTADA`, la linea `Busquedas:` y despues:

| Memoria | Que dice | Estado |
|---------|----------|--------|
| `#id` o `_LECCIONES.md:linea` | resumen | VERIFICADA (`archivo:linea`) / VIGENTE (hecho con el mismo hash) / DESCARTADA (contradice `archivo:linea` o cambio el hash) / SIN VERIFICAR (no aplica a esta HU) |

Sin resultados: la seccion dice "Ninguna", con la linea `Busquedas:` que lo prueba. Sin Engram: dice "sin Engram".

### F2 — Arquitecto (lee)

Busca por los patrones, tablas y archivos del diseno, con consultas cortas y `match_mode: "any"`, mas la consulta global de trampas. Lo que use en el SDD sale verificado contra el codigo, como cualquier otra afirmacion: `SPEC_VERIFY` lo trata igual.

### DONE — Docs (hechos y reclamo) y la persona (lecciones)

Docs guarda los hechos con el script y cierra `trabajo/<HU>`. Para las lecciones parte de las candidatas que junta `scripts/nexus_candidates.py` (bloqueos del hook de `.blocks.jsonl`, VIOLATION, BLQ y MAYOR de las revisiones, auto-blindaje) y las cura: la persona las aprueba en una sola ventana. Por cada leccion que sirva a otra HU (Auto-Blindaje, trampas del entorno, decisiones con su porque) escribe una entrada en `HU_DIR/lecciones.md`, con este formato. Cuando la persona la aprueba, el orquestador la guarda con `mem_save`; con fecha de revision a 60 dias, que se renueva cada vez que una HU la usa y la encuentra vigente:

```
title: "[proyecto] [tipo]: [resumen corto]"     # [tipo] en palabra: trampa, leccion, decision, hecho
type: bug | decision | pattern | discovery
topic_key: "trampa/[slug]" | "bug/[slug]" | "decision/[tema]" | "pattern/[nombre]"
scope: project | global                          # global solo para trampas del entorno o de las herramientas
content:
  What: [que paso o que se decidio]
  Why: [causa]
  Where: [archivo:linea, modulo]
  Learned: [la leccion, accionable]
  Evidence: [comando y salida, archivo:linea o sha]
  Verify: [como comprobar hoy si sigue siendo cierto]
  Source: [HU, fecha]
  Review: [fecha + 60 dias]
```

**Renovacion.** La fecha que cuenta es `review_after`, que Engram pone al guardar (6 meses para un `discovery`) y que `mem_review(action: "mark_reviewed")` vuelve a correr. Al cerrar, Docs renueva cada memoria que la HU uso y encontro cierta (VERIFICADA o VIGENTE en `## MEMORIA CONSULTADA`, que lee `nexus_memory.py usadas`), y lista las vencidas con `mem_review(action: "list")`: un hecho vencido se renueva solo si su `Verify:` da VIGENTE; lo demas se le pregunta a la persona en la misma ventana de las lecciones. Asi lo que se usa sigue vivo y lo que nadie usa sale a la luz en lugar de quedar como verdad vieja. Las memorias guardadas antes de Engram 3.7 no tienen `review_after`: nunca vencen hasta que una HU las renueva. La linea `Review:` del contenido es informativa. `mark_reviewed` solo encuentra memorias del proyecto que Engram resuelve para la sesion (probado con 3.7.2: desde otro proyecto da "observation not found in resolved project"), asi que se corre en la sesion del proyecto, con su `.engram/config.json`.

Una memoria por leccion: cada una con su `topic_key` y su `scope`, nunca varias juntas (tres lecciones en una sola memoria quedaron con un solo `scope`, y la global se perdio como de proyecto). Con `topic_key`, la misma leccion se actualiza en lugar de duplicarse. Una memoria que la HU encontro desactualizada se corrige con su mismo `topic_key`.

**Alcance global.** Docs propone `scope: global` solo si la leccion no nombra nada propio del repo; la persona lo aprueba junto con la leccion. Antes de proponerla, Docs lee `references/trampas_globales.md` y corre la consulta global: si ya existe, la propone como evidencia para esa trampa (T-N o #id), no como una nueva. Para una T-N del plugin, la evidencia entra por PR al repo de NexusAgil. Antes de guardar una global, el orquestador busca la misma trampa con la consulta global: si ya existe, la actualiza con `mem_update` (suma la evidencia nueva y la HU) en lugar de crear otra.

**Al final de DONE**, con `memory_share: git`: `engram sync --project <memory_project>`. El chunk de `.engram/chunks/` sigue la regla de las lineas de `.gates.jsonl` posteriores al cierre: entra en el primer commit de la proxima HU, en su rama y su PR, nunca en un push directo a `main`.

**Decisiones de la persona** (`decision/<tema>`): las guarda el orquestador cuando la persona decide en un gate o un escalado, con su respuesta citada y la HU. Son la fuente para no volver a preguntar lo mismo.

No se guarda: lo que ya esta en el repo o en `project-context.md`, el detalle de la HU (eso es `cierre.md`), ni defectos de la metodologia (van al repo de NexusAgil, no a la memoria del proyecto).

## Privacidad

La memoria es local y puede tener datos del cliente. No se copia a un repositorio publico: `memory_share: git` solo en repos privados. Cada proyecto usa su propio `project` en Engram, declarado en `project-context.md` (`memory_project`) y fijado con `engram init`. Una memoria global se lee desde todos los proyectos de la maquina: no lleva datos del cliente ni nada propio de un repo.

## Sin Engram

`$NEXUS_ROOT/doc/sdd/_LECCIONES.md`, una seccion por entrada (`## hecho/...`, `## trampa/...`, `## leccion/...`) con los mismos campos. El reclamo de trabajo, sin Engram, queda en la columna Responsable de `_INDEX.md`. Lo escribe Docs, lo leen el analista y el arquitecto con Read y Grep. Tiene una ventaja: se versiona y lo ve todo el equipo. Sin Engram no hay ambito global: cada proyecto tiene solo su `_LECCIONES.md`.

Probado con Engram 3.7.2 (`scope`, `all_projects`, `match_mode`, `engram init`, `engram sync`). Con una version sin alguna de esas opciones, se usa lo que haya y se anota en `## MEMORIA CONSULTADA`.
