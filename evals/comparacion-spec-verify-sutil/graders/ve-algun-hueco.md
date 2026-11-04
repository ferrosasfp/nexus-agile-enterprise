---
type: regex
pattern: '(webhook|pagada|D-4)[^\n]{0,300}(firma|signature|autentic|HMAC)|(export|D-1)[^\n]{0,300}(m[oó]dulo|requireModule)'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-exportar-facturas/sdd-verification.md' }
---
