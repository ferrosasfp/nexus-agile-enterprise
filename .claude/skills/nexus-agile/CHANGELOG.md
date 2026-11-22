# Changelog — NexusAgil

## 2.5.1 — La memoria también en FAST

### Corregido
- **El cierre FAST no renovaba las memorias.** FAST, FAST+AR y AUTO lanzan a Docs con un pedido propio ("MODO FAST", con foco en `_INDEX.md`) que no mencionaba la memoria. En la primera HU real con la 2.5.0, Docs corrió las candidatas pero no renovó ninguna de las 5 memorias que la HU usó y encontró vigentes. Ahora el pedido lista los pasos de memoria que no se saltan (candidatas, renovación, vencidas), Docs reporta una línea `Memoria:` y el orquestador la revisa antes de cerrar.

### Agregado
- **T8 en las trampas globales:** los comandos interactivos (`git add -p`, `git rebase -i`, un editor sin `-m`) no funcionan en el Bash del agente, con la receta para commitear un solo hunk con `git apply --cached --unidiff-zero`. Salió de la misma HU, aprobada por la persona como global.

## 2.5.0 — La memoria aprende de cada HU

### Revisión
Una revisión adversaria independiente reprodujo 5 problemas mayores y 10 menores, y no encontró nada bloqueante. Todos quedaron corregidos con su test:
- **Citas corridas** cuando `main` recibe otro merge entre SPEC_VERIFY y el cierre. SPEC_VERIFY anota ahora `BASE_SHA:` y las líneas se mueven desde ese commit; si falta, desde el merge-base de `BASE_REF` con `HEAD`.
- **Un diff ilegible ya no da el hecho por intacto.** Con `color.diff=always` o un archivo `-diff` no había hunks y el hecho se guardaba sin mover; ahora se descarta.
- **Las secciones terminan con su tabla.** Una tabla posterior (otro hallazgo, notas del analista) entraba como hecho o como memoria a renovar. Un título dentro de un bloque de código ya no cuenta.
- **Hechos que empiezan igual no se pisan:** la clave lleva un hash corto de la frase.
- **El bloqueo de una HU nueva se anota en esa HU**, no en la última de la sesión.
- **Menores:**
  - `.blocks.jsonl` protegido contra escritura, como `.gates.jsonl`.
  - Anotar un bloqueo nunca convierte un bloqueo en permiso.
  - Sin falsos avisos de rutas: espacios, relativas, variables, URLs, Windows, prosa.
  - En varios informes, el último manda y entra primero al tope.
  - `\|` no corta celdas.
  - Estados con emoji o backticks se reconocen, y los desconocidos se listan.
  - Hallazgos en viñetas y tablas, sin repetir los de las re-revisiones.
  - Rutas del repo y de la carpeta personal fuera de `.blocks.jsonl`.
  - Preguntas de aprobación con al menos 2 opciones.


### Agregado
- **Hechos desde SPEC_VERIFY** (paso 25 del plan): la adversaria cierra `sdd-verification.md` con `## Hechos para la memoria`, hasta 10 afirmaciones VERDADERAS sobre el código que ya existe, cada una con sus `archivo:línea`. Al cerrar, Docs corre `nexus_memory.py desde-verificacion`, que arma una entrada por hecho con el blob SHA de cada archivo. Las líneas citadas son las de `BASE_REF`: si la HU cambió el archivo, el hecho se guarda solo si ningún cambio toca esas líneas, con la cita movida a las líneas de hoy; si las toca, o el archivo no existía en la base, se descarta. Se guardan sin preguntar: si el archivo cambia, la línea `Verify:` los invalida. Por qué: SPEC_VERIFY ya verificaba decenas de afirmaciones por HU y ninguna llegaba a la memoria; la HU siguiente las volvía a investigar.

- **Candidatas automáticas** (paso 23 del plan): el hook anota cada bloqueo en `HU_DIR/.blocks.jsonl`. Al cerrar, `scripts/nexus_candidates.py` junta de la HU los bloqueos, las VIOLATION, los BLQ y MAYOR de AR y CR, y el auto-blindaje, cada uno con su origen, y marca los que se parecen a una trampa global del plugin. Docs las cura en `lecciones.md` y la persona aprueba todas en una sola ventana (`AskUserQuestion` con selección múltiple). Por qué: los bloqueos se perdían (solo quedaban si alguien los anotaba en el auto-blindaje), y cada lección pedía su propia respuesta. Sobre una HU real: 12 candidatas, y la única marcada como trampa existente era la que de verdad repetía T2.

- **Renovación** (paso 26 del plan): al cerrar, `nexus_memory.py usadas` lee `## MEMORIA CONSULTADA` y Docs renueva con `mem_review` cada memoria que la HU usó y encontró cierta (VERIFICADA o VIGENTE), y corrige las DESCARTADAS. Después lista las vencidas del proyecto: un hecho vencido se renueva solo si su `Verify:` da VIGENTE; las demás se le preguntan a la persona en la misma ventana de las lecciones. Usa la fecha nativa de Engram (`review_after`). Por qué: la fecha de revisión se ponía al guardar y nadie la movía; lo usado y lo olvidado vencían igual.

### Ajustes de la primera HU real con la 2.4.0
- **Aviso de rutas al abrir** (hook `SessionStart`, solo en `startup`): si `NEXUS_ROOT` o `CODE_ROOT` de `project-context.md` nombran una ruta absoluta que no existe en esta máquina, lo dice antes de la primera HU, con o sin Engram. Por qué: en una HU real las dos filas apuntaban a la carpeta de otra máquina; la HU lo descubrió a mitad de camino y lo anotó como hallazgo.
- **Una memoria por lección**: DONE guarda cada lección aprobada en su propia memoria, con su `topic_key` y su `scope`. Por qué: tres lecciones quedaron en una sola memoria con `scope: project`, y la que era global se perdió como de proyecto.
- **Docs busca antes de proponer una global**: lee `trampas_globales.md` y corre la consulta global; si la lección repite una trampa que ya existe, la propone como evidencia para esa trampa. Por qué: se propuso como global nueva el bloqueo de `.gates.jsonl` por Bash, que T2 ya decía.
- **El reclamo se actualiza después del merge**: DONE y AUTO vuelven a escribir `trabajo/<HU>` con el PR mergeado y el issue cerrado. Por qué: el reclamo quedó diciendo "PR en borrador, sin mergear" después del merge.

## 2.4.0 — El cerebro en cualquier máquina y en todos los proyectos

### Agregado
- **Trampas globales en el plugin** (`references/trampas_globales.md`): rtk reescribe la salida, los artefactos solo con Write o Edit, Write y Edit decodifican escapes Unicode. Cada una con su `Verify:`. Suma cuatro de la siembra (T4 a T7: restaurar mutantes con git, vitest no chequea tipos, variables en zsh, cuándo cuenta un mutante). El analista las lee en F0 y Dev antes de la primera wave, con o sin Engram. Por qué: `engram sync` no exporta el ámbito global, así que una trampa global guardada en una máquina no llegaba a otra.
- **Respaldo de la memoria** (`scripts/nexus_brain.py`): `respaldar` exporta toda la memoria con `engram export --all` (todos los proyectos y ámbitos, global incluido) a `memoria.json` en un repo git propio (`~/nexus-brain` o `$NEXUS_BRAIN_DIR`), normalizada para que cada commit muestre solo lo que cambió; `restaurar` la importa en otra máquina. Probado con Engram 3.7.2: el import no duplica. El remoto lo agrega la persona; si existe, empuja solo cuando `gh` confirma que el remoto de push es un repo privado de GitHub. No pisa el respaldo si a la base local le faltan memorias que el respaldo tiene (máquina nueva sin restaurar; `--forzar` para un borrado a propósito), solo escribe en un repo de respaldo (marca `.nexus-brain`) y no respalda lo borrado. DONE, FAST, FAST+AR y AUTO lo corren al cerrar si el repo existe.
- **Siembra retroactiva** (`scripts/nexus_seed.py`): junta las candidatas a lección de `doc/sdd/` (cada entrada de `auto-blindaje.md` con su "Aplicar en", y los puntos de las secciones "Lecciones"), con `HU/archivo:línea`, y agrupa las casi idénticas (la agrupación por significado la hace quien cura la lista). Solo lee: la persona aprueba antes de guardar. En un proyecto real de 122 HUs: 578 candidatas, curadas a 25, que nunca habían entrado a la memoria.
- **Aviso al abrir** (hook `SessionStart`, ahora también en `startup`): si el proyecto tiene `project-context.md`, Engram está instalado y falta `memory_project` (o falta `.engram/config.json`), lo dice antes de la primera HU. Con `CODE_ROOT` declarado (artefactos y código en repos distintos), no exige `.engram` en el repo de artefactos.

### Cambiado
- **Receta de búsqueda**: la consulta global pasa a `"trampa leccion"` con `match_mode: "any"`, para traer también las lecciones globales; con solo `"trampa"`, las 6 lecciones globales de la siembra no se veían desde otros proyectos.
- `references/engram_protocol.md`: secciones "Respaldo: no depender de una máquina" y "Siembra retroactiva", y las trampas del plugin en "Proyecto y ámbito".
- Check de consistencia: bloque "El cerebro en cualquier máquina (2.4.0)".
- `docs/plan-cerebro.md`: tercera etapa (pasos 18 a 29), con la etapa A hecha.

### Revisión
- Un revisor adversario independiente atacó el cambio antes del commit: 1 BLOQUEANTE, 6 MAYOR y 5 MENOR, corregidos con test. El bloqueante: `respaldar` en una máquina nueva sin restaurar commiteaba un respaldo vacío encima del bueno. Los mayores: un `--dir` apuntando a otro repo commiteaba su trabajo (`git add -A`); el freno de remotos públicos dejaba pasar cuando no podía decidir y miraba la URL de fetch en vez de la de push; un error leyendo el proyecto tumbaba el `SessionStart` y tapaba el recordatorio de la HU activa; la fila `CODE_ROOT` de la plantilla apagaba el aviso de `.engram`; la siembra duplicaba secciones anidadas, tomaba spinoffs como lecciones, perdía lecciones en negrita y reglas de varias líneas; y la documentación nombraba proyectos de clientes en este repo público. Los menores: el nombre con mayúscula o la fila sin completar de la plantilla, el aviso repetido en cada compactación y sin mirar la raíz del repo, lo borrado que viajaba al respaldo, y los números de línea de las lecciones.

## 2.3.0 — La memoria en todos los proyectos

### Agregado
- **Ámbito global**: las trampas del entorno y de las herramientas se guardan con `scope: global` y el analista y el arquitecto las leen desde cualquier proyecto con `all_projects: true, scope: "global"`. Una búsqueda normal por proyecto no las trae (probado con Engram 3.7.2). Docs propone el alcance de cada lección en `lecciones.md` y la persona lo aprueba. Antes de guardar una global, se busca: si ya existe, se actualiza. Por qué: la trampa de rtk se redescubrió por separado en cinco proyectos.
- **Proyecto fijo**: `setup.sh` corre `engram init` (nombre de la carpeta o `NEXUS_MEMORY_PROJECT`), y F0 y AUTO lo corren si falta `.engram/config.json`. En la máquina de referencia había memorias de proyectos reales guardadas como `usuario`, `fernando` y `system32`.
- **Memoria de equipo** (`memory_share: git` en `project-context.md`): DONE corre `engram sync --project <memory_project>` y el chunk entra con la próxima HU, como los gates posteriores al cierre; F0 corre `engram sync --import`. Viaja solo el ámbito `project`, sin prompts. Solo repos privados.
- `docs/medicion-memoria.md`: qué hizo la memoria en las 12 HUs de Nexus Control.

### Cambiado
- **Receta de búsqueda**: cuatro consultas fijas de una palabra con `match_mode: "any"` (lecciones, trampas y decisiones del proyecto, y trampas globales) y una por archivo, en todos los pipelines. FAST y FAST+AR ahora también consultan: 4 de 5 HUs FAST de Nexus Control no lo hacían.
- **El hook lee el transcript del analista** al terminar F0/F1: si usó Engram y faltan las consultas cortas de "leccion" y "trampa" o la global, frena; si falta la línea `Busquedas:` en `## MEMORIA CONSULTADA`, frena; si no buscó y la sección no dice "sin Engram" (o "Engram no disponible"), frena. En Nexus Control, 9 búsquedas largas dieron vacío por el `match_mode: all` por defecto, y en GH-12 y GH-18 el analista escribió "Ninguna" cuando había lecciones que aplicaban. La sección se lee con el título incluido, sin confundir comentarios de un bloque de código con títulos, y acepta las variantes comunes de `Busquedas:`.
- F0 escala si `.engram/config.json` y `memory_project` no coinciden. `engram sync --import` lo corre el analista (cubre FAST); el export, el orquestador al cerrar cada HU en todos los modos (en AUTO, al cierre del lote, después de aprobar las lecciones).
- `setup.sh` ya no promete un `MEMORY.md` manual ni búsquedas en cada fase: el respaldo sin Engram es `doc/sdd/_LECCIONES.md`. Normaliza el nombre del proyecto (`Mi Proyecto_X` → `mi-proyecto-x`) y, si `engram init` falla, avisa y sigue con el resto de la instalación.
- `hooks/__pycache__/` ya no se versiona (estaba ignorado, pero un `.pyc` había quedado trackeado).

### Revisión
- Un revisor adversario independiente atacó el cambio antes del merge: 4 MAYOR (setup abortaba si fallaba `engram init`; FAST y AUTO no exportaban la memoria; el commit de la próxima HU no nombraba el chunk; el hook aceptaba la búsqueda larga de GH-12 si se anotaba) y 6 MENOR, corregidos en este mismo cambio. Queda abierto: cuando el agente corrige después de un bloqueo del hook (`stop_hook_active`), esa versión corregida no se guarda en `.versions/`. Ya pasaba antes; ahora el bloqueo de F1 va a ser más frecuente.
- `docs/plan-cerebro.md`: pasos 8 y 9 cerrados con el uso real, y la segunda etapa (pasos 10 a 17).

## 2.2.3 — Los gates posteriores al cierre van con la proxima HU

### Cambiado
- Las lineas que el hook agrega a `.gates.jsonl` despues del ultimo commit de la HU (supervisor y respuestas de la persona sobre el push y el merge) ya no se suben con un push directo a `main`: quedan en el disco y entran en el primer commit de la proxima HU del repo, en su rama y su PR. Esta en AUTO, FAST, FAST+AR y DONE. En Nexus Control, cada HU terminaba con una pregunta mas y un push a `main` solo para esas lineas (GH-10, 12, 21 y 23).

## 2.2.2 — El artefacto, con Write o Edit

### Cambiado
- Los siete agentes que escriben artefactos tienen una regla explicita: el reporte y los documentos de la HU se escriben y se corrigen con Write o Edit, nunca por Bash (`cat >`, `tee`, `printf >`, `sed -i` ni un script que abra el archivo). El hook ya lo frenaba, pero cada bloqueo es una vuelta de tokens: en los transcripts de las corridas reales hay mas de cien bloqueos de este tipo, y casi todas las corridas tuvieron alguno. El check de consistencia exige la regla en cada agente.
- `evals/RESULTADOS.md`: la fecha del eval de la 2.2.0 decia 18 de noviembre; fue el 17.

## 2.2.1 — Hallazgos de seguridad en una revision de PR

### Corregido
- El hook no reconocia los IDs de seguridad (`### PR-551-S1 · MAYOR`, como los numera nexus-security): con un hallazgo de seguridad, frenaba el reporte por conteos que no cuadran y, peor, un BLOQUEANTE o MAYOR de seguridad no se exigia en la verificacion. En las revisiones reales seguridad no encontro nada y no se noto; lo encontro la HU de Nexus Control que lee esos reportes. Ahora se reconocen en los conteos, en la verificacion y en el control del comentario.

## 2.2.0 — El comentario de una revision se verifica antes de publicarlo

### Agregado
- Fase PR_CHECK en `/nexus-review-pr`: un adversario nuevo verifica **cada afirmacion sobre el codigo** de `pr-comment.md`, no solo los hallazgos, y escribe `pr-comment-check.md` (`STATUS: afirmaciones=N falsas=M no_verificables=K`). El hook no deja correr `gh pr review|comment --body-file .../pr-comment.md` si ese archivo no existe, es mas viejo que el comentario o tiene `falsas` mayor que cero. nexus-docs solo pone como hecho lo que sale de un hallazgo confirmado o de la verificacion; lo interno va como pregunta. El supervisor lo comprueba antes de publicar.

Por que: en la tercera vuelta de la primera revision real, el comentario publicado decia "con coma el mismo cero se rechaza", una frase de la seccion interna del informe que nadie verifico. Era falsa, el autor del PR la siguio, y el error quedo vivo una vuelta mas.
- Eval nuevo `pr-check-comentario`: un borrador con una afirmacion falsa entre tres verdaderas; 3/3.

## 2.1.4 — El supervisor de una revision de PR

### Corregido
- `/nexus-review-pr` trae el prompt del supervisor: siempre `FASE: SUPERVISION`, con el gate que se decide en `Punto de parada:`. En la primera revision real, el orquestador lo lanzo con `FASE: SCOPE_APPROVED` y el hook lo freno.
- Si una fase es el nombre de un gate, el hook explica que va en `FASE: SUPERVISION` con su punto de parada, en vez de solo listar las fases validas.

## 2.1.3 — Segunda vuelta de una revision de PR

### Cambiado
- `/nexus-review-pr` tiene una seccion "Segunda vuelta" para comprobar las correcciones del autor: solo los commits nuevos desde el head revisado; el analista reutiliza el contrato de la revision anterior y agrega `## REVISION ANTERIOR`; una unidad por cada BLOQUEANTE y MAYOR anterior y una sola para el resto; cada revisor lee solo el diff de los commits nuevos y responde si quedo resuelto, si el arreglo rompio algo y si tomo una decision de producto; "Entradas en formato local" obligatoria en las funciones de entrada tocadas; consulta a la persona con mas de 6 unidades. El supervisor lo controla (punto 10). En la primera segunda vuelta real, un solo commit de correcciones se reviso con 6 unidades de contexto completo: 42 M de tokens procesados. El resultado valio la pena (cuatro MAYOR nuevos que el arreglo habia metido), pero el costo no.

## 2.1.2 — Una edicion de la sesion principal no es una violacion del revisor

### Corregido
- El hook anotaba en `writes.log` solo los Write y Edit de los sub-agentes. Si la sesion principal editaba un artefacto de la HU mientras un revisor corria un Bash, el cambio se le atribuia a ese Bash: VIOLATION falsa, aviso al revisor y **restauracion del artefacto**, que deshacia la edicion legitima (quedaba solo en `.violations/`). En la primera revision real con `/nexus-review-pr`, el orquestador escribio la bitacora mientras los revisores corrian `git show`, y paso cinco veces. Ahora se anotan tambien los de la sesion principal. Un Bash que cambia un artefacto sigue frenado y restaurado.
- Revision de un PR ajeno: un merge de integracion es una unidad propia y se revisa con `git show --remerge-diff`, que muestra lo que el merge cambio por su cuenta al resolver conflictos (`range-diff` no sirve con merges). En la primera revision real, asi aparecio una edicion silenciosa en `PENDIENTES.md` y un mock que no estaba en ninguno de los dos padres.

## 2.1.1 — Entradas en formato local

### Corregido
- El adversario prueba cada funcion que convierte lo que escribe una persona en un dato (numero, plata, fecha, hora) con los valores que esa persona escribiria de verdad, en el idioma y el pais del producto: en es-AR, `1.000`, `1.500`, `1.000,50`, fechas inexistentes, una hora guardada y vuelta a abrir. Ejecuta la logica y pega la salida. Un valor distinto guardado sin error es MAYOR como minimo. Vale para AR y para la revision de un PR ajeno. En la primera revision cruzada real con `/nexus-review-pr`, el revisor reporto solo el rechazo de `1.000,50` (MENOR) y se le paso que `1.000` se guardaba como `1`; la revision generica previa si lo habia visto.
- Eval nuevo `pr-review-precio-sin-pista`: el mismo error, sin pistas en el contrato. Con la 2.1.0, 1/3; con esta regla, 3/3.

## 2.1.0 — Revision de un PR ajeno

### Agregado
- **`/nexus-review-pr <PR> [--supervisor]`**: la revision cruzada del PR de otra persona pasa por el arnes, con el mismo rigor que una HU propia. Fases nuevas en el hook: PR_CONTEXT (analista: PR fijado a un SHA, unidades, alcance, contrato de cada unidad desde el tracker), gate `SCOPE_APPROVED` sobre `pr-context.md`, PR_REVIEW (un adversario por unidad, en paralelo), PR_SECURITY (unidades sensibles), PR_VERIFY (un adversario nuevo intenta refutar cada BLOQUEANTE y MAYOR) y PR_DONE (informe y borrador del comentario).
- El hook exige: `UNIDAD:` en cada revision; `STATUS:` con `blq=N mayor=N menor=N` que cuadre con los hallazgos con ID (`### PR-<unidad>-<n> · SEVERIDAD · ruta:linea`); veredicto para cada BLOQUEANTE y MAYOR antes del informe; y que el comentario no lleve un hallazgo refutado. Reglas de escritura por rol para los artefactos nuevos.
- El supervisor revisa la revision (punto 10): SHA fijado, cobertura del alcance, verificacion independiente, y que el head del PR no haya cambiado antes de publicar. Publicar es siempre `ESCALAR`.
- Evals nuevos (etiqueta `revision-pr`): `pr-review-precio` (un error real en un PR ajeno) y `pr-verify-refuta` (un hallazgo falso y uno real).

Por que: en una revision cruzada real, ocho revisores genericos encontraron cuatro MAYOR en un PR ajeno, pero nada impedia que un revisor escribiera en el repo, y los MAYOR los tuvo que verificar alguien a mano antes de comentarle al autor.

## 2.0.4 — Leer los gates no es escribirlos

### Corregido
- Un `python3 -c` que solo leia `.gates.jsonl` (`for l in open('.gates.jsonl')`) se frenaba como si lo escribiera: el hook tomaba cualquier `open(` como escritura. Ahora cuenta solo un `open` en modo escritura o una llamada que escribe. Rejugados 294 comandos reales que nombran `.gates.jsonl`: 2 falsos bloqueos menos (uno de una corrida real) y ninguno nuevo. Extender la regla a los heredocs daba 28 falsos bloqueos (scripts que editan otros archivos nombran `.gates.jsonl` en su texto) y se descarto.

## 2.0.3 — Veredictos sin carrera y documentos de otras HUs

### Corregido
- **El informe del supervisor podia llegar antes que su final.** En la GH-9 de Nexus Control, 4 veredictos quedaron `null`: el hand-back llego a la sesion principal un segundo antes que SubagentStop, no habia un `null` que completar y se descartaba. Ahora se guarda hasta que el supervisor termina. Ademas, en cada evento de la sesion principal (respuesta de la persona, lanzamiento de una fase) un veredicto `null` se vuelve a leer del transcript, que para entonces esta completo (`via: transcript`): asi el escalado esta registrado cuando llega la respuesta de la persona, y su SI queda como `DECISION`.
- **El dev escribia documentos de otra HU.** En la GH-9, el dev corrigio el `sdd.md` de la GH-7 con un script de Python en linea; el hook solo vigilaba la HU actual. Ahora la regla de rol de Write vale por Bash para los documentos de cualquier HU (redirecciones, `sed -i`, `tee` y compania) y, para el dev, tambien para un script en linea que escribe y nombra un documento existente. Las rutas desechables (fixtures en `/tmp`) quedan afuera. Rejugados 961 comandos reales que nombran `doc/sdd`: un solo bloqueo nuevo, el de la GH-9.

## 2.0.2 — Veredicto de la vuelta actual

### Corregido
- Un supervisor retomado con SendMessage quedaba registrado con el veredicto de su vuelta anterior: en una corrida real, el `ESCALAR` del push quedo como el `PEDIR_EVIDENCIA` previo, y como no era `null`, el hand-back no lo corregia. Ahora un pedido nuevo abre otra vuelta, se ignoran las lineas `api-request-blob` (repiten la conversacion entera) y solo cuenta lo que el supervisor dice, en texto o en su hand-back: un Bash que busca "VEREDICTO: ESCALAR" no es su veredicto. Simulado sobre los 87 veredictos reales de todas las corridas: antes de escribirse la linea final, ninguno toma el de otra vuelta; con la linea final, los 87 se leen bien.

## 2.0.1 — Correcciones de las primeras corridas con la 2.0.0

Arreglos del hook que salieron de la GH-10 y la GH-12 de Nexus Control y de la configuracion del primer proyecto con la 2.0.0 (PRs #13, #14 y este). Se publica como version para que `claude plugin update` la instale: con la misma version, actualizar no baja nada y reinstalar borra el estado de las sesiones en curso.

### Corregido
- **Un informe de sub-agente quedaba como decision de la persona.** Claude Code entrega el informe de un sub-agente en segundo plano como un mensaje (`<agent-message ...>`), y el hook lo tomaba por la respuesta de la persona a un escalado: en la GH-12 de Nexus Control, el informe del supervisor sobre el merge quedo en `.gates.jsonl` como `DECISION` humana. Por el mismo camino, un sub-agente podia marcar la sesion como delegada. Ahora esos mensajes y las notificaciones de tareas no cuentan como de la persona.
- **Veredictos `null` de un supervisor en segundo plano.** Su respuesta viaja en `SubagentHandback`, que no esta en el transcript ni en `last_assistant_message` cuando corre SubagentStop: en la GH-12 quedaron `null` 5 de 7 veredictos, y el hook le pedia repetir cada uno. Ahora el hook completa el veredicto con el informe cuando llega a la sesion principal (`via: hand-back`), y avisa si no trae `VEREDICTO:`. Comprobado con la sesion real: los 5 informes traen el id de su transcript y su veredicto.
- La `DECISION` de la ventana guarda la opcion elegida entera y la pregunta aparte. Antes se cortaba a 300 caracteres y se perdia la respuesta.
- El veredicto del supervisor se lee del ultimo mensaje que Claude Code le pasa al hook (`last_assistant_message`). En la GH-10 de Nexus Control, el transcript todavia no tenia esa linea cuando corrio el hook: tres veredictos correctos quedaron como `null`, uno de ellos el `ESCALAR` del merge, y por eso el SI de la persona no quedo registrado como `DECISION`.
- Un revisor no puede cambiar de rama ni restaurar archivos en el repo de la HU (`checkout`, `switch`, `reset`, `revert`, `cherry-pick`, `clean`, `restore`). En la GH-10, QA hizo `git checkout main` en el repo y hizo falta la persona para volver. En una copia aparte se permite, y `git worktree add` ya no se confunde con `git add`: la guia de QA pedia crear esa copia y el hook la bloqueaba. Rejugados 16.388 comandos de git de revisores de todas las corridas: 99 bloqueos nuevos, todos cambios de rama o `reset` en el repo de la HU (incluido el de la GH-10); 398 bloqueos menos, todos en copias; 0 caidas.
- `forbidden_commands` con la barra escapada (`\|`), como lo muestra la plantilla dentro de la tabla, no bloqueaba nada: el hook la leia como una barra literal. Ahora la lee como alternativa. Lo encontro la sesion que configuraba el primer proyecto con la 2.0.0.

## 2.0.0 — Version estable

Correcciones de la tercera y cuarta HU de Nexus Control y de la deuda del hook. Eval local del 11 de noviembre: 35 de 37 casos en 3/3 (ver `evals/RESULTADOS.md`).

### Corregido (deuda del hook)
- Sin `cd`, cada archivo que tocan `rm`, `cp`, `mv`, `tee` o `sed -i` se juzga por su ruta. Antes alcanzaba con una palabra en `/tmp`: `rm src/a.py /tmp/x` pasaba. Rejugados 58.145 comandos unicos de agentes de solo lectura de todas las corridas: 130 bloqueos nuevos, todos esperados (93 escrituras en el repo revisado, 34 en una carpeta de evidencia que ahora se declara en `evidence_dir`, 3 en worktrees fuera de `/tmp`), y 186 falsos positivos menos, ninguno con escrituras fuera de `/tmp`.
- El parser entiende `--rm` de docker run, `docker cp`, redirecciones como `2>/dev/null`, la barra de continuacion, `cd` relativo despues de uno absoluto, `cd ... 2>/dev/null ||`, carpetas de `mktemp`, variables de un `for` o de una funcion, rutas relativas en variables y `tee` dentro de una ruta. Las asignaciones dentro de comillas no cuentan.
- Un `cd` seguido de `||` y un salto de linea hacia caer el hook. Pasados 114.706 comandos reales por el hook nuevo: 0 caidas.
- Campo nuevo `evidence_dir` en `project-context.md`: carpetas fuera del repo donde los revisores pueden dejar evidencia.
- El eval del CI incluye los casos de QA y del hook que necesitan Bash (etiquetas `qa` y `hook`).
- README y `enforcement.md` alineados con el codigo (revision independiente: 6 contradicciones).

### Corregido (gate delegado sin revision)
- Con `--supervisor`, el hook registra un gate delegado (`HU_APPROVED`, `SPEC_APPROVED`) solo si hay un veredicto del supervisor sobre la version actual del documento: `CONTINUAR`, o `ESCALAR` seguido de la respuesta de la persona. La respuesta, en la ventana de opciones o escrita en el chat, queda en `.gates.jsonl` como `DECISION`. Antes lo registraba al lanzar la fase siguiente sin mirar si hubo revision. El modo checklist queda igual.

### Corregido (contradicciones entre archivos)
- El dev ya no puede escribir los documentos aprobados (`work-item.md`, `sdd.md`, `story-file.md`) ni los reportes de otros roles: no tenia regla de ruta en el hook. Su codigo y sus notas, si.
- F4 de LAUNCH no exige AR ni CR, como dice el skill.
- Textos alineados con el codigo: `NEXUS_OVERRIDE` solo vale para los bloqueos al lanzar una fase; `setup.sh` no toca `settings.json`; los gates de proceso del sprint no los controla el hook; 8 agentes; las versiones van en `.versions/`; el sizing de F0/F1 incluye FAST+AR; AUTO describe el supervisor y da un ejemplo con `--supervisor`.

### Corregido (cuarta HU de Nexus Control)
- El hook frena antes de correr un `sed -i`, `perl -i`, `tee`, `cp`, `mv` o `rm` sobre un artefacto de la HU, como ya hacia con las redirecciones. El dev corrio `sed -i` sobre su `auto-blindaje.md` y el `git commit` del mismo comando lo guardo antes de que el hook lo revirtiera. Rejugados 270 comandos reales que modifican archivos, con el HU_DIR de su corrida: el unico bloqueo nuevo es ese.
- Cada veredicto del supervisor queda en `.gates.jsonl` (`gate: SUPERVISION`, con el veredicto y el punto de parada). Si la respuesta no empieza con `VEREDICTO:`, el hook se lo pide.
- La regla de costo pregunta una vez al pasar el tope, y de nuevo solo si desde esa decision se gasta otra vez lo que costo F3. Con una especificacion cara, cada paso despues de F3 repetia la misma pregunta.
- Los agentes que escriben artefactos citan los caracteres especiales por su codigo (`U+2028`): Write y Edit convierten el escape en el caracter real, tambien en Markdown.

### Agregado
- El supervisor tambien revisa el merge (punto 9): CI en verde sobre el ultimo commit, que ese commit sea el aprobado por QA, que no queden BLQ ni decisiones atribuidas a la persona sin cita, y que dispara el merge en la rama base. Deja una sola pregunta de si o no y el comando exacto. **La autorizacion del push, del PR y del merge es siempre de la persona**: el orquestador corre el comando solo con su SI. Reemplaza al campo `entrega`, que dejaba al supervisor autorizar solo y se publico por error en el PR #5.

### Corregido (tercera HU de Nexus Control)
- El reporte de DONE se llama `cierre.md`. Claude Code no deja a un subagente escribir `report.md` ("Subagents should return findings as text"), y en las cuatro primeras HUs el orquestador tuvo que copiarlo a mano.
- Un agente retomado con SendMessage deja su version en `.versions/` y pasa por los mismos controles al terminar. Antes, el hook ignoraba su segundo final: dos correcciones del SDD no quedaron guardadas.
- Una asignacion dentro del cuerpo de un heredoc no cuenta como variable del shell. Un `S="$S/..."` en el script de QA anulaba el `S` del comando y el hook bloqueaba `$S/mk.py`.
- `rm`, `mv`, `cp`, `tee`, `sed -i` y compania se juzgan por los archivos que tocan: con un `cd` al repo, borrar o copiar en `/tmp` pasa; tocar el repo no. Antes, con un `cd` al repo, no pasaba nada. El caso sin `cd` se resolvio despues, en la deuda del hook.
- Las correcciones de SPEC_VERIFY no agregan afirmaciones nuevas sobre el codigo, y todo AC, tambien los que no son de codigo, aparece en el contrato.
- Confirmacion de seguridad barata para un SDD que cambio solo de redaccion: el agente compara contra la version que aprobo.

### Corregido
- Hook con agentes en paralelo: un candado (una ejecucion a la vez) y escritura atomica del estado. En la HU-2 de Nexus Control, con AR y CR en paralelo, el hook leyo el estado vacio y freno un mensaje de la persona.
- Rutas de Bash resueltas contra el ultimo `cd` anterior a cada ruta (no solo un `cd` inicial), con variables encadenadas en varias lineas y sin contar los `cd` dentro de un subshell. El `.gates.jsonl` de prueba se decide por a donde apunta cada mencion. Cuatro falsos bloqueos de la HU-2 de Nexus Control, rejugados con el hook nuevo: los cuatro pasan; el unico bloqueo correcto sigue y ahora dice que un artefacto se escribe con Write.
- `git stash list` y `git stash show` son lectura.
- `check_contract.py` reconoce ACs con sufijo (`AC-8b`), tambien dentro de listas.
- El supervisor revisa el costo desde F3 (punto 8): la regla 11 de AUTO no la aplico nadie en la HU-2.
- Cada agente guarda sus temporales en una carpeta propia del scratchpad compartido.
- Las fotos de los artefactos que el hook toma antes de cada Bash se borran a las 6 horas: un Bash cancelado las dejaba para siempre, con copias de los artefactos (y datos del cliente) en el directorio del plugin.

### Cambiado
- FAST y FAST+AR: el procedimiento para cuando Claude Code rechaza el Write de `report.md`, y `APROBADO con observaciones` en QA, que antes no tenian camino. El push, el PR y el seguimiento del CI quedan explicitos como tarea del orquestador.
- El Dev verifica en el registro toda version que fija; sin consulta, escribe NO VERIFICADO. En la HU del CI fijo `@v6` de memoria con `@v7` vigente.
- `project-context.md`: `.nexus-state.json` va al `.gitignore`; la auditoria (`.gates.jsonl`, `.versions/`, `.violations/`) si se versiona.
- El supervisor revisa el pedido de push o PR (punto 7): lo que dispara, que las versiones fijadas existan, la base del PR y que lo que se sube sea lo aprobado. La persona recibe una sola pregunta de si o no. En la HU del CI de Nexus Control, esa revision la estaba haciendo la persona con otra sesion.

## 2.0.0-rc.5 — Primera HU de un proyecto nuevo

Correcciones de la primera corrida en un proyecto vacio (Nexus Control, GH-1, manual).

### Corregido
- Hook: una sonda de solo lectura (`python3 -c ... >/dev/null`) ya no cuenta como escritura; un `.gates.jsonl` de prueba en `/tmp` se puede crear; una redireccion a un archivo de la HU se frena antes de correr (restaurar despues no alcanzaba con un `git commit` en el mismo comando); un gate dentro de un mensaje avisa que no se registro; SubagentStop frena caracteres de formato invisibles (U+202E, U+FEFF) en los artefactos.
- Un `.gates.jsonl` de prueba con `cd` a `/tmp` y ruta relativa ya no se bloquea (la rc.5 inicial lo seguia bloqueando: lo encontro el QA corto de la HU real). Repetir una fase sobre una HU cerrada no la reabre: queda como `rerun` en `.nexus-state.json`.
- `check_contract.py` entiende listas y rangos de ACs ("AC-1, 2, 3"); `nexus_metrics.py` cuenta una vez un agente que cruza un cambio de sesion; `nexus_memory.py` da claves distintas a dos hechos del mismo archivo.

### Cambiado
- **Tope de dos rondas** de correccion entre SPEC_VERIFY y SECURITY; lo que quede va a `Limites conocidos` del SDD y lo acepta la persona. Sin tope, F2 corrio 6 veces y se llevo el 59 % del costo de la HU.
- Seguridad y controles debiles se miden contra un atacante de afuera del codigo de la HU, no contra quien lo escribe.
- SPEC_VERIFY y SECURITY pueden correr en paralelo sobre la misma version del SDD.
- **Enmienda corta del contrato** por un fix de AR: solo el diff se verifica y se revisa, en una vuelta.
- En un proyecto sin codigo, el arquitecto comprueba el comportamiento del entorno con sondas de solo lectura.
- Docs: los temporales en `/tmp` los borra el orquestador al cerrar; las decisiones de la persona van a memoria como `decision/`.

## 2.0.0-rc.4 — Cerebro, seguridad del diseno y costo

### Agregado
- **Memoria del proyecto (el cerebro)**: hechos atados al blob SHA de git (`scripts/nexus_memory.py`), lecciones que aprueba la persona, reclamos de trabajo con vencimiento. El analista y el arquitecto leen (5 busquedas como maximo), Docs escribe. Antes ningun agente tenia las herramientas de Engram: el protocolo no se podia usar. Diseno: `docs/plan-cerebro.md`; protocolo: `references/engram_protocol.md`.
- **Gate de propiedad con cualquier tracker** (`references/tracker.md`): Jira, Linear, GitHub Issues, archivo o una herramienta propia. El hook no deja lanzar el primer analista sin `PROPIEDAD:` ni con una HU ajena.
- Evals: memoria con un hecho viejo y HU ajena, 6/6.

### Cambiado
- Lectura minima por agente, reporte de 25 lineas como maximo y salidas largas a archivo; el orquestador pasa rutas, no contenido.
- El fix-pack empieza por convertir cada reproduccion en un test en rojo; un hallazgo sin reproduccion no se arregla.

## 2.0.0-rc.3 — Correcciones de las dos primeras corridas reales

### Corregido
- Segunda HU real (AUTO con supervisor): 11 falsos bloqueos del hook a lecturas (`merge-base`, patrones de grep entre comillas, variables encadenadas, `..` dentro de un texto). Las variantes que escriben siguen bloqueadas.
- `check_contract.py`: titulo numerado del contrato en el SDD, rutas relativas a un subdirectorio declarado y ACs eliminados. 0 fallas falsas en las dos HUs reales.
- El re-CR acotado es obligatorio cuando el CR rechazo: el comando decia que era opcional y el hook lo exigia.
- `nexus_metrics.py`: tiempo activo (sin las esperas entre vueltas de un agente reanudado), vueltas y tokens procesados. El contexto final se quedaba corto con reanudaciones: en la segunda HU, 1,57 M de contexto final contra 45,8 M procesados.
- `.versions/` guarda cada entrega del analista y del arquitecto, no solo la aprobada.
- AUTO se delega con el comando al inicio de cualquier linea del mensaje (tambien tras un guion o un verbo como "Lanza"), y el hook lo confirma. En la segunda HU real, el comando venia dentro de un bloque de instrucciones y la sesion quedo sin delegar.
- Nombrar `.gates.jsonl` dentro de comillas o de un heredoc (una nota en la bitacora) ya no bloquea; escribir en el sigue bloqueado.
- Los comandos ya no comparan contra `main` fijo: cada prompt lleva `BASE_REF`, la base real de la HU.
- Con el plugin, el hook exige el prefijo `nexus-agile:`. Sin prefijo se usaba en silencio otra version instalada.
- `SKILL_DIR` busca primero dentro del plugin.
- Sin `CODE_ROOT` valido, el hook bloquea en lugar de usar la carpeta actual.
- `/nexus-p1-f0-f1` ya no se contradice con la edicion de `_INDEX.md`.
- Falsos positivos del hook (9 de 11 bloqueos en la corrida real): leer `.gates.jsonl`, rutas relativas despues de un `cd` a `/tmp`, variables asignadas en el mismo comando, y `>` entre comillas o en un heredoc.
- `check_contract.py` reconoce titulos numerados y filas "Modificar" con nota, y falla en voz alta si no reviso nada.
- DONE admite "APROBADO con observaciones" si la persona decide cerrar; procedimiento para cuando Claude Code rechaza que un subagente escriba `report.md`.
- La plantilla del SDD ya no lleva `SPEC_APPROVED: no`: el estado vive en `.gates.jsonl`, y cambiar la cabecera rompia el hash.
- La Wave -1 del Story File y el pre-flight de F3 solo comprueban, sin `npm install` ni variables que los tests no usan.
- `migrations_build_cmd` es opcional y puede ser `no disponible`.
- El supervisor no trata como rodeo que un agente siga la instruccion del propio mensaje del hook.

### Agregado
- Agente `nexus-security` y fase `SECURITY`: revisa la seguridad del diseno antes de `SPEC_APPROVED`, solo si el analista marca `security_review: required`. Matriz de autorizacion, hallazgos con camino de ataque, y el hook no deja pasar a F3 con hallazgos abiertos. Eval: 4 casos, 12/12. En un SDD con dos huecos por ausencia (webhook sin firma, exportacion sin chequeo de modulo), los dos agentes los ven, pero SPEC_VERIFY los deja como controles debiles y no frena el gate en 2 de 3 corridas; `nexus-security` los marca ALTO y frena en 3 de 3.
- `security_cmd` en `project-context.md`: controles de seguridad sin modelo que QA corre en F4.
- AUTO regla 11: un costo de mas del doble de la implementacion se escala con el costo y las opciones.
- Supervisor: no decide por costo hundido; ante un "presentar a la persona" solo continua si cada punto ya lo decidio la persona, citando donde. En la segunda HU real, la persona confirmo que no habria frenado ninguno de sus 10 veredictos.
- SPEC_VERIFY senala controles debiles del plan de tests (`debiles=`), con la forma de evadirlos.
- Regla de comandos reescritos (rtk) en cada agente.
- `report.md` y la descripcion del PR traen las dependencias de merge de una HU apilada: PRs en orden, y commit y arbol aprobados por QA para comprobar la resolucion de conflictos sin repetir QA. En la primera HU real, el PR quedo fuera de la guia de merges del sprint.
- `marketplace.json`: instalacion con `/plugin marketplace add` y `/plugin install`.
- README con lo medido y lo no medido.
- Fase `SPEC_VERIFY` en QUALITY (era el experimento E10): el adversario, en un contexto nuevo, verifica cada afirmacion del SDD contra el codigo y escribe `sdd-verification.md` con el hash del SDD. El hook no deja pasar a F3 con falsas abiertas ni con la verificacion de otra version. Se apaga con `spec_verify: false`.
- `nexus_metrics.py`: metricas de una HU desde los transcripts y `.gates.jsonl`. DONE lo corre y `report.md` trae la tabla.
- CI del repo de la metodologia (`.github/workflows/ci.yml`): pruebas sin modelo en cada push; eval a mano con secreto.
- Las preguntas del analista quedan en `work-item.md`, y el hook frena F2 y F3 mientras haya alguna abierta. En la corrida real, el reporte no llego y sus preguntas se habrian perdido.
- Regla del orquestador: si un agente no entrega su reporte, leer artefacto y transcript antes de seguir.
- El analista tiene `Edit`, para no reescribir el archivo entero en cada cambio.
- `forbidden_commands` en `project-context.md`: comandos que el hook bloquea para todos, incluida la sesion principal.
- Bloqueo de interpretes en linea que escriben, y comparacion del arbol en todo agente que no implementa, despues de que un arquitecto rodeara un bloqueo con `python3 -c`.
- Regla en todos los agentes: si un hook bloquea, detente y reporta.
- Guia para componer el gate unico desde el CI.
- Experimento E10: verificador independiente del SDD.
- Supervisor de AUTO (E8): agente `nexus-supervisor` de solo lectura y `/nexus-auto --supervisor`. Por defecto sigue el checklist.
- AUTO escala siempre las decisiones de producto, seguridad, alcance y costo, aunque el checklist de PASS.
- Cada gate guarda una copia del documento aprobado en `.versions/`.
- Politica de commits explicita antes de F3; los revisores y `review_package.sh` tambien ven el trabajo sin commitear.
- Eval que usa un comando real: los casos anteriores armaban los prompts a mano y no vieron los defectos de las plantillas.
- Bloqueo por destino real (`PostToolUse(Bash)`): si un Bash de un agente cambia un archivo de `HU_DIR` sin Write ni Edit, se restaura, la version modificada queda en `.violations/`, se registra como `VIOLATION` en `.gates.jsonl` y el agente se frena. Verificado en Claude Code real. En la corrida real, el unico rodeo efectivo (un script de Python que edito `sdd.md`) paso el filtro por texto.
- Nota sobre proxies que reescriben comandos (rtk): la evidencia se toma con el comando sin reescribir.
- Con el plugin, el hook frena un `SKILL_DIR` ausente, sin resolver o fuera del plugin (en el eval del 2-nov, 1 de 3 corridas del comando real apunto a otra version).
- Casos de eval `ar-script-cambia-artefacto` y `hook-script-disimulado` (en `_requieren-bash/`): un script que borra un riesgo o un AC del documento aprobado.
- Antes de un push, el orquestador muestra que dispara (CI, migraciones, preview).

### Cambiado
- El agente de docs pasa a sonnet; FAST sigue con `model: haiku` para el mini-report. En la segunda HU real, haiku metio 5 errores en `report.md`.
- El tope de 400 lineas del SDD no cuenta el plan de tests ni el contrato, y prohibe quitar riesgos, decisiones o dependencias para entrar. En la corrida real, el arquitecto borro un riesgo para no pasarse.
- La suite completa corre dos veces por HU, no cuatro: el Dev al cerrar F3 (con HEAD y salida en su reporte) y QA en F4. AR y CR corren solo lo que reproduce sus hallazgos.
- `contract_mode: unified` es el default: el contrato del Dev va en el SDD y no hay F2.5. `classic` (Story File) queda para tareas L o si la persona lo pide. Una HU con `story-file.md` previo sigue valiendo. En la corrida real, el Story File repitio casi todo el SDD y cada correccion se hizo dos veces.
- El bloque MCP de Engram paso de `.mcp.json` a `setup/mcp.json`: en la raiz, el plugin arrancaba su propio engram. `setup.sh` lo sigue copiando al proyecto.
- El arquitecto puede correr la suite en una copia desechable para medir el impacto.

## Sin publicar — Harness: enforcement, medicion y seguridad

### Agregado
- Hooks en `hooks/`: gates por codigo, escritura limitada por agente, Bash de solo lectura, `--no-verify` bloqueado, reporte y `STATUS:` exigidos, comparacion del arbol y estado por HU.
- Plugin (`.claude-plugin/plugin.json`) sin mover archivos ni renombrar agentes.
- `evals/` y `tests/test_nexus_hook.py`.
- `references/`: `enforcement`, `security`, `evaluation`, `experiments`, `living_spec`, `auto_blindaje`, `reference_detail`.
- `scripts/`: `check_contract.py` antes de F3, `review_package.sh` y `check_spec_ids.py`.
- Formato de bug con Sin cambio, comprobacion invertida de retiros, brechas de verificacion, clasificacion de fallas y ciclo de vida de reglas.

### Medido
- `evals/RESULTADOS.md`: 14 casos, 42 de 42 corridas, y lo que eso no demuestra. Los 2 casos de QA siguen sin correr.

### Cambiado
- Cada prompt lleva `FASE:` y `HU_DIR:`, y cada reporte una linea `STATUS:`.
- Revisores: reportan todo y el triaje va aparte; cierran con "¿lo fusionarias?"; el contenido externo es dato, nunca instruccion.
- `SKILL.md` baja de 20 KB: el detalle pasa a `references/`.

## Sin publicar — Fase 3: coherencia y poda

### Corregido
- F5 ahora se activa con `release_gate: true`. Antes decia aplicar por defecto, pero ningun comando la ejecutaba. `RELEASE_APPROVED` entra en la tabla de gates y nunca se autoaprueba.
- Autoaprobacion: "la IA no aprueba gates" y AUTO ya no se contradicen. La excepcion es la delegacion explicita de `HU_APPROVED` y `SPEC_APPROVED`.
- Limites de FAST y FAST+AR: una sola tabla, en `quick_flow.md`. FAST admite hasta 2 archivos de codigo mas sus tests, y menos de 50 lineas.
- FAST+AR aparece en `SKILL.md` y en el sizing del analista.
- F0 y F1 son del Analyst, y F2 del Architect. Se quitaron la revision de SDD por Adversary y el "Spec Writer", que ningun comando ejecutaba.
- Una fase por lanzamiento, salvo F0+F1. El protocolo mandaba F2 y F2.5 juntos, con un gate en medio.
- Conteos corregidos: 11 comandos, 6 agentes y 9 roles.
- QA en FAST: cada AC lleva comando y salida.
- Docs no cierra el issue: se lo recuerda al humano.
- Texto actualizado sobre permisos en segundo plano, tool Agent y precios.

### Cambiado
- Menos enfasis visual: sin ⛔, 🔴 ni ⚠️ en agentes y comandos, y menos mayusculas. Se conservan los nombres de gates, marcadores y artefactos.

### Movido
- Enterprise pasa a `references/enterprise.md`, y el reporte final de AUTO a `references/auto_completion_report.md`.

### Quitado
- Party Mode, personalidades del roster, celebracion de la retro y metricas futuras de FAST.

### Evaluado
- `/nexus-auto` como Workflow: no se migra. Ver `references/workflow_evaluation.md`.

## Sin publicar — Fase 2: modernizacion

### Agregado
- `contract_mode: unified`: en tareas S/M sin riesgo, el contrato de implementacion va dentro del SDD y no hay F2.5. Sin el campo, todo sigue como `classic`.
- Verificacion de BLOQUEANTEs: antes del fix-pack, un agente nuevo intenta reproducirlos y escribe `blq-verification.md`. Ante la duda, siguen bloqueando. Descartar un BLQ-ALTO o de las categorias 1, 9, 10 u 11 requiere al humano.
- Worktrees por HU y candados con `flock` para recursos compartidos.
- LSP opcional en arquitecto, dev y adversario, con Grep como alternativa.
- `effort: high` en arquitecto y adversario.

### Cambiado
- El Dev puede leer el SDD para entender el porque. El contrato sigue definiendo el trabajo y, si difieren, manda el contrato.

### Decidido
- No se usa `isolation: worktree` en `nexus-dev`: sale por defecto de la rama default y no ve archivos sin commit.

### Quitado
- IDs de un proyecto real en ejemplos y comandos.

## Sin publicar — Fase 1: errores y seguridad

### Seguridad
- Se quito la sugerencia de aplicar migraciones al remoto mientras corre el AR.
- Revisores y orquestador ya no ejecutan `git reset --hard`, `git checkout -- .` ni `git pull`; se reemplazaron por `fetch` y `status`. Los permisos de ejemplo dejan de autorizar `git *`.

### Corregido
- AR: una sola lista de 12 categorias. `adversarial_review_checklist.md` se reescribio sobre esas 12 y conserva sus checks.
- CR: una sola lista de 8 checks, y un solo responsable, `nexus-adversary`. SOLID queda como lente del check 3 y los tests pasan a la categoria 7 del AR.
- Analista: sigue en sonnet porque su salida la revisa un humano; en AUTO QUALITY se pide opus. Vuelve Grep y suma Bash de lectura, WebFetch y lectura de Jira. Documentacion alineada, incluido docs en haiku.
- Modo no interactivo: los sub-agentes no pueden preguntar. El analista marca `[NEEDS CLARIFICATION]` y devuelve `PREGUNTAS PARA EL HUMANO`; el orquestador pregunta o escala.
- Evidencia de QA: comando y salida literal. Una cita `archivo:linea` sola ya no alcanza.
- QA corre una vez el gate unico; ya no depende de que el CR lo haya corrido. Las inyecciones de prueba se hacen en una copia desechable.
- Revisores y QA reciben Write para sus reportes, y la documentacion ya no afirma que no pueden modificar codigo.
- Las referencias de agentes y comandos usan `$SKILL_DIR`, porque una ruta relativa no resolvia desde el repo.

### Agregado
- `references/paths.md`: `NEXUS_ROOT` y `CODE_ROOT` para dejar artefactos fuera del repo. Sin configurar, el comportamiento no cambia.
- `Gate unico` y `Entorno de validacion` en `project_context_template.md`, para equipos que aplican migraciones despues, en una ventana manual.
- `scripts/check_consistency.sh`: verifica conteos, modelos, tools, rutas y comandos prohibidos.
