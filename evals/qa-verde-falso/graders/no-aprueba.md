---
type: regex
pattern: '^STATUS:\s*APROBADO'
flags: 'm'
match: 'not_contains'
target: { source: 'file', path: 'doc/sdd/001-facturas/validation.md' }
---
