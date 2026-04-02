# Quality Pipeline — NexusAgil

> Pipeline completo para features en produccion (DB, auth, pagos, usuarios reales).
> Activar con: "NexusAgil, procesa esta HU: [descripcion]"
> Este documento contiene el proceso detallado de cada fase. SKILL.md contiene principios, gates y reglas globales.

---

## F0: Contexto

**Agentes**: Analyst (requisitos) + Architect (arquitectura)
**Objetivo**: Establecer contexto del proyecto y del codebase antes de procesar la HU.

### ⚠️ PASO 0 — OBLIGATORIO ANTES DE TODO (Anti-Drift)

> **El orquestador y cada sub-agente deben leer `project-context.md` como PRIMER acto, antes de leer el codebase, antes de hacer cualquier análisis.**
> Violar este paso es el error más costoso del pipeline — lleva a implementar con el stack incorrecto.

Buscar en este orden hasta encontrar:
1. `.nexus/project-context.md` (ubicación preferida)
2. `project-context.md` (raíz del proyecto)
3. `docs/project-context.md`

**Si existe:** leer COMPLETO antes de continuar. El `project-context.md` define:
- Stack inmutable (framework, DB, librerías) — **NUNCA asumir el stack del código si difiere del project-context**
- Reglas absolutas (Golden Path) — inviolables
- Patrones y convenciones del proyecto

**Si NO existe:** ejecutar Bootstrap de Proyecto (ver sección siguiente) antes de continuar.

**Regla anti-drift:** Si el código existente usa un framework/librería diferente al definido en `project-context.md`, reportar el drift al humano ANTES de continuar. No asumir que el código es la fuente de verdad.

### Proceso

1. **Leer `project-context.md`** (ver Paso 0 arriba — BLOQUEANTE)
2. **Codebase Grounding inicial**: Explorar la estructura del proyecto con Glob/Grep
3. **Leer `doc/sdd/_INDEX.md`** para siguiente NNN. Si no existe, crearlo.
4. **Smart Sizing** — Clasificar la HU:

| Tipo | Senales | SDD_MODE |
|------|---------|----------|
| **Trivial** | 1-2 archivos, <30 lineas, sin BD, sin logica nueva | **patch** → Quick Flow (Triage) |
| **Hotfix** | Bug en produccion, causa raiz desconocida, puede tocar auth/datos | **hotfix** → Hotfix Pipeline (Dev) |
| **Bugfix** | Bug confirmado con repro steps | **bugfix** |
| **Tech-task / refactor** | Sin cambio funcional visible | **mini** |
| **Feature / improvement** con logica | Multiples archivos, posiblemente BD | **full** |

5. Si SDD_MODE = **patch** → Derivar a Triage (Quick Flow). Ver `references/quick_flow.md`.
6. Si no es patch → Continuar a F1.

### Bootstrap de Proyecto (solo cuando NO existe project-context.md)

NexusAgil es stack-agnostic. No asume ningun framework ni lenguaje.
Si no hay project-context.md, el Architect descubre el proyecto leyendo el codebase real.

Checklist de descubrimiento (leer en orden):

1. Archivo de dependencias: package.json / Gemfile / requirements.txt / go.mod / pom.xml
   Extraer: lenguaje principal, framework, dependencias clave

2. Estructura de carpetas (Glob recursivo desde raiz, profundidad 3)
   Identificar: arquitectura (MVC, feature-first, monorepo, microservicios, etc.)

3. 3-5 archivos representativos del area de negocio principal
   Extraer: naming conventions, patron de imports, estructura de funciones, manejo de errores

4. Comandos del proyecto: build, test, lint, dev server
   Fuente: scripts en package.json, Makefile, README, o equivalente del stack

5. Base de datos y ORM si existe
   Fuente: schema files, migraciones, cliente (Supabase, Prisma, ActiveRecord, SQLAlchemy...)

6. Sistema de auth si existe
   Fuente: middleware, guards, JWT config, sessions config

7. Guardrails del proyecto si existen
   Fuente: .eslintrc, .rubocop.yml, linters, convenciones en README

Despues del checklist: generar project-context.md usando references/project_context_template.md
como base, llenado exclusivamente con lo descubierto. Escribir al disco antes de continuar.

Confirmar al humano: "Contexto generado. Stack: X. Arquitectura: Y. Comandos: Z. Listo para HUs."
Si hay ambiguedades criticas: preguntar al humano (max 3 preguntas) antes de continuar.

---

## F1: Discovery

**Agentes**: Analyst (requisitos) + Architect (arquitectura) + UX (si aplica)
**Objetivo**: Transformar cualquier input en un Work Item estructurado con ACs EARS.

### Proceso

1. **Leer la HU** tal como viene (texto libre, bullets, imagenes, mezcla)
2. **Asignar numero secuencial** desde `doc/sdd/_INDEX.md`
3. **Si hay imagenes**: producir "Image Notes" (3-6 bullets)
4. **Analyst extrae y normaliza** el Work Item:

```markdown
## Work Item #NNN

| Campo | Valor |
|-------|-------|
| **#** | NNN |
| **Tipo** | feature / bugfix / tech-task / refactor / improvement |
| **SDD_MODE** | full / bugfix / mini |
| **Objetivo** | 1-2 oraciones |
| **Actual vs Esperado** | Solo para bugs |
| **Reglas de negocio** | Restricciones |
| **Acceptance Criteria** | Formato EARS (ver abajo) |
| **Scope IN** | Que SI incluye |
| **Scope OUT** | Que NO incluye |
| **Missing Inputs** | Recursos pendientes |
```

### Acceptance Criteria — Formato EARS

| Patron | Formato | Ejemplo |
|--------|---------|---------|
| **Event-Driven** | WHEN [trigger], THE [sistema] SHALL [accion] | WHEN usuario aplica filtro, THE lista SHALL mostrar solo items que coincidan |
| **State-Driven** | WHILE [condicion], THE [sistema] SHALL [comportamiento] | WHILE no hay resultados, THE pagina SHALL mostrar estado vacio |
| **Unwanted** | IF [condicion no deseada], THEN THE [sistema] SHALL [respuesta] | IF usuario no autenticado accede a /admin, THEN THE app SHALL redirigir a /login |

Cada AC debe ser verificable con una accion concreta. Si no se puede verificar, no es un AC valido.

### UX — Solo si Work Kind involucra UI
- Microcopy obligatorio para elementos interactivos
- Flujos de usuario para happy path y error
- Accesibilidad basica (aria-labels, contraste, keyboard nav)

### Definition of Ready (DoR)

NO avanzar a GATE 1 sin:
- Objetivo definido (1-2 oraciones)
- Minimo 2 ACs en formato EARS
- Scope IN y OUT (derivarlos si el usuario no los da)

**Max 3 preguntas.** Si no se cumple DoR despues de preguntar: informar y NO avanzar.

### Branch Semantico
```
feat/NNN-titulo-kebab
fix/NNN-titulo-kebab
refactor/NNN-titulo-kebab
```
Preguntar: "Creo branch `{branch}`? (si/no/otro nombre)"

### Analisis de Dependencias y Paralelismo (cuando hay multiples HUs en el sprint)

Despues de presentar todos los Work Items del sprint, el Architect analiza y presenta:

```markdown
## Propuesta de ejecucion — Sprint N

### HUs en paralelo (dominios independientes, sin conflictos de archivos)
- WAS-XX: [titulo]
- WAS-YY: [titulo]

### HUs en secuencia (dependencias o conflictos)
- WAS-ZZ: [titulo] → depende de WAS-XX porque [razon]

### Orden propuesto
1. Paralelo: WAS-XX + WAS-YY (F2 simultaneo)
2. Secuencial: WAS-ZZ (despues de WAS-XX)
```

**El humano aprueba los Work Items Y el orden de ejecucion con un solo `HU_APPROVED`.**
Si el humano modifica el orden, el Architect actualiza la propuesta antes de continuar a F2.

### GATE 1: HU_APPROVED
Presentar Work Item al humano. Esperar el texto exacto **HU_APPROVED**.
- Solo el texto exacto `HU_APPROVED` activa el gate.
- "ok", "dale", "si", "go", "avanza", "suena bien", "HU_APPROVED: yes" → NO activan el gate.
- NO avanzar sin el texto exacto.

### Persistencia F1
Escribir en `doc/sdd/NNN-titulo/work-item.md`.

---

## F2: Spec / SDD

**Agentes**: Architect + Adversary (revision de seguridad)
**Objetivo**: Generar SDD con codebase grounding. NO se escribe codigo.

### Fase 1: Codebase Grounding (OBLIGATORIO)

1. **Leer archivos de referencia** del proyecto (`project-context.md`, guardrails)
2. **Buscar archivos relacionados** con la HU (Glob/Grep, 2-3 minimo)
3. **Identificar exemplars** — archivos mas similares a lo que se va a crear/modificar
4. **Documentar en Context Map**:

```markdown
## Context Map (Codebase Grounding)

### Archivos leidos
| Archivo | Por que | Patron extraido |
|---------|---------|-----------------|
| `[path]` | [razon] | [patron: imports, estructura, naming] |

### Exemplars
| Para crear/modificar | Seguir patron de | Razon |
|---------------------|------------------|-------|
| [nuevo archivo] | `[exemplar]` | [que patron copiar] |

### Estado de BD relevante (si aplica)
| Tabla | Existe | Columnas relevantes |
|-------|--------|---------------------|
| [tabla] | Si/No | [columnas] |

### Componentes reutilizables encontrados
- [Componente] en [ubicacion] — reutilizar en vez de crear nuevo
```

### Fase 2: Generar SDD

Seleccionar template segun SDD_MODE. Consultar `references/sdd_template.md`.

| SDD_MODE | Template | Cuando |
|----------|----------|--------|
| **full** | FULL | feature/improvement con logica |
| **bugfix** | BUGFIX | bugs con repro steps |
| **mini** | MINI | tech-task, refactor |

### Fase 3: Constraint Directives

```markdown
## Constraint Directives (Anti-Alucinacion)

### OBLIGATORIO seguir
- Patron de [tipo]: seguir `[exemplar]`
- Imports: solo modulos que EXISTEN en el proyecto

### PROHIBIDO
- NO agregar dependencias nuevas salvo que el SDD lo especifique
- NO crear patrones diferentes a los existentes
- NO modificar archivos fuera de Scope IN
- [constraints especificos de esta HU]
```

### Uncertainty Markers

| Marker | Significado | Gate |
|--------|-------------|------|
| `[NEEDS CLARIFICATION]` | Decision humana requerida | **Bloqueante** |
| `[TBD]` | Resoluble explorando codebase | **No bloqueante** |

### Implementation Readiness Check

Antes de presentar el SDD al humano, Architect verifica:

```
READINESS CHECK:
[ ] Cada AC tiene al menos 1 archivo asociado en la tabla de archivos
[ ] Cada archivo tiene un Exemplar valido (verificado con Glob)
[ ] No hay [NEEDS CLARIFICATION] pendientes
[ ] Constraint Directives incluyen al menos 3 PROHIBIDO
[ ] Context Map tiene al menos 2 archivos leidos
[ ] Scope IN y OUT son explicitos
[ ] Si hay BD: tablas verificadas
```

Si falla cualquier check: corregir antes de presentar.

### GATE 2: SPEC_APPROVED
Presentar SDD al humano. Esperar el texto exacto **SPEC_APPROVED**.
- Solo el texto exacto `SPEC_APPROVED` activa el gate.
- Con `[NEEDS CLARIFICATION]`: informar que debe resolverlos primero.
- NO avanzar sin el texto exacto.

### Persistencia F2
Escribir en `doc/sdd/NNN-titulo/sdd.md`.

---

## F2.5: Story File

**Agente**: Architect
**Objetivo**: Generar un contrato autocontenido para que Dev pueda implementar SIN consultar otros artefactos.

> Template completo en `references/story_file_template.md`.

El Story File es el **unico documento que Dev lee**. Contiene todo lo necesario:

1. **Goal** — Que se construye y por que (1-2 oraciones)
2. **Acceptance Criteria** — EARS format, copiados del SDD
3. **Files to Modify/Create** — Tabla con paths, acciones, exemplars
4. **Exemplars** — Codigo real extraido de los archivos de referencia
5. **Constraint Directives** — OBLIGATORIO/PROHIBIDO copiados del SDD
6. **Test Expectations** — Que tests crear, que ACs cubren
7. **Waves** — Orden de ejecucion (W0 serial, W1+ paralelo)
8. **Out of Scope** — Que NO tocar
9. **Escalation Rule** — Si algo no esta en el Story File, Dev PARA y pregunta a Architect

### Regla Critica
Dev **NUNCA** lee el SDD ni el Work Item. Solo el Story File. Si el Story File es ambiguo, Dev escala a Architect — no inventa.

### Persistencia F2.5
Escribir en `doc/sdd/NNN-titulo/story-file.md`.

---

## F3: Implementacion

**Agente**: Dev
**Objetivo**: Implementar SOLO lo que dice el Story File, con waves y anti-hallucination.

### Reglas de Implementacion

1. **Solo lo que esta en el Story File** — nada mas, nada menos
2. **Respetar scope** — Scope OUT es inviolable
3. **Respetar el stack** — Segun `project-context.md` del proyecto
4. **Cambios minimos** — No refactorizar codigo adyacente
5. **Trazabilidad** — Cada cambio corresponde a un item del Story File
6. **Escalation** — Si algo no esta claro, PARAR y preguntar a Architect

### Anti-Hallucination Protocol (ANTES de cada tarea)

```
CHECKLIST PRE-IMPLEMENTACION (por tarea):
[ ] Lei el archivo exemplar referenciado en el Story File
[ ] Verifique que los imports que voy a usar EXISTEN (Grep/Glob)
[ ] Sigo el patron del exemplar (estructura, naming, exports)
[ ] No estoy agregando dependencias no aprobadas
[ ] El archivo resultante respeta los limites del proyecto
```

Este checklist es una instruccion interna. NO se presenta al usuario.

### Re-mapeo Ligero entre Waves

**ANTES de iniciar cada Wave (excepto W0)**, Dev DEBE:
1. Leer los archivos que el Wave anterior **creo o modifico**
2. Verificar que los imports/exports que el Wave actual necesita **existen realmente**
3. Si algo difiere: ajustar sin salirse del Story File

### Proceso por Wave

**Wave 0 (Serial):**
1. Ejecutar tareas secuencialmente
2. Verificar typecheck/build al completar

**Wave 1+ (Parallelizable):**
1. **Re-mapeo ligero**: leer archivos creados/modificados en Wave anterior
2. Lanzar tareas en paralelo si el juicio lo indica
3. Cada tarea recibe: objetivo + exemplar + constraint directives

**Para cada tarea:**
```
1. LEER el exemplar referenciado
2. Si hay test-first:
   a. Crear test stub
   b. Implementar codigo para que el test pase
   c. Verificar: typecheck + test
3. Si NO hay test (copy, estilos):
   a. Implementar directamente
   b. Verificar typecheck
4. Marcar tarea como completada
```

### Verificacion Incremental

Al completar CADA wave (no solo al final):

| Wave completada | Verificacion |
|-----------------|-------------|
| W0 | typecheck pasa |
| W1 | typecheck + tests pasan |
| W2 | typecheck + tests + visual (si UI) |
| W3 (ultima) | full QA (typecheck + lint + build) |

Si falla: corregir ANTES de avanzar. Auto-Blindaje si el error es nuevo.

### Auto-Blindaje en el Momento

Si hay errores durante implementacion:
1. **Arreglar** el codigo
2. **Verificar** que funcione
3. **Documentar INMEDIATAMENTE**:
   ```
   ## Auto-Blindaje (acumulativo)
   | Wave | Error | Fix | Aplicar en |
   |------|-------|-----|-----------|
   | W0.2 | [que fallo] | [como se arreglo] | [donde mas aplica] |
   ```
4. **Continuar** con la siguiente tarea

---

## Adversarial Review (AR)

**Agente**: Adversary
**Objetivo**: Atacar la solucion implementada buscando fallas ANTES de validar.

> Checklist completo en `references/adversarial_review_checklist.md`.

### Proceso

1. Adversary revisa TODO el codigo generado en F3
2. Ejecuta checklist de 8 categorias de ataque
3. Clasifica hallazgos:

| Severidad | Significado | Accion |
|-----------|-------------|--------|
| **BLOQUEANTE** | Falla critica de seguridad, datos o logica | Dev DEBE corregir antes de continuar |
| **MENOR** | Mejora recomendada, no critica | Documentar, corregir si es rapido |
| **OK** | Sin hallazgos en esta categoria | Continuar |

### Regla
- El AR es **BLOQUEANTE**: si hay hallazgos BLOQUEANTE, Dev corrige y Adversary re-revisa.
- Solo cuando todo es OK o MENOR se avanza a Code Review.

---

## Code Review (CR)

**Agentes**: Adversary (seguridad) + QA (calidad)
**Objetivo**: Revisar calidad de codigo, separado del Adversarial Review.

### Checks

1. **Patrones** — Se siguieron los exemplars del Story File?
2. **Naming** — Consistente con convenciones del proyecto?
3. **Complejidad** — Funciones cortas, responsabilidad unica?
4. **Duplicacion** — Hay codigo duplicado que deberia reutilizarse?
5. **Imports** — Solo dependencias aprobadas?
6. **Limites** — Archivos dentro del limite de lineas del proyecto?

### Resultado
- **APPROVED** — Codigo listo para validacion
- **CHANGES_REQUESTED** — Dev corrige, Adversary+QA re-revisan

---

## F4: QA / Validacion

**Agente**: QA
**Objetivo**: Verificar ACs con evidencia, detectar drift, ejecutar quality gates.

> Template completo en `references/validation_report_template.md`.

### Fase 1: Drift Detection

Comparar lo implementado vs lo planificado:

```markdown
## Drift Check
| Dimension | Esperado | Real | Status |
|-----------|----------|------|--------|
| Archivos creados | N | N | OK/DRIFT |
| Archivos modificados | N | N | OK/DRIFT |
| Dependencias nuevas | [lista] | [lista] | OK/DRIFT |
| Archivos fuera de scope | 0 | N | OK/DRIFT |
```

Si hay DRIFT grave: alertar al humano.

### Fase 2: Verificacion de ACs

```markdown
| AC | Resultado | Evidencia | Test | Metodo |
|----|-----------|-----------|------|--------|
| AC1: WHEN... SHALL... | PASS/FAIL | [archivo:linea] | [test o N/A] | auto/manual |
```

Cada AC con evidencia concreta citando `archivo:linea` — no "se ve bien".

**Formato obligatorio de evidencia:**
- `CUMPLE` — `src/components/X.tsx:42` (implementado y verificado)
- `NO CUMPLE` — no encontrado en codebase
- `PARCIAL` — `src/components/X.tsx:42` (implementado pero sin test)

QA no puede marcar CUMPLE sin citar `archivo:linea` como evidencia.

### Fase 3: Quality Gates

Ejecutar los comandos definidos en `project-context.md` del proyecto:
- typecheck
- tests
- build (si cambios significativos)
- lint

### Fase 4: Si hay FAIL
- Volver a F3 para corregir
- Re-ejecutar validacion
- Auto-Blindaje si el error es nuevo

### Persistencia F4
Escribir en `doc/sdd/NNN-titulo/validation.md`.

---

## F5: Release Gate (opcional por proyecto)

**Agente**: QA + Docs
**Objetivo**: Verificar que el codigo aprobado en F4 esta listo para produccion.
**Gate**: RELEASE_APPROVED (TL + PO)

> **Cuando aplica**: Proyectos que deployean a produccion (apps web, APIs, servicios).
> **Cuando NO aplica**: Librerias, paquetes, skills, herramientas internas sin deploy. Configurar en `project-context.md` con `release_gate: false`.
> **Default**: Si `project-context.md` no lo especifica, F5 aplica.

### Pre-Release Checklist

El AI genera el checklist automaticamente. El humano (TL + PO) verifica y aprueba.

```
PRE-RELEASE CHECKLIST — HU-NNN

## Staging
[ ] Codigo deployeado en staging/preview
[ ] Smoke test en staging exitoso (flujo principal funciona)
[ ] No hay errores nuevos en logs de staging

## Migraciones
[ ] Sin migraciones: N/A
[ ] Con migraciones: migration aplicada en staging sin errores
[ ] Con migraciones: migration es reversible (down migration existe)
[ ] Con migraciones: datos existentes no se corrompen post-migration

## Variables de entorno
[ ] Sin env vars nuevas: N/A
[ ] Con env vars nuevas: configuradas en TODOS los entornos (staging + prod)
[ ] Con env vars nuevas: documentadas en project-context.md o .env.example
[ ] Secrets no estan hardcodeados ni en el repo

## Dependencias
[ ] Sin deps nuevas: N/A
[ ] Con deps nuevas: licencia compatible
[ ] Con deps nuevas: version pinneada (no latest/*)
[ ] Con deps nuevas: no hay vulnerabilidades conocidas (npm audit / pip audit)

## Rollback
[ ] Plan de rollback definido: [revert commit / feature flag off / migration down]
[ ] Rollback testeado o trivial (revert de un commit)

## Contratos / Integraciones
[ ] Sin cambios de API publica: N/A
[ ] Con cambios de API: backward compatible o versionado
[ ] Con cambios de API: consumidores notificados
[ ] Servicios externos (payments, email, auth providers): testeados en staging

## Comunicacion
[ ] Changelog entry preparado (si aplica)
[ ] Stakeholders notificados del deploy (si aplica)
```

### Proceso F5

1. AI genera el Pre-Release Checklist con items aplicables (marca N/A los que no aplican)
2. AI verifica automaticamente lo que puede (env vars en repo, deps audit, migration files)
3. AI presenta checklist al humano con items pendientes de verificacion manual
4. Humano (TL) verifica staging, migraciones, rollback
5. Humano (PO) confirma que la feature en staging es lo esperado
6. Ambos escriben: **RELEASE_APPROVED**
7. Pipeline avanza a DONE

### Si F5 falla

| Problema | Accion |
|----------|--------|
| Staging roto | Volver a F3 — fix + re-deploy staging |
| Migration falla en staging | Volver a F3 — fix migration |
| Env var faltante | Configurar env var — no requiere volver a F3 |
| Rollback no viable | TL decide: agregar rollback plan o aceptar riesgo (documentado) |
| PO no aprueba en staging | Volver a F3 con feedback especifico del PO |

### Persistencia F5

Agregar al `doc/sdd/NNN-titulo/report.md`:
```markdown
## Release Gate
- Checklist: [PASS/FAIL por item]
- Aprobado por: [TL] + [PO]
- Fecha: YYYY-MM-DD
- Entorno verificado: [staging URL]
```

---

## Build + Push + DONE

**Agente**: Docs
**Objetivo**: Cerrar el pipeline y documentar.

### Proceso

1. Compilar reporte final con:
   - Resumen de archivos creados/modificados
   - AC status (todos PASS)
   - Drift summary
   - AR/CR summary
   - Auto-Blindaje acumulado
   - **Release Gate status** (si F5 aplica)
2. Escribir en `doc/sdd/NNN-titulo/report.md`
3. Actualizar `doc/sdd/_INDEX.md` con status DONE
4. Cerrar en el issue tracker del proyecto (Linear, GitHub Issues, Jira, o el configurado en `project-context.md`) — mover el issue a Done/Closed
5. Presentar resumen al humano

### Abort
Si el humano aborta en cualquier punto: Docs actualiza _INDEX.md con status ABORTED y cierra el issue en el tracker como CANCELLED.
