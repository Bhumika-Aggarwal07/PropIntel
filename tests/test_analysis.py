from analysis import calculate_location_analysis


def sample_properties():
    return [
        {"price_inr": 1000000, "carpet_area_sqft": 500, "property_type": "Apartment", "bhk": 1},
        {"price_inr": 3000000, "carpet_area_sqft": 1000, "property_type": "Apartment", "bhk": 2},
        {"price_inr": 2000000, "carpet_area_sqft": 0, "property_type": None, "bhk": None},
    ]


def test_location_statistics_include_average_and_median():
    result = calculate_location_analysis(sample_properties())
    assert result["property_count"] == 3
    assert result["average_price"] == 2000000
    assert result["median_price"] == 2000000
    assert result["minimum_price"] == 1000000
    assert result["maximum_price"] == 3000000


def test_price_per_sqft_ignores_zero_carpet_area():
    result = calculate_location_analysis(sample_properties())
    assert result["average_price_per_sqft"] == 2500


def test_group_distributions_handle_missing_values():
    result = calculate_location_analysis(sample_properties())
    assert result["property_type_distribution"]["Apartment"] == 2
    assert result["property_type_distribution"]["Unknown"] == 1


def test_empty_analysis_returns_none():
    assert calculate_location_analysis([]) is None
