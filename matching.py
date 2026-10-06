"""Transparent deterministic matching rules used by the property matcher."""

WEIGHTS = {
    "location": 30,
    "budget": 25,
    "property_type": 15,
    "area": 15,
    "bhk": 10,
    "bathrooms": 5,
}


def _value_matches(actual, requested):
    return str(actual).strip().casefold() == str(requested).strip().casefold()


def score_property(property_row, preferences):
    """Return a score (0-100) and explanations derived from the same rules.

    Only supplied preferences are scored, so a user is not penalised for an
    optional field they deliberately left blank. Budget up to 10% above the
    requested maximum receives half of its budget points.
    """
    points, possible, explanation = 0.0, 0.0, []

    locality = preferences.get("locality")
    city = preferences.get("city")
    if locality or city:
        possible += WEIGHTS["location"]
        match = _value_matches(property_row.get("locality"), locality) if locality else _value_matches(property_row.get("city"), city)
        if match:
            points += WEIGHTS["location"]
            explanation.append("✓ Locality matched" if locality else "✓ City matched")
        else:
            explanation.append("✗ Locality did not match" if locality else "✗ City did not match")

    budget = preferences.get("budget")
    if budget not in (None, ""):
        possible += WEIGHTS["budget"]
        price = float(property_row["price_inr"])
        if price <= float(budget):
            points += WEIGHTS["budget"]
            explanation.append("✓ Within budget")
        elif price <= float(budget) * 1.10:
            points += WEIGHTS["budget"] / 2
            explanation.append("~ Price is within 10% above budget")
        else:
            explanation.append("✗ Price exceeds budget")

    property_type = preferences.get("property_type")
    if property_type not in (None, "", "All"):
        possible += WEIGHTS["property_type"]
        if _value_matches(property_row.get("property_type"), property_type):
            points += WEIGHTS["property_type"]
            explanation.append("✓ Property type matched")
        else:
            explanation.append("✗ Property type did not match")

    min_area = preferences.get("min_area")
    if min_area not in (None, ""):
        possible += WEIGHTS["area"]
        actual_area = float(property_row["carpet_area_sqft"])
        if actual_area >= float(min_area):
            points += WEIGHTS["area"]
            explanation.append("✓ Area requirement satisfied")
        else:
            points += WEIGHTS["area"] * max(actual_area, 0) / float(min_area)
            explanation.append("✗ Area is below the requested minimum")

    bhk = preferences.get("bhk")
    if bhk not in (None, "", "All"):
        possible += WEIGHTS["bhk"]
        difference = abs(float(property_row["bhk"]) - float(bhk))
        if difference == 0:
            points += WEIGHTS["bhk"]
            explanation.append("✓ BHK matched")
        elif difference == 1:
            points += WEIGHTS["bhk"] / 2
            explanation.append("~ BHK differs by one")
        else:
            explanation.append("✗ BHK differs from preference")

    bathrooms = preferences.get("bathrooms")
    if bathrooms not in (None, ""):
        possible += WEIGHTS["bathrooms"]
        if property_row.get("bathrooms") is not None and float(property_row["bathrooms"]) >= float(bathrooms):
            points += WEIGHTS["bathrooms"]
            explanation.append("✓ Bathroom requirement satisfied")
        else:
            explanation.append("✗ Bathroom requirement was not met")

    furnishing = preferences.get("furnishing")
    if furnishing not in (None, "", "All"):
        explanation.append(
            "✓ Furnishing matched (display preference)" if _value_matches(property_row.get("furnishing"), furnishing)
            else "✗ Furnishing differs (display preference)"
        )

    score = round((points / possible) * 100, 1) if possible else 0.0
    return {"score": score, "explanation": explanation}


def rank_properties(properties, preferences):
    matches = []
    for property_row in properties:
        result = score_property(property_row, preferences)
        matches.append({**property_row, **result})
    return sorted(matches, key=lambda item: item["score"], reverse=True)
