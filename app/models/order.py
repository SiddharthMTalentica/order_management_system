from __future__ import annotations

from datetime import datetime
from typing import List

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Order(Base):
	__tablename__ = "orders"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	order_number: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
	customer_id: Mapped[str] = mapped_column(String(64), nullable=False)
	currency: Mapped[str] = mapped_column(String(8), nullable=False, default="INR")
	state: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING_PAYMENT")
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
	updated_at: Mapped[datetime] = mapped_column(
		DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
	)

	items: Mapped[List["OrderItem"]] = relationship(
		"OrderItem", back_populates="order", cascade="all, delete-orphan"
	)


class OrderItem(Base):
	__tablename__ = "order_items"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), index=True)
	sku: Mapped[str] = mapped_column(String(64), nullable=False)
	title: Mapped[str] = mapped_column(String(255), nullable=False)
	quantity: Mapped[int] = mapped_column(Integer, nullable=False)
	unit_price_minor: Mapped[int] = mapped_column(Integer, nullable=False)

	order: Mapped[Order] = relationship("Order", back_populates="items")
