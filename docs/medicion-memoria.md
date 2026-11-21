# Medicion: que hizo la memoria en las 12 HUs de Nexus Control

> Foto del 21-nov-2026, sacada de `doc/sdd/*/work-item.md` (seccion `## MEMORIA CONSULTADA`), `cierre.md`, las bitacoras `prueba-nexus-control-*.md` y la base de Engram del proyecto (`engram export --project nexus-control`). Es uso real, no un experimento: las HUs no son comparables entre si en tamano ni en tipo, asi que no hay una cifra de tokens ahorrados.

## Lo que hay guardado

68 entradas en el proyecto `nexus-control`:

| Tipo | Cantidad | Quien la escribe |
|------|----------|------------------|
| Reclamos `trabajo/GH-N` | 12 | Orquestador, en cada HU |
| Lecciones aprobadas por la persona | 15 | Orquestador, despues del visto bueno |
| Decisiones de la persona | 18 | Orquestador |
| Resumenes de sesion | 13 | El plugin de Engram, solo |
| Trampas | 3 | Orquestador (siembra de GH-1) |
| Hechos atados al hash | 2 | Docs (GH-1) |
| Otras | 5 | |

## HU por HU

| HU | Pipeline | Consulto | Que paso |
|----|----------|----------|----------|
| GH-1 | QUALITY | No | Proyecto nuevo: no habia nada que leer. Dejo 2 hechos y 3 trampas |
| GH-3 | FAST | No | "modo FAST, sin busqueda en memoria" |
| GH-5 | QUALITY | Si | 5 memorias. `#839` (hecho de `reader.py`) VIGENTE por hash: se cito sin releer el archivo. 3 trampas usadas en CD-5 y CD-6 |
| GH-7 | QUALITY | Si | `#839` verificada a mano: el archivo cambio, el contenido seguia valido. 2 busquedas largas vacias |
| GH-9 | FAST | No | Tomo las lecciones de los artefactos de GH-7, no de la memoria |
| GH-10 | FAST | No | "busqueda no ejecutada en esta corrida FAST" |
| GH-11 | QUALITY | Si | 3 busquedas, nada util |
| GH-12 | FAST | Si, tarde | Primero escribio "Ninguna" despues de dos busquedas largas vacias. Lo atrapo el supervisor. Con `"nexus-control leccion"` aparecieron 4 lecciones (L1, L2, L3, L-4), que cambiaron el fixture del test (CD-3) y la verificacion del mutante M1 |
| GH-17 | QUALITY | Si | 2 busquedas largas vacias; 3 lecciones usadas en CD-2 y CD-4 |
| GH-18 | FAST+AR | Si | 1 busqueda larga vacia y "Ninguna". Habia lecciones de tests de GH-17 (`#922`) que aplicaban |
| GH-21 | QUALITY | Si | Reclamo `trabajo/GH-21` verificado. 2 busquedas largas vacias |
| GH-23 | FAST | No | El work-item no tiene la seccion: el bloqueo del hook quedo sin resolver al terminar el agente |

## Lo que muestra

1. **Las lecciones aprobadas se usan y cambian el trabajo.** En GH-12 y GH-17, lecciones de HUs anteriores cambiaron fixtures y controles antes de escribir codigo. Es el valor que el plan esperaba: un error ya pagado no se vuelve a pagar.
2. **La busqueda falla en silencio.** 9 busquedas vacias en 5 HUs, todas de varias palabras. Engram exige por defecto que aparezcan todas (`match_mode: all`). En GH-12 y GH-18 eso termino en un "Ninguna" falso. Arreglo en 2.3.0: receta fija de consultas cortas con `match_mode: any`, y el hook exige la linea `Busquedas:`.
3. **FAST no consulta.** 4 de las 5 HUs FAST no buscaron; justo las HUs chicas, donde una leccion pesa mas sobre el total. Arreglo en 2.3.0: las tres consultas fijas tambien en FAST y FAST+AR.
4. **Los hechos con hash funcionan, pero casi no se escriben.** Solo 2 en 12 HUs. El unico que se reuso ahorro una relectura en GH-5 y se reverifico bien en GH-7 cuando el archivo cambio. Queda abierto: Docs guarda pocos hechos.
5. **Los reclamos se llevan bien** (12 de 12) y en GH-21 sirvieron para verificar la propiedad.
6. **Fuera del proyecto, el problema es otro.** La trampa de rtk se redescubrio en 5 proyectos distintos. Una memoria por proyecto no lo evita: hace falta el ambito global (2.3.0).

## Costo de la memoria

Las llamadas a Engram que registran los cierres van de 2 a 5 `mem_search` y hasta 2 `mem_get_observation` por HU, contra 45 a 62 M tokens procesados por HU. Su costo es marginal. Que ahorren mas de lo que cuestan esta probado en casos sueltos (GH-5, GH-12), no medido en total.

## Como volver a medir

Despues de 5 HUs con la 2.3.0 en un proyecto con memoria, repetir esta tabla y comparar:
- HUs con la linea `Busquedas:` y al menos una memoria usada (hoy: 4 de 12).
- "Ninguna" con lecciones que aplicaban (hoy: 2).
- HUs FAST que consultaron (hoy: 1 de 5).
- Trampas globales usadas fuera de su proyecto de origen (hoy: 0; el ambito no existia).
