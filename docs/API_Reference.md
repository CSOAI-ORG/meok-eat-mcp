# MEOK EAT API Reference

## restaurant_search
```json
{
  "postcode": "SW1A",
  "lat": 51.50,
  "lng": -0.14,
  "cuisine": "Indian",
  "min_rating": 4.5,
  "max_delivery_time": 30,
  "max_delivery_fee_gbp": 2.00
}
```

## menu_lookup
```json
{"restaurant_id": "r001"}
```

## order_estimate
```json
{
  "restaurant_id": "r001",
  "item_ids": ["m001", "m004"],
  "tip_percent": 10.0
}
```

## dietary_filter
```json
{
  "restaurant_id": "r001",
  "diet": "vegan",
  "exclude_allergens": ["dairy", "nuts"],
  "max_calories": 500
}
```

## promo_check
```json
{"restaurant_id": "r001"}
```

## order_place
```json
{
  "restaurant_id": "r001",
  "item_ids": ["m001", "m004"],
  "customer_name": "Nick Templeman",
  "delivery_address": "1 Sovereign Way, Spalding PE11",
  "tip_percent": 10.0,
  "promo_code": "CURRY20"
}
```

## delivery_track
```json
{"order_id": "ORD-123456"}
```
