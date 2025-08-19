from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from app.domain.states import ReturnState
from app.models.return_request import ReturnRequest
from app.models.state_transition import StateTransition
from app.domain.states import OrderState


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


def can_transition_return(current: ReturnState, target: ReturnState) -> bool:
	allowed = {
		ReturnState.REQUESTED: {ReturnState.APPROVED, ReturnState.REJECTED},
		ReturnState.APPROVED: {ReturnState.IN_TRANSIT},
		ReturnState.REJECTED: set(),
		ReturnState.IN_TRANSIT: {ReturnState.RECEIVED},
		ReturnState.RECEIVED: {ReturnState.COMPLETED},
		ReturnState.COMPLETED: set(),
	}
	return target in allowed[current]


def transition_return(db: Session, ret: ReturnRequest, target_state: ReturnState, actor: Optional[str] = None, reason: Optional[str] = None) -> ReturnRequest:
	current_state = ReturnState(ret.state)
	if current_state == target_state:
		return ret
	if not can_transition_return(current_state, target_state):
		raise ValueError(f"Invalid return transition: {current_state} -> {target_state}")

	prev = ret.state
	ret.state = target_state.value
	_record_transition(db, entity_type="return", entity_id=ret.id, from_state=prev, to_state=ret.state, actor=actor, reason=reason)
	db.add(ret)
	return ret


def approve(db: Session, ret: ReturnRequest, actor: Optional[str] = None, reason: Optional[str] = None) -> ReturnRequest:
	return transition_return(db, ret, ReturnState.APPROVED, actor, reason)


def reject(db: Session, ret: ReturnRequest, actor: Optional[str] = None, reason: Optional[str] = None) -> ReturnRequest:
	return transition_return(db, ret, ReturnState.REJECTED, actor, reason)


def mark_in_transit(db: Session, ret: ReturnRequest, actor: Optional[str] = None, reason: Optional[str] = None) -> ReturnRequest:
	return transition_return(db, ret, ReturnState.IN_TRANSIT, actor, reason)


def mark_received(db: Session, ret: ReturnRequest, actor: Optional[str] = None, reason: Optional[str] = None) -> ReturnRequest:
	return transition_return(db, ret, ReturnState.RECEIVED, actor, reason)


def complete(db: Session, ret: ReturnRequest, actor: Optional[str] = None, reason: Optional[str] = None) -> ReturnRequest:
	return transition_return(db, ret, ReturnState.COMPLETED, actor, reason)
