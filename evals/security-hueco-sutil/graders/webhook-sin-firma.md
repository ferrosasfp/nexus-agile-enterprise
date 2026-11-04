---
type: regex
pattern: '(webhook|pagada|D-4)[\s\S]{0,700}(firma|signature|autentic|secreto|cualquiera|HMAC)|(firma|signature|HMAC)[\s\S]{0,700}(webhook|pagada|D-4)'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-exportar-facturas/security-review.md' }
---
