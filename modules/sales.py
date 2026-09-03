"""
modules/sales.py
Point-of-Sale: create sales (reduces stock), list/view/delete sales.
"""

import pandas as pd
import database as db
from modules import inventory


def get_all_sales() -> pd.DataFrame:
    query = """
        SELECT id, sale_date, customer_name, total_amount, discount,
               payment_method, cashier
        FROM sales
        ORDER BY id DESC
    """
    return db.run_query_df(query)


def get_sale_items(sale_id: int) -> pd.DataFrame:
    query = """
        SELECT si.id, p.name AS product_name, si.quantity, si.sale_price, si.subtotal
        FROM sale_items si
        JOIN products p ON p.id = si.product_id
        WHERE si.sale_id = ?
    """
    return db.run_query_df(query, (sale_id,))


def create_sale(customer_name: str, items: list, discount: float = 0,
                 payment_method: str = "cash", cashier: str = "") -> int:
    """
    items: list of dicts {product_id, quantity, sale_price}
    Creates sale header + items, decreases stock, logs a cash-in transaction.
    """
    subtotal_total = sum(it["quantity"] * it["sale_price"] for it in items)
    total = max(subtotal_total - discount, 0)

    sale_id = db.execute(
        """INSERT INTO sales (customer_name, total_amount, discount, payment_method, cashier)
           VALUES (?, ?, ?, ?, ?)""",
        (customer_name or "Walk-in", total, discount, payment_method, cashier),
    )
    for it in items:
        subtotal = it["quantity"] * it["sale_price"]
        db.execute(
            """INSERT INTO sale_items (sale_id, product_id, quantity, sale_price, subtotal)
               VALUES (?, ?, ?, ?, ?)""",
            (sale_id, it["product_id"], it["quantity"], it["sale_price"], subtotal),
        )
        inventory.adjust_stock(it["product_id"], -it["quantity"], reason="sale", ref_id=sale_id)

    db.execute(
        """INSERT INTO cash_transactions (txn_type, category, amount, description)
           VALUES ('in', 'sales', ?, ?)""",
        (total, f"Sale #{sale_id} - {customer_name or 'Walk-in'}"),
    )
    return sale_id


def delete_sale(sale_id: int):
    """Reverse stock deduction, delete cash entry trace note, delete sale."""
    raw_items = db.run_query(
        "SELECT product_id, quantity FROM sale_items WHERE sale_id = ?", (sale_id,)
    )
    for row in raw_items:
        inventory.adjust_stock(row["product_id"], row["quantity"], reason="sale_deleted", ref_id=sale_id)
    db.execute("DELETE FROM sales WHERE id = ?", (sale_id,))


def sales_summary_today() -> dict:
    row = db.run_query(
        """SELECT COUNT(*) AS cnt, COALESCE(SUM(total_amount), 0) AS total
           FROM sales WHERE date(sale_date) = date('now')"""
    )[0]
    return {"count": row["cnt"], "total": row["total"]}
