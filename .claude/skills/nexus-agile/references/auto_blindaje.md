# Auto-Blindaje

> *"Los errores refuerzan el proceso. Blindamos para que la falla nunca se repita."*

### Formato
```markdown
### [YYYY-MM-DD]: [Titulo corto]
- **Error**: [Que fallo]
- **Fix**: [Como se arreglo]
- **Aplicar en**: [Donde mas aplica]
```

### Donde documentar

| Alcance | Donde |
|---------|-------|
| Solo esta HU | `$NEXUS_ROOT/doc/sdd/NNN-titulo/report.md` seccion Auto-Blindaje |
| Multiples features | Archivo de reglas del proyecto |
| Todo el proyecto | `project-context.md` o equivalente |

### Cuando
- **INMEDIATAMENTE** cuando el error ocurre, no al final del pipeline.
- El reporte final (DONE) copia la tabla acumulada — no se reconstruye de memoria.

### Que sube de la HU a la metodologia (criterio de promocion)

Al cerrar la HU, cada entrada del Auto-Blindaje pasa por **las dos** preguntas. Si no pasa las dos,
se queda en la HU y no sube a ningun lado.

1. **Es del proyecto o del oficio?** *"Mi resolvedor devolvia AMBIGUO sobre ese path"* es de esa HU.
   *"Un simbolo exportado sin llamador no es una defensa"* le pasa a cualquiera. Descartar sin culpa:
   **una regla de mas diluye a las que importan.** Una metodologia con 40 reglas no la lee nadie.
2. **Tiene test ejecutable?** Escribi el comando, el mutante o la pregunta concreta que la falsea. Si
   no lo podes escribir, la regla es prosa y no entra.

**Una regla sin responsable no se aplica.** La que sube va al archivo del rol que la puede cazar
(`.claude/agents/nexus-*.md`) o a la fase que la ejecuta (`references/quality_pipeline.md`), nunca
solo aca: esta seccion define el FORMATO del blindaje, no es su catalogo.

**El control contra uno mismo**: si al promover una regla escribis que algo "esta medido" sin
poder pegar la corrida, cometiste el defecto que estas documentando. "Esta medido" es una afirmacion
falsable, y al corregir un numero sin medicion es facilisimo poner otro numero sin medicion, porque
el que corrige se siente del lado bueno.

Reglas ya promovidas, y donde vive cada una:

| Regla | Responsable | Como se falsea |
|-------|-------------|----------------|
| El gate verde tiene que CONTENER lo que escribiste | `nexus-qa`, paso 4 | inyectar un error en un archivo nuevo: si el gate no se pone rojo, no te cubre |
| Un control que consulta el entorno se prueba en el entorno del CI | `nexus-dev`, controles | correrlo con las condiciones del runner, no con las de tu disco |
| Un control puede estar vacio: fixture, mutante, llamador | `nexus-dev`, controles | revertir el arreglo y exigir rojo, con el motivo literal |
| Afirmaciones sin testigo: numeros, ejemplos, "queda cerrado" | `nexus-adversary` cat. 12 y CR check 8 | la edicion minima que vuelve falsa la frase, con el gate en verde |

## Antes de arreglar, clasifica la falla

| Falla | Remedio |
|-------|---------|
| **Omision**: nadie lo penso | Agujero estructural: un campo obligatorio en la plantilla. Prohibir no ayuda, porque nadie sabe que debe aplicarlo |
| **Salto bajo presion**: se conocia la regla y se ignoro | Si debe ocurrir siempre, un hook. Si no, cerrar la excusa concreta con un caso de eval |
| **Error de juicio**: el texto era correcto | Un caso de eval. No agregues texto |
| **Del proyecto, no del oficio** | Se queda en `project-context.md` |

Cada regla nueva empieza por un caso que falle sin ella.

## Ciclo de vida de las reglas

- **Filtro**: solo sube lo que no se recupera leyendo el codigo o la historia de git, y lo que tiene un falsador ejecutable.
- **Presupuesto**: `project-context.md` hasta 150 lineas de reglas, y cada agente hasta 250 lineas. Si se supera, se retira una antes de agregar otra.
- **Revision**: cada 10 HUs o en la retro, para cada regla: ¿lo que protege todavia existe? ¿su falsador todavia corre?
- **Retiro**: una regla que funciona borra su propia evidencia, asi que "hace tiempo no pasa" no alcanza. Se retira si lo protegido desaparecio, si un hook o una eval ya la cubre, o si una persona lo decide. Queda anotado en el CHANGELOG.
