# Governance y Protocolos de Excepcion

> Los procesos funcionan hasta que la realidad los interrumpe.
> Este documento define que hacer cuando algo sale del camino feliz.

---

## Protocolo de Cambio de Scope (Post-Gate)

Cuando el PO necesita cambiar alcance despues de HU_APPROVED o SPEC_APPROVED:

### Tiers de Cambio

| Tier | Criterio | Proceso | Re-aprobacion |
|------|----------|---------|--------------|
| **Trivial** | <10% del scope, no agrega archivos, no cambia arquitectura | TL aprueba verbalmente. Dev actualiza Story File inline. | No |
| **Menor** | 10-30% del scope, puede agregar 1 archivo, no cambia arquitectura | PO re-aprueba AC (HU_APPROVED_V2). TL revisa impacto en SDD. Story File regenerado para waves restantes. | HU_APPROVED_V2 |
| **Mayor** | >30% del scope, agrega archivos, o cambia arquitectura | HU actual se completa con scope reducido (DONE-PARTIAL). Nueva HU para scope adicional. Pipeline completo para nueva HU. | Nueva HU completa |

### Artefacto de Cambio

Para Tier Trivial y Menor, documentar en el report.md:

SCOPE CHANGE
- HU: NNN
- Solicitado por: PO
- Tier: Trivial / Menor
- Cambio: [que cambio]
- Impacto: [archivos afectados, esfuerzo adicional]
- Aprobado por: TL
- Story File actualizado: Si / No

### Regla de Inmutabilidad Relajada

Los artefactos aprobados (work-item.md, sdd.md, story-file.md) pueden ser enmendados post-gate SOLO bajo este protocolo. Sin documentar el cambio = violacion de proceso.

---

## Protocolo de Disputa AR (BLOQUEANTE)

Cuando un Dev o TL considera que un hallazgo BLOQUEANTE del AR es un falso positivo:

### Proceso

1. **Dev documenta su argumento** con evidencia tecnica (no "creo que no aplica" sino "este endpoint esta detras de VPN + mTLS, request externo es imposible")
2. **TL evalua** en un maximo de 2 horas (SLA de escalacion)
3. **TL decide**:

| Decision | Efecto | Requiere |
|----------|--------|----------|
| **CONFIRMAR** | BLOQUEANTE se mantiene. Dev debe corregir. | Nada adicional |
| **DEGRADAR** | Baja a MENOR. No bloquea. Se corrige en proximo sprint. | Documentar razon + crear ticket de seguimiento |
| **DESCARTAR** | Falso positivo. No requiere accion. | Documentar razon + controles compensatorios |

4. **Documentar en Risk Acceptance**:

RISK ACCEPTANCE
- Finding: [texto del AR]
- Severidad original: BLOQUEANTE
- Decision: CONFIRMADO / DEGRADADO / DESCARTADO
- Razon: [justificacion tecnica]
- Controles compensatorios: [VPN, WAF, monitoring, etc.]
- Decidido por: [TL nombre]
- Responsable si se materializa: [nombre]
- Fecha de re-evaluacion: [cuando revisar]

5. Si el TL descarta, **PO es notificado** (riesgo de seguridad tiene implicaciones de negocio)

### Regla Actualizada

La regla "Corregir TODOS los BLOQUEANTEs" se actualiza a: "Resolver TODOS los BLOQUEANTEs." Resolver puede ser: corregir, degradar con justificacion, o descartar con justificacion. La resolucion sin correccion requiere Risk Acceptance documentado.

---

## Protocolo de Incidente / Hotfix Interrupt

Cuando produccion tiene un problema y hay que interrumpir el sprint:

### Severidad

| Nivel | Impacto | Tiempo de respuesta | Tiempo de fix |
|-------|---------|-------------------|--------------|
| **P0** | Sistema caido o todos los usuarios afectados | Inmediato | <2 horas |
| **P1** | Feature critica rota, existe workaround | <1 hora | <4 horas |
| **P2** | Feature menor rota | <4 horas | Proximo sprint |

### Quien Decide

1. **Cualquiera** puede reportar un incidente
2. **TL** clasifica la severidad (P0/P1/P2)
3. **TL** asigna el responder (el dev mas familiar con el area afectada)
4. **PO** es notificado inmediatamente para P0, en <1h para P1

### Que Pasa con el Trabajo en Curso

Si el dev asignado al hotfix tiene una HU en progreso:

1. **Commit WIP** al feature branch con mensaje "WIP: [descripcion del estado actual]"
2. **Documentar estado**: en que wave/tarea estaba, que falta
3. **Cambiar a hotfix branch**: git checkout -b hotfix/NNN-titulo (desde main)
4. **HU original queda en status PAUSED** (nuevo status valido para _INDEX.md)

### Protocolo de Reanudacion

Cuando el hotfix esta mergeado y el dev vuelve a su HU:

1. git checkout feat/NNN-titulo (su branch original)
2. git fetch origin main && git rebase origin/main
3. Resolver conflictos si los hay
4. Re-leer el Story File para re-orientarse
5. Re-mapeo: leer archivos modificados en waves completadas
6. Continuar desde la tarea incompleta
7. Status de HU vuelve de PAUSED a IN_PROGRESS

### Ajuste de Sprint

Si un hotfix P0/P1 consume >4 horas:
- TL evalua impacto en sprint inmediatamente (no esperar al Status Meeting)
- PO puede descoper la HU de menor prioridad
- Documentar en sprint dashboard: "HU-NNN removida por hotfix P0"

---

## Protocolo de Escalacion FAST a QUALITY

Cuando durante un FAST se descubre que el cambio es mas complejo de lo esperado:

### Trigger

Triage o Dev detecta que el cambio:
- Toca mas de 2 archivos
- Requiere mas de 30 lineas
- Involucra logica condicional, DB, o auth
- El typecheck/build falla por razones no triviales

### Proceso

1. Dev para la implementacion
2. Dev o Triage documenta:

ESCALATION: FAST -> QUALITY
- HU original: NNN
- Razon: [por que FAST no es suficiente]
- Complejidad descubierta: [que se encontro]
- Archivos afectados: [lista real]
- Recomendacion: SDD_MODE [mini/full/bugfix]

3. TL aprueba la escalacion (para solo: auto-aprobado)
4. Pipeline reinicia en F1 (no F0 — el contexto de F0 es valido)
5. Work Item se genera con scope expandido
6. Artefactos que se conservan:

| Artefacto | Accion |
|-----------|--------|
| Branch | Se conserva. Se renombra si es necesario. |
| Commits parciales | Se conservan. F3 continua desde donde quedo. |
| project-context.md | Se conserva (F0 no se repite) |
| Investigacion realizada | Se documenta en Work Item como "Descubrimientos previos" |

7. Gates aplican normalmente: HU_APPROVED, SPEC_APPROVED

---

## Precedencia de Reglas de Dependencia

Cuando una dependencia entre HUs encaja en multiples categorias:

| Si es... | Y tambien es... | Aplica |
|----------|-----------------|--------|
| Hard | Interface | **Hard** (mas restrictivo gana) |
| Hard | Soft | **Hard** |
| Soft | Interface | **Interface** (definir contrato, mockear) |

Regla: **la categoria mas restrictiva gana.** Hard > Interface > Soft > Ninguna.

Excepcion relajada: Si una HU dependiente tiene PR aprobado (AR + CR + F4 pasaron, PR en review o aprobado pero no mergeado), la HU downstream PUEDE empezar F3 contra el feature branch. Si el upstream recibe cambios en review, downstream debe rebasar.

---

## Statuses Validos para _INDEX.md

| Status | Significado |
|--------|-------------|
| DONE | HU completada y mergeada |
| DONE-PARTIAL | HU completada con scope reducido (scope change Tier Mayor) |
| PAUSED | HU interrumpida por hotfix o bloqueo, se reanudara |
| CARRY-OVER | HU no completada, pasa al siguiente sprint |
| ABORTED | HU cancelada por decision de PO |
| BANDAID | Hotfix temporal aplicado, fix definitivo pendiente |
| IN-PROGRESS | HU activamente en desarrollo |

---

## Reglas de Governance

1. **Scope change documentado** — Todo cambio post-gate tiene artefacto de cambio. Sin documento = no hay cambio.
2. **BLOQUEANTEs se resuelven, no siempre se corrigen** — Resolver = corregir O degradar con justificacion O descartar con justificacion.
3. **Incidentes tienen prioridad sobre sprint** — P0/P1 interrumpen inmediatamente. P2 espera al siguiente sprint.
4. **FAST escala limpiamente** — No se pierde trabajo. F0 se conserva, pipeline reinicia en F1.
5. **Mas restrictivo gana** — En dependencias, en seguridad, en duda: la opcion mas conservadora.
