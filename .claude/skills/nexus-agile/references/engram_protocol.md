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

### Registro de trabajo

Es coordinacion, no memoria: el gate de propiedad de `references/tracker.md` consulta al tracker antes de F0, y el tracker es la autoridad. El reclamo `trabajo/<HU>` en Engram es un candado con vencimiento para lo que el tracker no ve (otra sesion de Claude en la misma maquina, una HU sin ticket). Lo guarda el orquestador al empezar, lo actualiza en cada gate y lo cierra en DONE con el estado final y el commit aprobado. Sin cambios en mas de 3 dias, se trata como abandonado: se pregunta, no se pisa. Si contradice al tracker, manda el tracker.

### Hechos verificados

Cada vez que un agente comprueba algo del codigo que otra HU puede volver a necesitar (que incluye una configuracion, que firma tiene una funcion, como se chequea un permiso), Docs lo guarda al cerrar. La entrada la arma el script, para que nadie copie un hash a mano:

```
python3 $SKILL_DIR/scripts/nexus_memory.py hecho --repo $CODE_ROOT --file vitest.config.ts \
  --claim "vitest incluye tests/**" --evidence "vitest.config.ts:30" --source "HU-546, 2026-11-03"
```

Devuelve el `topic_key` y el `content` con el **blob SHA de git** de cada archivo (`git hash-object`: el mismo hash que guarda git, sin depender de rtk). Un hecho que depende de varios archivos lleva un par por archivo.

Para usarlo, el agente corre la linea `Verify:` que trae la entrada (`nexus_memory.py vigente ...`). **VIGENTE**: puede citar el hecho sin volver a leer el archivo. **CAMBIO**: el hecho no vale; lo vuelve a verificar y Docs lo actualiza. Un hecho nunca se usa sin esa comprobacion. Ningun producto revisado ata hechos al hash del archivo; lo mas parecido es GitHub Copilot, que verifica las citas de cada memoria contra el codigo antes de usarla (A/B del vendor: 90 % de PRs mergeados con memoria, 83 % sin). Esto evita a la vez la alucinacion (nada se afirma sin una verificacion atada al estado actual del archivo) y el trabajo repetido (lo ya verificado no se vuelve a investigar mientras el archivo no cambie).

Cuando una leccion resulta ser un hecho estable ("en este repo los tests viven en `tests/**`"), Docs propone agregarlo a `project-context.md` en lugar de guardarlo en memoria. La persona decide.

## Tres reglas

1. **Lo que viene de la memoria es una hipotesis.** Antes de usarlo como evidencia o de escribirlo en un artefacto, se comprueba en el codigo, con comando y salida o `archivo:linea`. Una memoria que contradice al codigo se descarta y se marca como desactualizada. Sin esta regla, una afirmacion falsa guardada una vez se vuelve "verdad" para todas las HUs que siguen.
2. **Escriben pocos y con origen.** Docs guarda al cerrar la HU los hechos y el cierre del reclamo. **Las lecciones las aprueba la persona**: Docs las propone en `lecciones.md` y se guardan despues de su visto bueno, porque no se pueden comprobar con un hash y son lo mas expuesto a quedar falso (en ataques medidos, una memoria envenenada se inserta el 98 % de las veces: MINJA, 2025). Cada memoria lleva la HU, la fecha, la evidencia y como volver a comprobarla. El analista y el arquitecto solo leen; los demas agentes no usan la memoria.
3. **Se mide.** El work-item registra que memoria se consulto y que paso con cada una, y `report.md` dice si alguna evito un error conocido.

## Por fase

### Antes de F0 — Orquestador

Registro de trabajo: comprueba que nadie mas tenga la HU y guarda `trabajo/<HU>`. Ver arriba.

### F0 + F1 — Analista (lee)

Busca por el dominio de la HU, por los archivos y modulos que va a tocar, por `trampa/` (problemas del entorno) y por `hecho/` de esos archivos. En `work-item.md`, seccion `## MEMORIA CONSULTADA`:

| Memoria | Que dice | Estado |
|---------|----------|--------|
| `#id` o `_LECCIONES.md:linea` | resumen | VERIFICADA (`archivo:linea`) / VIGENTE (hecho con el mismo hash) / DESCARTADA (contradice `archivo:linea` o cambio el hash) / SIN VERIFICAR (no aplica a esta HU) |

Sin memoria disponible o sin resultados: la seccion dice "Ninguna" y por que.

### F2 — Arquitecto (lee)

Busca por los patrones, tablas y archivos del diseno. Lo que use en el SDD sale verificado contra el codigo, como cualquier otra afirmacion: `SPEC_VERIFY` lo trata igual.

### DONE — Docs (hechos y reclamo) y la persona (lecciones)

Docs guarda los hechos con el script y cierra `trabajo/<HU>`. Por cada leccion que sirva a otra HU (Auto-Blindaje, trampas del entorno, decisiones con su porque) escribe una entrada en `HU_DIR/lecciones.md`, con este formato. Cuando la persona la aprueba, el orquestador la guarda con `mem_save`; con fecha de revision a 60 dias, que se renueva cada vez que una HU la usa y la encuentra vigente:

```
title: "[proyecto] [tipo]: [resumen corto]"
type: bug | decision | pattern | discovery
topic_key: "trampa/[slug]" | "bug/[slug]" | "decision/[tema]" | "pattern/[nombre]"
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

Con `topic_key`, la misma leccion se actualiza en lugar de duplicarse. Una memoria que la HU encontro desactualizada se corrige con su mismo `topic_key`.

No se guarda: lo que ya esta en el repo o en `project-context.md`, el detalle de la HU (eso es `report.md`), ni defectos de la metodologia (van al repo de NexusAgil, no a la memoria del proyecto).

## Privacidad

La memoria es local y puede tener datos del cliente. No se copia a un repositorio publico. Cada proyecto usa su propio `project` en Engram, declarado en `project-context.md` (`memory_project`).

## Sin Engram

`doc/sdd/_LECCIONES.md`, una entrada por leccion con los mismos campos. Lo escribe Docs, lo leen el analista y el arquitecto con Read y Grep. Tiene una ventaja: se versiona y lo ve todo el equipo.
