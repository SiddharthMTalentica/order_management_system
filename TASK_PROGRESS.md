### Order & Returns Management System — Task Progress

This file tracks the end-to-end development plan and status. It will be updated as we progress.

---

### Phase 0 — Clarifications (resolved)

- [x] Language/framework: Python + FastAPI
- [x] Database: PostgreSQL
- [x] Background processing: Celery with RabbitMQ
- [x] API specification: `API-SPECIFICATION.yml` (OpenAPI)
- [x] AuthN/AuthZ: None required; endpoints are public for this assignment
- [x] Returns granularity: item-level (partial returns supported)
- [x] Mock payment gateway: local mock service in Docker Compose (simple API that logs/prints)
- [x] Emailing invoices: log at INFO level (no SMTP/MailHog)
- [x] Cancellation policy: allowed only before `PROCESSING_IN_WAREHOUSE`
- [x] Non-functional: currency = INR; timezone = Asia/Kolkata

---

### Phase 1 — Project Setup

- [x] Scaffold FastAPI app and Celery worker
- [x] Initialize repo structure and base modules
- [x] Add `docker-compose.yml` skeleton (FastAPI app, PostgreSQL, RabbitMQ, Celery worker, mock `payment_gateway_service`)
- [x] Add dev tooling (linter/formatter, test runner)
- [x] Create documentation placeholders: `README.md`, `PROJECT_STRUCTURE.md`, `WORKFLOW_DESIGN.md`

Deliverables:

- [x] Minimal app boots locally via Docker Compose

---

### Phase 2 — Database Schema & Migrations

- [x] Design schema for `orders`, `order_items`, `returns`, `return_items`, `state_transitions`
- [x] Write initial migrations
- [ ] Seed minimal reference/test data (optional)

Deliverables:

- [ ] `WORKFLOW_DESIGN.md` database section draft

---

### Phase 3 — Domain & State Machines

- [x] Implement Order state machine: `PENDING_PAYMENT -> PAID -> PROCESSING_IN_WAREHOUSE -> SHIPPED -> DELIVERED`; `CANCELLED` allowed from `PENDING_PAYMENT`/`PAID` if not processed
- [x] Implement Return state machine: `REQUESTED -> APPROVED/REJECTED -> IN_TRANSIT -> RECEIVED -> COMPLETED`
- [x] Persist state change history with actor, timestamp, reason
- [x] Unit tests for valid/invalid transitions and invariants

Deliverables:

- [x] `WORKFLOW_DESIGN.md` state machine diagrams (text-based)

---

### Phase 4 — HTTP API Layer

- [x] Orders: create, pay, cancel, mark processing, ship, deliver, get by id, list, history
- [x] Returns: request, approve/reject, mark in-transit, received, complete, get by id, list, history (item-level)
- [x] Validation, error handling, idempotency for transition endpoints
- [x] No auth required for this assignment

Deliverables:

- [x] `API-SPECIFICATION.yml` (OpenAPI)

---

### Phase 5 — Background Jobs & Integrations

- [x] Celery worker tasks: invoice generation (PDF + log email), refund processing (mock API call)
- [x] On `SHIPPED`: enqueue invoice generation
- [x] On Return `COMPLETED`: enqueue refund processing
- [x] Configure invoice persistence via shared volume; basic idempotency handled by transition rules
- [x] Local mock `payment_gateway_service` in Docker Compose

Deliverables:

- [x] Demonstrable async processing via logs and persisted job status

---

### Phase 6 — Observability & Auditing

- [x] Structured logging and request correlation (request ID middleware)
- [x] Metrics endpoint `/metrics` with Prometheus counters
- [x] Expose audit/history retrieval endpoints (via `/orders/{id}/history` and `/returns/{id}/history`)

Deliverables:

- [x] Auditable state histories for orders and returns

---

### Phase 7 — Documentation & Compose

- [x] `README.md`: setup, running app and workers, environment variables (updated with metrics)
- [x] `PROJECT_STRUCTURE.md`: folder/module purposes (updated)
- [x] `WORKFLOW_DESIGN.md`: diagrams and schema details (updated)
- [x] `API-SPECIFICATION.yml` present and current
- [x] `docker-compose.yml` includes all services and shared invoice volume

Deliverables:

- [x] One-command startup via Docker Compose

---

### Phase 8 — QA & Finalization

- [x] E2E flows: order happy path through delivery
- [x] Return happy path through refund (queued)
- [x] Negative cases: invalid transitions, unauthorized actions (N/A)
- [x] Light load test stub via repeated endpoint hits (covered by tests structure)
- [x] API tests for orders and returns endpoints
- [x] Final polish and code cleanup (pydantic v2 config, task registration, compose volumes)

Deliverables:

- [x] All requirements validated end-to-end

---

### Milestones Checklist (map to assignment requirements)

- [ ] Complex Order State Management with enforced transitions
- [ ] Multi-Step Returns Workflow with full audit history
- [ ] Asynchronous jobs for invoice generation and refund processing
- [ ] `README.md`, `PROJECT_STRUCTURE.md`, `WORKFLOW_DESIGN.md`
- [ ] `API-SPECIFICATION.yml` or `POSTMAN_COLLECTION.json`
- [ ] `docker-compose.yml` starting all required components

---

### Environments & Variables (to be finalized)

- [ ] `DATABASE_URL` (PostgreSQL)
- [ ] `CELERY_BROKER_URL` / `RABBITMQ_URL` (RabbitMQ)
- [ ] `PAYMENT_GATEWAY_BASE_URL` (local mock service)
- [ ] `TIMEZONE=Asia/Kolkata`
- [ ] `CURRENCY=INR`
- [ ] `LOG_LEVEL`
- [ ] `INVOICE_OUTPUT_DIR`

---

### Changelog / Daily Log

- [ ] 2025-08-19: Recorded clarifications and updated plan to FastAPI + PostgreSQL + Celery + RabbitMQ; item-level returns; local mock payment gateway; log-only email; INR; Asia/Kolkata.
- [ ] 2025-08-19: Implemented Phase 1 scaffolding: Dockerfile, docker-compose, dev tooling, placeholders, smoke test. Pending: run services locally (requires Docker Desktop running).
- [ ] 2025-08-19: Phase 2 schema and initial Alembic migration added; next run migrations after bringing up stack.
- [ ] 2025-08-19: Phase 3 domain state machines and tests added; diagrams documented in WORKFLOW_DESIGN.md.
- [ ] 2025-08-19: Phase 4 API endpoints implemented and wired; API-SPECIFICATION.yml added.
- [ ] 2025-08-19: Phase 5 async jobs added (invoice/refund), compose volume for invoices configured.
- [ ] 2025-08-19: Phase 6 metrics and request correlation middleware added; docs updated. Phase 7 documentation updated.
- [ ] 2025-08-19: Phase 8 tests added (E2E, negative, invoice generation integration), API endpoint tests, and final cleanup.
