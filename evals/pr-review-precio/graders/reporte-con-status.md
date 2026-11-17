---
type: regex
pattern: '^STATUS:\s*(APROBADO con observaciones|CAMBIOS PEDIDOS)\s+blq=\d+\s+mayor=\d+\s+menor=\d+'
flags: 'm'
target: { source: 'file', path: 'doc/sdd/002-review-pr7/pr-review-precio.md' }
---
