# Experimentos abiertos

> No son reglas. Cada uno entra solo si gana en `references/evaluation.md`, y cada adicion viene con una retirada.

| # | Hipotesis | Como se prueba | Se adopta si |
|---|-----------|----------------|--------------|
| E1 | AR a ciegas primero (diff y ACs, sin relato) resiste mejor el framing | Brazo con casos `ar/framing-*` | Sube la deteccion en framing sin mas BLQ falsos |
| E2 | Mutacion en F4 mejora los tests | `mutation_cmd` en HUs de alto riesgo | Atrapa defectos que AR no vio, a costo aceptable |
| E3 | Pruebas de propiedades en parsers, dinero y fechas | Opcional por HU | Encuentra bugs validos; tratar cada uno como no verificado |
| E4 | Revisor de otro modelo | Brazo adicional del banco | Sube la recall de la union sin mas BLQ falsos. No es mejora automatica: Claude revisado por Codex bajo en un estudio |
| E5 | Un solo autor para F0 a F2.5 | Comparar costo y calidad del contrato | Mismo resultado, menos costo. Pierde separacion de roles |
| E6 | Quitar waves o la autoverificacion del Dev | Comparar por modelo | Sin perdida en F3 y AR. El revisor independiente no se toca |
| E7 | Umbrales de FAST, FAST+AR y QUALITY | Casos de punta a punta | QUALITY atrapa suficiente mas para pagar su costo |
| E8 | Supervisor de AUTO, ciego al razonamiento del orquestador (`references/supervisor.md`) | Puntos de decision de corridas reales supervisadas, contra el checklist actual | Menos aprobaciones indebidas sin escalar de mas. En la primera corrida real, el checklist habria atrapado 3 de 21 puntos de decision |
| E10 | Verificador independiente de las afirmaciones del SDD antes de `SPEC_APPROVED` | **Adoptado** como fase `SPEC_VERIFY` de QUALITY (nov-2026). Evidencia: en la primera HU real encontro 4 afirmaciones falsas con el Readiness Check en verde, por unos 200 mil tokens. Falta medirlo en mas HUs | Encuentra errores que el Readiness Check dejo pasar, a costo aceptable |
| E9 | Pasada de convergencia al salir de F3 | Brazo en QUALITY | Baja los hallazgos de AR |
