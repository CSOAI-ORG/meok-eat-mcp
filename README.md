# 🍽️ MEOK EAT — Food Delivery MCP Server

**The first MCP server for food delivery.** Aggregates restaurant search, menu browsing, order estimation, delivery tracking, and dietary filtering across UK food delivery platforms.

## Tools

| Tool | Purpose | Paid |
|------|---------|------|
| `restaurant_search` | Find restaurants by location, cuisine, rating, delivery time | Free |
| `menu_lookup` | Get full menu with prices, allergens, calories | Free |
| `order_estimate` | Calculate total cost including delivery + tip | Free |
| `dietary_filter` | Filter menu by vegan/vegetarian/gluten-free or allergens | Free |
| `promo_check` | Check active promotions | Free |
| `order_place` | Place an order (returns trackable order_id) | Free |
| `delivery_track` | Track order status and ETA | Free |

## Quick Start

```bash
pip install meok-eat-mcp
python -m meok_eat_mcp.server
```

Or with Claude / any MCP client:
```json
{
  "mcpServers": {
    "meok-eat": {
      "command": "python",
      "args": ["-m", "meok_eat_mcp.server"]
    }
  }
}
```

## Example Queries

- *"Find Indian restaurants near SW1A with rating above 4.5"*
- *"Show me the menu for The Golden Curry"*
- *"What's the total for Chicken Tikka Masala + Garlic Naan with 10% tip?"*
- *"Filter Sakura Sushi menu for gluten-free items under 300 calories"*
- *"Place an order for Pad Thai to 1 Sovereign Way, Spalding"*

## Architecture

See [docs/Architecture.md](docs/Architecture.md) for system design.

## License

MIT — MEOK AI LTD
