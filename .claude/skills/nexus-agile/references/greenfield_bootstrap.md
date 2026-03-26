# Greenfield Bootstrap — Proyectos Desde Cero

> El Bootstrap normal descubre un codebase existente. Este protocolo crea uno.
> Activar cuando: no hay package.json, no hay carpetas, no hay codigo.

---

## Cuando Aplica

El Architect detecta en F0 que:
- No existe package.json / Gemfile / requirements.txt / go.mod
- No hay estructura de carpetas (Glob retorna vacio o solo README)
- No hay archivos de codigo fuente

Si alguna de estas condiciones se cumple: usar Greenfield Bootstrap en lugar del Bootstrap normal.

---

## Paso 1: Capturar Decisiones de Stack

El AI pregunta al humano (max 5 preguntas):

1. Que tipo de aplicacion? (web app, API, CLI, mobile, etc.)
2. Que lenguaje/framework? (Next.js, Rails, Django, Express, etc.)
3. Base de datos? (PostgreSQL, MySQL, SQLite, Firestore, Supabase, ninguna)
4. Autenticacion? (OAuth, JWT, session, ninguna por ahora)
5. Hosting objetivo? (Vercel, Netlify, AWS, GCP, self-hosted)

Con estas respuestas, el AI genera project-context.md con:
- Stack definido (no descubierto)
- Patrones: los defaults del framework elegido
- Comandos: los estandar del framework
- Exemplars: "usar convenciones oficiales del framework hasta que exista codigo propio"

---

## Paso 2: Scaffold (Wave -1)

Antes de cualquier HU funcional, ejecutar el scaffold:

1. Inicializar proyecto con el CLI del framework (npx create-next-app, rails new, etc.)
2. Configurar linter (ESLint, RuboCop, Black, etc.)
3. Configurar testing framework (Jest, RSpec, pytest, etc.)
4. Configurar formatter (Prettier, etc.)
5. Primer commit: "chore: project scaffold"
6. Configurar branch protection si aplica

El scaffold NO es una HU. No genera SDD, Story File, ni entra en _INDEX.md. Es prerequisito del primer HU.

---

## Paso 3: Adaptar Anti-Alucinacion

Para el PRIMER HU despues del scaffold:

| Concepto | Adaptacion Greenfield |
|----------|----------------------|
| Codebase Grounding | Leer los archivos generados por el scaffold (layout, config, etc.) |
| Exemplar Pattern | Usar archivos del scaffold como exemplar. Si no hay equivalente, usar documentacion oficial del framework. |
| Constraint Directives | OBLIGATORIO: seguir convenciones del framework. PROHIBIDO: desviar de los defaults sin justificacion. |
| Context Map | Documentar que el proyecto es nuevo y que los patrones estan siendo establecidos. |

Para el SEGUNDO HU en adelante:
- Los archivos del primer HU se convierten en exemplars
- Codebase Grounding funciona normalmente
- El proyecto ya tiene patrones propios

---

## Reglas de Greenfield

1. **Stack se define, no se descubre** — El humano decide el stack. El AI no inventa uno.
2. **Scaffold es obligatorio** — No se implementa logica funcional sin un proyecto inicializado.
3. **Primer HU establece patrones** — El primer HU es especial: sus archivos se convierten en el standard para todo lo que sigue.
4. **Todas las dependencias son nuevas** — La regla "no agregar dependencias nuevas" no aplica para el primer HU. Aplica a partir del segundo.
5. **project-context.md se revisa** — Despues de generar, el TL (o el dev solo) DEBE revisar y confirmar antes del primer sprint.
