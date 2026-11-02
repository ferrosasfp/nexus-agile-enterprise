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
# Work Item 001: formatear totales
- Pipeline: FAST+AR
- contract_mode: classic

## Acceptance Criteria
- AC-1: WHEN se formatea un total, THE sistema SHALL devolver dos decimales.
- AC-2: IF el total no es un numero finito, THEN THE sistema SHALL lanzar TypeError.

## Scope IN
- src/money.js
- test/money.test.js
EOF
git add -A
git commit -q --amend -m "chore: base"
git checkout -qb feat/facturas
cat > src/money.js <<'EOF'
function formatTotal(total) {
  if (typeof total !== "number" || !Number.isFinite(total)) {
    throw new TypeError("total invalido");
  }
  return total.toFixed(2);
}

module.exports = { formatTotal };
EOF
cat > test/money.test.js <<'EOF'
const test = require("node:test");
const assert = require("node:assert");
const { formatTotal } = require("../src/money");

test("dos decimales", () => {
  assert.strictEqual(formatTotal(4), "4.00");
});

test("rechaza lo que no es numero finito", () => {
  for (const value of ["4", NaN, Infinity, null, undefined]) {
    assert.throws(() => formatTotal(value), TypeError);
  }
});
EOF
git add -A
git commit -qm "feat: cambio"
git diff main...HEAD > doc/sdd/001-facturas/review-package.diff
