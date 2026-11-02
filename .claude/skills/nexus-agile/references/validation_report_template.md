# Validation Report Template — NexusAgil

> QA genera este reporte en F4 (QA/Validacion).
> Combina: Drift Check + AC Verification + Quality Gates + AR Summary + CR Summary.
> Cada AC necesita evidencia concreta. "Se ve bien" no es evidencia.

---

## Cuando se genera

- **Fase**: F4 (QA/Validacion)
- **Quien lo genera**: QA (QA Engineer)
- **Donde se persiste**: `$NEXUS_ROOT/doc/sdd/NNN-titulo/validation.md`

---

## Template

```markdown
# Validacion — SDD #NNN: [titulo]

> Fecha: YYYY-MM-DD
> Validado por: QA

---

## 1. Drift Check

> Comparar lo implementado vs lo especificado en SDD/Story File.

| Dimension | Esperado | Real | Status |
|-----------|----------|------|--------|
| Archivos creados | N | N | OK/DRIFT |
| Archivos modificados | N | N | OK/DRIFT |
| Dependencias nuevas | [lista o "ninguna"] | [lista o "ninguna"] | OK/DRIFT |
| Archivos fuera de scope | 0 | N | OK/DRIFT |
| Patrones seguidos | [exemplars del Story File] | [que se uso realmente] | OK/DRIFT |

### Drift justificado (si aplica)
| Dimension | Justificacion |
|-----------|---------------|
| [dimension] | [por que se desvio y por que es aceptable] |

> DRIFT grave (archivos fuera de scope, dependencias no aprobadas): ALERTAR al humano.

## 2. Validacion de AC

> Cada AC del Work Item/SDD verificado con evidencia literal: comando + salida.

| # | AC | Resultado | Comando | Salida literal |
|---|----|-----------|---------|----------------|
| 1 | WHEN [trigger], THE [sistema] SHALL [accion] | PASS/FAIL/NO VERIFICABLE | `[comando corrido]` | `[lo relevante de la salida]` |

### Tipos de evidencia valida
- **Test corrido**: comando + nombre del test + resultado
- **Query**: consulta + filas devueltas
- **Llamada**: `curl` u otro comando + respuesta
- **Log**: linea literal + donde se obtuvo

### Tipos de evidencia NO valida
- "Se ve bien"
- "Deberia funcionar"
- "Es el mismo patron que X"
- Una cita `archivo:linea` sola: ubica el codigo, pero no dice que hace cuando corre
- Sin evidencia

Si no se puede ejecutar, el AC va **NO VERIFICABLE** con su motivo y el paso manual para el humano.

## 3. Quality Gates

> Correr UNA vez el comando unico de gate de `project-context.md`. No correr sus partes por separado.

| Gate | Comando | Exit code | Ultimas lineas de salida |
|------|---------|-----------|--------------------------|
| Gate del repo | [comando unico] | [codigo] | [salida literal] |

## 3b. Entorno de validacion

| Dato | Valor |
|------|-------|
| Entorno usado | [segun project-context.md] |
| Migraciones | [corridas en entorno / NO VERIFICABLE hasta ventana manual, con comando] |

## 4. Adversarial Review Summary

> Resumen del AR de Adversary (referencia completa en el reporte AR).

| Resultado AR | Hallazgos BLOQUEANTE | Hallazgos MENOR | Status |
|-------------|---------------------|-----------------|--------|
| APROBADO/APROBADO con MENORs/RECHAZADO | N | N | Resuelto/Pendiente |

### BLOQUEANTE resueltos (si hubo)
| # | Hallazgo | Fix aplicado | Verificado |
|---|----------|-------------|------------|
| 1 | [hallazgo] | [fix] | Si/No |

## 5. Code Review Summary

> Resumen del CR de Adversary.

| Resultado CR | Status |
|-------------|--------|
| APROBADO/APROBADO con MENORs/RECHAZADO | [estado] |

### Cambios solicitados (si hubo)
| # | Cambio | Aplicado | Verificado |
|---|--------|----------|------------|
| 1 | [cambio] | Si/No | Si/No |

## 6. Auto-Blindaje Acumulado

> Errores encontrados durante todo el pipeline (copiados de F3).

| Fase/Wave | Error | Fix | Aplicar en |
|-----------|-------|-----|-----------|
| [fase] | [que fallo] | [como se arreglo] | [donde mas aplica] |

> "Pipeline limpio" si no hubo errores.

## 7. Veredicto Global

| Criterio | Status |
|----------|--------|
| Todos los ACs PASS | Si/No |
| Gate del repo PASS | Si/No |
| AR resuelto | Si/No |
| CR aprobado | Si/No |
| Sin drift grave | Si/No |

### Resultado

- **PASS** — Todos los criterios cumplidos. Avanzar a DONE.
- **FAIL** — [criterios que fallaron]. Volver a F3 para corregir.

---

*Validacion generada por NexusAgil — F4*
```

---

## Reglas de Validacion

1. **Evidencia literal obligatoria**: Cada AC debe mostrar comando y salida. QA no puede marcar PASS sin eso.
2. **ACs no verificables**: Van NO VERIFICABLE, con la verificacion manual paso a paso para el humano.
3. **Drift grave es bloqueante**: Archivos fuera de scope o dependencias no aprobadas requieren aprobacion del humano.
4. **Gate del proyecto**: Usar el comando unico definido en `project-context.md`, no defaults.
5. **AR integrado**: El reporte de validacion incluye resumen del AR, no lo reemplaza.
6. **FAIL = volver a F3**: QA no "aprueba con reservas". Si falla, se corrige.
7. **Auto-Blindaje copiado**: Los errores de F3 se copian tal cual, no se reconstruyen de memoria.
