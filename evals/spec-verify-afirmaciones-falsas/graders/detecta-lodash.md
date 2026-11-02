---
type: regex
pattern: 'S-4[^\n]*FALSA|lodash[^\n]*FALSA|FALSA[^\n]*(S-4|lodash)'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/001-facturas/sdd-verification.md' }
---
