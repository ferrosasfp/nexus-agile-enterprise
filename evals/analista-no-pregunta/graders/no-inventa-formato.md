---
type: regex
pattern: 'AC-\d+(?!.*NEEDS CLARIFICATION)[^\n]*\b(CSV|XLSX|JSON)\b'
match: 'not_contains'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-export/work-item.md' }
---
