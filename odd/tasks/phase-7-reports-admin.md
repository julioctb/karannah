# Phase 7 — Reports, Promotions, and Administration

## Status

- State: active
- Route: organic development (ODD), delegated implementation per work unit
- Repository branch at creation: `feature/phase-6-repairs`
- Active feature branch: `feature/phase-7-reports-admin`
- Next task: `F7-02 — Connect selected report frontend to API`
- Delivery strategy: `ask-on-risk`
- Chain strategy: unset
- Engram mirror: active
- Forecast: substantial multi-area work across backend report APIs/tests/docs and later frontend report/config/promotion/admin workflows; split into reviewable work units

## Objective

Implement Phase 7 from `docs/PLAN.md`: server-side reports by business date and authorized branches, persistent configuration that removes browser-local sources of truth, a promotion engine integrated with quote/checkout, and profile/role/assignment administration via the auth adapter.

## Initial priority

Start with the recommended first slice: server-side reports by business date and authorized branches. Promotions, persistent configuration, and user administration remain later Phase 7 work units.

## Known Phase 7 requirements

1. Promotion engine integrated with quote/checkout.
2. Server-side reports by business date and authorized branches.
3. Persistent configuration for company, branches, prices, tickets, and terminals; no browser-local configuration source of truth.
4. Profile/role/assignment administration via auth adapter, with local auth now and Supabase Auth Admin in Phase 9.

## Initial exploration evidence

- `docs/PLAN.md` marks Phase 7 open and names reports, promotions, persistent configuration, and admin.
- Existing backend report surface: `backend/app/api/v1/reports.py` exposes `GET /reports/credit-recovery`.
- Existing report schemas: `backend/app/schemas/reports.py` contains credit recovery report DTOs.
- Existing router includes reports through `backend/app/api/v1/router.py`.
- Phase 4 closeout already delivered credit recovery reporting; Phase 7 should extend the server-side reporting pattern rather than duplicate frontend-local report logic.
- Delegated exploration recommended `GET /reports/sales-summary` as the first slice because existing UI already shows total sold, operations, and credit-sale count; `Sale` already has total, condition, status, branch, and timestamp; inventory valuation and top-products need more semantics/design.
- Frontend report preview currently calculates sales/inventory/product/client/receivable/repair reports from local/demo arrays in `frontend/src/screens/index.jsx`; F7-02 should replace the sales report first.

## Product decisions for first report slice

1. Count confirmed net sales only; cancelled sales are excluded.
2. Report revenue basis is invoiced sale total (`Sale.total`), not collected cash/payments.
3. Report access matches credit recovery: `admin` and `encargado`; vendors do not access this report.
4. Unauthorized branch filter returns a valid empty `200` report, matching current credit report behavior.
5. First slice returns totals only: total sold, operation count, and credit-sale count.
6. Date filters use the existing commercial-day/business-timezone semantics.

## Work units

### F7-00 — Map Phase 7 reporting surfaces and first slice

- [x] Complete delegated read-only mapping for backend reports, frontend report UI/local data, existing tests, and API docs.
- [x] Select the first report slice by business value and reviewability: `GET /reports/sales-summary` totals.
- [x] Confirm effective test mode and commands.
- [x] Reconcile this task document and Engram mirror before source writes.
- Route: parent coordination plus read-only delegated exploration.
- Checks: clean branch state and documented slice decision.
- Evidence:
  - Read-only delegated exploration mapped backend report patterns, frontend local report calculations, test fixtures, and candidate surfaces.
  - Selected F7-01 as backend-only `GET /reports/sales-summary` returning totals for confirmed net sales by business-date range and authorized branch scope.
  - User decisions captured: confirmed net sales only, `Sale.total` revenue basis, admin/encargado access, unauthorized branch returns empty `200`, totals only, commercial-day date filters.
  - Focused backend command: `cd backend && .venv/bin/pytest -q tests/test_domain_api.py -k sales_summary`; regressions: full backend pytest and Ruff.

### F7-01 — Implement first server-side report slice

- [x] Add or extend backend report endpoint(s) for the selected report.
- [x] Scope data by authorized branches and business-date filters.
- [x] Add schemas, focused tests, and API contract documentation.
- [x] Preserve existing credit recovery report behavior.
- Route: delegated writer.
- Surfaces: `backend/app/api/v1/reports.py`, `backend/app/schemas/reports.py`,
  `backend/tests/test_domain_api.py`, `docs/API_CONTRACT.md`, and this task file.
- Checks: focused backend report tests, full backend tests, Ruff.
- Evidence:
  - Strict TDD RED: sales-summary tests failed with `404 Not Found` before the route existed.
  - GREEN: focused sales-summary tests pass for confirmed/cancelled totals, invoiced
    revenue, credit count, commercial-day bounds, role access, and branch scope.
  - `GET /reports/sales-summary` returns totals-only data from `Sale.total` for
    confirmed sales and retains the credit recovery report contract.
  - Writer checks: `cd backend && .venv/bin/pytest -q tests/test_domain_api.py -k sales_summary` → 3 passed, 38 deselected; `cd backend && .venv/bin/pytest -q tests/test_domain_api.py -k 'sales_summary or credit_recovery_report'` → 4 passed, 37 deselected; full backend → 155 passed; Ruff → all checks passed.
  - Independent verification verdict: PASS, no blocking findings; noted residual risk that SQLite tests do not integration-test production database timezone behavior.
  - Native review approved and was acknowledged under lineage `review-77119cd1e2c404c5` for target `sha256:f377192bcf1d49126a105e9112a2852afefa1b18ba565fbfdf4bb3dfcc89927c`.
  - Work-unit commit was created as `feat(reports): add sales summary endpoint`; final amended identity is reported in session output because a commit cannot contain its own final hash.

### F7-02 — Connect selected report frontend to API

- [x] Add frontend API adapter and mapper for the selected report.
- [x] Replace local/demo report calculations for that report with server data.
- [x] Preserve existing Spanish UI copy and loading/error states.
- [x] Build frontend production bundle.
- Route: delegated writer.
- Surfaces: `frontend/src/lib/api.js`, `frontend/src/App.jsx`,
  `frontend/src/domain/appModel.js`, `frontend/src/screens/index.jsx`,
  `frontend/README.md`, and this task file.
- Checks: frontend production build plus focused structural spot-checks.
- Evidence:
  - Added the authenticated sales-summary adapter with the same `URLSearchParams`
    filter style and request/error conventions as credit recovery.
  - The sales report now uses server totals and authorized `sucursales`; other
    report previews retain their isolated demo behavior.
  - Preserved date validation and Spanish preview metrics while adding API loading,
    error, and retry states.
  - Strict TDD was not active because no frontend test runner is configured.
  - `cd frontend && npm run build` → passed; Vite retained the pre-existing
    invalid `/* @__PURE__ */` annotation warning at `src/screens/index.jsx:4522`.
  - Native review approved and was acknowledged under lineage `review-5ae09ea17ebfc540` for target `sha256:08ceed9cf48cdeae2c73ecede4569210c09d8c187ec2347e3c69226052f4df8f`; advisory `R3-sales-report-stale-response` at `frontend/src/screens/index.jsx:2864-2877` was informational/non-blocking.
  - Work-unit commit was created as `feat(frontend): connect sales summary report`; final amended identity is reported in session output because a commit cannot contain its own final hash.

### F7-03 — Persistent configuration foundations

- [ ] Map current localStorage/config sources.
- [ ] Add backend persistence for selected configuration domain.
- [ ] Replace frontend local source of truth for that domain.
- Route: delegated writer after reports slice.
- Evidence: pending.

### F7-04 — Promotion engine slice

- [ ] Design promotion rule scope integrated with quote/checkout.
- [ ] Implement one reviewable backend promotion slice with tests.
- [ ] Connect frontend visibility if needed.
- Route: delegated writer after reports/config foundations.
- Evidence: pending.

### F7-05 — Profile/role/assignment admin slice

- [ ] Map existing local auth/profile administration capabilities.
- [ ] Add reviewable admin workflow through the auth adapter.
- [ ] Keep Supabase Admin integration reserved for Phase 9.
- Route: delegated writer after reports/config foundations.
- Evidence: pending.

## Verification mode

- Backend focused runner: to be finalized in F7-00; likely a new or extended report-focused pytest file.
- Backend full runner: `cd backend && .venv/bin/pytest -q`.
- Backend lint runner: `cd backend && .venv/bin/ruff check --no-cache app tests alembic`.
- Frontend runner: `cd frontend && npm run build`.
- Strict TDD is preferred for backend behavior with deterministic expected outcomes; frontend remains ordinary build/structural validation unless a test runner is added.

## Closeout checklist

- [ ] All selected Phase 7 work units complete or consciously deferred.
- [ ] Backend tests, Ruff, and frontend build recorded where applicable.
- [ ] `docs/PLAN.md` and `docs/CHANGELOG.md` updated.
- [ ] Native review lifecycle handled when enabled for each candidate.
- [ ] Work-unit commits recorded as evidence.
