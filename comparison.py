"""Factual side-by-side property comparison helpers."""

COMPARISON_FIELDS = [
    ("Price", "price_inr"), ("Property Type", "property_type"), ("City", "city"),
    ("Locality", "locality"), ("BHK", "bhk"), ("Bathrooms", "bathrooms"),
    ("Carpet Area (sq ft)", "carpet_area_sqft"), ("Built-up Area (sq ft)", "built_up_area_sqft"),
    ("Super Built-up Area (sq ft)", "super_built_up_area_sqft"), ("Floor", "floor"),
    ("Total Floors", "total_floors"), ("Furnishing", "furnishing"), ("Parking", "parking"),
    ("Building Type", "building_type"), ("Age (years)", "age_years"),
    ("Amenities Count", "amenities_count"), ("RERA Status", "is_rera_registered"),
]


def _display_value(key, value):
    if value is None:
        return "Unknown"
    if key == "price_inr":
        return f"₹{float(value):,.0f}"
    return str(value)


def build_comparison_rows(properties):
    """Return factual comparison rows; intentionally does not choose a winner."""
    rows = []
    for label, key in COMPARISON_FIELDS:
        rows.append([label] + [_display_value(key, item.get(key)) for item in properties])
    if len(properties) >= 2:
        first, second = properties[0], properties[1]
        rows.append(["Price difference (first - second)", f"₹{float(first['price_inr']) - float(second['price_inr']):,.0f}"])
        first_rate = float(first["price_inr"]) / float(first["carpet_area_sqft"])
        second_rate = float(second["price_inr"]) / float(second["carpet_area_sqft"])
        rows.append(["Price/sq ft difference (first - second)", f"₹{first_rate - second_rate:,.0f}"])
    return rows
