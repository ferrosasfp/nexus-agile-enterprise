#!/usr/bin/env bash
set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p doc/sdd/001-demo
printf '# project-context\n| **gate_command** | `true` |\n' > project-context.md
printf '# Index\n| 001 | demo | in progress |\n' > doc/sdd/_INDEX.md
printf '# Work Item 001\n- Pipeline: QUALITY\n\n## ACs\n- AC-1: WHEN x, THE sistema SHALL y.\n' > doc/sdd/001-demo/work-item.md
git add -A
git commit -qm base
hash=$(sha256sum doc/sdd/001-demo/work-item.md | cut -d' ' -f1)
printf '{"gate":"HU_APPROVED","by":"human","sha256":"%s","ts":1}\n' "$hash" > doc/sdd/001-demo/.gates.jsonl
