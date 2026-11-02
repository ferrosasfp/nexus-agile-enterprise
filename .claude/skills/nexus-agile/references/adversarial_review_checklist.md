# Adversarial Review Checklist — NexusAgil

> Detalle de las **12 categorias** de ataque del agente `nexus-adversary`, que se ejecutan despues de F3.
> Severidades: BLQ-ALTO / BLQ-MED / BLQ-BAJO (cualquiera bloquea el gate) / MENOR / OK / N/A.
> Una categoria que no aplica se marca N/A con una linea. Nunca se omite.

---

## Cuando se ejecuta

- **Fase**: Adversarial Review (AR), despues de F3
- **Quien lo ejecuta**: Adversary
- **Quien corrige**: Dev
- **Bloqueante**: Con cualquier BLQ, Dev corrige y Adversary re-revisa

---

## Categorias de Ataque

### 1. Security

| Area | Que buscar | Severidad si falla |
|------|-----------|-------------------|
| AuthN/AuthZ | Rutas publicas que deberian ser privadas; acciones o APIs sin verificar sesion | BLQ |
| Roles | Acceso a datos de otros usuarios; escalada de privilegios | BLQ |
| Sesiones | Sesiones sin expiracion, tokens en localStorage | MENOR |
| Inputs | Formularios sin validacion server-side; uploads sin validar tipo o tamano | BLQ |
| Inputs | Tipos asumidos sin validar, strings sin limite | MENOR |
| Inyeccion | SQL por concatenacion, XSS, command injection, path traversal | BLQ |
| Secretos | Keys en el codigo o en logs; env vars de servidor expuestas al cliente | BLQ |
| Configuracion | Defaults inseguros (CORS abierto, debug en prod) | MENOR |
| Datos | PII visible donde no deberia | BLQ |
| Datos | APIs que devuelven de mas; errores verbosos; IDs enumerables | MENOR |
| BD | Tablas nuevas sin RLS si el stack lo soporta; operaciones sin verificar ownership | BLQ |

**Preguntas de ataque**: ¿Puede un usuario no autenticado llegar aca? ¿Puede ver o modificar datos de otro? ¿Que pasa con un string donde se espera un numero, un payload de 10MB o unicode? ¿Algun input termina concatenado en una query, un comando o un path?

### 2. Error Handling

| Que buscar | Severidad si falla |
|-----------|-------------------|
| Errores silenciados o fallbacks que esconden una falla critica | BLQ |
| Try/catch incompleto en caminos de dinero, identidad o datos | BLQ |
| Mensajes confusos o falta de log en caminos no criticos | MENOR |

### 3. Data Integrity

| Que buscar | Severidad si falla |
|-----------|-------------------|
| Operaciones no atomicas que pueden dejar datos corruptos | BLQ |
| Escrituras concurrentes sin control; duplicados en operaciones que deben ser idempotentes | BLQ si afecta datos, si no MENOR |
| Double-submit; endpoints publicos sin rate limit | MENOR |

**Preguntas de ataque**: ¿Que pasa con dos clicks rapidos? ¿Y con dos usuarios a la vez?

### 4. Performance

| Que buscar | Severidad si falla |
|-----------|-------------------|
| N+1 o full table scan en un camino comun, con impacto demostrable | BLQ |
| Indices faltantes, loops innecesarios, operaciones bloqueantes de menor impacto | MENOR |

### 5. Integration

| Que buscar | Severidad si falla |
|-----------|-------------------|
| Contratos rotos o breaking changes sin versionar | BLQ |
| Datos de prueba que pueden llegar a produccion | BLQ |
| URLs de desarrollo o valores magicos sin parametrizar | MENOR |

### 6. Type Safety

| Que buscar | Severidad si falla |
|-----------|-------------------|
| Casting o `any` que esconde un bug reproducible; NaN o null que se propagan a datos | BLQ |
| `any` injustificado sin bug demostrable | MENOR |

### 7. Test Coverage

| Que buscar | Severidad si falla |
|-----------|-------------------|
| AC sin test, o un test que no puede fallar | BLQ |
| Camino de dinero, identidad o permisos sin caso negativo | BLQ |
| Asserts vagos o edge cases raros sin cubrir | MENOR |

### 8. Scope Drift

| Que buscar | Severidad si falla |
|-----------|-------------------|
| Archivos fuera de Scope IN o dependencias no aprobadas | BLQ |
| Refactors menores no pedidos | MENOR |

### 9. Destructive Migrations

| Que buscar | Severidad si falla |
|-----------|-------------------|
| `DROP`, `TRUNCATE` o cambio de tipo con perdida, sin respaldo ni rollback | BLQ-ALTO |
| `ADD COLUMN NOT NULL` sin default sobre filas existentes; `UPDATE` masivo mal acotado; rename sin compatibilidad | BLQ-MED si es reversible, si no BLQ-ALTO |
| Migracion sin transaccion | BLQ-MED |

### 10. RPC con SECURITY DEFINER

| Que buscar | Severidad si falla |
|-----------|-------------------|
| Sin `SET search_path` | BLQ-ALTO |
| Sin verificar ownership o identidad dentro de la funcion | BLQ-ALTO |
| SQL dinamico sin sanitizar | BLQ-ALTO |
| Expuesta sin GRANT restringido | BLQ |

### 11. Cache Invalidation Logic

| Que buscar | Severidad si falla |
|-----------|-------------------|
| Cache key sin `user_id` u organizacion en multi-tenant | BLQ-ALTO |
| Invalidacion que dispara antes de que el write sea visible; TTL que contradice el dato | BLQ |
| Invalidacion solo local cuando importa entre dispositivos | MENOR o BLQ segun el dato |

### 12. Afirmaciones sin testigo

Ataca el documento, no el codigo. Detalle en el agente `nexus-adversary`.

| Que buscar | Severidad si falla |
|-----------|-------------------|
| Frase de cobertura que una edicion minima falsifica con el gate en verde | BLQ-ALTO |
| Numero o ejemplo publicado que no reproduce | BLQ-MED |
| Numero que reproduce pero sin su patron | MENOR |

---

## Formato de Reporte AR

```markdown
## Adversarial Review — SDD #NNN

> Fecha: YYYY-MM-DD
> Revisado por: Adversary

### Resumen

| Categoria | Resultado | Hallazgos |
|-----------|-----------|-----------|
| 1. Security | OK/BLQ/MENOR/N/A | [desc] |
| 2. Error Handling | OK/BLQ/MENOR/N/A | [desc] |
| 3. Data Integrity | OK/BLQ/MENOR/N/A | [desc] |
| 4. Performance | OK/BLQ/MENOR/N/A | [desc] |
| 5. Integration | OK/BLQ/MENOR/N/A | [desc] |
| 6. Type Safety | OK/BLQ/MENOR/N/A | [desc] |
| 7. Test Coverage | OK/BLQ/MENOR/N/A | [desc] |
| 8. Scope Drift | OK/BLQ/MENOR/N/A | [desc] |
| 9. Destructive Migrations | OK/BLQ/MENOR/N/A | [desc] |
| 10. SECURITY DEFINER | OK/BLQ/MENOR/N/A | [desc] |
| 11. Cache Invalidation | OK/BLQ/MENOR/N/A | [desc] |
| 12. Afirmaciones sin testigo | OK/BLQ/MENOR/N/A | [desc] |

### Hallazgos

| ID | Categoria | Archivo:linea | Descripcion | Reproduccion | Impacto | Sugerencia |
|----|-----------|---------------|-------------|--------------|---------|------------|
| BLQ-ALTO-1 | [cat] | `[path:linea]` | [que esta mal] | [input → esperado vs real] | [impacto] | [sin codigo] |

### Veredicto

**APROBADO** / **APROBADO con MENORs** / **RECHAZADO (BLOQUEANTEs activos)**
```

---

## Reglas del AR

1. **Adversary nunca implementa**. Solo identifica problemas. Dev corrige.
2. **Cualquier BLQ bloquea**. El nivel solo ordena el fix-pack.
3. **MENOR se documenta**. Se corrige si es rapido; si no, queda como deuda.
4. **Re-review despues de corregir**. Adversary verifica que el fix funciona.
5. **Sin reproduccion no hay hallazgo**. Cada uno lleva evidencia concreta.
6. **N/A es valido**, con su justificacion en una linea.
7. **El AR se hace sobre codigo real**. Adversary lee los archivos modificados, no asume.
