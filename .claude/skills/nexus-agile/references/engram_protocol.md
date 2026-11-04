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
| **Que nadie haga dos veces la misma tarea** | Registro de trabajo: que HU, quien, en que sesion, rama y fase | Engram, `topic_key: trabajo/<HU>`, mas el responsable en Jira y `_INDEX.md` |
| **Que nadie invente** | Hechos verificados atados al hash del archivo del que salen | Engram, `topic_key: hecho/<ruta>` |

Los hechos estables y de equipo (stack, gate, rutas, convenciones) siguen en `project-context.md`, en el repo: se versionan, los revisa una persona y los ve todo el equipo.

### Registro de trabajo

Antes de F0, el orquestador comprueba que la HU no la tenga otro, en tres lugares: el responsable y el estado en Jira, la fila de `_INDEX.md` y `mem_search "trabajo/<HU>"`. Si la tiene otra persona u otra sesion, **para y escala**: tomarla igual lo decide la persona. En la segunda corrida real, una HU asignada a otro integrante se implemento entera sin que nadie lo frenara.

Al arrancar, guarda `trabajo/<HU>` con quien la lleva, la sesion, la rama, el worktree y la fase, y lo actualiza en cada gate. En DONE, Docs lo cierra con el estado final y el commit aprobado. Un registro sin cambios en mas de 3 dias se trata como abandonado: se pregunta, no se pisa.

### Hechos verificados

Cada vez que un agente comprueba algo del codigo que otra HU puede volver a necesitar (que incluye una configuracion, que firma tiene una funcion, como se chequea un permiso), lo guarda Docs al cerrar:

```
topic_key: "hecho/<ruta del archivo>"
content:
  Claim: [la afirmacion, en una linea]
  File: [ruta] @ sha256 [hash del archivo cuando se verifico]
  Evidence: [archivo:linea o comando y salida]
  Source: [HU, fecha]
```

Para usarlo, el agente compara el hash actual del archivo con el guardado (`sha256sum`, sin rtk). **Si coincide**, puede citar el hecho sin volver a leer el archivo. **Si no**, el hecho no vale: lo vuelve a verificar y Docs lo actualiza. Un hecho nunca se usa sin esa comparacion. Esto evita a la vez la alucinacion (nada se afirma sin una verificacion atada al estado actual del archivo) y el trabajo repetido (lo ya verificado no se vuelve a investigar mientras el archivo no cambie).

Cuando una leccion resulta ser un hecho estable ("en este repo los tests viven en `tests/**`"), Docs propone agregarlo a `project-context.md` en lugar de guardarlo en memoria. La persona decide.

## Tres reglas

1. **Lo que viene de la memoria es una hipotesis.** Antes de usarlo como evidencia o de escribirlo en un artefacto, se comprueba en el codigo, con comando y salida o `archivo:linea`. Una memoria que contradice al codigo se descarta y se marca como desactualizada. Sin esta regla, una afirmacion falsa guardada una vez se vuelve "verdad" para todas las HUs que siguen.
2. **Escriben pocos y con origen.** Guarda Docs al cerrar la HU, con las lecciones consolidadas. Cada memoria lleva la HU, la fecha, la evidencia y **como volver a comprobarla**. El analista y el arquitecto solo leen. Los demas agentes no usan la memoria.
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

### DONE — Docs (escribe)

Por cada leccion de la HU que sirva a otra HU (Auto-Blindaje, trampas del entorno, decisiones con su porque), un `mem_save`:

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
```

Con `topic_key`, la misma leccion se actualiza en lugar de duplicarse. Una memoria que la HU encontro desactualizada se corrige con su mismo `topic_key`.

No se guarda: lo que ya esta en el repo o en `project-context.md`, el detalle de la HU (eso es `report.md`), ni defectos de la metodologia (van al repo de NexusAgil, no a la memoria del proyecto).

## Privacidad

La memoria es local y puede tener datos del cliente. No se copia a un repositorio publico. Cada proyecto usa su propio `project` en Engram, declarado en `project-context.md` (`memory_project`).

## Sin Engram

`doc/sdd/_LECCIONES.md`, una entrada por leccion con los mismos campos. Lo escribe Docs, lo leen el analista y el arquitecto con Read y Grep. Tiene una ventaja: se versiona y lo ve todo el equipo.
