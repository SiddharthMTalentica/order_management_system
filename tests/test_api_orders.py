from fastapi.testclient import TestClient
from app.main import app
import uuid


def test_orders_create_list_get_history_and_404s():
	client = TestClient(app)
	order_number = f"ORD-{uuid.uuid4().hex[:8]}"
	payload = {
		"order_number": order_number,
		"customer_id": "cust-api",
		"currency": "INR",
		"items": [
			{"sku": "AP-1", "title": "API Item", "quantity": 1, "unit_price_minor": 999},
		],
	}
	# create
	r = client.post("/orders", json=payload)
	assert r.status_code == 201, r.text
	order = r.json()
	order_id = order["id"]

	# list
	r = client.get("/orders")
	assert r.status_code == 200
	assert any(o["id"] == order_id for o in r.json())

	# get
	r = client.get(f"/orders/{order_id}")
	assert r.status_code == 200

	# history after no transition yet (creation not logged)
	r = client.get(f"/orders/{order_id}/history")
	assert r.status_code == 200
	assert isinstance(r.json(), list)

	# 404 for non-existent
	assert client.get("/orders/9999999").status_code in (404, 422)
	assert client.get("/orders/9999999/history").status_code in (404, 422)
