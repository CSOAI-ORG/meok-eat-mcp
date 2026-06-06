# MEOK EAT Technical Spec

## Stack

| Layer | Technology |
|-------|------------|
| Protocol | MCP (Model Context Protocol) via `mcp>=1.0.0` |
| Server Framework | FastMCP |
| Language | Python 3.10+ |
| Data Format | In-memory dicts (mock) → REST/GraphQL (production) |
| Testing | pytest |
| Linting | ruff |

## Tool Specifications

### restaurant_search
**Input:** postcode, lat/lng, cuisine, min_rating, max_delivery_time, max_delivery_fee  
**Output:** JSON list of restaurants sorted by distance then rating  
**Algorithm:** Haversine distance + multi-filter pass  
**Complexity:** O(n) where n = number of restaurants

### menu_lookup
**Input:** restaurant_id  
**Output:** JSON list of menu items  
**Complexity:** O(1) dict lookup

### order_estimate
**Input:** restaurant_id, item_ids[], tip_percent  
**Output:** JSON with subtotal, fees, tip, total, ETA  
**Validation:** Minimum order check, item existence check  
**Complexity:** O(m) where m = number of items

### dietary_filter
**Input:** restaurant_id, diet, exclude_allergens[], max_calories  
**Output:** Filtered menu items  
**Complexity:** O(m)

### order_place
**Input:** restaurant_id, item_ids[], customer_name, address, tip_percent, promo_code  
**Output:** order_id, total, status  
**Side Effects:** Writes to in-memory ORDERS dict  
**Validation:** Minimum order, promo code validity

### delivery_track
**Input:** order_id  
**Output:** Status (preparing | out_for_delivery | delivered), ETA  
**Logic:** Time-based state machine from `placed_at`

## Error Handling

All tools return JSON with `"error"` key on failure. No exceptions propagate to the MCP client.

## Security

- No PII is persisted to disk (in-memory only)
- Promo codes are case-insensitive but validated
- Order IDs are random 6-digit numbers (non-sequential)
