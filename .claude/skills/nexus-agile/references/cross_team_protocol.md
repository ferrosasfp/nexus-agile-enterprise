# Protocolo Cross-Team

> Para organizaciones con 2+ equipos NexusAgile que comparten dependencias.
> El NexusAgile base es per-equipo. Este documento coordina entre equipos.

---

## Scrum of Scrums

### Frecuencia

| Evento | Cuando | Duracion | Participantes |
|--------|--------|----------|--------------|
| **Pre-Sprint Sync** | Dia antes del Sprint Planning de cada equipo | 30 min | SMs + TLs de todos los equipos |
| **Weekly Sync** | Miercoles (coincide con Status Meeting) | 15 min | SMs de todos los equipos |
| **Ad-hoc Escalation** | Cuando un bloqueo cross-team supera 4h | Inmediato | TLs afectados + SMs |

### Agenda Pre-Sprint Sync

1. Cada SM presenta: HUs candidatas del proximo sprint que tienen dependencias externas (5 min por equipo)
2. Identificar dependencias cross-team (5 min)
3. Acordar compromisos: "Equipo Alpha entrega API X para miercoles" (5 min)
4. Documentar en Cross-Team Dependency Board (5 min)

### Agenda Weekly Sync

1. Status de compromisos cross-team (2 min por equipo)
2. Nuevos bloqueos descubiertos (5 min)
3. Ajustes a compromisos (5 min)

---

## Cross-Team Dependency Board

Artefacto compartido (puede ser un archivo MD, un board de Jira, o un Notion):

| Dependencia | Equipo Productor | Equipo Consumidor | Artefacto | Compromiso | Status |
|-------------|-----------------|-------------------|-----------|-----------|--------|
| POST /api/users/verify | Alpha (HU-A001) | Bravo (HU-B001) | Integration Contract v1 | Miercoles Sprint 3 | on-track |
| Tabla user_preferences | Alpha (HU-A005) | Charlie (HU-C003) | Schema migration | Lunes Sprint 4 | at-risk |

---

## Integration Contract Cross-Team

Cuando un equipo produce una API/servicio que otro consume:

### Template

INTEGRATION CONTRACT
- ID: IC-NNN
- Version: 1.0
- Productor: Equipo [nombre], HU-[NNN]
- Consumidor(es): Equipo [nombre], HU-[NNN]; Equipo [nombre], HU-[NNN]
- Endpoint/Interface: [descripcion]
- Request schema: [JSON schema o ejemplo]
- Response schema: [JSON schema o ejemplo]
- Error codes: [lista de codigos y significados]
- Auth: [como se autentica el consumidor]
- SLA: [latencia esperada, disponibilidad]
- Versionado: [como se manejan cambios breaking]
- Aprobado por: TL-Productor + TL-Consumidor(es)
- Fecha de compromiso: [cuando estara disponible]

### Reglas

1. **Ambos TLs aprueban** — El Integration Contract requiere firma de TL productor Y TL consumidor(es)
2. **Contrato antes de F3** — Ninguna F3 que dependa de la interfaz empieza sin contrato aprobado
3. **Mocks validos** — El consumidor puede mockear contra el contrato. Pero el mock DEBE ser validado cuando la implementacion real este disponible (contract test)
4. **Breaking changes** — Si el productor necesita cambiar el contrato, notificar a todos los consumidores. Nueva version del contrato con aprobacion de todos los TLs.

---

## Namespace de HUs

Para evitar colisiones de numeracion entre equipos que comparten repo:

| Equipo | Prefijo | Ejemplo branch |
|--------|---------|---------------|
| Alpha | A- | feat/A-001-user-verify |
| Bravo | B- | feat/B-001-payment-auth |
| Charlie | C- | feat/C-001-reporting |

Cada equipo mantiene su propio _INDEX.md: doc/sdd/_INDEX-alpha.md, doc/sdd/_INDEX-bravo.md.
O un solo _INDEX.md con columna de equipo.

---

## Escalacion Cross-Team

Cuando un equipo esta bloqueado por otro:

1. SM del equipo bloqueado contacta al SM del equipo bloqueante (inmediato)
2. SMs tienen 4 horas para resolver (re-priorizar, ofrecer ayuda, ajustar compromiso)
3. Si no se resuelve en 4h: TLs de ambos equipos se reunen
4. Si no se resuelve en 1 dia: POs de ambos equipos arbitran
5. Si no se resuelve en 2 dias: escalar a Engineering Manager / CTO

### Decision Rights

| Decision | Quien decide |
|----------|-------------|
| Prioridad dentro de un equipo | PO de ese equipo |
| Prioridad entre equipos | POs juntos, o Engineering Manager |
| Diseno tecnico de la interfaz | TLs juntos |
| Timeline de entrega cross-team | TLs juntos, POs validan |

---

## Feature-Level Completion

Cuando una feature se compone de HUs de multiples equipos:

1. Cada equipo completa sus HUs individualmente (DONE per HU)
2. Despues del ultimo DONE, QA Lead (del equipo consumidor principal) ejecuta:
   - Integration test end-to-end
   - Validacion de que los Integration Contracts se cumplen
   - Validacion de flujo completo de usuario
3. Si pasa: Feature marcada como DELIVERED en el Dependency Board
4. Si falla: identificar que equipo/HU tiene el defecto, crear hotfix HU

---

## Reglas Cross-Team

1. **Compromisos son compromisos** — Si un equipo se compromete a entregar X para miercoles, entregar o notificar desvio con >24h de anticipacion.
2. **Contratos antes de codigo** — No empezar F3 de una HU consumidora sin Integration Contract aprobado.
3. **Cada equipo es autonomo** — Un equipo no modifica el codigo de otro equipo sin permiso del TL de ese equipo.
4. **Namespace obligatorio** — Con 2+ equipos en el mismo repo, usar prefijos en branches y HU numbers.
5. **Post-mortem de fallos cross-team** — Si una dependencia causa un bloqueo >1 dia, documentar en retrospectiva de ambos equipos.
