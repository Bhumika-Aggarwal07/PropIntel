# PropIntel

PropIntel is a Python desktop application for residential real-estate analysis. It is a second-year B.Tech academic project that demonstrates Python, MySQL, Pandas, Tkinter, SQL filtering, rule-based matching, and testing. It does not use machine learning, price prediction, or charts.

## Problem statement

Property data can be difficult to inspect when records are spread across large files. PropIntel stores the supplied residential property records in a local MySQL database and lets a user search, analyse a location, compare properties, and see transparent preference matches.

## Objectives

- Import and clean the two supplied training workbooks conservatively.
- Search practical property fields using safe parameterized SQL.
- Produce descriptive city/locality statistics using Pandas.
- Rank matching properties using explainable fixed rules.
- Compare selected properties without declaring a winner.

## Features

- Search & Filter: city, locality, property type, BHK, furnishing, parking, price, and carpet-area filters.
- Property details: a clean table of the selected property’s fields.
- Location analysis: counts, average/median/minimum/maximum price, carpet-area statistics, average price per square foot, and type/BHK distributions.
- Rule-based matching: a ranked score and an explanation for every result.
- Comparison: factual attributes side-by-side, including price and price-per-square-foot differences for the first two selections.

## Technology stack

- Python and Tkinter/ttk for the desktop interface
- MySQL for persistent storage
- Pandas and openpyxl for workbook input and descriptive analysis
- pytest for automated tests

## Dataset and cleaning

Only these source files are used:

- `data/raw/train_part1.xlsx`
- `data/raw/train_part2.xlsx`

The importer checks the expected 24 columns, combines both files, trims text whitespace, and normalizes the case of RERA yes/no values. It preserves genuine missing data rather than inventing locations or IDs. Rows are rejected only when a fundamental rule fails: non-positive price/area/total floors, negative floor/amenities, floor above total floors, or an invalid carpet/built-up/super-built-up area order.

Both files reuse the same source `ListingID` values. Therefore `source_listing_id` is retained as source information, but MySQL creates a separate auto-incremented `property_id` as the primary key. An import explicitly replaces old rows, preventing accidental duplication when it is run again.

## Database design

The project intentionally uses one `properties` table. It includes the source fields plus internal `property_id`. Indexes on city, locality, property type, price, and BHK support the common filters. The schema is in `sql/propintel_schema.sql`.

## Matching methodology

Matching is deterministic, not AI. The weights are defined in `matching.py`:

| Criterion | Weight |
| --- | ---: |
| City or locality | 30% |
| Budget | 25% |
| Property type | 15% |
| Minimum carpet area | 15% |
| BHK | 10% |
| Minimum bathrooms | 5% |

Only entered preferences participate in the score. Exact matches receive full points; a price up to 10% above budget and a BHK differing by one receive half points. A smaller carpet area receives proportional area points. Furnishing is shown in the explanation as a display preference but has no weight because the main six weights already total 100%. Each result uses these same rules to generate its explanation.

## Project structure

```text
PropIntel/
├── main.py                 # starts the Tkinter application
├── config.py               # environment-based MySQL settings
├── database.py             # parameterized SQL access
├── data_import.py          # Excel import, cleaning, validation
├── analysis.py             # Pandas descriptive statistics
├── matching.py             # explainable scoring rules
├── comparison.py           # comparison helpers
├── gui.py                  # application screens
├── sql/propintel_schema.sql
├── data/raw/               # supplied train workbooks
└── tests/
```

## Installation and MySQL setup

1. Install Python 3.10+ and a local MySQL server on Windows.
2. From the project folder, install packages:

   ```powershell
   pip install -r requirements.txt
   ```

3. Set the MySQL password for the current PowerShell session. Do not put a real password in `config.py`:

   ```powershell
   $env:PROPINTEL_DB_PASSWORD = "your_mysql_password"
   ```

   Optional settings are `PROPINTEL_DB_HOST`, `PROPINTEL_DB_PORT`, `PROPINTEL_DB_NAME`, and `PROPINTEL_DB_USER`. Defaults are `localhost`, `3306`, `propintel`, and `root`.

4. Import the supplied data. This creates the schema and replaces any earlier import:

   ```powershell
   python data_import.py
   ```

5. Start the desktop application:

   ```powershell
   python main.py
   ```

## Application workflow

Start the application, import data if necessary, then choose Search & Filter, Location Analysis, Match Properties, or Compare Properties from the main menu. Search shows details for a selected row; matching shows both the score and its rationale; comparison leaves the final decision to the user.

## Tests

Run the non-database unit tests with:

```powershell
pytest
```

## Limitations

- Statistics depend entirely on the supplied dataset and may contain missing source values.
- The matching score is a simple preference aid, not professional real-estate advice.
- Source ListingIDs are not globally unique between the two supplied files.
- The application requires a running local MySQL server.

## Future scope

Possible future work includes larger and newer datasets, additional cities, improved identification of repeated source listings, an optional visualization module, more advanced recommendation methods, ML price prediction, and a web or mobile version. These are deliberately not implemented in this academic version.
