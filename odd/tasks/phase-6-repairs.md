# Phase 6 — Repairs

## Status

- State: active
- Route: organic development (ODD), delegated implementation per work unit
- Repository branch at creation: `feature/phase-5-transfers-counts`
- Active feature branch: `feature/phase-6-repairs`
- Next task: `F6-04 — Charge repairs through real sales`
- Delivery strategy: `ask-on-risk`
- Chain strategy: unset
- Engram mirror: active
- Forecast: substantial multi-area work across backend models/services/API/tests, frontend API/screen integration, and API documentation; split into reviewable work units before implementation

## Objective

Implement Phase 6 from `docs/PLAN.md`: operational repair intake, immutable repair status history, validated workflow transitions, and payment/delivery rules integrated with real sales so repairs cannot be double-charged or delivered unpaid.

## Problem and why it matters

Repairs are currently mostly read-only API data plus frontend-local actions. Payment and delivery state are not authoritative on the backend, status history is not immutable, and the frontend maps backend states into local concepts with unknown payment/delivery status. That permits double sources of truth, double collection risk, and delivery without enforceable payment evidence.

## Known Phase 6 requirements

1. Unify frontend and backend repair states.
2. Support repair intake with cost, price, and relevant dates.
3. Store immutable status history and validate transitions.
4. Charge repairs through real sales.
5. Prevent double charge.
6. Prevent delivery before payment.
7. Separate finished, paid, and delivered concepts.

## Initial exploration evidence

- `docs/PLAN.md` defines Phase 6 scope and exit bullets under “Fase 6 — Reparaciones”.
- `backend/app/models/repairs.py` currently has one `Repair` model with `RepairStatus` values `recibido`, `pendiente_taller`, `en_proceso`, `terminado`, `enviado`; no payment or delivered state is persisted.
- `backend/app/api/v1/repairs.py` currently exposes read-only `GET /repairs` with optional status filter.
- `backend/app/schemas/repairs.py` exposes only `RepairRead`.
- `frontend/src/lib/api.js` maps repair payment/delivery as unknown or false and compresses backend statuses to local UI statuses.
- `frontend/src/domain/appModel.js` keeps repair write actions as no-op placeholders in API-connected mode.
- `frontend/src/screens/index.jsx` already contains repair UI forms/actions, but they are not backed by repair write APIs.
- `backend/tests/test_domain_api.py` has existing read-only repair coverage; no dedicated Phase 6 tests exist yet.
- Delegated exploration confirmed the draft migration mirrors this limited model, backend seed data has five disposable demo repairs without price/payment/delivery/history, `repairToPosItem()` has no callers, and checkout currently requires inventory-backed `SaleItem.variant_id`, so repair charging needs a deliberate service-line/sale-link design rather than the unused frontend pseudo-item.

## Product decisions

1. Repairs remain globally visible, matching the current read-only endpoint behavior, but new operational records still need the selected branch context required for folio generation and sale/cash-session linkage.
2. New repair folios use `RP-SUC-AÑO-NÚMERO`.
3. Repair service workflow is `received` → `in_workshop` → `ready` (`Recibida` → `En taller` → `Lista`); legacy `enviado` is not preserved as a distinct Phase 6 service state.
4. Store only the customer-facing repair price for now; no internal repair cost is persisted in Phase 6.
5. Registered client is preferred for intake, but exceptional free-text customer intake is allowed with explicit confirmation.
6. Repair collection is recorded through a real linked sale, not a standalone repair payment ledger.
7. Partial payments are allowed.
8. Approved credit counts as paid enough for delivery, with debt remaining in accounts receivable.
9. A partially paid repair may be delivered by any otherwise-authorized user only after explicit confirmation; the remaining balance must remain visible/auditable.
10. A `ready` repair may reopen to `in_workshop` only with a mandatory reason recorded in immutable history.
11. Delivered repairs are terminal: no workflow, price, payment, or primary data changes after delivery.
12. If the linked sale is cancelled before delivery, the repair becomes blocked for admin/manager review before it can be reactivated or charged again.
13. Cancelling a linked repair sale after delivery is prohibited.

## Product decisions still required before source implementation

None currently known. If implementation exposes a new edge case, pause and resolve it before writing beyond that work unit.

## Work units

### F6-00 — Resolve repair workflow decisions and slice plan

- [x] Complete delegated architecture mapping for backend, frontend, tests, and docs.
- [x] Resolve remaining product decisions above.
- [x] Select chain strategy if the forecasted review workload exceeds a single reviewable PR: keep `ask-on-risk` with work-unit commits and promote to chained PRs if a unit approaches the review budget.
- [x] Confirm effective test mode and commands.
- [x] Reconcile this task document and Engram mirror before source writes.
- Route: parent coordination plus read-only delegated exploration.
- Checks: clean branch state and documented decisions.
- Evidence:
  - Read-only delegated exploration completed under task `mux5rp26-1-0kco` and mapped backend model/API/schema/test gaps, frontend mapping/no-op write gaps, seed/demo state, sale integration constraints, candidate surfaces, and verification commands.
  - User decisions captured: repairs globally visible; folios `RP-SUC-AÑO-NÚMERO`; service workflow `received` → `in_workshop` → `ready`; only customer-facing price is stored; registered client preferred with confirmed free-text exception; repair collection through a real linked sale; partial payments allowed; approved credit counts as paid enough for delivery; partially paid repairs may be delivered by any otherwise-authorized user after explicit confirmation, with remaining balance visible/auditable; `ready` may reopen with mandatory reason; delivered repairs are terminal; pre-delivery sale cancellation blocks the repair for admin/manager review; post-delivery linked sale cancellation is prohibited.
  - Verification mode: strict TDD for backend behavior; focused command starts as `cd backend && .venv/bin/pytest -q tests/test_repairs_phase6.py`; regression commands are full backend pytest and Ruff, with frontend build added when frontend work starts.

### F6-01 — Persist repair workflow foundations

- [x] Align backend repair state vocabulary with separated finished/paid/delivered concepts.
- [x] Add immutable repair status history model/table and relationships.
- [x] Add persisted payment/delivery references needed to prevent double charge and unpaid delivery.
- [x] Add model/migration/schema tests for constraints and history shape.
- [x] Update API contract vocabulary.
- Route: delegated writer.
- Candidate surfaces:
  - `backend/app/models/repairs.py`
  - `backend/app/models/__init__.py`
  - `backend/app/schemas/repairs.py`
  - `backend/app/seed_data.json`
  - `backend/alembic/versions/0009_phase6_repairs.py`
  - `backend/tests/test_repairs_phase6.py`
  - `backend/tests/test_domain_api.py`
  - `backend/tests/test_seed.py`
  - `docs/API_CONTRACT.md`
- Checks: focused backend repair tests, full backend tests, Ruff.
- Evidence:
  - Delegated writer implemented Phase 6 repair foundations with strict TDD: initial focused RED `3 failed, 2 passed` for canonical enum rejection, migration trigger SQL, and downgrade ordering; GREEN focused `5 passed`.
  - Changed foundations include canonical `RepairStatus` values `received`, `in_workshop`, `ready`; canonical `price` field; nullable `branch_id`, unique nullable `sale_id`, `delivered_at`, `blocked_for_review`; and `RepairStatusHistory` with repair/from/to/actor/timestamp/note.
  - PostgreSQL migration `0009_phase6_repairs.py` maps legacy statuses into canonical values, renames `quoted_price` to `price`, adds repair operational columns, creates `repair_status_history`, installs an UPDATE/DELETE rejection trigger for append-only history, and clears the status default before downgrade enum conversion.
  - Writer checks: `cd backend && .venv/bin/pytest -q tests/test_repairs_phase6.py tests/test_domain_api.py tests/test_seed.py` → 48 passed in 2.31s; `cd backend && .venv/bin/pytest -q` → 141 passed in 4.33s; `cd backend && .venv/bin/ruff check --no-cache app tests alembic` → all checks passed; `git diff --check` passed.
  - Native assessment was unassessable because new untracked Phase 6 files require explicit review declaration; risk-gated path required independent verification.
  - Independent verification initially failed transitional vocabulary/downgrade/append-only concerns; correction removed legacy enum aliases and `quoted_price`, updated schema/tests/seed to canonical values, fixed downgrade ordering, and added PostgreSQL append-only trigger/function.
  - Final independent verification verdict: PASS, no blocking findings; focused repair/domain/seed tests 48 passed in 2.25s; full backend 141 passed in 4.41s; Ruff all checks passed. Risk: migration and trigger behavior are structurally tested but not applied to live PostgreSQL.
  - Work-unit commit was created as `feat(repairs): add workflow foundations`; final amended identity is reported in session output because a commit cannot contain its own final hash.

### F6-02 — Implement repair intake and update APIs

- [x] Add repair create/update schemas and routes.
- [x] Validate required client, piece/service, price, received/expected dates, branch visibility, and roles.
- [x] Generate retry-safe repair intake results with idempotency where mutations need uncertainty safety.
- [x] Preserve branch/visibility rules once resolved in F6-00.
- [x] Add lifecycle and authorization tests.
- [x] Update API contract.
- Route: delegated writer, completed inline after two writer timeouts left a partial candidate.
- Candidate surfaces:
  - `backend/app/api/v1/repairs.py`
  - `backend/app/schemas/repairs.py`
  - `backend/app/services/repairs.py`
  - `backend/tests/test_repairs_phase6.py`
  - `docs/API_CONTRACT.md`
  - `odd/tasks/phase-6-repairs.md`
- Checks: focused backend repair tests, full backend tests, Ruff.
- Evidence:
  - The first delegated writer timed out after leaving strict RED tests in `backend/tests/test_repairs_phase6.py`; a second writer attempt also timed out after partial implementation. Parent completed the bounded candidate because the implementation was already confined to the F6-02 surfaces.
  - Implemented `POST /repairs` with required `Idempotency-Key`, branch authorization, `RP-SUC-YEAR-NUMBER` folio generation, registered-client canonical name, confirmed free-text customer exception, initial `received` status, and initial `RepairStatusHistory` entry.
  - Implemented `PATCH /repairs/{id}` for intake fields only, scoped to visible branches, rejecting delivered or blocked-for-review repairs and forbidding service status, branch, sale, delivery, and review-block mutations through schema `extra=forbid`.
  - Preserved global repair listing while hidden-branch mutations return `404`.
  - Parent checks: `cd backend && .venv/bin/pytest -q tests/test_repairs_phase6.py` → 9 passed in 0.64s; `cd backend && .venv/bin/pytest -q tests/test_repairs_phase6.py tests/test_domain_api.py tests/test_seed.py` → 52 passed in 2.40s; full backend `145 passed in 4.59s`; Ruff initially failed on one unused import, then passed after cleanup.
  - Independent verification initially failed only stale ODD tracking; implementation, API contract, and checks passed. The task document was then updated with this evidence.
  - Native review approved and was acknowledged under lineage `review-0b635b8f37c0995e` for target `sha256:d5ed6b8d459c700f60d7408c4881ef876aefa6c243f1bb81db39d364df85a197`.
  - Work-unit commit was created as `feat(repairs): add intake APIs`; final amended identity is reported in session output because a commit cannot contain its own final hash.

### F6-03 — Implement status transitions and immutable history

- [x] Add explicit status-transition endpoint(s).
- [x] Enforce allowed transitions and immutable history append behavior.
- [x] Keep completed, paid, and delivered states separate.
- [x] Reject transitions for delivered and blocked-for-review repairs.
- [x] Add transition/history tests including invalid transitions.
- [x] Update API contract.
- Route: delegated writer.
- Candidate surfaces:
  - `backend/app/api/v1/repairs.py`
  - `backend/app/schemas/repairs.py`
  - `backend/app/services/repairs.py` if introduced
  - `backend/tests/test_*repair*.py` or focused domain API tests
  - `docs/API_CONTRACT.md`
- Checks: focused backend repair tests, full backend tests, Ruff.
- Evidence:
  - Strict TDD RED: focused repair tests failed `3 failed, 9 passed` because
    `POST /api/v1/repairs/{repair_id}/transition` did not exist and returned 404.
  - Added `POST /repairs/{repair_id}/transition`, scoped to the actor's visible
    branches while preserving global list reads.
  - The service permits `received` → `in_workshop` → `ready` and reasoned
    `ready` → `in_workshop`; it rejects no-op, skipped/backward, delivered, and
    blocked-for-review transitions without appending history.
  - Every accepted transition locks and updates the repair and appends
    `RepairStatusHistory` with old/new status, actor, and normalized note in the
    route transaction. First readiness sets `completed_at`; reopening retains it
    and does not change sale, payment, delivery, or review-block state.
  - Focused GREEN: `cd backend && .venv/bin/pytest -q tests/test_repairs_phase6.py`
    → 12 passed in 0.67s.
  - Regression checks: repair/domain/seed selection → 55 passed in 2.49s; full
    backend → 148 passed in 4.59s; Ruff → all checks passed.
  - Native assessment reported medium risk under budget; native review approved and was acknowledged under lineage `review-ee7cd428f97556e4` for target `sha256:e93c4ceaac3714750fbbbeb64da81e916737c706a84833652687ce818c89e269`.
  - Work-unit commit was created as `feat(repairs): add status transitions`; final amended identity is reported in session output because a commit cannot contain its own final hash.

### F6-04 — Charge repairs through real sales

- [x] Add the chosen sale/repair linkage so a repair can be charged exactly once.
- [x] Make repair payment idempotent and prevent double charge.
- [x] Reflect paid state from the authoritative sale/payment result.
- [x] Preserve existing POS/sales invariants and money handling.
- [x] Add payment, double-charge, partial-payment, credit, and no-stock tests.
- [x] Update API contract.
- Route: delegated writer.
- Candidate surfaces:
  - `backend/app/models/repairs.py`
  - `backend/app/models/sales.py`
  - `backend/alembic/versions/0010_phase6_repair_sales.py`
  - `backend/app/services/pos.py`
  - `backend/app/api/v1/repairs.py`
  - `backend/app/schemas/repairs.py`
  - `backend/app/schemas/sales.py`
  - `backend/app/services/repairs.py`
  - `backend/tests/test_repairs_phase6.py`
  - `docs/API_CONTRACT.md`
- Checks: focused backend repair/POS tests, full backend tests, Ruff.
- Evidence:
  - Strict TDD RED: `cd backend && .venv/bin/pytest -q tests/test_repairs_phase6.py`
    failed `5 failed, 11 passed` for the missing service-line model/migration and
    missing charge endpoint.
  - Added nullable inventory variant plus unique `repair_id` sale-item source,
    protected by an exclusive-source check constraint and migration
    `0010_phase6_repair_sales.py`.
  - Added idempotent `POST /repairs/{repair_id}/charge`: it locks the repair,
    requires an open branch cash session, creates one real `VTA-*` sale/service
    item, rejects overpayment and double charge, and emits no stock movement.
  - Partial payments remain visible as `paid_amount` and `balance`; approved
    mayoreo credit uses the existing credit-limit/ledger rules and counts toward
    `paid_enough`. Repair reads derive these fields from the linked sale/payments.
  - Linked repair-sale cancellation skips inventory reversal, blocks the repair
    for review, and is rejected after delivery.
  - GREEN focused repair tests: 16 passed in 0.78s. Regression selection: 59
    passed in 2.71s. Full backend: 152 passed in 4.77s. Ruff: all checks passed.
  - Review-size note: the cohesive backend slice is 556 added/changed diff lines
    before this evidence update, including 193 focused test lines and migration/
    contract documentation; no frontend or delivery workflow was included.
  - Independent verification initially failed one schema contract issue: repair service lines returned `variant_id: null` while `SaleItemRead.variant_id` was typed as non-null. Correction changed it to `int | None` and added a regression assertion using `SaleItemRead.model_validate(...)`.
  - Re-verification verdict: PASS, no blocking findings. Focused repair tests 16 passed; repair/domain/seed selection 59 passed; full backend 152 passed; Ruff all checks passed. Residual risk: migration behavior was unit/source-validated, not applied to live PostgreSQL.
  - Native review approved and was acknowledged under lineage `review-cda3881fe48ccbf0` for target `sha256:6c4907602cb600b3bb07c8a906712e7cdb5ec5ad7149e2817ebb4cb39ea007e9`; advisory `R3-001` on `backend/alembic/versions/0010_phase6_repair_sales.py:49` was informational/non-blocking.
  - Work-unit commit was created as `feat(repairs): charge through sales`; final amended identity is reported in session output because a commit cannot contain its own final hash.

### F6-05 — Connect repair frontend to API workflows

- [ ] Add repair API adapters and response mappers for create/update/status/payment/delivery.
- [ ] Replace repair no-op API-mode actions with backend calls and refresh behavior.
- [ ] Remove repair payment/delivery unknown placeholders once backend exposes authoritative fields.
- [ ] Preserve existing Spanish UI copy and loading/error states.
- [ ] Build frontend production bundle.
- Route: delegated writer.
- Candidate surfaces:
  - `frontend/src/lib/api.js`
  - `frontend/src/domain/appModel.js`
  - `frontend/src/App.jsx`
  - `frontend/src/screens/index.jsx`
  - `frontend/README.md` if workflow docs need updating
- Checks: frontend production build plus focused structural spot-checks.
- Evidence: pending.

## Verification mode

- Backend focused runner: to be finalized in F6-00; likely `cd backend && .venv/bin/pytest -q tests/test_domain_api.py` until dedicated Phase 6 tests are created.
- Backend full runner: `cd backend && .venv/bin/pytest -q`.
- Backend lint runner: `cd backend && .venv/bin/ruff check --no-cache app tests alembic`.
- Frontend runner: `cd frontend && npm run build`.
- Strict TDD is preferred for behavior changes with deterministic expected outcomes; exact RED/GREEN evidence must be recorded when applicable.

## Closeout checklist

- [ ] All Phase 6 work units complete.
- [ ] Backend tests, Ruff, and frontend build recorded.
- [ ] `docs/PLAN.md` and `docs/CHANGELOG.md` updated.
- [ ] Native review lifecycle handled when enabled for each candidate.
- [ ] Work-unit commits recorded as evidence.
