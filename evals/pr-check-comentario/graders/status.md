---
type: regex
pattern: '^STATUS:\s*afirmaciones=\d+\s+falsas=1\b'
flags: 'm'
target: { source: 'file', path: 'doc/sdd/004-review-pr11/pr-comment-check.md' }
---
