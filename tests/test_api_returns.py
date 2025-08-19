from fastapi.testclient import TestClient
from app.main import app
import uuid


def make_delivered_order(client: TestClient):
	payload = {
		"order_number": f"ORD-{uuid.uuid4().hex[:8]}",
		"customer_id": "cust-ret",
		"currency": "INR",
		"items": [
			{"sku": "RET-1", "title": "Ret Item", "quantity": 1, "unit_price_minor": 100},
		],
	}
	r = client.post("/orders", json=payload)
	assert r.status_code == 201
	order = r.json()
	order_id = order["id"]
	client.post(f"/orders/{order_id}/pay", json={})
	client.post(f"/orders/{order_id}/processing", json={})
	client.post(f"/orders/{order_id}/ship", json={})
	client.post(f"/orders/{order_id}/deliver", json={})
	return order


def test_returns_create_approve_and_history():
	client = TestClient(app)
	order = make_delivered_order(client)
	order_id = order["id"]

	# create return
	payload = {"order_id": order_id, "items": [{"order_item_id": order["items"][0]["id"], "quantity": 1}]}
	r = client.post("/returns", json=payload)
	assert r.status_code == 201
	ret = r.json()
	ret_id = ret["id"]

	# approve
	assert client.post(f"/returns/{ret_id}/approve", json={}).status_code == 200

	# history
	r = client.get(f"/returns/{ret_id}/history")
	assert r.status_code == 200
	assert isinstance(r.json(), list)

	# 404
	assert client.get("/returns/9999999").status_code in (404, 422)
	assert client.get("/returns/9999999/history").status_code in (404, 422)
