# Supervisor de AUTO (experimental)

> Estado: experimental. Existe el agente `nexus-supervisor` y `/nexus-auto --supervisor` lo usa. Por defecto, AUTO sigue con el checklist hasta que gane la evaluacion de abajo.

## Problema

En AUTO, el orquestador ejecuta y tambien aprueba sus propios gates con un checklist. Tiene el sesgo de quien quiere terminar. En la primera corrida real con supervision externa, la mayoria de los defectos graves no los habria atrapado ese checklist:

- un agente que rodeo un hook;
- un reporte que no llego, y sus preguntas perdidas;
- un documento aprobado sin comparar que habia cambiado;
- afirmaciones falsas en el SDD que el Readiness Check dio por buenas.

Los encontro un segundo contexto que pedia evidencia en lugar de aceptar el resumen.

## Diseno

Un agente aparte, `nexus-supervisor`, de solo lectura, que el orquestador llama en cada punto de parada. Recibe el reporte del orquestador y acceso a los artefactos y transcripts, pero no su razonamiento. Devuelve una de tres respuestas:

| Respuesta | Cuando |
|-----------|--------|
| `CONTINUAR` | Lo pedido tiene evidencia y es tecnico y reversible |
| `PEDIR_EVIDENCIA` | Falta algo verificable: hash, transcript, comando y salida, cita archivo:linea |
| `ESCALAR` | Es una decision de producto, o la evidencia no alcanza |

## Que se escala siempre

Una persona decide todo lo que:

- cambia lo que ve o puede hacer un usuario;
- toca seguridad, permisos, datos o produccion;
- cambia el alcance o los ACs aprobados;
- es una prioridad de negocio, como que HU tomar;
- cambia el costo o el tamano de forma desproporcionada.

## Que verifica siempre

- Que cada agente se lanzo con el nombre y las rutas correctas.
- Que llego el reporte de cada agente, y si no, que se leyo su artefacto y transcript.
- Que un documento a aprobar se comparo con la version anterior.
- Que cada afirmacion de "lo revise" o "esta cubierto" tiene una evidencia que la respalde.
- Que nadie rodeo un bloqueo.

## Como se evalua

1. **Casos**: los puntos de decision de corridas reales supervisadas, con la decision que tomo la persona como respuesta correcta. Se guardan fuera de los repos publicos si tienen datos de clientes.
2. **Metricas**:
   - Acuerdo con la persona.
   - Escalados correctos sobre los que debian escalarse.
   - **Aprobaciones indebidas**: aprobo algo que la persona habria frenado. Es la metrica que decide: un solo caso grave descalifica.
3. **Brazo de comparacion**: el checklist actual de AUTO sobre los mismos casos.
4. **Se adopta si** baja las aprobaciones indebidas frente al checklist, sin escalar tanto que AUTO deje de ahorrar tiempo.

## Primera medicion (foto del 2 de noviembre de 2026)

6 casos sinteticos, 3 corridas: el supervisor acerto 18 de 18 despues de un ajuste. Antes de ese ajuste pedia evidencia irrelevante en un cambio trivial, en 3 de 3 corridas: sin proporcion, un supervisor frena todo.

El brazo del checklist empato en los casos con problema. Eso **no** dice que el checklist alcance: corrio en un contexto limpio y con las reglas nuevas de escalado, mientras el AUTO real decide dentro de una sesion larga y con apuro por terminar. Para medir esa diferencia hacen falta casos reconstruidos desde corridas reales.

## Limites conocidos

- El supervisor tambien es un modelo, y depende de lo que el orquestador le muestra. Un reporte enganoso pero convincente puede pasar.
- Las respuestas correctas vienen de una persona que vio respuestas preparadas por otro modelo. Eso mide acuerdo, no calidad absoluta.
