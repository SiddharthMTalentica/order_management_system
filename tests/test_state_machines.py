from sqlalchemy.orm import Session
from app.domain.states import OrderState, ReturnState
from app.domain.order_service import can_transition_order
from app.domain.return_service import can_transition_return


def test_order_transitions_matrix():
	assert can_transition_order(OrderState.PENDING_PAYMENT, OrderState.PAID)
	assert can_transition_order(OrderState.PENDING_PAYMENT, OrderState.CANCELLED)
	assert not can_transition_order(OrderState.PENDING_PAYMENT, OrderState.SHIPPED)
	assert can_transition_order(OrderState.PAID, OrderState.PROCESSING_IN_WAREHOUSE)
	assert can_transition_order(OrderState.PAID, OrderState.CANCELLED)
	assert not can_transition_order(OrderState.PAID, OrderState.DELIVERED)
	assert can_transition_order(OrderState.PROCESSING_IN_WAREHOUSE, OrderState.SHIPPED)
	assert can_transition_order(OrderState.SHIPPED, OrderState.DELIVERED)
	assert not can_transition_order(OrderState.DELIVERED, OrderState.SHIPPED)


def test_return_transitions_matrix():
	assert can_transition_return(ReturnState.REQUESTED, ReturnState.APPROVED)
	assert can_transition_return(ReturnState.REQUESTED, ReturnState.REJECTED)
	assert not can_transition_return(ReturnState.REQUESTED, ReturnState.IN_TRANSIT)
	assert can_transition_return(ReturnState.APPROVED, ReturnState.IN_TRANSIT)
	assert can_transition_return(ReturnState.IN_TRANSIT, ReturnState.RECEIVED)
	assert can_transition_return(ReturnState.RECEIVED, ReturnState.COMPLETED)
	assert not can_transition_return(ReturnState.REJECTED, ReturnState.COMPLETED)
