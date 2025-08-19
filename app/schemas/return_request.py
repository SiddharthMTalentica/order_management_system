from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict


class ReturnItemCreate(BaseModel):
	order_item_id: int
	quantity: int = Field(gt=0)


class ReturnCreate(BaseModel):
	order_id: int
	reason: Optional[str] = None
	items: List[ReturnItemCreate]


class ReturnReadItem(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: int
	order_item_id: int
	quantity: int


class ReturnRead(BaseModel):
	model_config = ConfigDict(from_attributes=True)
	id: int
	order_id: int
	state: str
	reason: Optional[str] = None
	items: List[ReturnReadItem]


class TransitionRequest(BaseModel):
	reason: Optional[str] = None
	actor: Optional[str] = None
