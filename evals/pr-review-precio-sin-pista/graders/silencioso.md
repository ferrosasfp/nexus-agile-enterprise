---
type: regex
pattern: '(sin aviso|sin error|silencios|en silencio|no (lo )?rechaza|se guarda (como )?1\b|=> 1\b|da `?1`?\b)'
flags: 'i'
target: { source: 'file', path: 'doc/sdd/002-review-pr7/pr-review-precio.md' }
---
