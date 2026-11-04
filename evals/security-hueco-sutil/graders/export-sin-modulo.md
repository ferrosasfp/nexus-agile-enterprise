---
type: regex
pattern: '(export|D-1)[\s\S]{0,700}(m[oó]dulo|requireModule)|(m[oó]dulo|requireModule)[\s\S]{0,700}(export|D-1)'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-exportar-facturas/security-review.md' }
---
