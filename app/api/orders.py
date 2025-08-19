from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order import Order, OrderItem
from app.domain import order_service
from app.domain.states import OrderState
from app.schemas.order import OrderCreate, OrderRead, TransitionRequest

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderRead, status_code=201)
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
	if db.query(Order).filter(Order.order_number == payload.order_number).first():
		raise HTTPException(status_code=400, detail="order_number already exists")
	order = Order(
		order_number=payload.order_number,
		customer_id=payload.customer_id,
		currency=payload.currency,
	)
	for it in payload.items:
		order.items.append(
			OrderItem(
				sku=it.sku,
				title=it.title,
				quantity=it.quantity,
				unit_price_minor=it.unit_price_minor,
			)
		)
	db.add(order)
	db.commit()
	db.refresh(order)
	return order


@router.get("/{order_id}", response_model=OrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
	order = db.get(Order, order_id)
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	return order


@router.get("", response_model=list[OrderRead])
def list_orders(db: Session = Depends(get_db)):
	return db.query(Order).order_by(Order.id.desc()).all()


@router.post("/{order_id}/pay", response_model=OrderRead)
def mark_paid_endpoint(order_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	order = db.get(Order, order_id)
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	try:
		order_service.mark_paid(db, order, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(order)
		return order
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/processing", response_model=OrderRead)
def mark_processing_endpoint(order_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	order = db.get(Order, order_id)
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	try:
		order_service.mark_processing(db, order, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(order)
		return order
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/ship", response_model=OrderRead)
def mark_shipped_endpoint(order_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	order = db.get(Order, order_id)
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	try:
		order_service.mark_shipped(db, order, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(order)
		# enqueue invoice generation
		try:
			from worker.tasks import generate_invoice_and_email
			generate_invoice_and_email.delay(order.id, order.order_number)
		except Exception:
			pass
		return order
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/deliver", response_model=OrderRead)
def mark_delivered_endpoint(order_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	order = db.get(Order, order_id)
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	try:
		order_service.mark_delivered(db, order, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(order)
		return order
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}/cancel", response_model=OrderRead)
def cancel_order_endpoint(order_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	order = db.get(Order, order_id)
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	try:
		order_service.cancel_order(db, order, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(order)
		return order
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/{order_id}/history")
def order_history(order_id: int, db: Session = Depends(get_db)):
	from app.models.state_transition import StateTransition

	order = db.get(Order, order_id)
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	rows = (
		db.query(StateTransition)
		.filter(StateTransition.entity_type == "order", StateTransition.entity_id == order_id)
		.order_by(StateTransition.id.asc())
		.all()
	)
	return [
		{
			"id": r.id,
			"entity_type": r.entity_type,
			"entity_id": r.entity_id,
			"from_state": r.from_state,
			"to_state": r.to_state,
			"actor": r.actor,
			"reason": r.reason,
			"created_at": r.created_at.isoformat() if r.created_at else None,
		}
		for r in rows
	]
