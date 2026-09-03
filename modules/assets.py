"""
modules/assets.py
CRUD for fixed assets (equipment, furniture, vehicles, etc.).
"""

import pandas as pd
import database as db


def get_all_assets() -> pd.DataFrame:
    query = """
        SELECT id, name, category, purchase_date, value, status, notes
        FROM assets
        ORDER BY id DESC
    """
    return db.run_query_df(query)


def get_asset(asset_id: int):
    rows = db.run_query("SELECT * FROM assets WHERE id = ?", (asset_id,))
    return rows[0] if rows else None


def create_asset(name, category, purchase_date, value, status="in_use", notes="") -> int:
    asset_id = db.execute(
        """INSERT INTO assets (name, category, purchase_date, value, status, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (name, category, purchase_date, value, status, notes),
    )
    db.execute(
        """INSERT INTO ledger (account, description, debit, credit)
           VALUES ('Assets', ?, ?, 0)""",
        (f"Asset purchased: {name}", value),
    )
    return asset_id


def update_asset(asset_id, name, category, purchase_date, value, status, notes):
    db.execute(
        """UPDATE assets
           SET name=?, category=?, purchase_date=?, value=?, status=?, notes=?
           WHERE id=?""",
        (name, category, purchase_date, value, status, notes, asset_id),
    )


def delete_asset(asset_id):
    db.execute("DELETE FROM assets WHERE id = ?", (asset_id,))


def total_asset_value() -> float:
    row = db.run_query(
        "SELECT COALESCE(SUM(value), 0) AS total FROM assets WHERE status != 'disposed'"
    )[0]
    return row["total"]
