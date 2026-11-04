---
type: regex
pattern: '(verFactura|D-2)[\s\S]{0,600}(otra organizaci|organization_id|RLS|admin|IDOR)|(IDOR|createAdminClient|saltea RLS|otra organizaci)[\s\S]{0,600}(verFactura|D-2)'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-exportar-facturas/security-review.md' }
---
