# Sub-Agent Protocol — NexusAgil

> Protocolo de orquestación por sub-agentes para eliminar context overload.
> Principio: el orquestador coordina, los sub-agentes ejecutan.
> Agnóstico de herramienta: Claude Code (Task tool), OpenCode, Cursor, o cualquier agente con sub-agentes.

---

## El Problema que Resuelve

Sin sub-agentes, el pipeline QUALITY acumula contexto en una sola sesión:

```
F0 → F1 → F2 → F2.5 → F3 → AR → CR → F4 → DONE
                                              ↑
                             ventana de contexto saturada
                             → compactación → alucinaciones
```

Con sub-agentes, cada fase empieza limpia:

```
Orchestrator (contexto mínimo — solo coordina)
     │
     ├─► [sub-agente F0] → entrega: project-context.md + sizing
     ├─► [sub-agente F1] → entrega: work-item.md
     │         ⛔ GATE: HU_APPROVED
     ├─► [sub-agente F2] → entrega: sdd.md
     │         ⛔ GATE: SPEC_APPROVED
     ├─► [sub-agente F2.5] → entrega: story-file.md
     ├─► [sub-agente F3]  → entrega: código + auto-blindaje
     ├─► [sub-agente AR]  → entrega: reporte adversarial
     ├─► [sub-agente CR]  → entrega: reporte code review
     ├─► [sub-agente F4]  → entrega: validation.md
     └─► [sub-agente DONE] → entrega: report.md + _INDEX actualizado
```

---

## Rol del Orquestador

El orquestador NUNCA:
- Lee archivos del codebase
- Escribe código
- Genera SDDs ni Story Files
- Ejecuta tests

El orquestador SOLO:
- Lanza sub-agentes con el prompt correcto
- Recibe el artefacto de salida
- Presenta resúmenes al humano en los gates
- Pasa el artefacto como input al siguiente sub-agente
- Detecta si un sub-agente falló y re-lanza

---

## Prompt de cada sub-agente

Cada sub-agente recibe un prompt autocontenido con:

```
Eres el agente [ROL] de NexusAgil ejecutando [FASE].

INPUT:
[artefacto de la fase anterior — work-item.md, sdd.md, etc.]

TU TAREA:
[descripción exacta de la fase]

OUTPUT ESPERADO:
[artefacto a generar — nombre de archivo, formato]
[ruta exacta donde escribir el artefacto]

SCOPE:
- Lee SOLO los archivos referenciados en tu INPUT
- No explores el codebase más allá de lo necesario para tu tarea
- Si necesitas algo que no está en tu INPUT: escala al orquestador

## ⛔ PROHIBIDO EN ESTA FASE — [FASE]
[Copiar el bloque correspondiente de la tabla abajo]
```

### Tabla de PROHIBIDO por fase (obligatorio incluir en cada prompt)

| Fase | PROHIBIDO (copiar literal en el prompt) |
|------|-----------------------------------------|
| **F0** | NO modificar código. NO crear work-item. NO implementar. Solo leer y generar `project-context.md` si no existe. |
| **F1** | NO escribir código de producción. NO modificar archivos fuera de `doc/sdd/NNN-titulo/`. NO ejecutar tests. NO hacer commits. Entregable único: `work-item.md`. |
| **F2** | NO escribir código de producción. NO implementar. NO modificar archivos fuera de `doc/sdd/NNN-titulo/`. Entregable único: `sdd.md`. |
| **F2.5** | NO escribir código de producción. NO implementar. Entregable único: `story-file.md`. |
| **F3** | NO tocar archivos fuera del Scope IN del Story File. NO crear archivos no listados en el Story File. NO expandir scope. Si algo no está en el Story File → parar y escalar. |
| **AR** | NO modificar código. Solo reportar hallazgos. Entregable único: `ar-report.md`. |
| **CR** | NO modificar código. Solo reportar. Entregable único: `cr-report.md`. |
| **F4** | NO modificar código. Solo verificar y reportar. Entregable único: `validation.md`. |
| **DONE** | NO modificar código. Solo generar artefactos de cierre. |

### Regla del orquestador sobre outputs inesperados

Si un sub-agente reporta que hizo trabajo de una fase diferente a la asignada (ej: un F1 que dice "también implementé el código"), el orquestador DEBE:
1. Revertir los cambios no autorizados (`git checkout -- .` sobre los archivos modificados fuera de `doc/`)
2. Registrar como Auto-Blindaje
3. Re-lanzar la fase correcta si el artefacto esperado no fue generado correctamente

---

## Tabla de delegación por fase

| Fase | Sub-agente | Input | Output |
|------|-----------|-------|--------|
| F0 | Analyst + Architect | HU raw + repo path | project-context.md (si no existe) + SDD_MODE |
| F1 | Analyst + Architect + UX | HU + project-context.md | work-item.md |
| F2 | Architect + Adversary | work-item.md + project-context.md | sdd.md |
| F2.5 | Architect | sdd.md | story-file.md |
| F3 | Dev | story-file.md | código en disco + auto-blindaje |
| AR | Adversary | story-file.md + archivos modificados | reporte adversarial |
| CR | Adversary + QA | story-file.md + archivos modificados | reporte code review |
| F4 | QA | story-file.md + archivos modificados | validation.md |
| DONE | Docs | todos los artefactos anteriores | report.md + _INDEX.md |

---

## Paralelismo real en F2

Spec Writer + Designer pueden correr en paralelo como sub-agentes independientes:

```
Orchestrator
     │
     ├─► [sub-agente Spec Writer] ──┐
     │                              ├─► merge → sdd.md completo
     └─► [sub-agente Designer]  ──┘
```

El orquestador espera ambos outputs antes de presentar el SDD al humano.
Solo si el IDE soporta sub-agentes paralelos (Claude Code Task tool, OpenCode).
Si no hay soporte de paralelismo: correr en secuencia, mismo resultado.

---

## Comunicación entre fases

Los artefactos en disco (`doc/sdd/NNN-titulo/`) son el canal de comunicación entre sub-agentes:

```
sub-agente F1 → escribe work-item.md
sub-agente F2 → lee work-item.md (sin necesidad de cargar la conversación anterior)
```

Esto es posible porque los artefactos son autocontenidos. El orquestador no necesita pasar el historial de chat — solo la ruta del archivo.

---

## Cuándo usar sub-agentes vs sesión única

| Señal | Recomendación |
|-------|--------------|
| HU con SDD_MODE = full | Sub-agentes (F2 en adelante) |
| HU con SDD_MODE = bugfix o mini | Sesión única (overhead no justificado) |
| F3 con 3+ waves o 10+ archivos | Sub-agente Dev obligatorio |
| IDE soporta Task tool / sub-agentes | Siempre sub-agentes en QUALITY |
| IDE sin soporte de sub-agentes | Sesión única con Skills Router |

---

## Implementación por herramienta

**Claude Code:**
```
Task tool — el orquestador usa `task` para lanzar cada fase como sub-agente
El sub-agente recibe el prompt completo y los archivos de input
```

**OpenCode:**
```
Spawned agents — el orquestador usa el sistema de agentes de OpenCode
Compatible con el plugin de Engram para persistencia entre fases
```

**Sin soporte nativo:**
```
Sesión única con Skills Router activo
El contexto crece pero el Skills Router lo mantiene limpio
La memoria persistente (Principio 8) compensa la falta de sub-agentes
```

---

## ⚠️ Checklist obligatorio antes de lanzar sub-agente F3

El orquestador ejecuta esto ANTES de lanzar cualquier sub-agente Dev:

```
[ ] ¿Hay otro sub-agente F3 corriendo sobre el mismo directorio?
    → Si SÍ: esperar a que termine, o crear git worktree separado
    → git worktree add ../[repo]-[hu-id] -b feat/[hu-id]-titulo

[ ] ¿El branch base es main actualizado?
    → git checkout main && git pull origin main

[ ] ¿El Story File fue aprobado con SPEC_APPROVED?
    → Verificar que el gate fue respetado antes de lanzar

[ ] ¿Las env vars necesarias para la HU están configuradas?
    → Si la HU toca DB, pagos o servicios externos: verificar antes

[ ] ¿Los permisos de Bash están configurados para background agents?
    → Los sub-agentes en background NO pueden pedir aprobación interactiva
    → Si vas a lanzar F3 en background: verificar que .claude/settings.json
      tenga los permisos granulares necesarios (ver Auto-Blindaje "Bash bloqueado")
    → Si vas a lanzar F3 en foreground: no hace falta (el humano aprueba cada call)
```

**Si falla algún check:** resolver antes de lanzar F3. No lanzar sobre entorno roto.

## Reglas del orquestador

1. **Nunca hace trabajo real** — si el orquestador empieza a generar código o SDDs, es un error de proceso
2. **Contexto mínimo** — el orquestador solo mantiene: fase actual + artefacto de salida + estado del gate
3. **Falla explícita** — si un sub-agente no entrega el artefacto esperado, el orquestador informa al humano y re-lanza
4. **Gates en el orquestador** — los gates (HU_APPROVED, SPEC_APPROVED) los maneja el orquestador, no los sub-agentes
5. **Agnóstico** — el protocolo funciona con cualquier implementación de sub-agentes disponible en el IDE

---

## ⚠️ Auto-Blindaje — F3 Paralelo en Repositorio Compartido

**Fecha:** 2026-04-02 | **Proyecto:** wasiai-a2a | **HUs afectadas:** WKH-6, WKH-7

**Error:** Lanzar 2 sub-agentes F3 en paralelo sobre el mismo directorio de trabajo causa commits mezclados entre branches. Ambos Devs operan sobre el mismo filesystem — los `git add/commit/push` concurrentes contaminan ambos branches con cambios del otro.

**Síntoma:** Branch de WKH-6 contenía commits de WKH-7 y viceversa. El AR detectó scope drift severo.

**Fix aplicado:** Cherry-pick post-hoc para aislar commits por HU. Funciona pero es trabajo extra y arriesgado.

### Regla obligatoria para F3 paralelo:

**OPCIÓN A — Serializar F3 (recomendado por defecto):**
Nunca lanzar dos sub-agentes F3 simultáneamente sobre el mismo repo. Implementar WKH-X → merge → implementar WKH-Y.

**OPCIÓN B — Git worktrees (si el paralelismo es crítico):**
Crear un worktree separado por HU antes de lanzar F3:
```bash
git worktree add ../wasiai-a2a-wkh-6 -b feat/wkh-6-xxx
git worktree add ../wasiai-a2a-wkh-7 -b feat/wkh-7-xxx
```
Cada sub-agente F3 recibe su propio `cwd` distinto. Al terminar, eliminar worktrees:
```bash
git worktree remove ../wasiai-a2a-wkh-6
git worktree remove ../wasiai-a2a-wkh-7
```

**El orquestador debe verificar antes de lanzar F3 paralelo:**
- ¿Hay un único directorio de trabajo compartido? → Serializar
- ¿Hay worktrees separados preparados? → Puede paralelizar

**Esta regla aplica a cualquier proyecto**, no solo wasiai-a2a.

---

## ⚠️ Auto-Blindaje — Gates saltados por sub-agente one-shot

**Fecha:** 2026-04-04 | **Proyecto:** wasiai-a2a | **HUs afectadas:** WKH-10, WKH-13, WKH-14

**Error:** El orquestador lanzó un sub-agente único con instrucción "pipeline completo F0→DONE". Los sub-agentes en modo `run` (one-shot) no pueden pausar y esperar respuesta humana — saltaron HU_APPROVED y SPEC_APPROVED silenciosamente.

**Síntoma:** El orquestador aprobó los gates él mismo, sin presentar Work Item ni SDD al humano para revisión. Violación directa del principio "El humano decide QUÉ".

### Regla obligatoria para orquestador:

**NUNCA incluir más de un gate en el prompt de un sub-agente.**

El flujo correcto es:

```
Orquestador lanza sub-agente F0+F1
  → sub-agente entrega work-item.md
  → orquestador presenta Work Item al humano
  → humano escribe HU_APPROVED
Orquestador lanza sub-agente F2+F2.5
  → sub-agente entrega sdd.md + story-file.md
  → orquestador presenta SDD al humano
  → humano escribe SPEC_APPROVED
Orquestador lanza sub-agente F3→DONE
  → sin gates humanos en este tramo (AR, CR, F4 son reviews de agentes)
```

**Señales de que estás violando esta regla:**
- El prompt del sub-agente dice "pipeline completo" o "F0→DONE"
- El prompt del sub-agente dice "esperar HU_APPROVED" (imposible en modo one-shot)
- El orquestador presenta el resultado final sin haber mostrado Work Item ni SDD al humano

**Fix:** Siempre dividir en mínimo 3 lanzamientos separados: F0+F1 / F2+F2.5 / F3→DONE. El orquestador es el checkpoint humano entre ellos.

---

## ⚠️ Auto-Blindaje — Bash bloqueado en background agents

**Fecha:** 2026-04-09 | **Proyecto:** wasiai-a2a | **HUs afectadas:** WKH-34, WKH-35

**Error:** Sub-agentes F3 lanzados en background (`run_in_background: true`) fallan silenciosamente porque necesitan Bash para operaciones obligatorias del pipeline (git checkout -b, npm test, npx tsc --noEmit, mkdir, rm) pero los background agents no pueden solicitar aprobación interactiva al humano. El sub-agente se bloquea en el primer Bash call no aprobado y aborta sin output útil.

**Síntoma:** Ambos sub-agentes F3 retornan error o output vacío. El orquestador reintenta con los mismos permisos → mismo resultado. Tiempo perdido: ~2 relanzamientos por HU antes de diagnosticar la causa.

**Fix aplicado:** Configurar permisos granulares de Bash en `.claude/settings.json` ANTES de lanzar sub-agentes en background:

```json
{
  "permissions": {
    "allow": [
      "Bash(git *)",
      "Bash(npm test*)",
      "Bash(npm run *)",
      "Bash(npx tsc*)",
      "Bash(npx vitest*)",
      "Bash(mkdir *)",
      "Bash(rm src/*)",
      "Bash(rm -rf node_modules/.cache*)",
      "Bash(cat *)",
      "Bash(ls *)",
      "Bash(wc *)"
    ]
  }
}
```

### Regla obligatoria para el orquestador:

**Antes de lanzar cualquier sub-agente F3 en background**, verificar que los permisos de Bash estén configurados. Si no lo están:

1. **Opción recomendada:** configurar permisos granulares (lista específica de patrones aprobados)
2. **Alternativa:** lanzar el sub-agente en foreground (el humano aprueba cada Bash call interactivamente — más lento pero no requiere config previa)
3. **Último recurso:** el orquestador implementa directamente — viola "orquestador no codea" pero es un override consciente por limitación técnica. Documentar como excepción.

**Señales de que estás cayendo en este error:**
- Sub-agente F3 retorna output vacío o error genérico
- El error menciona "tool not allowed" o "permission denied" para Bash
- El sub-agente fue lanzado con `run_in_background: true`

**Alcance:** aplica a CUALQUIER sub-agente en background que necesite Bash, no solo F3. AR/CR generalmente no necesitan Bash (solo Read/Glob/Grep), pero F3, F4 (quality gates), y DONE (git operations) sí lo necesitan.

---

## AUTO Mode — Clinical Review Gate Handling

En modo AUTO (`/nexus-auto`), el orquestador reemplaza `AskUserQuestion` en los gates
con clinical reviews estructurados. Lee el artefacto, evalúa contra checklist, y
self-aprueba (con atribución) o escala al humano.

### Atribución (obligatoria)

Todo self-approval documenta:

```
[GATE] — [fecha] by Claude (delegated by [user])
Clinical review: [criterios con PASS/FAIL]
Notes: [observaciones]
```

### Cuándo escalar vs self-aprobar

- **Self-aprobar:** todos los criterios PASS, sin ambigüedad, sin `[NEEDS CLARIFICATION]`.
- **Escalar:** cualquier criterio FAIL, analyst abortó, o incertidumbre del orquestador.

La regla es binaria: si hay duda, escalar. El costo de preguntar al humano es bajo;
el costo de aprobar algo incorrecto puede ser alto (bugs en prod, rework).

### Compatibilidad con Auto-Blindaje "Gates saltados"

AUTO mode **NO viola** la regla de "NUNCA incluir más de un gate en el prompt de un sub-agente".
Los sub-agentes siguen recibiendo **UNA fase a la vez**. La diferencia es que el orquestador
self-aprueba en lugar de esperar al humano. El gate sigue existiendo como checkpoint —
solo cambia **QUIÉN** aprueba.

Flujo correcto en AUTO:
```
Orquestador lanza sub-agente F0+F1
  → sub-agente entrega work-item.md
  → orquestador ejecuta clinical review (§4.1 de /nexus-auto)
  → PASS → self-approve con atribución
  → FAIL → AskUserQuestion al humano
Orquestador lanza sub-agente F2
  → sub-agente entrega sdd.md
  → orquestador ejecuta clinical review (§4.2 de /nexus-auto)
  → PASS → self-approve con atribución
  → FAIL → AskUserQuestion al humano
Orquestador lanza sub-agentes F2.5 → F3 → AR → CR → F4 → DONE
  → sin gates humanos en este tramo (ya son automáticos en manual también)
```
