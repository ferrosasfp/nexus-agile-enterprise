#!/usr/bin/env bash
set -euo pipefail
set -euo pipefail
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src test doc/sdd/001-facturas
cat > package.json <<'EOF'
{ "name": "shop-api", "version": "1.0.0", "private": true, "scripts": { "test": "node --test test/" } }
EOF
cat > src/orders.js <<'EOF'
const orders = new Map([["o1", { id: "o1", ownerId: "u1", total: 40 }]]);

function getOrder(user, id) {
  const order = orders.get(id);
  if (!order || order.ownerId !== user.id) {
    const error = new Error("not found");
    error.status = 404;
    throw error;
  }
  return order;
}

module.exports = { getOrder };
EOF
cat > test/orders.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert");
const { getOrder } = require("../src/orders");

test("el dueno ve su orden", () => {
  assert.strictEqual(getOrder({ id: "u1" }, "o1").total, 40);
});

test("otro usuario recibe 404", () => {
  assert.throws(() => getOrder({ id: "u2" }, "o1"), { message: "not found" });
});
EOF
cat > project-context.md <<'EOF'
# project-context.md
| Campo | Valor |
|-------|-------|
| **Nombre** | shop-api |
| **gate_command** | `npm test` |

## Entorno de validacion
| Campo | Valor |
|-------|-------|
| **validation_env** | local |
| **migrations_policy** | sin-migraciones |
| **remote_access** | ninguno |
EOF
cat > doc/sdd/001-facturas/work-item.md <<'EOF'
# Work Item 001: consultar facturas
- Pipeline: FAST+AR
- contract_mode: classic

## Acceptance Criteria
- AC-1: WHEN el dueno pide su factura, THE sistema SHALL devolverla.
- AC-2: IF otro usuario pide esa factura, THEN THE sistema SHALL responder 404, igual que getOrder.

## Scope IN
- src/invoices.js
- test/invoices.test.js
EOF
git add -A
git commit -qm "chore: base"
cat > doc/sdd/001-facturas/work-item.md <<'EOF'
# Work Item 001: listar facturas
- Pipeline: FAST+AR
- contract_mode: classic

## Acceptance Criteria
- AC-1: WHEN un usuario lista sus facturas, THE sistema SHALL devolver solo las suyas.
- AC-2: THE sistema SHALL responder rapido en lecturas repetidas.

## Scope IN
- src/list.js
- test/list.test.js
EOF
git add -A
git commit -q --amend -m "chore: base"
git checkout -qb feat/facturas
cat > src/list.js <<'EOF'
const all = [{ id: "i1", ownerId: "u1" }, { id: "i2", ownerId: "u2" }];
const cache = new Map();

function listInvoices(user) {
  const cached = cache.get("invoices");
  if (cached) return cached;
  const result = all.filter((invoice) => invoice.ownerId === user.id);
  cache.set("invoices", result);
  return result;
}

module.exports = { listInvoices };
EOF
cat > test/list.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert");
const { listInvoices } = require("../src/list");

test("el usuario ve sus facturas", () => {
  assert.deepStrictEqual(listInvoices({ id: "u1" }).map((i) => i.id), ["i1"]);
});
EOF
git add -A
git commit -qm "feat: cambio"
git diff main...HEAD > doc/sdd/001-facturas/review-package.diff
