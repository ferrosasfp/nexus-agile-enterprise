# Plan hacia NexusAgil 2.0

> Origen: la prueba real en SCRUM-545 (2-nov-2026) y su informe final. Cada paso dice que problema medido resuelve y como se verifica.

| # | Paso | Problema que resuelve (prueba real) | Verificacion | Estado |
|---|------|-------------------------------------|--------------|--------|
| 1 | Script de metricas por HU | El informe final se reconstruyo a mano desde 20 transcripts | Reproduce los totales de SCRUM-545: 20 lanzamientos, 2.565.396 tokens, 6.472 s | Hecho: 20 lanzamientos, 11 bloqueos, tokens a 0,09% |
| 2 | CI del repo de la metodologia | Las pruebas, el check de consistencia y el eval se corren a mano | El workflow corre en local las mismas pruebas que en GitHub | Hecho: 98 pruebas sin modelo; eval a mano con secreto |
| 3 | `contract_mode: unified` por defecto | El Story File (591 lineas) repitio el SDD (484) y hubo que corregir los dos | check_consistency y eval de gates en verde | Hecho |
| 4 | Verificacion del SDD contra el codigo en QUALITY | La verificacion independiente encontro 4 afirmaciones falsas con el Readiness Check en verde | Caso de eval con una afirmacion falsa sembrada en el SDD | Hecho: caso de eval 3/3 |
| 5 | Una corrida de la suite completa por HU, mas la de QA | La suite corrio 4 veces sobre casi el mismo codigo | Texto de los comandos y check de consistencia | Hecho |
| 6 | El plan de tests fuera del tope de lineas del SDD | El arquitecto quito un riesgo y una tabla para no pasar de 400 | Plantilla y check de consistencia | Hecho |
| 7 | Version 2.0.0, marketplace y README con la evidencia | Instalacion a mano y version vieja en `~/.claude` | `claude plugin validate` y eval completo | rc.2 lista: eval 87/87. La 2.0.0 final espera la HU con supervisor |

## Lo que necesita a una persona

- **Prueba real del supervisor**: la proxima HU con `/nexus-auto --supervisor`, sin la sesion supervisora en el medio.
- **QA medido**: resolver los enlaces simbolicos de `~/.docker` para que el sandbox del eval de Bash.
- **Publicar**: push, PR y marketplace son decision de Fernando.
