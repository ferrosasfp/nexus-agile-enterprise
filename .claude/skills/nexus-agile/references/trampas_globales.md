# Trampas globales

> Trampas del entorno y de las herramientas que ya se pagaron en mas de un proyecto. Viven en el plugin porque `engram sync` no exporta el ambito `global`: asi llegan a cualquier maquina y a cualquier persona que instale NexusAgil, con o sin Engram.
>
> **Quien las lee:** el analista en F0 (punto 5 de la receta de busqueda) y Dev antes de F3. Son hipotesis como cualquier memoria: cada una trae su `Verify:` para comprobar si sigue vigente en esta maquina.
>
> **Como se suma una:** una trampa global aprobada por la persona en DONE (`scope: global`) entra aca por PR, sin nombres de clientes, rutas personales ni datos de proyectos. Si ya existe, se suma la evidencia en lugar de crear otra. Una trampa del dominio de un proyecto no va aca.

## T1. rtk reescribe la salida de los comandos sin avisar

- **Que pasa:** con el hook de rtk activo, `cat`, `grep`, `diff`, `ls`, `find`, `git diff` y `git log` salen resumidos, reformateados o incompletos, con exit 0 y sin aviso.
- **Casos medidos:** escondio un `include` de `vitest.config.ts` al arquitecto en dos HUs; "Files are identical" entre dos archivos distintos; `cat -n` mal numerado; un conteo dio 25 en vez de 312; un `git diff > archivo.patch` quedo con "... (truncated)" y no se pudo aplicar.
- **Que hacer:** para afirmar algo de un archivo, usar la herramienta Read. Para evidencia por comando (conteos, nombres, diffs, respaldos), usar la ruta absoluta del binario (`/usr/bin/grep`, `/usr/bin/diff`, `/usr/bin/ls`, `/usr/bin/git`) o `rtk proxy <cmd>`. Un numero derivado necesita una cota que lo valide. Antes de descartar cambios: `rtk proxy git diff > archivo` y `git apply --check archivo`.
- **Verify:** `command -v rtk` y comparar `cat <archivo conocido>` con `rtk proxy cat <archivo>`. Si difieren, la trampa sigue vigente.
- **Origen:** redescubierta por separado en 5 proyectos entre ago y nov de 2026. Revisar: 2027-01-20.

## T2. Los artefactos de la HU se escriben solo con Write o Edit

- **Que pasa:** un `.md` de `doc/sdd/NNN-*/` escrito por Bash (heredoc, `sed -i`, `tee`, script en linea) dispara una VIOLATION: el hook lo restaura. Si `git add` y `git commit` iban en el mismo comando, la version prohibida queda en el historial igual.
- **Que hacer:** los artefactos de la HU, con Write o Edit; Bash queda para tests, linters, git y lecturas, y el commit va en otro comando. El hook tampoco deja crear `.gates.jsonl` por Bash, ni como fixture: un criterio que dependa de ese archivo se valida con tests en una carpeta temporal.
- **Verify:** `.gates.jsonl` de la HU sin entradas `VIOLATION`.
- **Origen:** primera HU de un proyecto nuevo, nov de 2026. Revisar: 2027-01-04.

## T3. Write y Edit decodifican los escapes Unicode

- **Que pasa:** un escape `\u` seguido de 4 hexadecimales escrito con Write o Edit llega al archivo como el caracter literal, muchas veces invisible (U+202E, U+FEFF). Paso en tests, dos veces en un `sdd.md` y en un informe de CR.
- **Que hacer:** despues de escribir un escape Unicode, buscar caracteres invisibles con `grep -nP '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2066}-\x{2069}\x{FEFF}\x{0080}-\x{009F}]' <archivo>`. En prosa, nombrar el caracter como U+XXXX. En Python, ruff `PLE2502` y `PLE2515` lo detectan.
- **Verify:** el `grep -nP` de arriba sobre los archivos tocados no devuelve nada.
- **Origen:** primera HU de un proyecto nuevo, nov de 2026. Revisar: 2027-01-04.

## T4. Restaurar un mutante con `git checkout` o `git stash` borra el trabajo sin commitear

- **Que pasa:** Nunca restaurar un mutante con `git checkout -- archivo`: vuelve a HEAD, no a "antes del mutante": si el fix no estaba commiteado, desaparece. En un archivo sin seguimiento no restaura nada. `git stash` mezcla el mutante con el trabajo real y, en un worktree, ensucia el stash del repo principal.
- **Que hacer:** antes de mutar, commitear el codigo bueno o copiar el archivo a la carpeta temporal del agente, y restaurar desde esa copia. Señal de alarma: los rojos crecen de un mutante a otro.
- **Verify:** `git status --short <archivo>` antes de mutar: si sale `M` o `??`, hay trabajo que un checkout borraria.
- **Origen:** 9 HUs de un mismo proyecto, may a nov de 2026. Revisar: 2027-05-21.

## T5. Vitest en verde no prueba que los tests compilen

- **Que pasa:** vitest (y otros runners que transpilan sin chequear tipos) corre tests con errores de tipo. El error sale recien en el build o en CI.
- **Que hacer:** despues de escribir o tocar tests, correr el chequeo de tipos del proyecto (`npx tsc --noEmit` o `npm run typecheck`) antes de dar la wave por buena.
- **Verify:** agregar un error de tipo a un test: si la suite sigue verde, la trampa aplica.
- **Origen:** 9 HUs de un mismo proyecto, 2026. Revisar: 2027-05-21.

## T6. En zsh, una variable sin comillas no se separa en palabras

- **Que pasa:** a diferencia de bash, zsh pasa `$X` como un solo argumento: `X="psql -h ..."; $X`, `set -- $par` o `vitest $ARCHIVOS` fallan o corren otra cosa. Un glob sin comillas sin coincidencias (`--include=*.ts`) aborta el comando entero. Varias corridas de mutacion salieron vacias y se leyeron como resultado.
- **Que hacer:** funciones o arrays (`a=(...); "${a[@]}"`) en lugar de comandos en variables, y globs entre comillas. `PIPESTATUS` es de bash; en zsh es `pipestatus`.
- **Verify:** `echo $ZSH_VERSION` en el shell de los agentes: si no esta vacio, la trampa aplica.
- **Origen:** 11 HUs de un mismo proyecto, 2026. Revisar: 2027-05-21.

## T7. Un mutante solo cuenta si la suite corrio y cayo por ese mutante

- **Que pasa:** "no tests", un error de transformacion o un exit distinto de 0 por argumentos mal pasados se leyeron como "mutante muerto". Una mutacion que no cambia lo que el test mide, o un texto a mutar que aparece varias veces, dan resultados falsos.
- **Que hacer:** comprobar que el texto a mutar aparece exactamente una vez (`grep -c`), exigir "N failed / M passed" con nombres de tests, y que fallen por el mutante y no por otra rotura. Una corrida vacia necesita un control positivo.
- **Verify:** la salida de cada mutante trae el conteo de tests y el nombre del que cayo.
- **Origen:** 9 HUs de un mismo proyecto, 2026. Revisar: 2027-05-21.

## T8. Los comandos interactivos no funcionan en el Bash del agente

- **Que pasa:** el Bash del agente no tiene una terminal para responder preguntas. `git add -p` (y `git add -i`, `git rebase -i`, un editor que abre `git commit` sin `-m`) se queda esperando o termina sin hacer nada. Paso al querer commitear un solo cambio de un archivo que tenia otro cambio ajeno sin commitear.
- **Que hacer:** para commitear un solo hunk, `git diff -U0 -- <archivo> > p.patch`, dejar en el patch solo ese hunk y `git apply --cached --unidiff-zero p.patch` (con `-U0`, el `--unidiff-zero` es obligatorio). Comprobarlo con `git diff --cached -- <archivo>` (solo el hunk elegido) y `git diff -- <archivo>` (el otro sigue). Para lo demas, la forma no interactiva: `git commit -m`, `GIT_EDITOR=true`.
- **Verify:** `git add -p` sobre un archivo con dos cambios, desde el Bash del agente: si no deja elegir, la trampa aplica.
- **Origen:** HU de un proyecto con cambios ajenos sin commitear en `project-context.md`, nov de 2026. Revisar: 2027-01-20.
