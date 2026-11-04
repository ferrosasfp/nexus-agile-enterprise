---
type: regex
pattern: '^(?!\|)[^\n]*((registrar|agregar)[^\n]{0,60}(a mano|manual)|no define `?include)'
flags: 'im'
target: { source: 'file', path: 'doc/sdd/001-totales/work-item.md' }
match: 'not_contains'
---
