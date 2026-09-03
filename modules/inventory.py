"""
modules/inventory.py
Stock level tracking, manual adjustments, low-stock reporting.
"""

import pandas as pd
import database as db


def get_inventory() -> pd.DataFrame:
    query = """
        SELECT p.id AS product_id, p.name, p.category, p.unit,
               COALESCE(i.quantity, 0) AS quantity, p.reorder_level,
               i.updated_at
        FROM products p
        LEFT JOIN inventory i ON i.product_id = p.id
        WHERE p.is_active = 1
        ORDER BY p.name ASC
    """
    return db.run_query_df(query)


def get_low_stock() -> pd.DataFrame:
    query = """
        SELECT p.id AS product_id, p.name, p.category,
               COALESCE(i.quantity, 0) AS quantity, p.reorder_level
        FROM products p
        LEFT JOIN inventory i ON i.product_id = p.id
        WHERE p.is_active = 1 AND COALESCE(i.quantity, 0) <= p.reorder_level
        ORDER BY quantity ASC
    """
    return db.run_query_df(query)


def adjust_stock(product_id: int, change_qty: float, reason: str = "adjustment", ref_id=None):
    """
    Apply a stock change (positive = add stock, negative = remove stock).
    Creates the inventory row if missing, logs the movement.
    """
    db.execute(
        "INSERT OR IGNORE INTO inventory (product_id, quantity) VALUES (?, 0)",
        (product_id,),
    )
    db.execute(
        """UPDATE inventory
           SET quantity = quantity + ?, updated_at = datetime('now')
           WHERE product_id = ?""",
        (change_qty, product_id),
    )
    db.execute(
        """INSERT INTO stock_movements (product_id, change_qty, reason, ref_id)
           VALUES (?, ?, ?, ?)""",
        (product_id, change_qty, reason, ref_id),
    )


def set_stock(product_id: int, new_qty: float):
    """Manually set stock to an exact value (used by inventory CRUD page)."""
    current = db.run_query(
        "SELECT quantity FROM inventory WHERE product_id = ?", (product_id,)
    )
    current_qty = current[0]["quantity"] if current else 0
    diff = new_qty - current_qty
    adjust_stock(product_id, diff, reason="manual_set")


def get_movements(product_id: int = None) -> pd.DataFrame:
    query = """
        SELECT sm.id, p.name AS product_name, sm.change_qty, sm.reason,
               sm.ref_id, sm.created_at
        FROM stock_movements sm
        JOIN products p ON p.id = sm.product_id
    """
    params = ()
    if product_id:
        query += " WHERE sm.product_id = ?"
        params = (product_id,)
    query += " ORDER BY sm.id DESC LIMIT 200"
    return db.run_query_df(query, params)
