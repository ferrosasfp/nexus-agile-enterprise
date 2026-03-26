# Integration Contract Template

> Contrato formal entre componentes, HUs, o equipos que necesitan comunicarse.
> BLOQUEANTE: si hay comunicacion entre modulos, debe existir un Integration Contract.

---

## Cuando Usar

- Una HU crea un API endpoint que otra HU consume
- Dos componentes intercambian datos (props, events, callbacks)
- Un equipo produce un servicio que otro equipo consume
- Una HU modifica un formato de datos que otras HUs leen

---

## Template

### Metadata
- **ID**: IC-NNN
- **Version**: 1.0
- **Creado por**: Architect (F2)
- **Aprobado por**: TL (o TL-Productor + TL-Consumidor si cross-team)
- **HU Productora**: HU-NNN
- **HU(s) Consumidora(s)**: HU-NNN, HU-NNN

### Interface

**Tipo**: REST API / GraphQL / Event / Props / Function call / Message queue

#### Endpoint / Signature

Ejemplo REST:
- **Method**: POST
- **Path**: /api/users/verify
- **Auth**: Bearer token (JWT)

#### Request

Ejemplo:
{
  "userId": "string (UUID)",
  "documentType": "DNI | PASSPORT | CUIT",
  "documentNumber": "string"
}

Campos obligatorios: userId, documentType, documentNumber
Campos opcionales: ninguno

#### Response (Success)

Status: 200
{
  "verified": true,
  "verifiedAt": "2026-03-26T10:00:00Z",
  "level": "basic | enhanced | full"
}

#### Response (Error)

Status 400:
{ "error": "INVALID_DOCUMENT", "message": "Document number format is invalid" }

Status 404:
{ "error": "USER_NOT_FOUND", "message": "No user with the given ID" }

Status 500:
{ "error": "VERIFICATION_SERVICE_ERROR", "message": "External verification service unavailable" }

#### Comportamiento

- Idempotente: Si (misma request, mismo resultado)
- Rate limit: N/A (interno) o X req/min (externo)
- Timeout: 5 segundos
- Retry policy: 3 retries con exponential backoff para 500

### Versionado

- Version actual: 1.0
- Breaking changes: nueva version (2.0) con migracion documentada
- Non-breaking changes (agregar campo opcional): bump minor (1.1)

### SLA (si cross-team)

- Disponibilidad: 99.9%
- Latencia p95: <200ms
- Fecha de disponibilidad: YYYY-MM-DD

---

## Reglas

1. **Contrato antes de implementacion** — Ambas partes (productor y consumidor) acuerdan el contrato antes de empezar F3.
2. **Inmutable despues de F3** — Una vez que ambas HUs estan en F3, el contrato no cambia sin aprobacion de ambos TLs. Usar governance.md Protocolo de Cambio de Scope si es necesario.
3. **Mocks basados en contrato** — El consumidor puede mockear. Pero el mock DEBE seguir el contrato exactamente.
4. **Contract test** — Cuando la implementacion real reemplaza al mock, ejecutar un test que valide que la respuesta real cumple el contrato.
5. **1 contrato por interfaz** — No mezclar multiples interfaces en un contrato. Si hay 3 endpoints, hay 3 contratos (o 1 contrato con 3 secciones claramente separadas).
