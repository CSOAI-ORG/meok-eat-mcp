#!/usr/bin/env python3
"""
MEOK EAT MCP Server — Food Delivery Platform Aggregator

Provides unified access to restaurant search, menu browsing, order estimation,
delivery tracking, and dietary filtering across UK food delivery platforms.

Inspired by: Swiggy, Deliveroo, Uber Eats, DoorDash (reverse-engineered APIs)
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("meok-eat-mcp")

# ---------------------------------------------------------------------------
# Mock Data — realistic UK restaurant corpus
# ---------------------------------------------------------------------------

CUISINES = ["British", "Indian", "Chinese", "Italian", "Thai", "Japanese", "Mexican", "Turkish", "Fish & Chips", "Pizza"]

RESTAURANTS: list[dict[str, Any]] = [
    {"id": "r001", "name": "The Golden Curry", "cuisine": "Indian", "rating": 4.7, "delivery_time_min": 25, "delivery_fee_gbp": 1.49, "min_order_gbp": 12.00, "postcodes": ["SW1A", "SW1W", "SW1X"], "lat": 51.5014, "lng": -0.1419},
    {"id": "r002", "name": "Dragon Palace", "cuisine": "Chinese", "rating": 4.3, "delivery_time_min": 35, "delivery_fee_gbp": 2.49, "min_order_gbp": 15.00, "postcodes": ["SW1A", "SW1P", "SW1V"], "lat": 51.4980, "lng": -0.1350},
    {"id": "r003", "name": "Bella Napoli", "cuisine": "Italian", "rating": 4.5, "delivery_time_min": 30, "delivery_fee_gbp": 1.99, "min_order_gbp": 10.00, "postcodes": ["W1J", "W1K", "W1S"], "lat": 51.5074, "lng": -0.1278},
    {"id": "r004", "name": "Sakura Sushi", "cuisine": "Japanese", "rating": 4.8, "delivery_time_min": 20, "delivery_fee_gbp": 0.99, "min_order_gbp": 15.00, "postcodes": ["EC2A", "EC2M", "EC2V"], "lat": 51.5200, "lng": -0.0800},
    {"id": "r005", "name": "Thai Orchid", "cuisine": "Thai", "rating": 4.4, "delivery_time_min": 28, "delivery_fee_gbp": 1.79, "min_order_gbp": 12.00, "postcodes": ["SE1", "SE11", "SE17"], "lat": 51.4950, "lng": -0.1000},
    {"id": "r006", "name": "The Codfather", "cuisine": "Fish & Chips", "rating": 4.2, "delivery_time_min": 22, "delivery_fee_gbp": 1.29, "min_order_gbp": 8.00, "postcodes": ["E1", "E2", "E3"], "lat": 51.5200, "lng": -0.0500},
    {"id": "r007", "name": "Taco Republic", "cuisine": "Mexican", "rating": 4.1, "delivery_time_min": 32, "delivery_fee_gbp": 2.99, "min_order_gbp": 14.00, "postcodes": ["N1", "N5", "N7"], "lat": 51.5400, "lng": -0.1000},
    {"id": "r008", "name": "Kebab Kingdom", "cuisine": "Turkish", "rating": 4.0, "delivery_time_min": 18, "delivery_fee_gbp": 0.79, "min_order_gbp": 7.00, "postcodes": ["W2", "W9", "W11"], "lat": 51.5150, "lng": -0.1800},
    {"id": "r009", "name": "The Royal Platter", "cuisine": "British", "rating": 4.6, "delivery_time_min": 40, "delivery_fee_gbp": 3.49, "min_order_gbp": 20.00, "postcodes": ["SW3", "SW7", "SW10"], "lat": 51.4900, "lng": -0.1700},
    {"id": "r010", "name": "Pizza Pronto", "cuisine": "Pizza", "rating": 4.3, "delivery_time_min": 20, "delivery_fee_gbp": 0.00, "min_order_gbp": 10.00, "postcodes": ["SW1A", "W1J", "SE1"], "lat": 51.5050, "lng": -0.1200},
]

MENUS: dict[str, list[dict[str, Any]]] = {
    "r001": [
        {"id": "m001", "name": "Chicken Tikka Masala", "price_gbp": 10.50, "dietary": ["gluten-free"], "allergens": ["dairy"], "calories": 850},
        {"id": "m002", "name": "Lamb Rogan Josh", "price_gbp": 12.00, "dietary": ["gluten-free"], "allergens": ["dairy"], "calories": 920},
        {"id": "m003", "name": "Vegetable Biryani", "price_gbp": 9.00, "dietary": ["vegetarian", "vegan"], "allergens": [], "calories": 650},
        {"id": "m004", "name": "Garlic Naan", "price_gbp": 2.50, "dietary": ["vegetarian"], "allergens": ["gluten", "dairy"], "calories": 320},
    ],
    "r002": [
        {"id": "m005", "name": "Sweet & Sour Chicken", "price_gbp": 9.50, "dietary": [], "allergens": ["gluten", "soy"], "calories": 780},
        {"id": "m006", "name": "Kung Pao Tofu", "price_gbp": 8.50, "dietary": ["vegetarian", "vegan"], "allergens": ["peanuts", "soy"], "calories": 560},
        {"id": "m007", "name": "Prawn Chow Mein", "price_gbp": 10.00, "dietary": [], "allergens": ["gluten", "shellfish", "soy"], "calories": 720},
    ],
    "r003": [
        {"id": "m008", "name": "Margherita", "price_gbp": 8.00, "dietary": ["vegetarian"], "allergens": ["gluten", "dairy"], "calories": 720},
        {"id": "m009", "name": "Diavola", "price_gbp": 10.50, "dietary": [], "allergens": ["gluten", "dairy"], "calories": 890},
        {"id": "m010", "name": "Pasta Carbonara", "price_gbp": 11.00, "dietary": [], "allergens": ["gluten", "dairy", "eggs"], "calories": 950},
    ],
    "r004": [
        {"id": "m011", "name": "Salmon Nigiri (6pc)", "price_gbp": 7.50, "dietary": ["gluten-free"], "allergens": ["fish"], "calories": 280},
        {"id": "m012", "name": "Dragon Roll", "price_gbp": 12.00, "dietary": [], "allergens": ["gluten", "fish", "dairy"], "calories": 420},
        {"id": "m013", "name": "Miso Soup", "price_gbp": 2.50, "dietary": ["vegetarian", "vegan"], "allergens": ["soy"], "calories": 80},
    ],
    "r005": [
        {"id": "m014", "name": "Pad Thai", "price_gbp": 9.50, "dietary": [], "allergens": ["peanuts", "gluten", "eggs", "soy"], "calories": 680},
        {"id": "m015", "name": "Green Curry", "price_gbp": 10.00, "dietary": ["gluten-free"], "allergens": ["dairy"], "calories": 620},
        {"id": "m016", "name": "Som Tam", "price_gbp": 7.00, "dietary": ["vegetarian", "vegan", "gluten-free"], "allergens": ["peanuts"], "calories": 220},
    ],
    "r006": [
        {"id": "m017", "name": "Cod & Chips", "price_gbp": 9.00, "dietary": [], "allergens": ["gluten", "fish"], "calories": 850},
        {"id": "m018", "name": "Sausage & Chips", "price_gbp": 8.00, "dietary": [], "allergens": ["gluten", "sulphites"], "calories": 920},
    ],
    "r007": [
        {"id": "m019", "name": "Chicken Tacos (3)", "price_gbp": 8.50, "dietary": ["gluten-free"], "allergens": [], "calories": 540},
        {"id": "m020", "name": "Veggie Burrito", "price_gbp": 9.00, "dietary": ["vegetarian", "vegan"], "allergens": ["gluten"], "calories": 680},
    ],
    "r008": [
        {"id": "m021", "name": "Lamb Doner", "price_gbp": 7.50, "dietary": [], "allergens": ["gluten", "dairy"], "calories": 780},
        {"id": "m022", "name": "Falafel Wrap", "price_gbp": 6.50, "dietary": ["vegetarian", "vegan"], "allergens": ["gluten", "sesame"], "calories": 520},
    ],
    "r009": [
        {"id": "m023", "name": "Sunday Roast", "price_gbp": 16.00, "dietary": [], "allergens": ["gluten", "dairy", "sulphites"], "calories": 1200},
        {"id": "m024", "name": "Fish Pie", "price_gbp": 14.00, "dietary": [], "allergens": ["gluten", "fish", "dairy"], "calories": 980},
    ],
    "r010": [
        {"id": "m025", "name": "Pepperoni Feast", "price_gbp": 12.00, "dietary": [], "allergens": ["gluten", "dairy"], "calories": 1050},
        {"id": "m026", "name": "Vegan Supreme", "price_gbp": 11.50, "dietary": ["vegan"], "allergens": ["gluten"], "calories": 780},
    ],
}

ORDERS: dict[str, dict[str, Any]] = {}

PROMOS = {
    "r001": [{"code": "CURRY20", "discount_percent": 20, "min_order": 15.00, "expiry": "2026-06-30"}],
    "r003": [{"code": "PIZZA25", "discount_percent": 25, "min_order": 20.00, "expiry": "2026-06-15"}],
    "r010": [{"code": "FREEDEL", "discount_percent": 0, "free_delivery": True, "min_order": 10.00, "expiry": "2026-06-30"}],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Distance in km between two lat/lng points."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def restaurant_search(
    postcode: str = "",
    lat: float = 0.0,
    lng: float = 0.0,
    cuisine: str = "",
    min_rating: float = 0.0,
    max_delivery_time: int = 60,
    max_delivery_fee_gbp: float = 999.0,
) -> str:
    """
    Search for restaurants by location, cuisine, rating, or delivery constraints.
    Returns a JSON list of matching restaurants.
    """
    results = []
    for r in RESTAURANTS:
        if cuisine and r["cuisine"].lower() != cuisine.lower():
            continue
        if min_rating and r["rating"] < min_rating:
            continue
        if r["delivery_time_min"] > max_delivery_time:
            continue
        if r["delivery_fee_gbp"] > max_delivery_fee_gbp:
            continue
        if postcode and postcode.upper() not in r["postcodes"]:
            continue
        # Distance sort if lat/lng provided
        distance_km = None
        if lat and lng:
            distance_km = round(_haversine(lat, lng, r["lat"], r["lng"]), 2)
        results.append({
            **{k: v for k, v in r.items() if k not in ("postcodes", "lat", "lng")},
            "distance_km": distance_km,
        })

    results.sort(key=lambda x: (x["distance_km"] or 0, x["rating"]), reverse=False)
    return json.dumps(results, indent=2)


@mcp.tool()
def menu_lookup(restaurant_id: str) -> str:
    """
    Fetch the full menu for a given restaurant_id.
    Returns JSON list of menu items with prices, dietary tags, allergens, calories.
    """
    items = MENUS.get(restaurant_id, [])
    if not items:
        return json.dumps({"error": f"Restaurant {restaurant_id} not found or menu unavailable"})
    return json.dumps(items, indent=2)


@mcp.tool()
def order_estimate(
    restaurant_id: str,
    item_ids: list[str],
    tip_percent: float = 10.0,
) -> str:
    """
    Calculate total order cost including delivery fee, tip, and estimated delivery time.
    item_ids: list of menu item IDs to order.
    """
    restaurant = next((r for r in RESTAURANTS if r["id"] == restaurant_id), None)
    if not restaurant:
        return json.dumps({"error": f"Restaurant {restaurant_id} not found"})

    items = MENUS.get(restaurant_id, [])
    subtotal = 0.0
    ordered = []
    for iid in item_ids:
        item = next((it for it in items if it["id"] == iid), None)
        if item:
            subtotal += item["price_gbp"]
            ordered.append(item["name"])
        else:
            return json.dumps({"error": f"Menu item {iid} not found"})

    if subtotal < restaurant["min_order_gbp"]:
        return json.dumps({
            "error": f"Minimum order is £{restaurant['min_order_gbp']:.2f}. Your basket is £{subtotal:.2f}."
        })

    delivery_fee = restaurant["delivery_fee_gbp"]
    tip = round(subtotal * (tip_percent / 100), 2)
    total = round(subtotal + delivery_fee + tip, 2)

    return json.dumps({
        "restaurant": restaurant["name"],
        "items": ordered,
        "subtotal_gbp": round(subtotal, 2),
        "delivery_fee_gbp": delivery_fee,
        "tip_gbp": tip,
        "total_gbp": total,
        "estimated_delivery_min": restaurant["delivery_time_min"],
    }, indent=2)


@mcp.tool()
def delivery_track(order_id: str) -> str:
    """
    Track the status and ETA of an existing order.
    """
    order = ORDERS.get(order_id)
    if not order:
        return json.dumps({"error": f"Order {order_id} not found"})

    placed_at = datetime.fromisoformat(order["placed_at"])
    eta = placed_at + timedelta(minutes=order["estimated_delivery_min"])
    now = datetime.now()
    status = "preparing"
    if now > placed_at + timedelta(minutes=order["estimated_delivery_min"] - 5):
        status = "out_for_delivery"
    if now > eta:
        status = "delivered"

    return json.dumps({
        "order_id": order_id,
        "restaurant": order["restaurant"],
        "status": status,
        "placed_at": order["placed_at"],
        "estimated_delivery": eta.isoformat(),
        "total_gbp": order["total_gbp"],
    }, indent=2)


@mcp.tool()
def dietary_filter(
    restaurant_id: str,
    diet: str = "",
    exclude_allergens: list[str] = None,
    max_calories: int = 0,
) -> str:
    """
    Filter a restaurant's menu by dietary preference, allergens, or calorie limit.
    diet: vegetarian | vegan | gluten-free
    exclude_allergens: list of allergens to exclude (e.g. ["dairy", "nuts"])
    """
    items = MENUS.get(restaurant_id, [])
    if not items:
        return json.dumps({"error": f"Restaurant {restaurant_id} not found"})

    exclude_allergens = set((exclude_allergens or []))
    results = []
    for item in items:
        dietary = set(item.get("dietary", []))
        allergens = set(item.get("allergens", []))
        if diet and diet.lower() not in dietary:
            continue
        if exclude_allergens & allergens:
            continue
        if max_calories and item.get("calories", 9999) > max_calories:
            continue
        results.append(item)

    return json.dumps(results, indent=2)


@mcp.tool()
def promo_check(restaurant_id: str) -> str:
    """
    Check active promotions for a restaurant.
    """
    promos = PROMOS.get(restaurant_id, [])
    if not promos:
        return json.dumps({"promotions": [], "message": "No active promotions"})
    return json.dumps({"promotions": promos}, indent=2)


@mcp.tool()
def order_place(
    restaurant_id: str,
    item_ids: list[str],
    customer_name: str,
    delivery_address: str,
    tip_percent: float = 10.0,
    promo_code: str = "",
) -> str:
    """
    COST WARNING: Place a food delivery order. Returns an order_id for tracking.
    """
    restaurant = next((r for r in RESTAURANTS if r["id"] == restaurant_id), None)
    if not restaurant:
        return json.dumps({"error": f"Restaurant {restaurant_id} not found"})

    items = MENUS.get(restaurant_id, [])
    subtotal = 0.0
    ordered = []
    for iid in item_ids:
        item = next((it for it in items if it["id"] == iid), None)
        if item:
            subtotal += item["price_gbp"]
            ordered.append(item["name"])
        else:
            return json.dumps({"error": f"Menu item {iid} not found"})

    if subtotal < restaurant["min_order_gbp"]:
        return json.dumps({
            "error": f"Minimum order is £{restaurant['min_order_gbp']:.2f}. Your basket is £{subtotal:.2f}."
        })

    delivery_fee = restaurant["delivery_fee_gbp"]
    tip = round(subtotal * (tip_percent / 100), 2)
    discount = 0.0

    # Apply promo
    if promo_code:
        for p in PROMOS.get(restaurant_id, []):
            if p["code"].upper() == promo_code.upper():
                if p.get("free_delivery"):
                    delivery_fee = 0.0
                else:
                    discount = round(subtotal * (p["discount_percent"] / 100), 2)

    total = round(subtotal + delivery_fee + tip - discount, 2)
    order_id = f"ORD-{random.randint(100000, 999999)}"
    ORDERS[order_id] = {
        "order_id": order_id,
        "restaurant": restaurant["name"],
        "items": ordered,
        "subtotal_gbp": round(subtotal, 2),
        "delivery_fee_gbp": delivery_fee,
        "tip_gbp": tip,
        "discount_gbp": discount,
        "total_gbp": total,
        "customer_name": customer_name,
        "delivery_address": delivery_address,
        "estimated_delivery_min": restaurant["delivery_time_min"],
        "placed_at": datetime.now().isoformat(),
    }

    return json.dumps({
        "order_id": order_id,
        "restaurant": restaurant["name"],
        "total_gbp": total,
        "estimated_delivery_min": restaurant["delivery_time_min"],
        "status": "confirmed",
    }, indent=2)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
