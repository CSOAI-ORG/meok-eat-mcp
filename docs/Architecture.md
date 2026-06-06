# MEOK EAT Architecture

## Overview

MEOK EAT is a Model Context Protocol (MCP) server that unifies food delivery platform APIs under a single tool interface. It is designed to be extended with real API integrations for Deliveroo, Uber Eats, Just Eat, and DoorDash.

## System Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Claude /      │────▶│  MEOK EAT MCP   │────▶│  Mock Data      │
│   MCP Client    │◀────│    Server       │◀────│  (now)          │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼ (future)
                        ┌─────────────────┐
                        │  Deliveroo API  │
                        │  Uber Eats API  │
                        │  Just Eat API   │
                        │  DoorDash API   │
                        └─────────────────┘
```

## Design Principles

1. **Unified Interface** — One schema for all platforms
2. **Mock-First** — Works out of the box with realistic UK data
3. **Pluggable Backends** — Swap mock for real APIs per restaurant
4. **Dietary Safety** — Allergen and dietary filters are first-class
5. **Cost Transparency** — Delivery fees, tips, promos calculated upfront

## Data Model

### Restaurant
- `id`, `name`, `cuisine`, `rating`
- `delivery_time_min`, `delivery_fee_gbp`, `min_order_gbp`
- `postcodes[]`, `lat`, `lng`

### Menu Item
- `id`, `name`, `price_gbp`
- `dietary[]` (vegetarian | vegan | gluten-free)
- `allergens[]` (dairy | gluten | nuts | shellfish | soy | eggs | sesame | sulphites | fish)
- `calories`

### Order
- `order_id`, `restaurant`, `items[]`
- `subtotal_gbp`, `delivery_fee_gbp`, `tip_gbp`, `discount_gbp`, `total_gbp`
- `customer_name`, `delivery_address`
- `placed_at`, `estimated_delivery_min`

## Extending with Real APIs

To add a real platform backend:

1. Create `backends/deliveroo.py` implementing `DeliverooBackend`
2. In `server.py`, add platform detection logic:
   ```python
   if restaurant.get("platform") == "deliveroo":
       return deliveroo.menu_lookup(restaurant_id)
   ```
3. Add API key to `.env` and load via `pydantic-settings`

## Performance

- Mock data is in-memory — sub-millisecond lookups
- Haversine distance calculation for location-based search
- Hash-based dedup on content for menu caching
