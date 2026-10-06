"""Pandas-based descriptive analysis for a selected location."""

import pandas as pd


def calculate_location_analysis(properties):
    """Calculate location statistics from database rows without hardcoded values."""
    frame = pd.DataFrame(properties)
    if frame.empty:
        return None
    price = pd.to_numeric(frame["price_inr"], errors="coerce")
    carpet = pd.to_numeric(frame["carpet_area_sqft"], errors="coerce")
    valid_carpet = carpet.gt(0)
    price_per_sqft = price[valid_carpet] / carpet[valid_carpet]
    return {
        "property_count": int(len(frame)),
        "average_price": float(price.mean()),
        "median_price": float(price.median()),
        "minimum_price": float(price.min()),
        "maximum_price": float(price.max()),
        "average_carpet_area": float(carpet.mean()),
        "median_carpet_area": float(carpet.median()),
        "average_price_per_sqft": float(price_per_sqft.mean()) if not price_per_sqft.empty else None,
        "property_type_distribution": frame["property_type"].fillna("Unknown").value_counts().to_dict(),
        "bhk_distribution": frame["bhk"].fillna("Unknown").value_counts().to_dict(),
    }


def format_currency(value):
    return "Not available" if value is None or pd.isna(value) else f"₹{value:,.0f}"
