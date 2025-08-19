from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReturnRequest(Base):
	__tablename__ = "returns"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
	state: Mapped[str] = mapped_column(String(32), nullable=False, default="REQUESTED")
	reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
	)

	items: Mapped[List[ReturnItem]] = relationship(
		"ReturnItem", back_populates="return_request", cascade="all, delete-orphan"
	)


class ReturnItem(Base):
	__tablename__ = "return_items"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	return_id: Mapped[int] = mapped_column(ForeignKey("returns.id", ondelete="CASCADE"), index=True)
	order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id", ondelete="CASCADE"))
	quantity: Mapped[int] = mapped_column(Integer, nullable=False)

	return_request: Mapped[ReturnRequest] = relationship("ReturnRequest", back_populates="items")
