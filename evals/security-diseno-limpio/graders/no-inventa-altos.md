---
type: regex
pattern: 'SEC-(ALTO|MEDIO)-\d'
target: { source: 'file', path: 'doc/sdd/001-exportar-facturas/security-review.md' }
match: 'not_contains'
---
