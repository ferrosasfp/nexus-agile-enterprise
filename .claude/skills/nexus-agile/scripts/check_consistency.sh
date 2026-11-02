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
check_count "agentes" 6 "$(ls $A/nexus-*.md | wc -l)"
check_count "comandos" 11 "$(ls $C/nexus-*.md | wc -l)"
for art in work-item.md sdd.md story-file.md ar-report.md cr-report.md validation.md report.md; do
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
for ag in analyst architect dev adversary qa docs; do
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

# --- Evidencia y entorno de validacion
check_absent "evidencia: archivo:linea ya no alcanza como PASS" 'no puede marcar (CUMPLE|PASS) sin citar' $R $A
grep -q 'Entorno de validacion' $R/project_context_template.md || fail "plantilla sin Entorno de validacion"
grep -q 'Paso 0 — Leé el entorno de validación' $A/nexus-qa.md || fail "nexus-qa no lee el entorno"
check_absent "QA no depende de gates del CR" 'CR ya corrió|confirmed from CR' $A/nexus-qa.md

echo
if [ "$fails" -eq 0 ]; then echo "RESULTADO: sin fallas"; exit 0; fi
echo "RESULTADO: $fails falla(s)"; exit 1
