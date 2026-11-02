---
type: regex
pattern: '(cache|caché)[^\n]*(user|usuario|clave|key)|(user|usuario|clave|key)[^\n]*(cache|caché)'
flags: i
target: { source: 'file', path: 'doc/sdd/001-facturas/ar-report.md' }
---
