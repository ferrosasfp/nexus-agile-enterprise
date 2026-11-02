# Rutas — NEXUS_ROOT y CODE_ROOT

> Permite dejar los artefactos fuera del repo, por ejemplo para no meterlos en el repo de un cliente.
> Sin configurar nada, todo queda como siempre: `doc/sdd/` dentro del repo.

| Variable | Que contiene | Default |
|----------|--------------|---------|
| `NEXUS_ROOT` | `project-context.md`, `product-context.md`, `doc/sdd/`, `doc/prd/` | raiz git del directorio actual |
| `CODE_ROOT` | El repo donde corren git, tests y gates | raiz git del directorio actual |
| `SKILL_DIR` | Este skill | la que exista de `.claude/skills/nexus-agile` o `~/.claude/skills/nexus-agile` |

## Como las resuelve el orquestador

Primero gana lo mas explicito:

**NEXUS_ROOT**
1. Variable de entorno `NEXUS_ROOT`.
2. Campo `NEXUS_ROOT` del `project-context.md` encontrado en el directorio actual.
3. Si el directorio actual tiene `project-context.md` y no es un repo git: el directorio actual.
4. La raiz git del directorio actual.

**CODE_ROOT**
1. Variable de entorno `CODE_ROOT`.
2. Campo `CODE_ROOT` de `$NEXUS_ROOT/project-context.md`.
3. La raiz git del directorio actual.
4. Si no hay ninguno: escalar al humano. No se adivina.

El `project-context.md` se busca en `$NEXUS_ROOT/.nexus/`, `$NEXUS_ROOT/` y `$NEXUS_ROOT/docs/`, en ese orden.

## Paso a sub-agentes

Los sub-agentes no heredan estos valores por si solos. El orquestador los escribe resueltos, como rutas absolutas, en cada prompt:

```
RUTAS: NEXUS_ROOT=/ruta/absoluta · CODE_ROOT=/ruta/absoluta · SKILL_DIR=/ruta/absoluta
```

## Artefactos fuera del repo: que revisar

- **Permisos**: si tienes reglas de permisos que autorizan escribir bajo `doc/sdd/`, agrega tambien la ruta absoluta de `NEXUS_ROOT`. Si no, los agentes se detienen a pedir permiso.
- **Worktrees**: con artefactos fuera del repo, cada HU apunta `CODE_ROOT` a su propio worktree.
- **Respaldo**: los artefactos ya no viajan con git. Versiona `NEXUS_ROOT` por tu cuenta si los necesitas.
