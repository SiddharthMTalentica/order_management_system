from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table(
		"orders",
		sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
		sa.Column("order_number", sa.String(length=32), nullable=False, unique=True),
		sa.Column("customer_id", sa.String(length=64), nullable=False),
		sa.Column("currency", sa.String(length=8), nullable=False),
		sa.Column("state", sa.String(length=32), nullable=False),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
		sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
	)

	op.create_table(
		"order_items",
		sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
		sa.Column("order_id", sa.BigInteger(), sa.ForeignKey("orders.id", ondelete="CASCADE"), index=True),
		sa.Column("sku", sa.String(length=64), nullable=False),
		sa.Column("title", sa.String(length=255), nullable=False),
		sa.Column("quantity", sa.Integer(), nullable=False),
		sa.Column("unit_price_minor", sa.Integer(), nullable=False),
	)

	op.create_table(
		"returns",
		sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
		sa.Column("order_id", sa.BigInteger(), sa.ForeignKey("orders.id", ondelete="CASCADE"), index=True),
		sa.Column("state", sa.String(length=32), nullable=False),
		sa.Column("reason", sa.String(length=255), nullable=True),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
		sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
	)

	op.create_table(
		"return_items",
		sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
		sa.Column("return_id", sa.BigInteger(), sa.ForeignKey("returns.id", ondelete="CASCADE"), index=True),
		sa.Column("order_item_id", sa.BigInteger(), sa.ForeignKey("order_items.id", ondelete="CASCADE")),
		sa.Column("quantity", sa.Integer(), nullable=False),
	)

	op.create_table(
		"state_transitions",
		sa.Column("id", sa.BigInteger(), primary_key=True, autoincrement=True),
		sa.Column("entity_type", sa.String(length=16), nullable=False),
		sa.Column("entity_id", sa.BigInteger(), nullable=False),
		sa.Column("from_state", sa.String(length=32), nullable=True),
		sa.Column("to_state", sa.String(length=32), nullable=False),
		sa.Column("actor", sa.String(length=64), nullable=True),
		sa.Column("reason", sa.String(length=255), nullable=True),
		sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
	)

	op.create_index("ix_state_transitions_entity", "state_transitions", ["entity_type", "entity_id"])  # composite for queries


def downgrade() -> None:
	op.drop_index("ix_state_transitions_entity", table_name="state_transitions")
	op.drop_table("state_transitions")
	op.drop_table("return_items")
	op.drop_table("returns")
	op.drop_table("order_items")
	op.drop_table("orders")
