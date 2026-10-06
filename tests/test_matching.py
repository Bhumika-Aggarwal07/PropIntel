from matching import rank_properties, score_property


PROPERTY = {
    "city": "Pune", "locality": "Baner", "property_type": "Apartment", "bhk": 2,
    "bathrooms": 2, "carpet_area_sqft": 900, "price_inr": 8000000,
    "furnishing": "Semi-Furnished",
}

PREFERENCES = {
    "city": "Pune", "locality": "Baner", "budget": 8000000,
    "property_type": "Apartment", "bhk": 2, "min_area": 800, "bathrooms": 2,
    "furnishing": "Semi-Furnished",
}


def test_exact_match_scores_100_and_explains_it():
    result = score_property(PROPERTY, PREFERENCES)
    assert result["score"] == 100
    assert "✓ Locality matched" in result["explanation"]
    assert "✓ Within budget" in result["explanation"]


def test_price_more_than_ten_percent_over_budget_gets_no_budget_points():
    property_row = {**PROPERTY, "price_inr": 10000000}
    result = score_property(property_row, PREFERENCES)
    assert result["score"] == 75
    assert "✗ Price exceeds budget" in result["explanation"]


def test_property_type_and_bhk_mismatches_are_explained():
    property_row = {**PROPERTY, "property_type": "Villa", "bhk": 4}
    result = score_property(property_row, PREFERENCES)
    assert result["score"] == 75
    assert "✗ Property type did not match" in result["explanation"]
    assert "✗ BHK differs from preference" in result["explanation"]


def test_matches_are_sorted_by_score_descending():
    lower = {**PROPERTY, "price_inr": 12000000}
    ranked = rank_properties([lower, PROPERTY], PREFERENCES)
    assert ranked[0]["price_inr"] == 8000000
