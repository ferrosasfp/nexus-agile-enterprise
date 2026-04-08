---
description: NexusAgil FAST — Pipeline compacto para HUs chicas (bugfix, config, doc-only)
argument-hint: <HU-ID>
allowed-tools: Task, Read, Bash, AskUserQuestion
---

# /nexus-fast-pipeline — FAST mode (alternativa al pipeline QUALITY de 8 fases)

Pipeline compacto para Historias de Usuario que **no justifican** el overhead del pipeline QUALITY completo (8 fases con AR/CR/QA exhaustivos).

**Argumentos**: `$ARGUMENTS` (esperado: `WKH-XX`)

## ⚠️ Cuándo usar FAST y cuándo NO

### ✅ FAST está diseñado para
- **Bugfixes < 50 líneas** en código que ya existe y tiene tests
- **Cambios de config** (env vars, feature flags, constantes)
- **Doc-only changes** (README, comentarios, docstrings)
- **Pequeños refactors mecánicos** (rename, mover archivo, format)
- **HUs con sizing FAST** declarado por el analyst en el work-item
- **Hot-fixes urgentes** donde la velocidad importa más que la cobertura exhaustiva

### ❌ FAST NO debe usarse para
- Features nuevas (cualquier código que no exista todavía)
- Cambios en módulos sin tests existentes (no hay safety net)
- Código security-critical (auth, payments, crypto, RBAC, validación de inputs externos)
- Cambios que tocan ≥3 archivos
- Refactors que cambian contratos (signatures, exports, schemas)
- HUs donde el humano duda si vale la pena el overhead → si dudás, usá QUALITY

**Regla de oro**: en duda → `/nexus-p1-f0-f1` (QUALITY). FAST es para casos donde **demostradamente** no necesitás el pipeline completo.

## 📋 Estructura del FAST pipeline

| Fase | Equivalente QUALITY | Agente | Modelo | Saltado |
|------|---------------------|--------|--------|---------|
| F1 fast | p1 (F0/F1) | nexus-analyst | sonnet | F0 bootstrap (asume project-context.md ya existe) |
| **GATE** | HU_APPROVED | humano | — | — |
| F3 fast | p4 (F3) | nexus-dev | opus | usa work-item como contrato (sin SDD ni Story File) |
| F4 fast | p7 (F4) | nexus-qa | sonnet | solo quality gates (typecheck/tests/lint), sin AC verification exhaustiva |
| DONE fast | p8 (DONE) | nexus-docs | haiku | mini-report (5 líneas) + update _INDEX.md |
| **SKIPPED** | p2 (F2 SDD) | — | — | El work-item compacto sirve de spec |
| **SKIPPED** | p3 (F2.5 Story File) | — | — | El dev usa el work-item como contrato |
| **SKIPPED** | p5/p6 (AR + CR) | — | — | ⚠️ NO hay adversarial review — riesgo asumido |

**Tiempo real observado** (datos LUM-11 + P3/P4 dev-puro):

| Métrica | Rango real | Nota |
|---------|-----------|------|
| F3 dev-puro (solo implementación) | 5-7 min | Lo que tarda `nexus-dev` solo |
| FAST total (orquestador incluido) | **10-14 min** | F1 + gate + F3 + F4 fast + DONE fast |
| Ahorro vs QUALITY (60-120 min) | ~80-90% | Depende del tamaño de la HU QUALITY de referencia |

**NO uses el número "3-7 min" de versiones previas** — era optimista, medía solo dev-puro. El wallclock real de una HU chica FAST real es **10-14 min**.

**Costo del ahorro**: NO hay AR ni CR. Si la HU requiere review de seguridad o calidad, **NO uses FAST**:
- **HU chica + bajo riesgo** (UI pura, reads, typos, doc) → `/nexus-fast-pipeline` (este)
- **HU chica + alto riesgo** (writes, auth, streaming, admin, RLS) → `/nexus-fast-plus-ar` ⭐ (sweet spot — 17-32 min con AR+CR)
- **HU grande o arquitectónica** → `/nexus-p1-f0-f1` (QUALITY completo)

## 🎯 Ejecución

Vos sos el orquestador. NO codeás vos mismo. Lanzás los sub-agentes con instrucciones de **modo FAST**.

### Fase 1 — Analyst FAST (compact work-item)

```
Task tool:
  subagent_type: nexus-analyst
  description: F1 FAST para HU [WKH-XX]
  prompt: |
    Eres nexus-analyst en MODO FAST para la HU [WKH-XX].

    DIFERENCIAS vs modo normal:
    - NO ejecutás F0 (bootstrap de project-context.md). Asumí que ya existe; si no existe, ABORTÁ y pedile al humano que corra /nexus-p1-f0-f1 primero.
    - El work-item.md que generás debe ser COMPACTO pero SUFICIENTE como contrato directo para el dev (sin SDD ni Story File).
    - Máximo 3 ACs en EARS.
    - Scope IN debe ser EXHAUSTIVO (lista exacta de archivos a tocar, máx 5). Si supera 5, ABORTÁ — esta HU no es FAST.
    - Smart Sizing forzado a "FAST" en el work-item.
    - NO necesitás Análisis de paralelismo (FAST asume secuencial).

    INPUT:
    - HU del humano: $ARGUMENTS
    - project-context.md (debe existir)
    - doc/sdd/_INDEX.md (para asignar NNN)

    OUTPUT:
    - doc/sdd/NNN-titulo/work-item.md compacto que dobla como story-file (porque el dev lo va a leer directo en F3)
    - Reporte al orquestador: path del work-item + 3 líneas explicando qué se va a hacer

    REGLA CRÍTICA: si al revisar el alcance ves que NO califica como FAST (>5 archivos, código nuevo no trivial, security-critical, sin tests existentes), ABORTÁ con el mensaje: "Esta HU NO es FAST — usar /nexus-p1-f0-f1 (pipeline QUALITY)". El humano decide si reclasifica.

    ## ⛔ PROHIBIDO en FAST mode (igual que en normal + extras)
    - NO generar SDD
    - NO generar Story File
    - NO ACs vagos ("debería", "quizás")
    - NO scope ambiguo
```

### GATE — HU_APPROVED (humano)

Después de Fase 1, **PARAR**. Presentar el work-item al humano y esperar aprobación explícita.

Usar `AskUserQuestion`:
- Pregunta: "El work-item compacto está en `<path>`. ¿Aprobás avanzar a F3 FAST? (revisá ACs, scope IN/OUT, y que efectivamente esto califique como FAST)"
- Opciones: APROBAR / RECHAZAR (con feedback) / RECLASIFICAR a QUALITY (cancela FAST y sugiere /nexus-p1-f0-f1)

Si RECHAZA o RECLASIFICA → ABORT del FAST pipeline. Reportar al humano.

### Fase 2 — Dev FAST (implementación directa)

```
Task tool:
  subagent_type: nexus-dev
  description: F3 FAST para HU [WKH-XX]
  prompt: |
    Eres nexus-dev en MODO FAST para la HU [WKH-XX].

    DIFERENCIAS vs modo normal:
    - Tu input es el WORK-ITEM directamente (NO hay Story File). Tratá el work-item.md como tu contrato autocontenido.
    - NO hay waves declaradas — implementá secuencialmente, todo en un solo bloque.
    - Anti-Hallucination Protocol sigue en vigor: verificás exemplars, no inventás APIs.
    - Auto-Blindaje sigue siendo obligatorio si cometés errores.

    INPUT:
    - doc/sdd/NNN-titulo/work-item.md (usar Scope IN como límite estricto)
    - project-context.md (stack y convenciones)

    OUTPUT:
    - Código en disco según Scope IN del work-item
    - Tests pasando (si aplica — para FAST puede ser solo "los tests existentes siguen pasando")
    - auto-blindaje.md si hubo errores
    - Reporte al orquestador: archivos tocados + comandos corridos + status typecheck/tests

    REGLAS CRÍTICAS:
    - Si descubrís que el cambio requiere tocar archivos FUERA del Scope IN del work-item → STOP, esta HU no era FAST. Reportá al orquestador para escalar a QUALITY.
    - Si descubrís complejidad inesperada (tests rotos en cascada, dependencias ocultas, refactor implícito) → STOP, escalar.
    - NO expandas scope, NO refactors no pedidos, NO docstrings extras.
```

### Fase 3 — QA FAST (quality gates only)

```
Task tool:
  subagent_type: nexus-qa
  description: F4 FAST para HU [WKH-XX]
  prompt: |
    Eres nexus-qa en MODO FAST para la HU [WKH-XX].

    DIFERENCIAS vs modo normal:
    - SKIP drift detection exhaustivo (en FAST el scope es chico, drift se ve a ojo).
    - SKIP AC verification con evidencia detallada — solo confirmá que los ACs SON cumplidos a alto nivel.
    - FOCUS: ejecutar quality gates del stack (typecheck, tests, build, lint) y reportar resultados.

    INPUT:
    - doc/sdd/NNN-titulo/work-item.md (los ACs viven acá en FAST mode)
    - Archivos modificados por el dev: `git diff main...HEAD`

    OUTPUT:
    - doc/sdd/NNN-titulo/validation.md COMPACTO con:
      - Quality gates: PASS/FAIL con output
      - ACs: PASS/FAIL a alto nivel (sin evidencia detallada por AC)
      - Veredicto final: APROBADO / RECHAZADO

    NOTA IMPORTANTE: en FAST mode NO hubo AR ni CR — vos sos la única red de seguridad antes de DONE. Si los quality gates fallan, RECHAZAR sin contemplaciones.
```

### Fase 4 — Docs FAST (mini-report)

```
Task tool:
  subagent_type: nexus-docs
  description: DONE FAST para HU [WKH-XX]
  prompt: |
    Eres nexus-docs en MODO FAST para la HU [WKH-XX].

    DIFERENCIAS vs modo normal:
    - SKIP report.md exhaustivo. Generá solo un mini-report de 5-10 líneas.
    - FOCUS: actualizar _INDEX.md con status DONE.
    - Si hubo Auto-Blindaje, conservá el archivo original sin consolidar (en FAST no se hace consolidación).

    INPUT:
    - doc/sdd/NNN-titulo/{work-item.md, validation.md, auto-blindaje.md}

    OUTPUT:
    1. doc/sdd/NNN-titulo/report.md (compacto, formato:
       ```
       # Report — HU WKH-XX [Título] (FAST mode)

       **Modo**: FAST pipeline (sin SDD/Story File/AR/CR)
       **Fecha cierre**: YYYY-MM-DD
       **Branch**: feat/NNN-titulo

       ## Cambios
       - [archivo]: [descripción de 1 línea]

       ## ACs
       - AC-1: PASS
       - AC-2: PASS

       ## Quality gates
       - typecheck: PASS, tests: PASS, lint: PASS

       ## Riesgo asumido por usar FAST
       [1 línea: qué cobertura no se hizo y por qué se asumió OK]
       ```
    2. doc/sdd/_INDEX.md actualizado con la fila de la HU en status DONE
    3. Reporte al orquestador: 3 líneas resumen
```

## 🛡️ Reglas críticas del FAST pipeline

1. **NO hay AR ni CR**: si la HU descubierta requiere review de seguridad o calidad → ABORT y escalar a QUALITY (`/nexus-p1-f0-f1`).
2. **Cualquier agente puede ABORTAR el FAST**: si analyst, dev, o qa detectan que la HU no califica como FAST (alcance crece, complejidad inesperada, security-critical), DEBEN parar y escalar.
3. **Scope IN es contrato estricto**: si el dev necesita tocar algo fuera del Scope IN, NO lo hace silenciosamente — escala.
4. **Quality gates son no-negociables**: typecheck, tests, lint deben pasar. Si fallan, RECHAZADO.
5. **Auto-Blindaje sigue activo**: si hubo errores durante implementación, se documentan igual.
6. **El humano siempre puede rechazar y reclasificar**: si en cualquier gate ve que era más complejo de lo esperado, FAST se cancela y se reinicia con `/nexus-p1-f0-f1`.

## 🔄 Relación con el pipeline QUALITY

FAST y QUALITY **coexisten**. NO se reemplazan.

- **FAST** = `/nexus-fast-pipeline WKH-XX` (este comando)
- **QUALITY** = `/nexus-p1-f0-f1 WKH-XX` → `/nexus-p2-f2` → ... → `/nexus-p8-done`

El analyst (en cualquier modo) puede recomendar cuál usar, pero el humano decide. FAST es **opt-in explícito** — nunca se invoca por accidente.

## 📊 Métricas (Fase 2 — futuro)

Cuando se instrumenten métricas, FAST trackeará:
- Tiempo total wallclock (target: **10-14 min** para HU chica real)
- Tasa de escalación a QUALITY (target: <20% — si pasa 30%, las heurísticas de "qué califica como FAST" están mal)
- Tasa de escalación a FAST+AR (si está >40% → muchas HUs tienen riesgo oculto y FAST puro está mal elegido por default)
- Bugs post-DONE en HUs FAST vs FAST+AR vs QUALITY (si FAST dispara más bugs, hay que recalibrar el threshold o mover la HU a FAST+AR)

## 🎯 Tabla de elección rápida (leé esto antes de elegir pipeline)

| Señal | Pipeline |
|-------|----------|
| Toca solo UI / CSS / layout / typography | FAST |
| Solo reads a tablas ya validadas | FAST |
| Fix de typo / copy / string | FAST |
| Refactor mecánico de código ya cubierto por AR previo | FAST |
| Server Action con DB write (insert/update/delete) | **FAST+AR** ⭐ |
| Cambio en auth/RBAC/middleware | **FAST+AR** ⭐ |
| Nuevo endpoint que recibe input externo | **FAST+AR** ⭐ |
| Refactor de streaming/tool calling | **FAST+AR** ⭐ |
| Panel admin o gate `is_admin` | **FAST+AR** ⭐ |
| RLS policy nueva o modificada | **FAST+AR** ⭐ |
| Llamada a API externa con secrets | **FAST+AR** ⭐ |
| Feature grande (>5 archivos o >10 ACs) | QUALITY |
| Migration destructiva o no-additive sobre data | QUALITY |
| Función postgres con `SECURITY DEFINER` | QUALITY |
| Necesitás SDD para pensar antes de codear | QUALITY |

**Regla de oro**: en duda → subí un escalón (FAST → FAST+AR → QUALITY), nunca bajes.
