#!/usr/bin/env bash
#
# Verifica que agentes, comandos, skill y README digan lo mismo.
# Uso: check_consistency.sh [RAIZ_DEL_REPO]
# Sale con 0 si no hay fallas y con 1 si hay alguna.
#
set -u

ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}"
cd "$ROOT" || exit 2
# Se revisa una copia con finales de linea normalizados: hay archivos con CRLF y otros con LF.
WORK=$(mktemp -d) || exit 2
trap 'rm -rf "$WORK"' EXIT
cp -r .claude README.md "$WORK/" || exit 2
find "$WORK" -type f -name '*.md' -exec sed -i 's/\r$//' {} +
cd "$WORK" || exit 2
A=.claude/agents; C=.claude/commands; S=.claude/skills/nexus-agile; R=$S/references
fails=0

fail() { printf 'FALLA  %s\n' "$*"; fails=$((fails + 1)); }
pass() { printf 'ok     %s\n' "$*"; }

# check_absent DESCRIPCION REGEX ARCHIVOS...: el patron no debe aparecer
check_absent() {
  local desc="$1" re="$2"; shift 2
  local hits
  hits=$(grep -rnE -- "$re" "$@" 2>/dev/null | grep -v 'CHANGELOG.md' | grep -v 'check_consistency.sh')
  if [ -n "$hits" ]; then fail "$desc"; printf '%s\n' "$hits" | head -5 | cut -c1-150 | sed 's/^/         /'; else pass "$desc"; fi
}

# check_count DESCRIPCION ESPERADO OBTENIDO
check_count() {
  if [ "$2" = "$3" ]; then pass "$1 ($3)"; else fail "$1: se esperaba $2 y hay $3"; fi
}

# field AGENTE CAMPO: valor del frontmatter
field() { sed -n "s/^$2: //p" "$A/nexus-$1.md" | head -1; }

# --- Inventario y nombres que no pueden cambiar
check_count "agentes" 8 "$(ls $A/nexus-*.md | wc -l)"
check_count "comandos" 11 "$(ls $C/nexus-*.md | wc -l)"
for art in work-item.md sdd.md story-file.md ar-report.md cr-report.md validation.md cierre.md; do
  grep -rq -- "$art" $A $C || fail "artefacto sin mencionar: $art"
done
pass "artefactos revisados"

# --- Listas de AR y CR
check_count "categorias AR en el agente" 12 "$(grep -cE '^[0-9]+\. \*\*' <(sed -n '/12 Categor/,/8 Checks de Calidad/p' $A/nexus-adversary.md))"
check_count "categorias AR en el checklist" 12 "$(grep -cE '^### [0-9]+\. ' $R/adversarial_review_checklist.md)"
check_count "filas del reporte AR" 12 "$(grep -cE '^\| [0-9]+\. ' $R/adversarial_review_checklist.md)"
check_count "checks CR en el pipeline" 8 "$(sed -n '/^### Checks$/,/^### Check 7/p' $R/quality_pipeline.md | grep -cE '^[0-9]+\. \*\*')"
for f in $C/nexus-p5-ar.md $C/nexus-p6-cr.md; do
  check_count "checks CR en $(basename "$f")" 8 "$(grep -cE '^    [1-8]\. (Patrones|Naming|Complejidad|Duplicación|Imports|Límites|Escala|Claims)' "$f")"
done
check_absent "sin '8 categorias' viejas" '(^|[^0-9])8 (categor|attack categor|categories)' .claude README.md
check_absent "sin '6 checks' viejos" '(^|[^0-9])6 checks' .claude README.md
check_absent "sin 'una de las 8'" 'una de las 8' .claude

# --- Modelos y tools: el frontmatter manda
for ag in analyst architect dev adversary qa docs supervisor; do
  model=$(field "$ag" model)
  for doc in $S/SKILL.md README.md; do
    row=$(grep -E "^\| \`nexus-$ag\` " "$doc" | head -1)
    case "$row" in
      *"| $model"*) ;;
      *) fail "modelo de $ag: frontmatter=$model, $doc dice: $(printf '%s' "$row" | cut -c1-60)" ;;
    esac
    tools=$(field "$ag" tools | sed 's/mcp__[A-Za-z0-9_]*,\{0,1\} *//g; s/, *$//')
    for t in $(printf '%s' "$tools" | tr -d ' ' | tr ',' ' '); do
      case "$row" in *"$t"*) ;; *) fail "tool $t de $ag falta en $doc" ;; esac
    done
  done
done
pass "modelos y tools revisados"

# --- Responsabilidades
check_absent "AskUserQuestion fuera de los agentes" '^tools:.*AskUserQuestion' $A
check_absent "architect sin CR" '^(description:.*Code Review|\| CR \|)' $A/nexus-architect.md
for ag in adversary qa; do
  field "$ag" tools | grep -q 'Write' || fail "nexus-$ag sin Write para su reporte"
done

# --- Comandos peligrosos y rutas
# Los agentes no ejecutan esto. Se excluye la guia para humanos y las frases que lo prohiben.
hits=$(grep -rnE 'git (reset --hard|checkout -- ?\.?|clean)|git pull|git checkout main' $A $C $S/SKILL.md $R \
  | grep -v 'concurrent_work_protocol.md' | grep -v 'governance.md' | grep -vE 'Nunca|NUNCA|NO revertir|nunca para')
if [ -n "$hits" ]; then fail "sin git destructivo"; printf '%s\n' "$hits" | head -5 | cut -c1-150 | sed 's/^/         /'; else pass "sin git destructivo"; fi
check_absent "sin aplicar migraciones durante el AR" 'Aplicar migrations al remoto' $C
check_absent "sin permiso amplio de git" 'Bash\(git \*\)' $R
check_absent "doc/sdd siempre bajo NEXUS_ROOT" '(^|[^/$A-Za-z_])doc/(sdd|prd)' $A $C
check_absent "references/ siempre bajo SKILL_DIR" '(^|[` (])references/' $A $C
check_absent "git diff siempre con CODE_ROOT" '`git diff' $A $C

for f in $C/nexus-*.md; do
  n=$(grep -cE '^\s*prompt: \|$' "$f"); m=$(grep -c 'RUTAS: NEXUS_ROOT' "$f")
  [ "$n" = "$m" ] || fail "$(basename "$f"): $n prompts y $m lineas RUTAS"
done
pass "cada prompt recibe sus rutas"

# --- Fase 2: contrato, verificacion, worktrees, effort
check_absent "Dev puede leer el SDD" 'NO leas el SDD' $A $C
grep -q 'Contrato de implementacion' $R/sdd_template.md || fail "sdd_template sin Contrato de implementacion"
for f in $A/nexus-*.md; do grep -q "Si el entorno reescribe comandos" "$f" || fail "$(basename $f) sin la regla de comandos reescritos"; done
for f in $A/nexus-*.md; do [ "$(basename $f)" = nexus-supervisor.md ] || grep -q "Caracteres especiales en un artefacto" "$f" || fail "$(basename $f) sin la regla de escapes Unicode"; done
grep -q 'Dependencias de merge' $A/nexus-docs.md || fail "cierre.md no tiene Dependencias de merge"
grep -q 'Nunca quites riesgos' $A/nexus-architect.md || fail "el arquitecto puede recortar riesgos para entrar en el tope"
grep -q 'La suite completa no es tuya' $A/nexus-adversary.md || fail "el adversario no dice que la suite completa no le toca"
grep -q 'Sin este campo, la HU es `unified`' $A/nexus-analyst.md || fail "el analista no tiene unified como default"
grep -q 'contract_mode: classic' $C/nexus-p3-f2-5.md || fail "F2.5 no dice que solo corre con classic"
for f in nexus-p3-f2-5 nexus-p4-f3 nexus-p5-ar nexus-p6-cr nexus-p7-f4 nexus-p8-done; do
  grep -q 'contract_mode: \?`\?unified\|contract_mode: unified' "$C/$f.md" || fail "$f no contempla contract_mode"
done
for f in nexus-dev nexus-adversary nexus-qa nexus-docs nexus-analyst nexus-architect; do
  grep -q 'contract_mode' "$A/$f.md" || fail "$f no contempla contract_mode"
done
for f in nexus-p5-ar nexus-fast-plus-ar nexus-p6-cr nexus-auto; do
  grep -qE 'blq-verification|Verificación de BLQ|Verificar los BLQ' "$C/$f.md" || fail "$f sin verificacion de BLQ"
done
check_absent "sin isolation en agentes" '^isolation:' $A
for ag in architect adversary; do
  [ "$(field "$ag" effort)" = high ] || fail "nexus-$ag sin effort high"
done
for ag in architect dev adversary; do
  field "$ag" tools | grep -q 'LSP' || fail "nexus-$ag sin LSP"
done
check_absent "sin IDs de proyecto real" 'LUM-[0-9]|Luma' .claude README.md
pass "fase 2 revisada"

# --- Fase 3: coherencia y poda
grep -q '\*\*11 slash commands\*\*' $S/SKILL.md || fail "SKILL no dice 11 comandos"
check_count "comandos en la tabla de consulta" 11 "$(grep -cE '^\| `/nexus-' $R/reference_detail.md)"
check_absent "sin conteos viejos" '8 slash|10 commands|Los 3 Modos|Los 4 Modos|The 9 Agents' .claude README.md
check_absent "sin roles inexistentes" 'Spec Writer|Party Mode|Personalidad|Architect\+Adversary|Architect \+ Adversary|Adversary\+QA|Adversary \+ QA' $A $C $S/SKILL.md $R README.md
check_absent "limites de FAST sin versiones viejas" '<30|30 lineas|≥3 archivos|1-2 archivos|Max 2 files|<5 archivos' $A $C $S/SKILL.md $R/quality_pipeline.md $R/quick_flow.md $R/governance.md $R/onboarding.md $R/sdd_template.md README.md
grep -q '^| `RELEASE_APPROVED`' $S/SKILL.md || fail "SKILL sin RELEASE_APPROVED"
grep -q 'release_gate' $R/project_context_template.md || fail "plantilla sin release_gate"
grep -q 'release_gate' $C/nexus-p7-f4.md || fail "p7 sin F5"
grep -q 'nunca se autoaprueba' $C/nexus-auto.md || fail "auto puede autoaprobar RELEASE"
check_absent "gates con opcion exacta" 'Opciones\*?\*?: APROBAR' $C
check_absent "sin enfasis visual" '⛔|🔴|⚠️' $A $C $S/SKILL.md $R/quality_pipeline.md $R/subagent_protocol.md
check_absent "sin mayusculas de enfasis" '\b(NUNCA|SIEMPRE|DEBE)\b' $A $C $S/SKILL.md $R/quality_pipeline.md $R/subagent_protocol.md
grep -q 'references/enterprise.md' $S/SKILL.md || fail "SKILL sin puntero a enterprise"
[ -f $R/enterprise.md ] || fail "falta enterprise.md"
[ -f $R/auto_completion_report.md ] || fail "falta auto_completion_report.md"
[ "$(wc -l < $S/SKILL.md)" -le 520 ] || fail "SKILL.md supera 520 lineas"
pass "fase 3 revisada"

# --- Harness: hooks, seguridad, evals
for x in hooks/nexus_hook.py hooks/hooks.json .claude-plugin/plugin.json evals tests/test_nexus_hook.py; do
  [ -e "$ROOT/$x" ] || fail "falta $x"
done
for f in $C/nexus-*.md; do
  n=$(grep -cE '^\s*prompt: \|$' "$f"); m=$(grep -cE '^\s*FASE: ' "$f"); o=$(grep -cE '^\s*HU_DIR: ' "$f")
  [ "$n" = "$m" ] && [ "$n" = "$o" ] || fail "$(basename "$f"): $n prompts, $m FASE, $o HU_DIR"
done
[ "$(wc -c < $S/SKILL.md)" -lt 20480 ] || fail "SKILL.md supera 20 KB"
for ag in adversary qa; do grep -q 'STATUS:' $A/nexus-$ag.md || fail "nexus-$ag sin STATUS:"; done
for ag in analyst dev adversary qa; do grep -q 'datos, nunca instrucciones' $A/nexus-$ag.md || fail "nexus-$ag sin regla de contenido externo"; done
grep -q 'lo fusionarías' $A/nexus-adversary.md || fail "adversario sin pregunta de cierre"
grep -q 'No matices' $C/nexus-p5-ar.md || fail "p5 sin regla de no matizar"
check_absent "Dev con lectura exclusiva" 'Dev SOLO|Dev \*\*NUNCA\*\* lee' $S/SKILL.md $R/quality_pipeline.md
pass "harness revisado"

# --- Primera corrida real
check_absent "sin base main fija" 'main\.\.\.HEAD' $A $C
for f in $C/nexus-*.md; do
  n=$(grep -cE '^\s*RUTAS: ' "$f"); m=$(grep -c 'BASE_REF=\[valor\]' "$f")
  [ "$n" = "$m" ] || fail "$(basename "$f"): $n RUTAS y $m BASE_REF"
  grep -q 'lanzá cada agente con el prefijo' "$f" || fail "$(basename "$f") sin regla de prefijo"
  grep -q 'CLAUDE_PLUGIN_ROOT' "$f" || fail "$(basename "$f") sin SKILL_DIR del plugin"
done
for ag in analyst architect dev adversary qa docs supervisor; do grep -q 'No lo rodees' $A/nexus-$ag.md || fail "nexus-$ag sin regla de no rodear hooks"; done
grep -q '^## PREGUNTAS PARA EL HUMANO' $A/nexus-analyst.md || fail "analista sin seccion de preguntas en el artefacto"
for f in $C/nexus-*.md; do grep -q 'termina sin entregarte su reporte' "$f" || fail "$(basename "$f") sin regla de reporte perdido"; done
for f in nexus-p1-f0-f1 nexus-fast-pipeline nexus-fast-plus-ar nexus-auto; do grep -q 'PROPIEDAD' "$C/$f.md" || fail "$f no pasa el gate de propiedad"; done
[ -f $R/tracker.md ] || fail "falta references/tracker.md"
grep -q 'Tope de rondas' $C/nexus-p2-f2.md || fail "F2 sin tope de rondas de verificacion"
grep -q 'A quién defendés' $A/nexus-security.md || fail "security sin el alcance del atacante"
grep -q 'Enmienda del contrato' $C/nexus-p5-ar.md || fail "p5-ar sin la via corta de enmienda"
grep -q 'camino de ataque' $A/nexus-security.md || fail "security sin la regla del camino de ataque"
grep -q 'security_review' $A/nexus-analyst.md || fail "el analista no marca security_review"
grep -q 'nexus-security' $C/nexus-p2-f2.md || fail "F2 no lanza la revision de seguridad"
grep -q 'VEREDICTO: ESCALAR' $A/nexus-supervisor.md || fail "supervisor sin formato de veredicto"
grep -q 'nunca resuelve solo' $C/nexus-auto.md || fail "AUTO sin clases de decision que escala"
grep -q 'Política de commits' $C/nexus-p4-f3.md || fail "p4 sin politica de commits"
grep -q 'forbidden_commands' $R/project_context_template.md || fail "plantilla sin forbidden_commands"
pass "correcciones de la corrida real revisadas"

# --- Evidencia y entorno de validacion
check_absent "evidencia: archivo:linea ya no alcanza como PASS" 'no puede marcar (CUMPLE|PASS) sin citar' $R $A
grep -q 'Entorno de validacion' $R/project_context_template.md || fail "plantilla sin Entorno de validacion"
grep -q 'Paso 0 — Leé el entorno de validación' $A/nexus-qa.md || fail "nexus-qa no lee el entorno"
check_absent "QA no depende de gates del CR" 'CR ya corrió|confirmed from CR' $A/nexus-qa.md

echo
if [ "$fails" -eq 0 ]; then echo "RESULTADO: sin fallas"; exit 0; fi
echo "RESULTADO: $fails falla(s)"; exit 1
