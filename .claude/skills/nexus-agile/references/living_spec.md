# Especificacion viva (opt-in)

> Con `spec_mode: delta` en el work-item. Probar en **una sola capacidad** antes de extenderlo: esta combinacion no tiene evidencia medida, y otro framework documenta perdidas silenciosas al fusionar por nombre. Por eso aqui se fusiona por ID.

## Formato

`$NEXUS_ROOT/doc/spec/<capacidad>.md`, una seccion por requisito, con ID estable:

```markdown
### REQ-PAGOS-003: Reembolso parcial
WHEN ... THE sistema SHALL ...
```

## Deltas en el SDD

```markdown
## Deltas de especificacion
Capacidad: pagos · Huella base: <sha256 del archivo al empezar>

### ADDED REQ-PAGOS-007: ...
### MODIFIED REQ-PAGOS-003: <texto completo nuevo>
### REMOVED REQ-PAGOS-002: <motivo>
### RENAMED REQ-PAGOS-001 -> REQ-PAGOS-010
```

## Fases

| Fase | Que cambia |
|------|-----------|
| F2 | Architect escribe los deltas y la huella base |
| SPEC_APPROVED | Si la huella ya no coincide, otra HU cambio la capacidad: se revisa antes de aprobar |
| F4 | REMOVED y RENAMED llevan comprobacion invertida |
| DONE | Docs fusiona y corre `scripts/check_spec_ids.py` |

## Salida

Si las fusiones salen ruidosas, conserva la seccion de deltas y abandona el archivo vivo: la revision del SDD igual mejora.
