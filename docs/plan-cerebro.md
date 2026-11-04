# Plan: el cerebro de NexusAgil (memoria con Engram)

> Objetivo: una memoria que guarde contexto entre HUs, evite que dos agentes o dos personas hagan la misma tarea, corte las alucinaciones y baje el consumo de tokens. Cada paso dice que resuelve y como se comprueba.

## Lo que tiene que lograr

| Objetivo | Como lo logra | Como se mide |
|----------|---------------|--------------|
| Guardar contexto | Lecciones, trampas y decisiones con su porque, escritas por Docs al cerrar cada HU | Errores conocidos que no se repiten en la HU siguiente |
| No duplicar tareas | Registro `trabajo/<HU>` mas Jira y `_INDEX.md`, comprobado antes de F0 | HUs tomadas por dos personas o sesiones: tiene que ser 0 |
| No alucinar | Hechos atados al sha256 del archivo; lo que viene de la memoria es una hipotesis hasta comprobarlo | Afirmaciones falsas que llegan a SPEC_VERIFY por memoria vieja: tiene que ser 0 |
| Gastar menos | Un hecho vigente evita releer el archivo; topes de busqueda | Tokens procesados por HU con `nexus_metrics.py`, contra las dos HUs sin memoria |

## Estado de partida (medido)

- El protocolo de Engram pedia buscar y guardar en cada fase, pero ningun agente tenia sus herramientas: **nunca se uso** en las HUs reales.
- Probado el 4-nov: un subagente del plugin puede usar Engram si sus herramientas estan en `tools:`; los nombres que no existen en la maquina se ignoran; `tools:` recorta (sin `mem_save`, no escribe).
- Referencia sin memoria: 545 (2 puntos, manual) 62,2 M tokens procesados; 546 (1 punto, AUTO) 45,8 M.

## Pasos

| # | Paso | Estado |
|---|------|--------|
| 1 | Diseno: tres trabajos (contexto, registro de trabajo, hechos con hash) y tres reglas (la memoria es hipotesis, escriben pocos con origen, se mide). `references/engram_protocol.md` | Hecho |
| 2 | Permisos por rol: analista y arquitecto leen (`mem_search`, `mem_get_observation`), Docs escribe (`mem_save`, `mem_update`). Las dos variantes de nombre. Topes: 5 busquedas y 3 lecturas completas por agente | Hecho |
| 3 | Registro de trabajo: el orquestador comprueba Jira, `_INDEX.md` y `trabajo/<HU>` antes de F0 y escala si la HU es de otro; lo actualiza en cada gate; Docs lo cierra. El supervisor lo verifica en su primer punto | Hecho: interfaz de tracker (Jira, Linear, GitHub, archivo, propio), gate de propiedad en el hook |
| 4 | Hechos con hash: formato `hecho/<ruta>`, regla de reuso (hash igual: se cita sin releer; distinto: se reverifica). Script `nexus_memory.py` que da el sha y arma la entrada, para que nadie la escriba a mano | Hecho, con el blob SHA de git y pares por archivo; las lecciones las aprueba la persona |
| 5 | Controles: el hook exige `## MEMORIA CONSULTADA` en el work-item, y `report.md` trae "Memoria guardada"; check de consistencia | Hecho: `MEMORIA CONSULTADA` exigida |
| 6 | Consumo: `nexus_metrics.py` cuenta las llamadas a la memoria y lo que costaron, para saber si ahorra o suma | Hecho |
| 7 | Evals con un Engram simulado (`mocks/`): un hecho con hash viejo (tiene que reverificarlo y descartarlo), una memoria falsa (no puede entrar al SDD), y una HU registrada por otra sesion (tiene que escalar) | Hecho con el respaldo en archivo: 6/6. Simular Engram en el eval no es viable hoy |
| 8 | Siembra inicial en el proyecto Limitless: las trampas y hechos que ya conocemos de la 545 y la 546 (rtk, `vitest.config.ts`, `check_contract.py`) y el registro de las HUs en curso. **Escribe en tu memoria: necesita tu visto bueno** | Pendiente |
| 9 | Prueba real: la HU siguiente a la 541, con la memoria activa, comparando contra la 545 y la 546 | Pendiente |

## Riesgos y como se cubren

| Riesgo | Cobertura |
|--------|-----------|
| Una memoria falsa se vuelve "verdad" | Regla 1 (hipotesis) y hechos atados al hash; SPEC_VERIFY revisa lo que entra al SDD |
| Memoria vieja | El hash del archivo la invalida sola; un registro de trabajo sin cambios en 3 dias se pregunta |
| Mas tokens en lugar de menos | Topes de busqueda y medicion en el paso 6; si no ahorra, se recorta |
| Datos del cliente | La memoria es local y por proyecto (`memory_project`); nunca se copia a un repo publico |
| El equipo no la ve (Engram es local) | `$NEXUS_ROOT/doc/sdd/_LECCIONES.md` como respaldo versionado; compartir Engram entre personas queda fuera de este plan |

## Lo que no se puede prometer

- Que el consumo quede en un "estandar de mercado": no hay un numero publico confiable de tokens por HU con el que comparar. Lo que si se puede: medir cada HU con el mismo script y fijar un tope por tamano con nuestros propios datos.
- Que la memoria evite todo error repetido: evita los que alguien guardo. Lo que nadie anoto, se vuelve a descubrir.
