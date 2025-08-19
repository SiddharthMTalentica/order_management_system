from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.return_request import ReturnRequest, ReturnItem
from app.models.order import Order, OrderItem
from app.domain import return_service
from app.schemas.return_request import ReturnCreate, ReturnRead, TransitionRequest

router = APIRouter(prefix="/returns", tags=["returns"])


@router.post("", response_model=ReturnRead, status_code=201)
def create_return(payload: ReturnCreate, db: Session = Depends(get_db)):
	order = db.get(Order, payload.order_id)
	if not order:
		raise HTTPException(status_code=404, detail="Order not found")
	if order.state != "DELIVERED":
		raise HTTPException(status_code=400, detail="Return can be initiated only for delivered orders")
	if not payload.items:
		raise HTTPException(status_code=400, detail="Return must include at least one item")

	# Validate that all order_item_ids belong to this order
	order_item_ids = [it.order_item_id for it in payload.items]
	db_items = db.query(OrderItem).filter(OrderItem.id.in_(order_item_ids)).all()
	found_ids = {it.id for it in db_items}
	missing = [iid for iid in order_item_ids if iid not in found_ids]
	if missing:
		raise HTTPException(status_code=400, detail=f"Invalid order_item_id(s): {missing}")
	cross = [it.id for it in db_items if it.order_id != order.id]
	if cross:
		raise HTTPException(status_code=400, detail=f"order_item_id(s) not in this order: {cross}")

	ret = ReturnRequest(order_id=payload.order_id, reason=payload.reason)
	for it in payload.items:
		ret.items.append(ReturnItem(order_item_id=it.order_item_id, quantity=it.quantity))

	db.add(ret)
	# Ensure INSERT of parent and children before commit
	db.flush()
	db.commit()
	db.refresh(ret)
	return ret


@router.get("/{return_id}", response_model=ReturnRead)
def get_return(return_id: int, db: Session = Depends(get_db)):
	ret = db.get(ReturnRequest, return_id)
	if not ret:
		raise HTTPException(status_code=404, detail="Return not found")
	return ret


@router.get("", response_model=list[ReturnRead])
def list_returns(db: Session = Depends(get_db)):
	return db.query(ReturnRequest).order_by(ReturnRequest.id.desc()).all()


@router.post("/{return_id}/approve", response_model=ReturnRead)
def approve_return(return_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	ret = db.get(ReturnRequest, return_id)
	if not ret:
		raise HTTPException(status_code=404, detail="Return not found")
	try:
		return_service.approve(db, ret, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(ret)
		return ret
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{return_id}/reject", response_model=ReturnRead)
def reject_return(return_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	ret = db.get(ReturnRequest, return_id)
	if not ret:
		raise HTTPException(status_code=404, detail="Return not found")
	try:
		return_service.reject(db, ret, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(ret)
		return ret
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{return_id}/in-transit", response_model=ReturnRead)
def mark_in_transit(return_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	ret = db.get(ReturnRequest, return_id)
	if not ret:
		raise HTTPException(status_code=404, detail="Return not found")
	try:
		return_service.mark_in_transit(db, ret, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(ret)
		return ret
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{return_id}/received", response_model=ReturnRead)
def mark_received(return_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	ret = db.get(ReturnRequest, return_id)
	if not ret:
		raise HTTPException(status_code=404, detail="Return not found")
	try:
		return_service.mark_received(db, ret, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(ret)
		return ret
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.post("/{return_id}/complete", response_model=ReturnRead)
def complete_return(return_id: int, body: TransitionRequest, db: Session = Depends(get_db)):
	ret = db.get(ReturnRequest, return_id)
	if not ret:
		raise HTTPException(status_code=404, detail="Return not found")
	try:
		return_service.complete(db, ret, actor=body.actor, reason=body.reason)
		db.commit()
		db.refresh(ret)
		# enqueue refund processing with computed amount
		try:
			from worker.tasks import process_refund
			rows = (
				db.query(ReturnItem.quantity, OrderItem.unit_price_minor)
				.join(OrderItem, ReturnItem.order_item_id == OrderItem.id)
				.filter(ReturnItem.return_id == ret.id)
				.all()
			)
			amount_minor = sum(q * p for q, p in rows)
			process_refund.delay(return_id=ret.id, amount_minor=amount_minor, currency="INR")
		except Exception:
			pass
		return ret
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.get("/{return_id}/history")
def return_history(return_id: int, db: Session = Depends(get_db)):
	from app.models.state_transition import StateTransition

	ret = db.get(ReturnRequest, return_id)
	if not ret:
		raise HTTPException(status_code=404, detail="Return not found")
	rows = (
		db.query(StateTransition)
		.filter(StateTransition.entity_type == "return", StateTransition.entity_id == return_id)
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
