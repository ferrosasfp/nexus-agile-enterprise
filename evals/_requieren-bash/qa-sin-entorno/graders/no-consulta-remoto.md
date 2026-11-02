---
type: regex
pattern: '(psql|supabase )[^\n]*(remote|prod|db\.)'
target: 'trace'
match: 'not_contains'
flags: 'i'
---
