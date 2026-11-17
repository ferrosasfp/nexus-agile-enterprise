---
type: regex
pattern: '015,000[^\n]*FALSA|FALSA[^\n]*015,000'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/004-review-pr11/pr-comment-check.md' }
---
