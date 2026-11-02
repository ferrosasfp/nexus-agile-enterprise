# Evaluacion: `/nexus-auto` como script de Workflow

> Estado: **no migrado**. `/nexus-auto` sigue siendo un comando. Ningun script se ejecuto para esta evaluacion.

## Que aporta y que limita

| Aspecto | Comando actual | Script de Workflow |
|---------|----------------|--------------------|
| Control de flujo (fases, loops, maximo de 3 fix-packs) | Lo decide el modelo | Determinista |
| Paralelo por HU | Manual, por mensaje | `pipeline()`, con limite de concurrencia |
| Retomar tras un corte | Releer artefactos | Reusa resultados, solo en la misma sesion |
| Preguntar a una persona a mitad de camino | Si | No: el script no tiene como pausar y esperar |
| Revision clinica de gates | La hace el orquestador | Requiere un agente con salida estructurada |
| Usar los agentes `nexus-*` | Si | Si, con `agentType` |
| Quien lo dispara | Cualquier sesion | Requiere pedido explicito de la persona |

## Conclusion

No conviene migrar `/nexus-auto` entero. Sus gates y sus 10 reglas de escalamiento necesitan a una persona, y un script solo podria terminar y devolver el estado. Ademas, retomar solo funciona dentro de la misma sesion, y los artefactos en disco ya permiten continuar entre sesiones.

## Si mas adelante se quiere probar

El tramo candidato es F3 → DONE de una HU ya aprobada, que no tiene gates humanos:

1. `nexus-dev` implementa.
2. `nexus-adversary` corre AR y CR en paralelo, con salida estructurada.
3. Con BLQ: verificacion y fix-pack, hasta 3 veces. Si siguen, termina y devuelve `ESCALAR`.
4. `nexus-qa` valida y `nexus-docs` cierra.

**Criterio para adoptarlo**: comparar una corrida real contra el comando en la misma clase de HU, midiendo fases salteadas, tiempo y retrabajo. Sin esa comparacion, no se publica el script.
