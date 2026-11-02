# Evaluar la metodologia

> Un cambio de prompt no esta probado porque suene mejor. Se prueba corriendolo contra casos conocidos.

## Tres niveles

| Nivel | Que prueba | Comando | Costo |
|-------|-----------|---------|-------|
| Textos | Que los documentos coincidan | `scripts/check_consistency.sh` | Nulo |
| Hooks | Que los controles bloqueen | `python3 tests/test_nexus_hook.py` | Nulo |
| Conducta | Que los agentes actuen bien | `claude plugin eval . --ablation none --allow-tools Write Edit Bash --scaffold` | Tokens |

## Reglas de la suite

- **Por fase, con entradas congeladas.** El pipeline completo no sirve como un caso: `claude -p` no tiene persona en los gates.
- **`--ablation none`, comparando commits.** El brazo sin plugin falla al lanzar agentes del plugin.
- **`--model` fijo** y `claudeVersion` registrado, para no confundir un cambio de modelo con uno de prompt.
- **Graders de codigo primero.** `llm` solo para textos cortos.
- **Tres estratos del revisor**: diff chico sembrado, defecto enterrado en un diff grande y bug real revertido, mas controles limpios. Se reportan por separado: la recall sintetica engana.

## Cuando se acepta un cambio de prompt

1. Ningun caso `regression` empeora.
2. Sin perdida de recall en comparacion pareada.
3. Sin aumento de BLOQUEANTEs falsos en los controles: uno falso quema un fix-pack.

## Cuanto dice una suite chica

Con 30 defectos y recall real de 60%, el intervalo ronda ±18 puntos; con 50, ±14. Detecta regresiones grandes, no cambios de 3 puntos. Los F1 de otras herramientas no son meta: dependen del metodo.

## Costo

`costUsd` del JSON de la eval da el costo por caso. Para cifras reales por fase, OpenTelemetry con `OTEL_LOG_TOOL_DETAILS=1`, sabiendo que eso exporta comandos y rutas.
