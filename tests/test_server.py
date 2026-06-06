"""Tests for MEOK EAT MCP Server."""

import json

import pytest

from meok_eat_mcp.server import (
    RESTAURANTS,
    MENUS,
    ORDERS,
    restaurant_search,
    menu_lookup,
    order_estimate,
    delivery_track,
    dietary_filter,
    promo_check,
    order_place,
)


class TestRestaurantSearch:
    def test_search_all(self):
        result = json.loads(restaurant_search())
        assert len(result) == len(RESTAURANTS)

    def test_search_by_cuisine(self):
        result = json.loads(restaurant_search(cuisine="Indian"))
        assert len(result) == 1
        assert result[0]["name"] == "The Golden Curry"

    def test_search_by_postcode(self):
        result = json.loads(restaurant_search(postcode="SW1A"))
        assert len(result) == 3  # r001, r002, r010

    def test_search_by_rating(self):
        result = json.loads(restaurant_search(min_rating=4.5))
        assert all(r["rating"] >= 4.5 for r in result)

    def test_search_by_max_delivery_time(self):
        result = json.loads(restaurant_search(max_delivery_time=20))
        assert len(result) == 3  # r004 (20), r008 (18), r010 (20)

    def test_search_by_max_fee(self):
        result = json.loads(restaurant_search(max_delivery_fee_gbp=1.00))
        assert all(r["delivery_fee_gbp"] <= 1.00 for r in result)

    def test_search_by_lat_lng_sorts_by_distance(self):
        result = json.loads(restaurant_search(lat=51.50, lng=-0.14))
        assert result[0]["distance_km"] is not None


class TestMenuLookup:
    def test_valid_restaurant(self):
        result = json.loads(menu_lookup("r001"))
        assert len(result) == 4
        assert result[0]["name"] == "Chicken Tikka Masala"

    def test_invalid_restaurant(self):
        result = json.loads(menu_lookup("r999"))
        assert "error" in result


class TestOrderEstimate:
    def test_valid_order(self):
        result = json.loads(order_estimate("r001", ["m001", "m004"]))
        assert result["subtotal_gbp"] == 13.00
        assert result["delivery_fee_gbp"] == 1.49
        assert result["total_gbp"] == 15.79

    def test_below_minimum(self):
        result = json.loads(order_estimate("r001", ["m004"]))
        assert "error" in result

    def test_invalid_item(self):
        result = json.loads(order_estimate("r001", ["m999"]))
        assert "error" in result


class TestDietaryFilter:
    def test_vegan(self):
        result = json.loads(dietary_filter("r001", diet="vegan"))
        assert len(result) == 1
        assert result[0]["name"] == "Vegetable Biryani"

    def test_exclude_allergen(self):
        result = json.loads(dietary_filter("r001", exclude_allergens=["dairy"]))
        assert all("dairy" not in i.get("allergens", []) for i in result)

    def test_max_calories(self):
        result = json.loads(dietary_filter("r001", max_calories=500))
        assert all(i["calories"] <= 500 for i in result)


class TestPromoCheck:
    def test_has_promo(self):
        result = json.loads(promo_check("r001"))
        assert len(result["promotions"]) == 1
        assert result["promotions"][0]["code"] == "CURRY20"

    def test_no_promo(self):
        result = json.loads(promo_check("r002"))
        assert result["promotions"] == []


class TestOrderPlace:
    def test_place_and_track(self):
        result = json.loads(order_place(
            "r001",
            ["m001", "m004"],
            "Nick Templeman",
            "1 Sovereign Way, Spalding PE11",
        ))
        assert "order_id" in result
        assert result["status"] == "confirmed"
        oid = result["order_id"]

        track = json.loads(delivery_track(oid))
        assert track["order_id"] == oid
        assert track["status"] in ("preparing", "out_for_delivery", "delivered")

    def test_place_with_promo(self):
        result = json.loads(order_place(
            "r001",
            ["m001", "m002"],
            "Nick Templeman",
            "1 Sovereign Way",
            promo_code="CURRY20",
        ))
        assert result["total_gbp"] < 24.00  # 22.50 + 1.49 - 20%

    def test_invalid_restaurant(self):
        result = json.loads(order_place("r999", ["m001"], "Nick", "Address"))
        assert "error" in result
