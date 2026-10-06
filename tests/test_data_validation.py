import pandas as pd
import pytest

from data_import import EXPECTED_COLUMNS, validate_expected_columns, validate_numeric_rows


def valid_frame():
    row = {
        "ListingID": "L1", "City": "Pune", "Locality": "Baner", "PropertyType": "Apartment",
        "BHK": 2, "Bathrooms": 2, "Balconies": 1, "Furnishing": "Semi-Furnished",
        "SuperBuiltUpArea_sqft": 1200, "BuiltUpArea_sqft": 1000, "CarpetArea_sqft": 800,
        "Floor": 2, "TotalFloors": 10, "Parking": "Yes", "BuildingType": "Residential",
        "YearBuilt": 2020, "AgeYears": 4, "Facing": "East", "AmenitiesCount": 5,
        "IsRERARegistered": "Yes", "RERAID": "R1", "Latitude": 18.5, "Longitude": 73.8,
        "Price_INR": 8000000,
    }
    return pd.DataFrame([row])


def test_expected_columns_are_accepted():
    validate_expected_columns(valid_frame())


def test_missing_expected_column_is_rejected():
    frame = valid_frame().drop(columns=["Price_INR"])
    with pytest.raises(ValueError, match="Price_INR"):
        validate_expected_columns(frame)


def test_non_positive_price_is_rejected():
    frame = valid_frame()
    frame.loc[0, "Price_INR"] = 0
    valid, rejected = validate_numeric_rows(frame)
    assert valid.empty
    assert len(rejected) == 1


def test_invalid_floor_or_area_relationship_is_rejected():
    frame = valid_frame()
    frame.loc[0, "Floor"] = 11
    valid, rejected = validate_numeric_rows(frame)
    assert valid.empty
    assert len(rejected) == 1
