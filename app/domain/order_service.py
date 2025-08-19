from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from app.domain.states import OrderState
from app.models.order import Order
from app.models.state_transition import StateTransition


def _record_transition(db: Session, entity_type: str, entity_id: int, from_state: Optional[str], to_state: str, actor: Optional[str], reason: Optional[str]) -> None:
	transition = StateTransition(
		entity_type=entity_type,
		entity_id=entity_id,
		from_state=from_state,
		to_state=to_state,
		actor=actor,
		reason=reason,
	)
	db.add(transition)


def can_transition_order(current: OrderState, target: OrderState) -> bool:
	# Base allowed edges
	allowed = {
		OrderState.PENDING_PAYMENT: {OrderState.PAID, OrderState.CANCELLED},
		OrderState.PAID: {OrderState.PROCESSING_IN_WAREHOUSE, OrderState.CANCELLED},
		OrderState.PROCESSING_IN_WAREHOUSE: {OrderState.SHIPPED},
		OrderState.SHIPPED: {OrderState.DELIVERED},
		OrderState.DELIVERED: set(),
		OrderState.CANCELLED: set(),
	}
	return target in allowed[current]


def transition_order(db: Session, order: Order, target_state: OrderState, actor: Optional[str] = None, reason: Optional[str] = None) -> Order:
	current_state = OrderState(order.state)
	if current_state == target_state:
		return order
	if not can_transition_order(current_state, target_state):
		raise ValueError(f"Invalid order transition: {current_state} -> {target_state}")

	prev = order.state
	order.state = target_state.value
	_record_transition(db, entity_type="order", entity_id=order.id, from_state=prev, to_state=order.state, actor=actor, reason=reason)
	db.add(order)
	return order


def mark_paid(db: Session, order: Order, actor: Optional[str] = None, reason: Optional[str] = None) -> Order:
	return transition_order(db, order, OrderState.PAID, actor, reason)


def mark_processing(db: Session, order: Order, actor: Optional[str] = None, reason: Optional[str] = None) -> Order:
	return transition_order(db, order, OrderState.PROCESSING_IN_WAREHOUSE, actor, reason)


def mark_shipped(db: Session, order: Order, actor: Optional[str] = None, reason: Optional[str] = None) -> Order:
	return transition_order(db, order, OrderState.SHIPPED, actor, reason)


def mark_delivered(db: Session, order: Order, actor: Optional[str] = None, reason: Optional[str] = None) -> Order:
	return transition_order(db, order, OrderState.DELIVERED, actor, reason)


def cancel_order(db: Session, order: Order, actor: Optional[str] = None, reason: Optional[str] = None) -> Order:
	# Allowed only before processing stage
	current_state = OrderState(order.state)
	if current_state not in {OrderState.PENDING_PAYMENT, OrderState.PAID}:
		raise ValueError("Order can only be cancelled before processing in warehouse")
	return transition_order(db, order, OrderState.CANCELLED, actor, reason)
