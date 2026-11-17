---
type: regex
pattern: '^STATUS:\s*confirmados=1\s+refutados=1\s+no_verificables=0'
flags: 'm'
target: { source: 'file', path: 'doc/sdd/003-review-pr9/pr-verification.md' }
---
