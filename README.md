### Order & Returns Management System (Backend)

Stack: FastAPI, PostgreSQL, Celery, RabbitMQ

### Prerequisites

- Docker and Docker Compose

### Quick start

1. Build and start all services:
   - `docker compose up -d --build`
2. Apply database migrations:
   - `docker compose exec web alembic upgrade head`
3. Verify services:
   - App health: `http://localhost:8000/health`
   - OpenAPI docs: `http://localhost:8000/docs`
   - Metrics: `http://localhost:8000/metrics` (Prometheus format)
   - Payment gateway: `http://localhost:9000/docs`
   - RabbitMQ mgmt UI: `http://localhost:15672` (guest/guest)
4. Stop services:
   - `docker compose down`

### Services

- `web`: FastAPI application
- `worker`: Celery worker (broker: RabbitMQ)
- `payment-gateway`: Local mock payment gateway (logs refund requests)
- `postgres`: PostgreSQL database
- `rabbitmq`: Message broker with management UI

### Environment

- `DATABASE_URL=postgresql+psycopg://oms_user:oms_pass@postgres:5432/oms_db`
- `CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//`
- `TIMEZONE=Asia/Kolkata`, `CURRENCY=INR`
- `PAYMENT_GATEWAY_BASE_URL=http://payment-gateway:9000`
- `INVOICE_OUTPUT_DIR=./invoices`

### Observability

- Request ID: header `X-Request-ID` echoed on responses; also available in `request.state.request_id`
- Metrics: `/metrics` endpoint exposes Prometheus metrics; basic `http_requests_total` by path/method/status
- Logs: follow services with `docker compose logs -f web`, `docker compose logs -f worker`, `docker compose logs -f payment-gateway`

### Database Schema (tables)

- `orders`: Customer orders and their lifecycle.
  - id (bigint PK), order_number (unique), customer_id, currency, state, created_at, updated_at
- `order_items`: Line items per order.
  - id (bigint PK), order_id (FK), sku, title, quantity, unit_price_minor
- `returns`: Return requests for delivered orders.
  - id (bigint PK), order_id (FK), state, reason, created_at, updated_at
- `return_items`: Item-level details for returns (partial allowed).
  - id (bigint PK), return_id (FK), order_item_id (FK), quantity
- `state_transitions`: Audit trail for state changes.
  - id (bigint PK), entity_type ('order'|'return'), entity_id, from_state, to_state, actor, reason, created_at

### Development

- Lint: `flake8`
- Test: `pytest`

### Test
TEST CASE ANALYSIS : docker compose exec web pytest -q
REPORT GENERATION :  docker compose exec web pytest --cov=app --cov=worker --cov-report=html -q
<!-- open htmlcov/index.html -->

### Reset database (dev)

- Full reset (removes DB volume):
  - `docker compose down -v`
  - `docker compose up -d --build`
  - `docker compose exec web alembic upgrade head`
- Quick reset without recreating containers (drops all tables):
  - `docker compose exec postgres psql -U oms_user -d oms_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"`
  - `docker compose exec web alembic upgrade head`

