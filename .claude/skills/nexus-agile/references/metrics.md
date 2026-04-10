# Metricas y Dashboard

> **Principio**: Lo que no se mide no se mejora. Un CTO necesita visibilidad.
> Estas metricas responden: "Esta funcionando NexusAgile?" y "Donde estan los cuellos de botella?"

---

## KPIs del Pipeline

### Velocidad y Entrega

| Metrica | Definicion | Como medir | Target |
|---------|-----------|-----------|--------|
| **Lead Time** | Tiempo desde F0 hasta DONE de una HU | fecha_DONE - fecha_F0 | < 3 dias (FAST), < 1 semana (QUALITY) |
| **Cycle Time por Fase** | Tiempo que cada fase toma | Timestamps en artefactos | F0-F1: <1h, F2: <2h, F3: variable, AR+CR: <1h, F4: <30min |
| **Throughput** | HUs completadas por sprint | Contar DONE en _INDEX.md | Aumentar o mantener sprint a sprint |
| **Carry-over Rate** | HUs que pasan al siguiente sprint | HUs_no_completadas / HUs_planificadas * 100 | < 20% |
| **PR Merge Time** | Tiempo desde PR abierto hasta mergeado | GitHub/GitLab metrics | < 24h |

### Calidad

| Metrica | Definicion | Como medir | Target |
|---------|-----------|-----------|--------|
| **Tasa de BLOQUEANTEs en AR** | % de HUs con hallazgos BLOQUEANTE | HUs_con_BLOQUEANTE / HUs_totales * 100 | Tendencia descendente sprint a sprint |
| **Categorias de BLOQUEANTE** | Distribucion de hallazgos por categoria | Clasificar de adversarial_review_checklist.md | Sin concentracion en una categoria |
| **Drift Rate** | % de archivos implementados que difieren del plan | archivos_drift / archivos_planificados * 100 en F4 | < 10% |
| **Bug Escape Rate** | Bugs encontrados en produccion post-deploy | Bug tracker | 0 es el target, < 2 por sprint es aceptable |
| **Re-work Rate** | HUs que vuelven de F4 a F3 | Contar iteraciones QA->Dev | < 15% |

### Anti-Alucinacion

| Metrica | Definicion | Como medir | Target |
|---------|-----------|-----------|--------|
| **Imports Fantasma** | Imports generados que no existen | Contar en AR/CR | 0 |
| **Archivos Fuera de Scope** | Archivos tocados que no estaban en el SDD | Drift Detection en F4 | 0 |
| **Exemplar Miss Rate** | Exemplars referenciados que no existian | Auto-Blindaje log | 0 |
| **Upgrade Rate** | % de FAST que escalan a QUALITY | upgrades / total_FAST * 100 | < 25% (mas = mala estimacion en F0) |

### Eficiencia AI

| Metrica | Definicion | Como medir | Target |
|---------|-----------|-----------|--------|
| **Tokens por HU** | Consumo total de tokens por HU | API usage logs | Tendencia estable o descendente |
| **Costo por HU** | Costo en USD por HU completada | tokens * precio_por_token | Establecer baseline en sprint 1 |
| **Sub-agent Count** | Cantidad de sub-agentes por HU | Contar en orchestrator log | Consistente con complejidad |
| **Context Overflow Events** | Veces que el contexto se saturo | Logs del agente | 0 (sub-agents deberian prevenirlo) |

---

## Sprint Dashboard — Template

### Sprint NNN Dashboard

**Periodo**: YYYY-MM-DD a YYYY-MM-DD
**Equipo**: [nombre]
**Capacidad**: N devs x M dias = P dev-days

#### Estado de HUs

| HU | Owner | Fase actual | Status | Bloqueado por | PR |
|----|-------|-------------|--------|--------------|-----|
| 001 | @dev-1 | F4 (QA) | on-track | — | #42 |
| 002 | @dev-2 | F3 (W2) | on-track | — | — |
| 003 | @dev-3 | F2 (SDD) | blocked | SPEC_APPROVED pendiente | — |

#### Metricas del Sprint

| Metrica | Valor | Target | Tendencia |
|---------|-------|--------|-----------|
| HUs completadas | 2/5 | 5 | on-track |
| BLOQUEANTEs en AR | 1 | 0 | neutral |
| Drift rate | 5% | <10% | OK |
| PRs pendientes review | 1 | 0 | needs-attention |

---

## Sprint Report — Template de Cierre

### Resumen Ejecutivo

| Indicador | Planificado | Real | Delta |
|-----------|------------|------|-------|
| HUs comprometidas | N | N | +/- |
| HUs completadas | — | N | — |
| HUs carry-over | — | N | — |

### Velocidad (tendencia)

| Sprint | HUs completadas | Trend |
|--------|----------------|-------|
| N-2 | X | — |
| N-1 | Y | +/- vs N-2 |
| N | Z | +/- vs N-1 |

### Calidad (tendencia)

| Metrica | Sprint N-1 | Sprint N | Trend |
|---------|-----------|----------|-------|
| BLOQUEANTEs en AR | X | Y | mejoro/empeoro |
| Drift rate promedio | X% | Y% | mejoro/empeoro |
| Bug escapes | X | Y | mejoro/empeoro |
| Re-work rate | X% | Y% | mejoro/empeoro |

### Costos AI

| Metrica | Sprint N-1 | Sprint N | Trend |
|---------|-----------|----------|-------|
| Tokens totales | Xk | Yk | +/-% |
| Costo total USD | $X | $Y | +/-% |
| Costo por HU | $X | $Y | +/-% |

---

## Baselines Reales (datos de produccion)

> Datos del proyecto Luma AI: 53 HUs en 4 dias, 256 tests, 0 bugs en prod.

### Tiempos por pipeline (wallclock medido)

| Pipeline | Rango real | Incluye |
|----------|-----------|---------|
| **FAST** | 8-15 min | F1 + HU_APPROVED + F3 + F4 + DONE |
| **FAST+AR** | 15-20 min | F1 + HU_APPROVED + F3 + AR+CR paralelo + fix-pack + F4 + DONE |
| **QUALITY** | 45-90 min | F0+F1 + HU_APPROVED + F2 + SPEC_APPROVED + F2.5 + F3 + AR+CR + F4 + DONE |

### Distribucion tipica de pipelines

```
QUALITY:    ████████░░░░░░░░░░░░░░░░░░░░░░  15%  (core architecture)
FAST+AR:    ████████████░░░░░░░░░░░░░░░░░░  23%  (small + risky)
FAST:       ██████████████████░░░░░░░░░░░░  34%  (hotfixes, UI, config)
Sin Nexus:  ███████████████░░░░░░░░░░░░░░░  28%  (pre-Nexus, mecanico)
```

**Patron observado**: conforme el sprint avanza, QUALITY baja y FAST+AR/FAST sube (la arquitectura se estabiliza, los cambios son incrementales).

### Costo por sesion (Claude Code, Opus pricing)

| Metrica | Valor observado |
|---------|----------------|
| Costo por turn | $0.08-0.11 |
| Cache read ratio | ~89% del input (ahorro ~90% vs sin cache) |
| Output tokens (dominante) | $75/M — el mayor componente de costo |
| Sesion mediana | $20-40 por sesion de trabajo |
| Sprint completo (8 HUs, mixed pipelines) | ~$89 |
| Costo estimado por HU | ~$11 (promedio FAST+QUALITY mixed) |

### Token analysis script

Parsear los transcripts `.jsonl` de Claude Code para extraer tokens y costo:

```python
# Guardar como scripts/analyze-sessions.py
import json, os, glob

base = os.path.expanduser("~/.claude/projects/")
# Buscar en el subdirectorio del proyecto
for project_dir in glob.glob(base + "*/"):
    files = sorted(glob.glob(project_dir + "*.jsonl"), key=os.path.getmtime, reverse=True)
    for fp in files[:5]:
        ti = to = tcr = tcc = turns = 0
        with open(fp, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line.strip())
                    if obj.get("type") == "assistant":
                        msg = obj.get("message", {})
                        if isinstance(msg, dict) and "usage" in msg:
                            u = msg["usage"]
                            ti += u.get("input_tokens", 0)
                            to += u.get("output_tokens", 0)
                            tcr += u.get("cache_read_input_tokens", 0)
                            tcc += u.get("cache_creation_input_tokens", 0)
                            turns += 1
                except:
                    pass
        cost = (ti/1e6)*15 + (tcc/1e6)*3.75 + (tcr/1e6)*0.375 + (to/1e6)*75
        fname = os.path.basename(fp)[:10]
        size = os.path.getsize(fp) / 1e6
        print(f"{fname}  {size:5.1f}MB  {turns:>4}t  out:{to:>8,}  ${cost:.2f}")
```

---

## Project Metrics Report — Template

> Formato validado en Luma AI (53 HUs, 4 dias). Usar al cierre de proyecto o sprint largo.

### Seccion 1 — Totales

```
┌───────────────────────────────────────────┬──────────────────────────────────┐
│                  Metrica                  │              Valor               │
├───────────────────────────────────────────┼──────────────────────────────────┤
│ HUs completadas (Done)                    │ N                                │
├───────────────────────────────────────────┼──────────────────────────────────┤
│ Pipeline QUALITY                          │ N                                │
├───────────────────────────────────────────┼──────────────────────────────────┤
│ Pipeline FAST+AR                          │ N                                │
├───────────────────────────────────────────┼──────────────────────────────────┤
│ Pipeline FAST                             │ N                                │
├───────────────────────────────────────────┼──────────────────────────────────┤
│ Sin pipeline Nexus                        │ N                                │
├───────────────────────────────────────────┼──────────────────────────────────┤
│ Periodo                                   │ YYYY-MM-DD → YYYY-MM-DD (N dias) │
├───────────────────────────────────────────┼──────────────────────────────────┤
│ Promedio HUs/dia                          │ ~N                               │
└───────────────────────────────────────────┴──────────────────────────────────┘
```

### Seccion 2 — Detalle por pipeline

Tabla por HU agrupada por pipeline: #, HU-ID, Feature (1 linea), Closed date, Docs generados.

### Seccion 3 — Distribucion visual

```
QUALITY:    ████████░░░░░░░░░░░░░░░░░░░░░░  N  (N%)
FAST+AR:    ████████████░░░░░░░░░░░░░░░░░░  N  (N%)
FAST:       ██████████████████░░░░░░░░░░░░  N  (N%)
Sin Nexus:  ███████████████░░░░░░░░░░░░░░░  N  (N%)
```

### Seccion 4 — Distribucion temporal

Tabla dia por dia: fecha, HUs cerradas, tipo predominante, notas.

### Seccion 5 — Tiempos por pipeline (medidos)

Datos reales de la ejecucion, no estimados. Incluir ejemplo representativo por pipeline.

### Seccion 6 — Resumen ejecutivo

```
┌────────────────────────────┬───────────────────────────────────────────┐
│          Metrica           │                  Valor                    │
├────────────────────────────┼───────────────────────────────────────────┤
│ HUs totales                │ N                                         │
├────────────────────────────┼───────────────────────────────────────────┤
│ Dias de desarrollo         │ N                                         │
├────────────────────────────┼───────────────────────────────────────────┤
│ HUs/dia promedio           │ N                                         │
├────────────────────────────┼───────────────────────────────────────────┤
│ Tests al cierre            │ N passing                                 │
├────────────────────────────┼───────────────────────────────────────────┤
│ Errores en produccion      │ N                                         │
├────────────────────────────┼───────────────────────────────────────────┤
│ Pipeline mas usado         │ [nombre] (N%) — [contexto]                │
├────────────────────────────┼───────────────────────────────────────────┤
│ Pipeline mas valioso       │ [nombre] (N%) — [contexto]                │
└────────────────────────────┴───────────────────────────────────────────┘
```

---

## Herramientas de Medicion

### Opcion 1: Manual (equipo chico)

- Timestamps en artefactos (work-item.md, sdd.md, validation.md, report.md)
- Conteo manual en _INDEX.md
- Sprint report manual con el template de arriba
- Token analysis script (ver seccion anterior)
- Costo: 30 min por sprint para compilar

### Opcion 2: Semi-automatizado (equipo mediano)

- GitHub Actions que extrae metricas de PRs (merge time, review time)
- Script que parsea _INDEX.md y genera estadisticas
- Token analysis script integrado en CI
- Dashboard en Notion/Confluence
- Costo: setup inicial 2-4h, luego 15 min por sprint

### Opcion 3: Automatizado (equipo grande / enterprise)

- Pipeline de CI que mide cycle time, cuenta BLOQUEANTEs, calcula drift rate, trackea token usage
- Dashboard en Grafana/Datadog/Metabase
- Alertas automaticas: PR sin review >24h, gate pendiente >48h, CI rojo >2h
- Costo: setup inicial 1-2 sprints, luego automatico

---

## Alertas y Umbrales

| Alerta | Condicion | Accion | Notificar a |
|--------|----------|--------|------------|
| **PR sin review** | >24h abierto sin reviewer | SM asigna reviewer | SM + TL |
| **Gate pendiente** | >48h sin aprobacion | SM escala al aprobador | SM + aprobador |
| **CI rojo** | >2h en rojo | Dev owner investiga | Dev + TL |
| **Sprint en riesgo** | >30% carry-over estimado en Status | Re-priorizar o reducir scope | PO + TL + SM |
| **Costo anomalo** | >2x el costo promedio por HU | TL investiga (context overflow? HU muy grande?) | TL |
| **BLOQUEANTE recurrente** | Misma categoria 3+ sprints | TL define training o regla preventiva | TL + equipo |

---

## Reglas de Metricas

1. **No gamificar** — Las metricas son para mejorar el proceso, no para evaluar personas. No rankear devs por throughput.
2. **Tendencias > valores absolutos** — Un drift rate de 15% no es malo si el anterior era 30%. Lo que importa es la direccion.
3. **Baseline primero** — Sprint 1 establece baseline. No hay targets hasta sprint 2.
4. **Revisar en retro** — Metricas se revisan en cada retrospectiva. Si una metrica no genera accion, dejar de medirla.
5. **Costo es informativo** — El costo por HU se reporta para presupuesto, no para limitar. Si una HU critica necesita mas tokens, se gasta.
6. **Automatizar gradualmente** — Empezar manual, automatizar lo que duela. No over-engineer el tooling de metricas.
