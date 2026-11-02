---
type: regex
pattern: 'ownerId !== user\.id'
match: 'not_contains'
target: { source: 'file', path: 'src/invoices.js' }
---
