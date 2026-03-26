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

## Herramientas de Medicion

### Opcion 1: Manual (equipo chico)

- Timestamps en artefactos (work-item.md, sdd.md, validation.md, report.md)
- Conteo manual en _INDEX.md
- Sprint report manual con el template de arriba
- Costo: 30 min por sprint para compilar

### Opcion 2: Semi-automatizado (equipo mediano)

- GitHub Actions que extrae metricas de PRs (merge time, review time)
- Script que parsea _INDEX.md y genera estadisticas
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
