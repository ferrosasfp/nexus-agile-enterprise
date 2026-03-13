# Skills Router — NexusAgil

> Router liviano que carga solo las skills relevantes según el tipo de tarea.
> Evita el "context bloat" de cargar 1000+ líneas cuando solo se necesitan 200.
> Compatible con skills de clawhub.com / skills.sh y skills propias del proyecto.

---

## El Problema que Resuelve

Sin router → AGENTS.md monolítico de 1000+ líneas cargado en CADA turno:
- El agente carga Angular skills aunque la HU sea de testing
- Context window desperdiciada en instrucciones irrelevantes
- Compactación temprana → alucinaciones

Con router → Carga SELECTIVA por tipo de tarea:
- HU de frontend React → carga solo skill de frontend
- HU de DB/Supabase → carga solo skill de base de datos
- HU de contratos Solidity → carga solo skill de Web3

---

## Cómo funciona

El Architect ejecuta el router en F0 después del Smart Sizing:

```
1. Leer señales de la HU (keywords, archivos afectados, dominio)
2. Seleccionar 1-2 skills relevantes del registro del proyecto
3. Cargar SOLO esas skills antes de proceder al SDD
4. El resto del pipeline corre con contexto limpio
```

---

## Señales de detección

| Señal en la HU | Skill a cargar |
|----------------|----------------|
| componente, UI, frontend, React, Vue, CSS, layout | skill-frontend |
| base de datos, tabla, schema, migración, query, Supabase, Prisma | skill-database |
| auth, autenticación, login, JWT, sesión, permisos | skill-auth |
| contrato, Solidity, blockchain, Web3, wallet, USDC | skill-web3 |
| API, endpoint, route, REST, middleware | skill-backend |
| test, testing, spec, coverage, QA | skill-testing |
| deploy, CI/CD, build, Docker, Vercel | skill-devops |
| performance, optimización, lighthouse, cache | skill-performance |

---

## Estructura de una skill del proyecto

```
.claude/skills/
├── nexus-agile/          ← metodología (siempre cargada)
│   ├── SKILL.md
│   └── references/
├── skill-frontend/       ← skill de dominio (carga selectiva)
│   └── SKILL.md
├── skill-database/
│   └── SKILL.md
├── skill-web3/
│   └── SKILL.md
└── skill-auth/
    └── SKILL.md
```

---

## Plantilla para crear una skill de proyecto

```markdown
---
name: skill-[dominio]
description: >
  [Descripción de cuándo usar esta skill — máx 2 líneas]
  Activar cuando: [señales que la activan]
---

# [Dominio] — Reglas y Patrones

## Stack
- Framework: [X]
- Librerías clave: [Y, Z]
- Archivos de referencia: [paths]

## Patrones establecidos
[extracto real del proyecto]

## OBLIGATORIO
- [regla 1]
- [regla 2]

## PROHIBIDO
- [restricción 1]
- [restricción 2]

## Exemplar canónico
[archivo de referencia del proyecto a seguir siempre]
```

Máximo 200 líneas por skill. Si supera ese límite, dividir en 2 skills más específicas.

---

## Skills externas recomendadas

Recursos para skills de dominio listas para usar:
- **clawhub.com** — marketplace de skills para OpenClaw/Claude Code
- **skills.sh** — registry de skills agnostícas de stack

Antes de crear una skill desde cero, buscar si ya existe una para el dominio.

---

## Integración con NexusAgil

El router se ejecuta en **F0, paso 4** (después del Smart Sizing):

```
F0 checklist (actualizado):
1. Verificar project-context.md
2. Codebase Grounding inicial
3. Leer _INDEX.md
4. Smart Sizing → determinar SDD_MODE
5. 🆕 Skills Router → cargar skills relevantes para esta HU
6. Si SDD_MODE = patch → Triage. Si no → F1.
```

El Architect declara explícitamente qué skills cargó:
```
Skills cargadas para esta HU:
- nexus-agile/SKILL.md (siempre)
- skill-frontend/SKILL.md (señal: componente React)
```

---

## Reglas del router

1. **NexusAgile siempre** — la metodología base nunca se omite
2. **Máximo 2 skills adicionales** — más de 2 = señal de que la HU es demasiado grande (dividir)
3. **Declarar siempre** — el Architect lista las skills cargadas en F0
4. **No cargar por precaución** — si no hay señal clara, no cargar la skill
5. **Revisar en F1** — si la HU resulta ser de otro dominio, actualizar el skill cargado antes de F2
