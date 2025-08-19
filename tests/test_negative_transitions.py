from fastapi.testclient import TestClient
from app.main import app
import uuid


def new_order(client: TestClient):
	payload = {
		"order_number": f"ORD-{uuid.uuid4().hex[:8]}",
		"customer_id": "cust-neg",
		"currency": "INR",
		"items": [
			{"sku": "NEG-1", "title": "Neg Item", "quantity": 1, "unit_price_minor": 100},
		],
	}
	r = client.post("/orders", json=payload)
	assert r.status_code == 201
	return r.json()


def test_invalid_cancellation_after_processing():
	client = TestClient(app)
	order = new_order(client)
	order_id = order["id"]
	client.post(f"/orders/{order_id}/pay", json={})
	client.post(f"/orders/{order_id}/processing", json={})
	r = client.post(f"/orders/{order_id}/cancel", json={})
	assert r.status_code == 400


def test_return_cannot_be_initiated_before_delivery():
	client = TestClient(app)
	order = new_order(client)
	order_id = order["id"]
	r = client.post("/returns", json={"order_id": order_id, "items": []})
	assert r.status_code == 400
