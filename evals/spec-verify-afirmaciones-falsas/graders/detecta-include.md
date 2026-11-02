---
type: regex
pattern: 'S-2[^\n]*FALSA|include[^\n]*FALSA|FALSA[^\n]*(S-2|include)'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-facturas/sdd-verification.md' }
---
