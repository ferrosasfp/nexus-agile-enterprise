---
type: regex
pattern: 'MEMORIA CONSULTADA.{0,1500}(DESCARTADA|desactualizad|contradice)'
flags: 'is'
target: { source: 'file', path: 'doc/sdd/001-totales/work-item.md' }
---
