---
type: regex
pattern: 'AC-\d+[^\n]*\b(CSV|XLSX|JSON)\b'
match: 'not_contains'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-export/work-item.md' }
---
