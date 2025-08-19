from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class StateTransition(Base):
	__tablename__ = "state_transitions"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
	entity_type: Mapped[str] = mapped_column(String(16), nullable=False)  # 'order' | 'return'
	entity_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
	from_state: Mapped[str | None] = mapped_column(String(32), nullable=True)
	to_state: Mapped[str] = mapped_column(String(32), nullable=False)
	actor: Mapped[str | None] = mapped_column(String(64), nullable=True)
	reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
	created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
