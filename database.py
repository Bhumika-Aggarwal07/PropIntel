"""Database access functions for PropIntel.

All filter values are passed as query parameters rather than being added to SQL
text directly.
"""

from pathlib import Path

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:  # Lets the main menu explain a missing dependency gracefully.
    mysql = None
    Error = Exception

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


class DatabaseError(Exception):
    """A user-friendly wrapper around database connection errors."""


class PropertyDatabase:
    def connect(self, include_database=True):
        if "mysql" not in globals() or mysql is None:
            raise DatabaseError(
                "MySQL connector is not installed. Run: pip install -r requirements.txt"
            )
        settings = {
            "host": DB_HOST,
            "port": DB_PORT,
            "user": DB_USER,
            "password": DB_PASSWORD,
        }
        if include_database:
            settings["database"] = DB_NAME
        try:
            return mysql.connector.connect(**settings)
        except Error as exc:
            raise DatabaseError(f"Could not connect to MySQL: {exc}") from exc

    def initialise_schema(self):
        """Create the database and the single property table if needed."""
        schema_path = Path(__file__).parent / "sql" / "propintel_schema.sql"
        statements = [
            item.strip() for item in schema_path.read_text(encoding="utf-8").split(";")
            if item.strip()
        ]
        connection = self.connect(include_database=False)
        try:
            cursor = connection.cursor()
            for statement in statements:
                cursor.execute(statement)
            connection.commit()
        except Error as exc:
            connection.rollback()
            raise DatabaseError(f"Could not create the database schema: {exc}") from exc
        finally:
            connection.close()

    def search_properties(self, filters=None):
        filters = filters or {}
        clauses, values = [], []
        mapping = {
            "city": "city", "locality": "locality", "property_type": "property_type",
            "bhk": "bhk", "furnishing": "furnishing", "parking": "parking",
            "building_type": "building_type",
        }
        for name, column in mapping.items():
            if filters.get(name) not in (None, "", "All"):
                clauses.append(f"{column} = %s")
                values.append(filters[name])
        ranges = {
            "min_price": ("price_inr >= %s",), "max_price": ("price_inr <= %s",),
            "min_area": ("carpet_area_sqft >= %s",), "max_area": ("carpet_area_sqft <= %s",),
            "min_bathrooms": ("bathrooms >= %s",),
        }
        for name, (clause,) in ranges.items():
            if filters.get(name) not in (None, ""):
                clauses.append(clause)
                values.append(filters[name])
        query = "SELECT * FROM properties"
        if clauses:
            query += " WHERE " + " AND ".join(clauses)
        query += " ORDER BY price_inr ASC"
        return self._fetch_all(query, values)

    def get_property(self, property_id):
        rows = self._fetch_all("SELECT * FROM properties WHERE property_id = %s", [property_id])
        return rows[0] if rows else None

    def get_properties(self, property_ids):
        if not property_ids:
            return []
        placeholders = ", ".join(["%s"] * len(property_ids))
        return self._fetch_all(
            f"SELECT * FROM properties WHERE property_id IN ({placeholders})", property_ids
        )

    def distinct_values(self, column, city=None):
        allowed = {"city", "locality", "property_type", "bhk", "furnishing", "parking", "building_type"}
        if column not in allowed:
            raise ValueError("Unsupported filter column")
        query = f"SELECT DISTINCT {column} FROM properties WHERE {column} IS NOT NULL"
        values = []
        if city and column == "locality":
            query += " AND city = %s"
            values.append(city)
        query += f" ORDER BY {column}"
        rows = self._fetch_all(query, values)
        return [row[column] for row in rows]

    def replace_properties(self, records):
        """Explicitly replace previous imported data to avoid duplicate imports."""
        columns = [
            "source_listing_id", "city", "locality", "property_type", "bhk", "bathrooms",
            "balconies", "furnishing", "super_built_up_area_sqft", "built_up_area_sqft",
            "carpet_area_sqft", "floor", "total_floors", "parking", "building_type",
            "year_built", "age_years", "facing", "amenities_count", "is_rera_registered",
            "rera_id", "latitude", "longitude", "price_inr",
        ]
        placeholders = ", ".join(["%s"] * len(columns))
        query = f"INSERT INTO properties ({', '.join(columns)}) VALUES ({placeholders})"
        connection = self.connect()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM properties")
            cursor.executemany(query, records)
            connection.commit()
        except Error as exc:
            connection.rollback()
            raise DatabaseError(f"Could not import properties: {exc}") from exc
        finally:
            connection.close()

    def _fetch_all(self, query, values):
        connection = self.connect()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, values)
            return cursor.fetchall()
        except Error as exc:
            raise DatabaseError(f"Database query failed: {exc}") from exc
        finally:
            connection.close()
