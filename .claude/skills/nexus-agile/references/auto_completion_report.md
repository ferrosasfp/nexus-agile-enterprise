# AUTO — Completion Report

Al terminar TODAS las HUs del batch (o al escalar en la regla #10), presentar un reporte
estructurado con 3 secciones obligatorias:

**Sección 1 — Tabla de resultados**

Tabla con una fila por HU (o bloque de trabajo si hubo tareas no-HU como memory/Jira reorg):

```
Resumen de la sesión YYYY-MM-DD

┌────────┬──────────┬───────────────┬───────────────┬──────────────────────────────────────────┐
│ Bloque │  Ticket  │     Modo      │    Estado     │          Deliverable clave                │
├────────┼──────────┼───────────────┼───────────────┼──────────────────────────────────────────┤
│ 1      │ WKH-XX   │ FAST          │ ✅ Finalizada │ [descripción 1 línea del output]          │
├────────┼──────────┼───────────────┼───────────────┼──────────────────────────────────────────┤
│ 2      │ WKH-YY   │ FAST+AR       │ ✅ Finalizada │ [descripción 1 línea del output]          │
├────────┼──────────┼───────────────┼───────────────┼──────────────────────────────────────────┤
│ 3      │ WKH-ZZ   │ QUALITY       │ ✅ Finalizada │ [descripción 1 línea del output]          │
├────────┼──────────┼───────────────┼───────────────┼──────────────────────────────────────────┤
│ 4      │ WKH-AA   │ QUALITY W1-W3 │ ⚠️ Parcial    │ [descripción + qué falta]                 │
└────────┴──────────┴───────────────┴───────────────┴──────────────────────────────────────────┘
```

**Columnas:**
- **Bloque**: número secuencial de ejecución
- **Ticket**: HU-ID o nombre de tarea
- **Modo**: FAST / FAST+AR / QUALITY / QUALITY W1-WN (si parcial)
- **Estado**: ✅ Finalizada / ⚠️ Parcial / ❌ Escalada / ❌ Abortada
- **Deliverable clave**: 1 línea concisa del output principal (archivos creados, features deployed, etc.)

**Sección 2 — Pipeline summary**

Resumen agrupado por tipo de pipeline con árbol visual:

```
Pipeline NexusAgil ejecutado

N HUs procesadas:
├── N FAST (WKH-XX, WKH-YY)
├── N FAST+AR (WKH-ZZ) — con nexus-adversary AR+CR
└── N QUALITY (WKH-AA, WKH-BB) — full pipeline F0→...→DONE

AR encontró N BLOQUEANTEs → fix-pack → N resueltos
Gates self-approved: N | Gates escalated: N
Total wallclock: NN min
```

**Sección 3 — Production State (si hubo merge)**

Tabla por capa/feature mostrando qué está live en producción después del batch:

```
Lo que está en producción ahora

┌───────────────┬──────────────────────────────────────────────────┬─────────┐
│     Capa      │                    Feature                       │ Status  │
├───────────────┼──────────────────────────────────────────────────┼─────────┤
│ L2 Adapters   │ PaymentAdapter, GaslessAdapter, etc.             │ ✅ Live │
├───────────────┼──────────────────────────────────────────────────┼─────────┤
│ L3 Identity   │ POST /auth/agent-signup → wasi_a2a_ keys         │ ✅ Live │
├───────────────┼──────────────────────────────────────────────────┼─────────┤
│ Hardening     │ Rate limit, circuit breaker, error boundary      │ ✅ Live │
├───────────────┼──────────────────────────────────────────────────┼─────────┤
│ Smoke test    │ scripts/smoke-test.sh — 8/8 endpoints            │ ✅ Live │
└───────────────┴──────────────────────────────────────────────────┴─────────┘
```

**Columnas:**
- **Capa**: nivel arquitectónico o subsistema (L1/L2/L3/L4, Middleware, Hardening, Docs, etc.)
- **Feature**: descripción concisa de lo que se deployó
- **Status**: ✅ Live / 🔄 Deploying / ⚠️ Pending review

Incluir también el estado técnico:

```
- PR #N merged a main: [timestamp]
- Tests: N/N passing, tsc clean
- Deploy: [status — auto-triggered / manual / pending]
- New deps: [si aplica]
```

Si no hubo merge (branches pendientes de review humano):

```
Branches pendientes de merge

- feat/NNN-titulo (WKH-XX) — ready for PR
- feat/NNN-titulo (WKH-YY) — ready for PR
```

**Sección 4 — What Remains (siempre)**

Tabla de tickets pendientes del proyecto/sprint que NO se procesaron en este batch:

```
Lo que queda

┌────────┬──────────────────────────────────────┬───────────────────┐
│ Ticket │                 Qué                  │     Esfuerzo      │
├────────┼──────────────────────────────────────┼───────────────────┤
│ WKH-26 │ Mid-checkpoint submission            │ Operativo — horas │
├────────┼──────────────────────────────────────┼───────────────────┤
│ WKH-17 │ Video + README final                 │ 1 día             │
├────────┼──────────────────────────────────────┼───────────────────┤
│ WKH-31 │ Pitch deck final                     │ Owner: [nombre]   │
└────────┴──────────────────────────────────────┴───────────────────┘
```

**Columnas:**
- **Ticket**: HU-ID o nombre
- **Qué**: descripción de 1 línea
- **Esfuerzo**: estimación libre (horas, días, "owner-name-owned", etc.)

Si no quedan tickets pendientes, indicar: "El backlog está vacío. Sprint completo."

**Sección 5 — Cross-session summary (si aplica)**

Si el batch es parte de un sprint de múltiples sesiones, incluir totales acumulados:

```
Resumen acumulado (sesiones YYYY-MM-DD a YYYY-MM-DD)

- N HUs shipped en producción
- Tests: N → N (+N new)
- BLOQUEANTEs encontrados por AR: N → todos resueltos
- PRs merged: #N, #N, #N
- Modos usados: N FAST, N FAST+AR, N QUALITY
```

Esta sección solo aparece cuando hay contexto de sesiones anteriores (vía Engram o memoria persistente).
Si es la primera sesión del sprint, omitir.
