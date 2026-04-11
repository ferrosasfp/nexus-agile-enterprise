# product-context.md — Contexto de Negocio

> Contenido definido por el humano (PO/founder).
> El analyst lo genera y actualiza a partir de lo que el humano provea
> (texto libre, link, o archivo PRD en `doc/prd/`).
>
> El analyst lo lee en F0 antes de cada HU para entender el dominio.
> El humano puede pedir actualizarlo en cualquier momento.
>
> **Limite: ~200 lineas.** Este documento es siempre un RESUMEN.
> El PRD completo (si existe) vive en `doc/prd/` y se linkea en "Fuentes".

---

## Producto

| Campo | Valor |
|-------|-------|
| **Nombre** | [nombre del producto] |
| **Que resuelve** | [problema principal, en 1-2 lineas] |
| **Para quien** | [audiencia principal] |
| **Estado** | idea / MVP / growth / mature |

## Personas

| Persona | Objetivo | Pain point | Comportamiento tipico |
|---------|----------|------------|----------------------|
| [nombre] | [que quiere lograr] | [que le frustra hoy] | [como usa el producto] |

> Maximo 3 personas. Si hay mas, priorizar las que impactan al sprint actual.

## Flujos principales

[Describir el happy path del usuario principal en 5-10 pasos]

1. ...
2. ...

## Restricciones de negocio

- [Regulaciones, compliance, SLAs]
- [Presupuesto, timeline, dependencias externas]
- [Integraciones con terceros requeridas]

## Backlog priorizado (sprint actual)

| HU | Titulo | Prioridad | Estado |
|----|--------|-----------|--------|
| WKH-XX | ... | Alta | TODO |

> Opcional: linkear al board de Jira/Linear si existe.

## Decisiones de producto

> Decisiones ya tomadas que el analyst debe respetar.
> Formato: "Elegimos X sobre Y porque Z."

- [decision 1]
- [decision 2]

## Fuentes

> El PRD completo y documentos largos viven en `doc/prd/`.
> El analyst consulta estos links solo si necesita profundizar en una HU especifica.

- PRD completo: doc/prd/prd-raw.md
- Disenos/Figma: [link]
- Research/interviews: [link]

---

*Ultima actualizacion: YYYY-MM-DD por [nombre]*
