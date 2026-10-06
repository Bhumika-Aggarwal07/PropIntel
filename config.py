"""Small, central configuration module for the local MySQL database."""

import os

DB_HOST = os.getenv("PROPINTEL_DB_HOST", "localhost")
DB_PORT = int(os.getenv("PROPINTEL_DB_PORT", "3306"))
DB_NAME = os.getenv("PROPINTEL_DB_NAME", "propintel")
DB_USER = os.getenv("PROPINTEL_DB_USER", "root")
DB_PASSWORD = os.getenv("PROPINTEL_DB_PASSWORD", "")
