# Roles Humanos y Matriz de Autoridad

> **Principio**: NexusAgile define agentes AI. Este documento define los **roles humanos** que los gobiernan.
> En equipo, ningun agente AI actua sin un humano responsable. Los gates son de personas, no de bots.

---

## Roles Humanos

### Product Owner (PO)

| Aspecto | Definicion |
|---------|-----------|
| **Responsabilidad** | Define QUE se construye. Prioriza backlog. Acepta o rechaza trabajo terminado. |
| **Decide** | Alcance, prioridad, orden de HUs en sprint, criterio de aceptacion de negocio |
| **No decide** | Arquitectura, tecnologia, patron de implementacion |
| **Participa en** | Sprint Planning, Status Meeting, Retrospectiva, gate HU_APPROVED |
| **Cantidad** | 1 por producto. No se comparte entre equipos. |

### Tech Lead (TL)

| Aspecto | Definicion |
|---------|-----------|
| **Responsabilidad** | Define COMO se construye. Calidad tecnica. Arquitectura. |
| **Decide** | Stack, patrones, branch strategy, cuando escalar de FAST a QUALITY, aprobacion tecnica de SDDs |
| **No decide** | Prioridad de negocio, alcance funcional |
| **Participa en** | Sprint Planning, gate SPEC_APPROVED, Code Review final, Retrospectiva |
| **Cantidad** | 1 por equipo. Puede cubrir 2 equipos max si los dominios son similares. |

### Developer (Dev)

| Aspecto | Definicion |
|---------|-----------|
| **Responsabilidad** | Implementa. Revisa PRs de peers. Mantiene calidad del codigo que toca. |
| **Decide** | Detalles de implementacion dentro del Story File. Refactors locales. |
| **No decide** | Arquitectura global, alcance, saltar restricciones del SDD |
| **Participa en** | F3 (implementacion), CR (como reviewer de peers), Daily/Status |
| **Cantidad** | 1-N por equipo. Cada dev es owner de sus HUs asignadas. |

### QA Lead

| Aspecto | Definicion |
|---------|-----------|
| **Responsabilidad** | Valida que lo construido cumple lo especificado. Drift detection. Evidencia. |
| **Decide** | Si la evidencia es suficiente, si un AC esta realmente cumplido, si el drift es aceptable |
| **No decide** | Arquitectura, alcance, prioridad |
| **Participa en** | F4 (validacion), CR, Retrospectiva |
| **Cantidad** | 1 por equipo. En equipos chicos, el TL puede asumir este rol. |

### Scrum Master / Facilitador (SM)

| Aspecto | Definicion |
|---------|-----------|
| **Responsabilidad** | Facilita ceremonias. Remueve impedimentos. Protege al equipo de interrupciones. |
| **Decide** | Formato de ceremonias, timeboxing, cuando escalar un impedimento |
| **No decide** | Alcance, arquitectura, prioridad de negocio |
| **Participa en** | Sprint Planning, Status, Retrospectiva, Sprint Closure |
| **Cantidad** | 1 por equipo. En equipos chicos, el TL puede facilitar. |

---

## Matriz de Gates — Quien Aprueba Que

| Gate | Aprobador primario | Aprobador backup | Condicion para aprobar |
|------|-------------------|------------------|----------------------|
| SPRINT_APPROVED | PO + TL (ambos) | — | Backlog priorizado, HUs estimadas, capacidad confirmada |
| HU_APPROVED | PO | SM (si PO delega) | ACs claros, scope definido, sin [NEEDS CLARIFICATION] |
| SPEC_APPROVED | TL | Senior Dev (si TL delega) | SDD tecnicamente viable, Readiness Check OK, sin BLOQUEANTEs en AR de SDD |
| REVIEW_APPROVED | PO + TL | — | Status revisado, bloqueos identificados, plan de accion |
| RELEASE_APPROVED | TL + PO (ambos) | Senior Dev + SM | Pre-release checklist OK, staging verificado, rollback definido |
| RETRO_APPROVED | SM | TL | Action items registrados, retrospectiva completada |

### Reglas de aprobacion

1. **Aprobador primario ausente** — el backup puede aprobar. Si ambos ausentes, la HU espera. No se salta el gate.
2. **Conflicto PO vs TL** — PO decide alcance, TL decide implementacion. Si el conflicto es de riesgo tecnico, TL tiene veto.
3. **Delegacion** — Un aprobador puede delegar por escrito (Slack, issue comment). La delegacion es por gate especifico, no permanente.
4. **Audit trail** — Cada aprobacion queda registrada: quien, cuando, donde (comment en PR, mensaje en canal, firma en artefacto).

---

## Matriz de Delegacion AI — Que Puede Hacer el Agente Solo

> No toda tarea necesita supervision humana. Esta matriz define cuando el agente AI opera autonomo y cuando necesita aprobacion.

| Accion | Autonomia AI | Requiere humano |
|--------|-------------|-----------------|
| F0: Bootstrap + project-context | Autonomo | — |
| F0: Smart Sizing | Autonomo | TL revisa si duda entre modos |
| F1: Generar Work Item | Autonomo | PO aprueba en gate |
| F2: Codebase Grounding | Autonomo | — |
| F2: Generar SDD | Autonomo | TL aprueba en gate |
| F2: Adversarial Review del SDD | Autonomo | TL revisa BLOQUEANTEs |
| F2.5: Generar Story File | Autonomo | — |
| F3: Implementacion | Autonomo | Dev humano revisa PR |
| AR: Adversarial Review | Autonomo | TL revisa BLOQUEANTEs |
| CR: Code Review | Autonomo + Dev peer | TL aprueba merge |
| F4: QA Validation | Autonomo | QA Lead valida evidencia |
| F5: Release Gate checklist | Autonomo | TL + PO aprueban RELEASE_APPROVED |
| DONE: Documentacion | Autonomo | — |
| **Crear branch** | Autonomo | — |
| **Crear PR** | Autonomo | — |
| **Mergear PR** | NUNCA | TL o Dev asignado |
| **Modificar CI/CD** | NUNCA | TL |
| **Borrar branches/datos** | NUNCA | TL |
| **Deploy a produccion** | NUNCA | TL + PO (ambos) |
| **Cambiar dependencias** | Autonomo | TL revisa en CR |

### Niveles de autonomia

| Nivel | Significado | Ejemplo |
|-------|------------|---------|
| **Autonomo** | El agente ejecuta sin esperar. El humano revisa el output. | Generar SDD, Codebase Grounding |
| **Autonomo + Review** | El agente ejecuta, pero un humano debe revisar antes de que el output avance. | F3, PR, review humano |
| **Requiere humano** | El agente propone, el humano decide y ejecuta. | Merge, deploy, cambios de infra |
| **NUNCA** | El agente no puede ejecutar esta accion bajo ninguna circunstancia. | Deploy a prod, borrar datos |

---

## Escalation Path

Dev (humano o AI) encuentra problema
  |
  v
Esta en scope del Story File?
  SI -> Dev resuelve
  NO -> Escala a Architect (AI)
         |
         Requiere cambio de scope?
           SI -> Escala a TL
                   Impacta negocio?
                     SI -> Escala a PO
                     NO -> TL decide
           NO -> Architect ajusta Story File

### Tiempos de respuesta esperados

| Escalacion | Tiempo esperado | Si no hay respuesta |
|-----------|----------------|-------------------|
| Dev a TL | 2 horas | Dev pasa a otra HU, marca como BLOCKED |
| TL a PO | 4 horas | TL toma decision conservadora + documenta |
| BLOQUEANTE en AR | 1 dia | Sprint Status Meeting lo aborda |
| Gate pendiente | 1 dia | SM escala al rol correspondiente |

---

## Configuracion por Tamano de Equipo

### Solo (1 persona)

PO + TL + Dev + QA = misma persona.
Gates: auto-aprobados (modo original NexusAgile).
AI: maxima delegacion.

### Equipo chico (2-4 personas)

PO: 1 persona (puede ser part-time).
TL + QA: 1 persona (Dev senior asume ambos).
Dev: 1-2 personas.
SM: rotativo o el TL facilita.

### Equipo mediano (5-8 personas)

PO: 1 persona dedicada.
TL: 1 persona.
QA: 1 persona (o 1 por cada 4 devs).
Dev: 3-5 personas.
SM: 1 persona (puede ser compartido con otro equipo).

### Equipo grande (9+ personas)

Dividir en 2+ equipos con NexusAgile independiente cada uno.
1 PO puede servir a 2 equipos si el dominio es el mismo.
Cada equipo tiene su propio TL.
Coordinacion entre equipos: Scrum of Scrums facilitado por SMs.

---

## Reglas Globales de Roles

1. **Un rol, una persona** — Nadie ocupa 2 roles en la misma HU (excepcion: equipo solo/chico segun configuracion arriba).
2. **Quien especifica no implementa** — Si el TL escribe el SDD, no deberia ser el reviewer de su propio PR.
3. **Gates son de personas** — Los agentes AI nunca auto-aprueban gates. Ni aunque la calidad sea perfecta.
4. **Delegacion explicita** — No se asume. Se declara por escrito, por gate, por periodo.
5. **Audit trail obligatorio** — Toda aprobacion de gate tiene: quien, cuando, donde. Sin esto, el gate no cuenta.
6. **Veto tecnico** — TL puede vetar una HU si el riesgo tecnico es inaceptable. PO puede escalar a CTO/VP si no esta de acuerdo.
7. **Disponibilidad** — Si un aprobador no esta disponible en el tiempo esperado, el backup actua. Si no hay backup, la HU espera.
