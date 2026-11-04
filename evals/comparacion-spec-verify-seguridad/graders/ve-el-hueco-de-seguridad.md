---
type: regex
pattern: 'IDOR|otra organizaci|saltea RLS|sin chequear el m[oó]dulo|requireModule[^\n]{0,80}(falta|no llama|no se llama|ausente)'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-exportar-facturas/sdd-verification.md' }
---
