### Workflow Design

#### State Machine Diagrams

Order Lifecycle:

```
PENDING_PAYMENT -> PAID -> PROCESSING_IN_WAREHOUSE -> SHIPPED -> DELIVERED
           \-> CANCELLED (allowed only from PENDING_PAYMENT or PAID)
```

Return Lifecycle (item-level):

```
REQUESTED -> APPROVED -> IN_TRANSIT -> RECEIVED -> COMPLETED
REQUESTED -> REJECTED (terminal)
```

#### Database Schema

- `orders(id, order_number[uniq], customer_id, currency, state, created_at, updated_at)`
- `order_items(id, order_id[FK], sku, title, quantity, unit_price_minor)`
- `returns(id, order_id[FK], state, reason, created_at, updated_at)`
- `return_items(id, return_id[FK], order_item_id[FK], quantity)`
- `state_transitions(id, entity_type['order'|'return'], entity_id, from_state, to_state, actor, reason, created_at)`

Relationships:

- `orders 1..N order_items`
- `orders 1..N returns`
- `returns 1..N return_items`
- `state_transitions` polymorphic by `(entity_type, entity_id)` for auditing.

#### Table Descriptions

- orders
  - Purpose: Represents a customer order and its lifecycle state.
  - Columns:
    - id: bigint PK
    - order_number: string(32), unique business identifier
    - customer_id: string(64), customer reference
    - currency: string(8), e.g., INR
    - state: string(32), lifecycle state (see Order state machine)
    - created_at, updated_at: timestamps (UTC)
- order_items
  - Purpose: Line items attached to an order.
  - Columns:
    - id: bigint PK
    - order_id: FK -> orders.id (CASCADE delete)
    - sku: string(64), product identifier
    - title: string(255), human-readable name
    - quantity: int, number of units
    - unit_price_minor: int, price per unit in minor currency units (paise)
- returns
  - Purpose: A return request for an order (initiated only when the order is DELIVERED).
  - Columns:
    - id: bigint PK
    - order_id: FK -> orders.id (CASCADE delete)
    - state: string(32), return lifecycle state (see Return state machine)
    - reason: string(255), optional explanation
    - created_at, updated_at: timestamps (UTC)
- return_items
  - Purpose: Item-level details for a return request (partial returns allowed).
  - Columns:
    - id: bigint PK
    - return_id: FK -> returns.id (CASCADE delete)
    - order_item_id: FK -> order_items.id
    - quantity: int, number of units being returned from the associated order item
- state_transitions
  - Purpose: Immutable audit trail for state changes across orders and returns.
  - Columns:
    - id: bigint PK
    - entity_type: 'order' | 'return'
    - entity_id: bigint, references the primary key of the entity row 
            If entity_type="order" → entity_id = orders.id
            If entity_type="return" → entity_id = returns.id
    - from_state: string(32), nullable for initial state
    - to_state: string(32), target state
    - actor: string(64), optional (e.g., user or system trigger)
    - reason: string(255), optional justification
    - created_at: timestamp (UTC)

Notes:

- Monetary values are stored as integers in minor units to avoid floating-point errors.
- All destructive operations use CASCADE to maintain referential integrity on deletion.
- Timezone is set to Asia/Kolkata at the application level; DB timestamps are stored in UTC.
