"""
config.py
Central configuration for the Supermarket Management System.
"""

import os

# ---------------- Paths ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "supermarket.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "sql", "schema.sql")

# ---------------- App Info ----------------
APP_NAME = "SuperMart Manager"
APP_ICON = "🛒"
CURRENCY = "Rs. "

# ---------------- Business Rules ----------------
DEFAULT_REORDER_LEVEL = 10
LOW_STOCK_WARNING = True

# ---------------- Categories (used across modules) ----------------
PRODUCT_CATEGORIES = [
    "Grocery", "Dairy", "Bakery", "Beverages", "Snacks",
    "Household", "Personal Care", "Frozen Food", "Produce", "Other",
]

PAYMENT_METHODS = ["cash", "card", "credit"]
CASH_CATEGORIES = ["sales", "purchase", "salary", "expense", "asset", "other"]
EMPLOYEE_POSITIONS = ["Cashier", "Manager", "Stock Keeper", "Cleaner", "Security", "Other"]
ATTENDANCE_STATUSES = ["present", "absent", "leave", "half-day"]
ASSET_CATEGORIES = ["Furniture", "Electronics", "Vehicle", "Equipment", "Other"]
ASSET_STATUSES = ["in_use", "maintenance", "disposed"]
LEDGER_ACCOUNTS = ["Sales", "Purchases", "Salaries", "Cash", "Assets", "Expenses", "Returns", "Other"]

# Ensure database directory exists
os.makedirs(DB_DIR, exist_ok=True)
