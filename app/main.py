from fastapi import FastAPI
from prometheus_client import CollectorRegistry, CONTENT_TYPE_LATEST, Counter, generate_latest
from fastapi.responses import Response

from app.api.orders import router as orders_router
from app.api.returns import router as returns_router
from app.middleware.request_id import request_id_middleware

app = FastAPI(title="Order & Returns Management System")

# Middleware
app.middleware("http")(request_id_middleware)

# Metrics
registry = CollectorRegistry()
requests_total = Counter("http_requests_total", "Total HTTP requests", ["path", "method", "status"], registry=registry)


@app.middleware("http")
async def metrics_middleware(request, call_next):
	response = await call_next(request)
	try:
		requests_total.labels(path=request.url.path, method=request.method, status=str(response.status_code)).inc()
	except Exception:
		pass
	return response


app.include_router(orders_router)
app.include_router(returns_router)


@app.get("/metrics")
def metrics() -> Response:
	return Response(generate_latest(registry), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health() -> dict:
	return {"status": "ok"}
