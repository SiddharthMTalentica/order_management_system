from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class OrderItemCreate(BaseModel):
	sku: str
	title: str
	quantity: int = Field(gt=0)
	unit_price_minor: int = Field(ge=0)


class OrderCreate(BaseModel):
	order_number: str
	customer_id: str
	currency: str = "INR"
	items: List[OrderItemCreate]


class OrderReadItem(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: int
	sku: str
	title: str
	quantity: int
	unit_price_minor: int


class OrderRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: int
	order_number: str
	customer_id: str
	currency: str
	state: str
	items: List[OrderReadItem]


class TransitionRequest(BaseModel):
	reason: Optional[str] = None
	actor: Optional[str] = None
