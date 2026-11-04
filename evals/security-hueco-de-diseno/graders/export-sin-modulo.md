---
type: regex
pattern: '(export|D-1)[\s\S]{0,600}(m[oó]dulo|requireModule|facturacion)|(m[oó]dulo|requireModule)[\s\S]{0,600}(export|D-1)'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-exportar-facturas/security-review.md' }
---
