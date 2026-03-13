# Engram Protocol — NexusAgil (Implementación de referencia)

> **Opcional.** NexusAgil es agnóstico de herramientas de memoria.
> Este documento es la implementación de referencia usando Engram (Go binary + SQLite + MCP).
> Alternativas válidas: MEMORY.md manual, cualquier sistema MCP de memoria, claude-mem, etc.
> Requiere: engram instalado y MCP configurado (`engram mcp` en mcpServers).
> Repo: https://github.com/Gentleman-Programming/engram

---

## ¿Por qué Engram en NexusAgil?

Sin memoria persistente, cada sesión empieza desde cero:
- Se repiten los mismos errores de implementación
- Se olvidan decisiones arquitectónicas del sprint anterior
- Los patrones aprendidos en una HU no se aplican en la siguiente
- El Auto-Blindaje muere con la sesión

Con Engram, **el sistema mejora con cada HU procesada**.

---

## Integración por fase

### F0 — Inicio de sesión
```
ACCIÓN OBLIGATORIA al iniciar cualquier sesión NexusAgil:
mem_context  → cargar contexto de sesiones anteriores del proyecto
mem_search "[nombre-proyecto] architecture"  → recuperar decisiones arquitectónicas
mem_search "[nombre-proyecto] sprint [N]"  → contexto del sprint actual
```

### F1 — Discovery
Después de generar el Work Item, buscar memoria relevante:
```
mem_search "[dominio-de-la-HU]"  → aprendizajes anteriores en este dominio
```
Si hay memoria relevante: incluirla como "Lessons from Memory" en el Work Item.

### F2 — SDD
Después de generar el SDD y antes del gate:
```
mem_search "[patrones-usados]"  → verificar si hay errores conocidos con estos patrones
mem_search "[tablas-BD-usadas]"  → decisiones de schema anteriores
```

### F3 — Implementación (Auto-Blindaje → Engram)
Cuando Dev documenta Auto-Blindaje, TAMBIÉN guardar en Engram:
```
mem_save(
  title: "[proyecto] [tipo-error]: [descripción-corta]",
  type: "bug",
  content: "What: [qué falló] / Why: [por qué falló] / Where: [archivo:línea] / Learned: [lección]",
  topic_key: "bug/[slug-del-error]"  // upsert si el mismo bug aparece de nuevo
)
```

### AR — Adversarial Review
Guardar hallazgos BLOQUEANTE resueltos:
```
mem_save(
  title: "[proyecto] security: [descripción-hallazgo]",
  type: "decision",
  content: "What: [hallazgo] / Why: [por qué es crítico] / Where: [archivo] / Learned: [fix aplicado]",
  topic_key: "decision/security-[slug]"
)
```

### DONE — Cierre de HU
Guardar resumen de la HU completa:
```
mem_save(
  title: "[proyecto] HU-NNN: [título]",
  type: "session",
  content: "
    Goal: [objetivo de la HU en 1 oración]
    Accomplished: [qué se implementó]
    Files: [archivos clave creados/modificados]
    Patterns used: [patrones o exemplars aplicados]
    Lessons: [lecciones aprendidas, si hay]
    Auto-Blindaje: [errores encontrados y fixes]
  "
)
```

### Cierre de Sesión (SIEMPRE al terminar)
```
mem_session_summary → OBLIGATORIO. Sin esto, la próxima sesión empieza ciega.
```
El SM ejecuta este paso en la Retrospectiva del sprint.

---

## Formato What/Why/Where/Learned

Todo mem_save en NexusAgil sigue este formato estructurado:

| Campo | Qué incluir |
|-------|-------------|
| **What** | Qué se hizo / qué falló / qué se decidió |
| **Why** | Por qué se tomó esa decisión / por qué falló |
| **Where** | Archivo:línea, componente, o módulo afectado |
| **Learned** | La lección concreta aplicable a futuras HUs |

---

## Tipos de memoria en NexusAgil

| type | Cuándo usar |
|------|-------------|
| `bug` | Auto-Blindaje: error encontrado y fix aplicado |
| `decision` | Decisión arquitectónica o de diseño |
| `pattern` | Patrón de código descubierto/establecido en el proyecto |
| `session` | Resumen de HU completada (en DONE) |
| `discovery` | Algo inesperado encontrado en el codebase |

---

## Topic Keys — Evitar duplicados

Usar `topic_key` para temas evolutivos (la misma decisión que cambia con el tiempo):

```
architecture/[componente]    → decisiones de arquitectura del componente
pattern/[nombre-patrón]      → patrones de código establecidos
bug/[slug-del-error]         → errores recurrentes (se acumula en el mismo registro)
decision/[tema]              → decisiones de negocio o técnicas
```

Sin topic_key → cada save crea un registro nuevo (usar para eventos únicos como HUs).

---

## Búsqueda efectiva

```bash
# Al inicio de sesión
engram context [proyecto]        # contexto de sesiones recientes
engram search "[dominio]"        # buscar por área de código

# Durante el pipeline
engram search "auth middleware"  # buscar memorias sobre autenticación
engram search "supabase schema"  # decisiones de BD
engram search "error boundary"   # patrones de manejo de errores

# Progressive disclosure (no volcar todo)
1. mem_search → resultados compactos con IDs
2. mem_timeline [id] → contexto cronológico alrededor de esa memoria
3. mem_get_observation [id] → contenido completo si se necesita
```

---

## Reglas globales

1. **mem_context al inicio** — siempre, sin excepción
2. **mem_session_summary al cierre** — siempre, sin excepción. "Si lo omites, la próxima sesión empieza ciega."
3. **Auto-Blindaje → Engram** — cada error documentado en F3 va también a Engram
4. **topic_key para patrones** — evitar fragmentar la misma decisión en múltiples registros
5. **Progressive disclosure** — no usar mem_get_observation directamente; buscar primero, profundizar solo si es necesario
6. **No volcar todo** — Engram no es un log. Solo guardar lo que aporta valor a futuras HUs.
