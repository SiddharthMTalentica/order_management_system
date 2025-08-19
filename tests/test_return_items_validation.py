from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.order import OrderItem
from app.models.return_request import ReturnItem as ReturnItemModel
import uuid


def make_order(client: TestClient):
	payload = {
		"order_number": f"ORD-{uuid.uuid4().hex[:8]}",
		"customer_id": "cust-validate",
		"currency": "INR",
		"items": [
			{"sku": "VAL-1", "title": "Val Item 1", "quantity": 1, "unit_price_minor": 100},
			{"sku": "VAL-2", "title": "Val Item 2", "quantity": 2, "unit_price_minor": 200},
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


def test_return_requires_items():
	client = TestClient(app)
	order = make_order(client)
	r = client.post("/returns", json={"order_id": order["id"], "items": []})
	assert r.status_code == 400
	assert "at least one item" in r.text


def test_return_invalid_item_id():
	client = TestClient(app)
	order = make_order(client)
	invalid_item_id = 99999999
	r = client.post(
		"/returns",
		json={"order_id": order["id"], "items": [{"order_item_id": invalid_item_id, "quantity": 1}]},
	)
	assert r.status_code == 400
	assert "Invalid order_item_id" in r.text


def test_return_item_not_in_this_order():
	client = TestClient(app)
	order_a = make_order(client)
	order_b = make_order(client)

	# Pick an item id from order A, try to return it under order B
	with SessionLocal() as db:
		any_item_a = db.query(OrderItem).filter(OrderItem.order_id == order_a["id"]).first()
		assert any_item_a is not None

	r = client.post(
		"/returns",
		json={"order_id": order_b["id"], "items": [{"order_item_id": any_item_a.id, "quantity": 1}]},
	)
	assert r.status_code == 400
	assert "not in this order" in r.text


def test_return_items_persisted():
	client = TestClient(app)
	order = make_order(client)
	item_ids = [order["items"][0]["id"], order["items"][1]["id"]]
	r = client.post(
		"/returns",
		json={
			"order_id": order["id"],
			"items": [
				{"order_item_id": item_ids[0], "quantity": 1},
				{"order_item_id": item_ids[1], "quantity": 2},
			],
		},
	)
	assert r.status_code == 201, r.text
	ret = r.json()
	# Verify via DB
	with SessionLocal() as db:
		rows = db.query(ReturnItemModel).filter(ReturnItemModel.return_id == ret["id"]).all()
		assert len(rows) == 2
