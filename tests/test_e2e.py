from fastapi.testclient import TestClient
from app.main import app
import uuid


def create_order(client: TestClient):
	unique_order_number = f"ORD-{uuid.uuid4().hex[:8]}"
	payload = {
		"order_number": unique_order_number,
		"customer_id": "cust-1",
		"currency": "INR",
		"items": [
			{"sku": "SKU-1", "title": "Item 1", "quantity": 1, "unit_price_minor": 1000},
			{"sku": "SKU-2", "title": "Item 2", "quantity": 2, "unit_price_minor": 500},
		],
	}
	r = client.post("/orders", json=payload)
	assert r.status_code == 201, r.text
	return r.json()


def test_order_happy_path_and_return_flow():
	client = TestClient(app)
	order = create_order(client)
	order_id = order["id"]

	# invalid: ship before processing
	r = client.post(f"/orders/{order_id}/ship", json={})
	assert r.status_code == 400

	# pay -> processing -> ship -> deliver
	assert client.post(f"/orders/{order_id}/pay", json={}).status_code == 200
	assert client.post(f"/orders/{order_id}/processing", json={}).status_code == 200
	assert client.post(f"/orders/{order_id}/ship", json={}).status_code == 200
	assert client.post(f"/orders/{order_id}/deliver", json={}).status_code == 200

	# create return (must be delivered)
	ret_payload = {
		"order_id": order_id,
		"items": [{"order_item_id": order["items"][0]["id"], "quantity": 1}],
	}
	r = client.post("/returns", json=ret_payload)
	assert r.status_code == 201, r.text
	ret = r.json()
	ret_id = ret["id"]

	# approve -> in-transit -> received -> complete
	assert client.post(f"/returns/{ret_id}/approve", json={}).status_code == 200
	assert client.post(f"/returns/{ret_id}/in-transit", json={}).status_code == 200
	assert client.post(f"/returns/{ret_id}/received", json={}).status_code == 200
	assert client.post(f"/returns/{ret_id}/complete", json={}).status_code == 200

	# negative: cancel after processing should fail
	r = client.post(f"/orders/{order_id}/cancel", json={})
	assert r.status_code == 400


def test_return_reject_path():
	client = TestClient(app)
	order = create_order(client)
	order_id = order["id"]
	assert client.post(f"/orders/{order_id}/pay", json={}).status_code == 200
	assert client.post(f"/orders/{order_id}/processing", json={}).status_code == 200
	assert client.post(f"/orders/{order_id}/ship", json={}).status_code == 200
	assert client.post(f"/orders/{order_id}/deliver", json={}).status_code == 200

	ret_payload = {
		"order_id": order_id,
		"items": [{"order_item_id": order["items"][0]["id"], "quantity": 1}],
	}
	r = client.post("/returns", json=ret_payload)
	assert r.status_code == 201
	ret_id = r.json()["id"]

	# reject becomes terminal
	assert client.post(f"/returns/{ret_id}/reject", json={}).status_code == 200
	assert client.post(f"/returns/{ret_id}/in-transit", json={}).status_code == 400
