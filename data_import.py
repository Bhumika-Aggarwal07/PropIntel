"""Read, clean, validate, and explicitly import the two supplied workbooks."""

import argparse
from pathlib import Path

import pandas as pd

EXPECTED_COLUMNS = [
    "ListingID", "City", "Locality", "PropertyType", "BHK", "Bathrooms", "Balconies",
    "Furnishing", "SuperBuiltUpArea_sqft", "BuiltUpArea_sqft", "CarpetArea_sqft", "Floor",
    "TotalFloors", "Parking", "BuildingType", "YearBuilt", "AgeYears", "Facing",
    "AmenitiesCount", "IsRERARegistered", "RERAID", "Latitude", "Longitude", "Price_INR",
]

DB_COLUMNS = [
    "source_listing_id", "city", "locality", "property_type", "bhk", "bathrooms", "balconies",
    "furnishing", "super_built_up_area_sqft", "built_up_area_sqft", "carpet_area_sqft", "floor",
    "total_floors", "parking", "building_type", "year_built", "age_years", "facing",
    "amenities_count", "is_rera_registered", "rera_id", "latitude", "longitude", "price_inr",
]

RENAME_COLUMNS = dict(zip(EXPECTED_COLUMNS, DB_COLUMNS))
REQUIRED_POSITIVE = [
    "Price_INR", "SuperBuiltUpArea_sqft", "BuiltUpArea_sqft", "CarpetArea_sqft", "TotalFloors",
]


def validate_expected_columns(frame):
    missing = sorted(set(EXPECTED_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError("Workbook is missing expected columns: " + ", ".join(missing))


def validate_numeric_rows(frame):
    """Return valid and rejected rows; invalid fundamentals are not imported."""
    valid = pd.Series(True, index=frame.index)
    for column in REQUIRED_POSITIVE:
        valid &= pd.to_numeric(frame[column], errors="coerce").gt(0)
    valid &= pd.to_numeric(frame["Floor"], errors="coerce").ge(0)
    valid &= pd.to_numeric(frame["AmenitiesCount"], errors="coerce").ge(0)
    valid &= pd.to_numeric(frame["Floor"], errors="coerce").le(
        pd.to_numeric(frame["TotalFloors"], errors="coerce")
    )
    valid &= pd.to_numeric(frame["CarpetArea_sqft"], errors="coerce").le(
        pd.to_numeric(frame["BuiltUpArea_sqft"], errors="coerce")
    )
    valid &= pd.to_numeric(frame["BuiltUpArea_sqft"], errors="coerce").le(
        pd.to_numeric(frame["SuperBuiltUpArea_sqft"], errors="coerce")
    )
    return frame.loc[valid].copy(), frame.loc[~valid].copy()


def clean_properties(frame):
    cleaned = frame.copy()
    text_columns = cleaned.select_dtypes(include="object").columns
    for column in text_columns:
        cleaned[column] = cleaned[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )
    # The source may use differently cased yes/no values; this is a display cleanup only.
    cleaned["IsRERARegistered"] = cleaned["IsRERARegistered"].map(
        lambda value: value.title() if isinstance(value, str) else value
    )
    return cleaned


def load_source_data(raw_directory=None):
    raw_directory = Path(raw_directory or Path(__file__).parent / "data" / "raw")
    files = [raw_directory / "train_part1.xlsx", raw_directory / "train_part2.xlsx"]
    frames = []
    for file_path in files:
        if not file_path.exists():
            raise FileNotFoundError(f"Required source file was not found: {file_path}")
        frame = pd.read_excel(file_path)
        validate_expected_columns(frame)
        frames.append(frame)
    combined = pd.concat(frames, ignore_index=True)
    valid, rejected = validate_numeric_rows(clean_properties(combined))
    return valid, rejected


def dataframe_to_records(frame):
    database_frame = frame.rename(columns=RENAME_COLUMNS)[DB_COLUMNS].copy().astype(object)
    database_frame = database_frame.where(pd.notna(database_frame), None)
    records = []
    for row in database_frame.itertuples(index=False, name=None):
        # Pandas may use NumPy scalar types; MySQL expects ordinary Python values.
        records.append(tuple(value.item() if hasattr(value, "item") else value for value in row))
    return records


def import_data(raw_directory=None):
    valid, rejected = load_source_data(raw_directory)
    # Import here so validation and cleaning can be tested without a MySQL driver.
    from database import PropertyDatabase

    database = PropertyDatabase()
    database.initialise_schema()
    database.replace_properties(dataframe_to_records(valid))
    return len(valid), len(rejected)


def main():
    parser = argparse.ArgumentParser(description="Import PropIntel training workbooks into MySQL.")
    parser.add_argument("--data-dir", help="Directory containing the two train workbooks")
    args = parser.parse_args()
    imported, rejected = import_data(args.data_dir)
    print(f"Imported {imported} properties. Rejected {rejected} invalid rows.")


if __name__ == "__main__":
    main()
