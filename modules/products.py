"""
modules/products.py
CRUD operations for the products catalog. Also seeds an inventory
row (qty=0) whenever a new product is created.
"""

import pandas as pd
import database as db


def get_all_products(active_only: bool = False) -> pd.DataFrame:
    query = """
        SELECT p.id, p.name, p.category, p.unit, p.barcode,
               p.cost_price, p.sale_price, p.reorder_level, p.is_active,
               COALESCE(i.quantity, 0) AS stock_qty
        FROM products p
        LEFT JOIN inventory i ON i.product_id = p.id
    """
    if active_only:
        query += " WHERE p.is_active = 1"
    query += " ORDER BY p.id DESC"
    return db.run_query_df(query)


def get_product(product_id: int):
    rows = db.run_query("SELECT * FROM products WHERE id = ?", (product_id,))
    return rows[0] if rows else None


def get_active_product_choices() -> pd.DataFrame:
    """Lightweight list for dropdowns (id, name, sale_price, cost_price, stock)."""
    query = """
        SELECT p.id, p.name, p.sale_price, p.cost_price,
               COALESCE(i.quantity, 0) AS stock_qty
        FROM products p
        LEFT JOIN inventory i ON i.product_id = p.id
        WHERE p.is_active = 1
        ORDER BY p.name ASC
    """
    return db.run_query_df(query)


def create_product(name, category, unit, barcode, cost_price, sale_price, reorder_level) -> int:
    product_id = db.execute(
        """INSERT INTO products (name, category, unit, barcode, cost_price, sale_price, reorder_level)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, category, unit, barcode or None, cost_price, sale_price, reorder_level),
    )
    # seed inventory row
    db.execute(
        "INSERT OR IGNORE INTO inventory (product_id, quantity) VALUES (?, 0)",
        (product_id,),
    )
    return product_id


def update_product(product_id, name, category, unit, barcode, cost_price, sale_price, reorder_level, is_active):
    db.execute(
        """UPDATE products
           SET name=?, category=?, unit=?, barcode=?, cost_price=?, sale_price=?,
               reorder_level=?, is_active=?
           WHERE id=?""",
        (name, category, unit, barcode or None, cost_price, sale_price,
         reorder_level, int(is_active), product_id),
    )


def delete_product(product_id):
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))


def search_products(term: str) -> pd.DataFrame:
    like = f"%{term}%"
    query = """
        SELECT p.id, p.name, p.category, p.unit, p.barcode,
               p.cost_price, p.sale_price, p.reorder_level, p.is_active,
               COALESCE(i.quantity, 0) AS stock_qty
        FROM products p
        LEFT JOIN inventory i ON i.product_id = p.id
        WHERE p.name LIKE ? OR p.barcode LIKE ? OR p.category LIKE ?
        ORDER BY p.name ASC
    """
    return db.run_query_df(query, (like, like, like))
