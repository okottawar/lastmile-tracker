# System Design Write-Up: Last-Mile Delivery Tracker

## Rate Calculation Engine

The rate engine is designed so every price shown to a customer is reproducible from admin-configured data. Pickup and drop pincodes are resolved to zones, volumetric weight is `(L×B×H)/5000`, and chargeable weight is the higher of actual and volumetric weight, floored by the selected rate card's minimum. The exact origin-zone, destination-zone, and order-type rate card supplies the base and per-kg prices. COD adds the configured maximum of flat and percentage surcharge. The same calculation function serves the pre-confirmation estimate and the final order creation path, while the resulting breakdown is persisted on the order so historical charges do not change when future rate cards are edited.

## Zone Detection Approach

Zone detection uses an explicit admin-managed pincode mapping table. This is deterministic and auditable: unmapped pincodes fail with a clear validation error rather than silently guessing a location or relying on an external geocoding service.

## Auto-Assignment Logic

Auto-assignment filters to available agents below their configured active-order capacity. Candidates are ranked first by pickup-zone match, then by active-order load for balancing, then by haversine distance when GPS coordinates are available. This keeps the business rule readable and isolates distance calculation so a real routing service can replace it later.

## Order Status Lifecycle & Failed Delivery Handling

The state machine is `Created → Assigned → Picked Up → In Transit → Out for Delivery → Delivered`, with `Out for Delivery → Failed → Rescheduled → Assigned` for re-attempts. Agents can only move their assigned orders through valid transitions. Admins can override any status, but every transition or override still appends a history row with timestamp, actor, and note. A failed delivery increments the failed-attempt counter and frees the agent capacity slot. On reschedule, the requested date is recorded, the customer is notified of the `Rescheduled` state, and the system attempts to assign a fresh available agent; if none is available, the order remains `Rescheduled` for admin intervention.
