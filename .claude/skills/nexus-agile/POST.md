# NexusAgile: La metodologia que convierte agentes AI en tu equipo de desarrollo

## El problema que todos tenemos con AI y codigo

Usas Claude, Cursor, Copilot o cualquier otro asistente AI para programar. Funciona increible para preguntas puntuales. Pero cuando le pides algo mas ambicioso — "implementa el flujo de pagos" — pasan cosas:

- **Inventa imports** que no existen en tu proyecto
- **Ignora tus patrones** y escribe codigo con estilo propio
- **No valida** si lo que genero realmente funciona
- **Alucina** archivos, funciones y APIs que nunca existieron
- **No hay proceso**: un dia genera bien, otro dia genera basura, y no hay forma de predecir cual

Ahora multiplica eso por un equipo de 5 personas. Cada uno usando AI a su manera. Sin estandar. Sin trazabilidad. Sin control de calidad sistematico.

NexusAgile resuelve esto.

---

## Que es NexusAgile

NexusAgile es una **metodologia de desarrollo de software** inspirada en **Scrum** y **Spec-Driven Development (SDD)** donde agentes AI especializados ejecutan un pipeline completo de ingenieria — analisis, diseno, implementacion, ataque adversarial, validacion — y los humanos toman decisiones en puntos de control llamados **gates**.

**Tu describes una feature.** El AI analiza, disena, implementa, ataca su propia solucion, y valida con evidencia. **Tu aprobas en 2-3 checkpoints.** Feature lista con spec, review de seguridad, y evidencia de QA.

No es un prompt. No es un template. Es un **sistema completo** que se instala como un Claude Code skill y transforma como tu equipo desarrolla software.

### De Scrum toma:

- **Sprints** con planning, daily standups, status meetings y retrospectivas
- **Roles claros** con responsabilidades definidas (PO, TL, Dev, QA, SM)
- **Ceremonies** con cadencia regular y output concreto
- **Historias de Usuario (HU)** como unidad de trabajo
- **Velocidad y carry-over** como metricas de equipo

### De Spec-Driven Development toma:

- **Spec primero, codigo despues** — nada se implementa sin un SDD (Software Design Document) aprobado
- **Contratos explicitos** — el Story File define que archivos crear, que modificar, que patrones seguir, que esta prohibido
- **Trazabilidad** — cada Acceptance Criteria se verifica con evidencia `archivo:linea`
- **Drift Detection** — se verifica que lo implementado coincide exactamente con lo especificado

### Lo que NexusAgile agrega:

- **9 agentes AI especializados** con roles separados (quien especifica NO implementa, quien implementa NO valida)
- **Anti-alucinacion** como pilar fundamental (Codebase Grounding, Exemplar Pattern, Constraint Directives)
- **Adversarial Review** — un agente AI ataca la solucion de otro agente AI antes de que llegue a review
- **3 modos** adaptados a la complejidad real del cambio (FAST, LAUNCH, QUALITY)
- **Gates estrictos** donde solo texto exacto activa la aprobacion (no "si", no "ok", no "dale")
- **Release Gate** con checklist pre-produccion (staging, migraciones, env vars, rollback)

---

## Como funciona: el pipeline

Cada HU pasa por este flujo:

```
HU (en lenguaje natural)
    |
    v
[ F0: Contexto ] -------- AI lee tu codebase real, detecta stack, patrones, estructura
    |
    v
[ F1: Discovery ] ------- AI genera Work Item con Acceptance Criteria precisos
    |
    v
[ HU_APPROVED ] --------- Humano aprueba scope (texto exacto)
    |
    v
[ F2: Spec/SDD ] -------- AI disena solucion referenciando TU codigo como exemplar
    |
    v
[ SPEC_APPROVED ] ------- Humano aprueba diseno tecnico (texto exacto)
    |
    v
[ F2.5: Story File ] ---- AI genera contrato de implementacion (waves, archivos, constraints)
    |
    v
[ F3: Implementacion ] -- AI implementa siguiendo el Story File, wave por wave
    |
    v
[ Adversarial Review ] -- OTRO agente AI ataca la solucion buscando fallas
    |
    v
[ Code Review ] --------- Revision automatica de calidad + peer review humano
    |
    v
[ F4: QA Validation ] --- Verificacion de cada AC con evidencia archivo:linea
    |
    v
[ RELEASE_APPROVED ] ---- Humano verifica staging + pre-release checklist
    |
    v
DONE -------------------- Documentacion completa, trazable, auditada
```

**Entre gates, el pipeline corre solo.** No te pide permiso para pasar de una fase a otra. Solo se detiene donde necesita tu decision.

---

## Los 3 modos: no todo necesita el pipeline completo

| Modo | Cuando usarlo | Ejemplo | Tiempo |
|------|--------------|---------|--------|
| **FAST** | Cambio trivial: 1-2 archivos, <30 lineas, sin DB, sin logica | Corregir un typo, cambiar un color, actualizar texto | 5-15 min |
| **LAUNCH** | MVP o prototipo nuevo desde cero | Primera version de una app, demo para inversores | 1-2 dias |
| **QUALITY** | Feature para produccion | Flujo de pagos, autenticacion, dashboard con DB | 1-3 dias |

En duda, QUALITY. Es mejor sobre-procesar que dejar pasar un bug a produccion.

FAST no es "sin proceso" — es proceso adaptado. El AI hace triage automatico: si detecta que el cambio toca DB, auth o mas de 2 archivos, auto-escala a QUALITY.

---

## Los 9 agentes: especializacion, no generalismo

NexusAgile no usa "un AI para todo". Usa agentes con roles separados, como un equipo real:

| Agente | Rol | Principio |
|--------|-----|-----------|
| **Analyst** | Business Analyst — extrae requisitos, normaliza la HU | Entiende el QUE |
| **Architect** | Software Architect — lee codebase, disena SDD, genera Story File | Decide el COMO |
| **UX** | UX Designer — microcopy, flujos, accesibilidad | Protege al usuario |
| **Dev** | Senior Developer — implementa SOLO desde Story File | Ejecuta sin inventar |
| **Adversary** | Security Adversary — ataca la solucion buscando fallas | Rompe lo que Dev construyo |
| **QA** | QA Engineer — valida cada AC con evidencia | Verifica con pruebas |
| **SM** | Scrum Master — facilita ceremonias | Coordina al equipo |
| **Triage** | Quick Flow Specialist — pipeline abreviado para cambios triviales | Evita over-engineering |
| **Docs** | Documentation Specialist — documenta todo | Deja trazabilidad |

**Regla de separacion**: Quien especifica (Architect) NO implementa (Dev). Quien implementa (Dev) NO valida (QA). Quien revisa adversarialmente (Adversary) NO implemento.

Es el mismo principio de segregation of duties de seguridad, aplicado a AI.

---

## Anti-alucinacion: el diferenciador

La mayoria de las herramientas AI generan codigo "en el vacio". NexusAgile invierte esto con 3 mecanismos:

### 1. Codebase Grounding

Antes de generar CUALQUIER cosa, el agente DEBE:
1. Leer archivos reales de tu proyecto
2. Extraer patrones (naming, imports, estructura)
3. Documentar lo leido en un Context Map
4. Referenciar archivos existentes como exemplars

**El AI no imagina codigo. Lee tu codigo real y genera codigo que sigue tus patrones.**

### 2. Exemplar Pattern

Cada decision del SDD referencia un archivo real de tu codebase:

```markdown
## Exemplars (codigo real referenciado)
| Patron | Archivo:Linea | Usar como |
|--------|--------------|-----------|
| API route handler | src/app/api/recipes/route.ts:5-25 | Template para nuevo endpoint |
| Component props | src/components/RecipeCard.tsx:8 | Extender interface |
| Auth check | src/lib/auth.ts:15 | Reutilizar patron exacto |
```

Si el exemplar no existe, el agente lo busca. Si no lo encuentra, escala. **Nunca referencia un archivo que no confirmo que existe.**

### 3. Constraint Directives

El Story File incluye reglas explicitas de que esta permitido y que esta prohibido:

```
REQUIRED: Usar getCurrentUser() de src/lib/auth.ts — no crear auth propio
REQUIRED: Seguir patron de API route de recipes/route.ts
FORBIDDEN: No usar localStorage para persistir datos sensibles
FORBIDDEN: No crear tabla intermedia manual — usar relacion del ORM
```

Esto elimina la clase de errores mas comun del AI: inventar soluciones cuando ya existe una en el codebase.

---

## Adversarial Review: el AI que ataca al AI

Despues de que el Dev agent implementa, el Adversary agent ataca la solucion con 8 categorias de revision:

1. **Imports fantasma** — importa algo que no existe?
2. **Regression** — rompe funcionalidad existente?
3. **Seguridad** — XSS, injection, auth bypass?
4. **Performance** — N+1 queries, renders innecesarios?
5. **Drift** — se desvio del SDD?
6. **Edge cases** — que pasa con null, vacio, concurrencia?
7. **Dependencias** — agrego algo sin justificar?
8. **Accesibilidad** — aria labels, contraste, keyboard nav?

Los hallazgos se clasifican:
- **BLOQUEANTE**: No se puede mergear hasta que se corrija
- **MENOR**: Se documenta, se puede mergear
- **OK**: Sin hallazgos

Un dev humano que detecta algo que el AI no → se documenta en **Auto-Blindaje** y el sistema mejora para la proxima HU.

---

## Para equipos: roles humanos y gates

NexusAgile escala desde 1 persona hasta equipos de 12+:

| Tamano | Configuracion |
|--------|--------------|
| **1 persona** | Tu eres PO + TL + Dev. Gates auto-aprobados. AI maxima delegacion. |
| **2 personas** | PO (scope) + TL/Dev (tecnico). Gates separados — quien aprueba scope no implementa. |
| **3-4 personas** | PO + TL + 1-2 Devs. Peer review humano real. SM rotativo. |
| **5-8 personas** | Roles dedicados. PO, TL, 2+ Devs, QA Lead, SM. Paralelismo de HUs. |
| **9+ personas** | Dividir en equipos. Scrum of Scrums. Cross-team protocol. |

### Los gates son de personas, no de bots

| Gate | Quien aprueba | Que verifica |
|------|--------------|-------------|
| HU_APPROVED | Product Owner | El scope captura lo que se necesita |
| SPEC_APPROVED | Tech Lead | El diseno tecnico es viable |
| RELEASE_APPROVED | TL + PO | Staging verificado, migraciones OK, rollback definido |

**Solo texto exacto activa un gate.** Decir "si" o "ok" no activa nada. Esto no es burocracia — es trazabilidad.

---

## Case Types: no todas las HUs son iguales

NexusAgile detecta automaticamente cuando una HU necesita checks adicionales:

| Case Type | Que agrega al pipeline | Nunca FAST |
|-----------|----------------------|-----------|
| **DB-MIGRATION** | Rollback plan, down migration, staging verification | Si |
| **CONTRACT-CHANGE** | Backward compatibility, consumer notification, contract tests | Si |
| **INFRA-ENV** | Env vars en todos los entornos, secrets check | Excepto trivial |
| **SECURITY-INCIDENT** | AR obligatorio completo, buscar variantes, test de vulnerabilidad | Si |
| **DATA-BACKFILL** | Script idempotente, dry-run obligatorio, supervision humana | Si |

El Case Type no cambia el pipeline — lo enriquece con checks especificos.

---

## Como empezar: en 15 minutos

### Paso 1: Instalar el skill

Clona el repositorio dentro de tu proyecto:

```bash
# En la raiz de tu proyecto
mkdir -p .claude/skills
git clone https://github.com/ferrosasfp/nexus-agile-enterprise.git .claude/skills/nexus-agile
```

### Paso 2: Generar el contexto de tu proyecto

Abre Claude Code y di:

> "NexusAgile, this is a new project. Read the codebase and generate project-context.md"

El AI escanea tu stack, dependencias, estructura, patrones y comandos. Genera `project-context.md` una vez. De ahi en adelante, todos los agentes conocen tu proyecto.

### Paso 3: Procesar tu primera HU

Di:

> "NexusAgile, procesa esta HU: Como usuario, quiero [tu feature]"

El pipeline arranca automaticamente:
1. AI analiza tu codebase y genera un Work Item con Acceptance Criteria
2. Tu revisas y escribes: **HU_APPROVED**
3. AI disena la solucion referenciando tu codigo real
4. Tu revisas y escribes: **SPEC_APPROVED**
5. AI implementa, ataca su propia solucion, valida con evidencia
6. Tu revisas el PR y mergeas

**Tu primera HU te va a tomar entre 30 minutos (FAST) y 4 horas (QUALITY).** A partir de la segunda, ya conoces el flujo.

### Paso 4: Para equipos

Lee la seccion de tu rol en `references/onboarding.md`:
- **Product Owner**: 15 min de lectura
- **Tech Lead**: 30 min de lectura
- **Developer**: 20 min de lectura
- **QA Lead**: 20 min de lectura

Cada rol lee solo lo que necesita. No hay que leer todo.

---

## Lo que NO es NexusAgile

- **No es un reemplazo de Scrum** — es una extension que agrega agentes AI al proceso
- **No es un prompt** — es una metodologia completa con 25+ documentos de referencia
- **No es dependiente de Claude** — la metodologia es LLM-agnostic, pero esta optimizada y testeada con Claude Code
- **No es rigido** — tiene 3 modos (FAST/LAUNCH/QUALITY) para adaptar la ceremonia a la complejidad real
- **No es solo para devs** — POs, QA Leads y Scrum Masters tienen roles definidos

---

## Metricas: lo que mide NexusAgile

| Metrica | Que responde | Target |
|---------|-------------|--------|
| Lead Time | Cuanto tarda una HU de inicio a fin? | <3 dias (FAST), <1 semana (QUALITY) |
| BLOQUEANTE Rate | Cuantas HUs tienen issues de seguridad? | Tendencia descendente |
| Drift Rate | El codigo implementado difiere del spec? | <10% |
| Bug Escape Rate | Cuantos bugs llegan a produccion? | 0 |
| Carry-over Rate | Cuantas HUs no se completan en el sprint? | <20% |
| Costo por HU | Cuantos tokens/USD por HU? | Baseline en sprint 1 |

Sprint 1 establece baseline. No hay targets hasta sprint 2. Las metricas son para mejorar el proceso, no para evaluar personas.

---

## La diferencia en numeros

Escenario real simulado: feature de favoritos (DB + API + UI + Auth)

| Sin NexusAgile | Con NexusAgile |
|----------------|----------------|
| Dev escribe codigo sin spec | SDD aprobado con exemplars del codebase real |
| PR sin estructura | PR con checklist, evidencia de AR, evidencia de QA |
| Review informal | Peer review + Adversarial Review + Drift Detection |
| "Funciona en mi maquina" | 6/6 ACs verificados con archivo:linea |
| 0 documentacion | work-item + sdd + story-file + validation + report |
| Bug descubierto en produccion | BLOQUEANTE detectado por AR antes del PR |

---

## Codigo abierto

NexusAgile Enterprise esta disponible en GitHub:

**https://github.com/ferrosasfp/nexus-agile-enterprise**

25 documentos de referencia. Casos de uso documentados. Listo para instalar.

El humano decide QUE. Los agentes deciden COMO. Los gates garantizan que nadie — ni humano ni AI — se salte el proceso.

---

*NexusAgile es stack-agnostic. Funciona con Next.js, Rails, Django, Laravel, Go, o cualquier otro stack. Lo unico que necesitas es Claude Code y una HU.*
