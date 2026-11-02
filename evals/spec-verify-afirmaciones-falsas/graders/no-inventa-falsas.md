---
type: regex
pattern: '(S-1|S-3)[^\n]*\bFALSA\b'
target: { source: 'file', path: 'doc/sdd/001-facturas/sdd-verification.md' }
match: 'not_contains'
---
