"""
modules/purchases.py
CRUD for supplier purchases (purchase orders + line items).
Adding a purchase increases stock; deleting reverses it.
"""

import pandas as pd
import database as db
from modules import inventory


def get_all_purchases() -> pd.DataFrame:
    query = """
        SELECT id, supplier_name, purchase_date, total_amount, payment_status, notes
        FROM purchases
        ORDER BY id DESC
    """
    return db.run_query_df(query)


def get_purchase_items(purchase_id: int) -> pd.DataFrame:
    query = """
        SELECT pi.id, p.name AS product_name, pi.quantity, pi.cost_price, pi.subtotal
        FROM purchase_items pi
        JOIN products p ON p.id = pi.product_id
        WHERE pi.purchase_id = ?
    """
    return db.run_query_df(query, (purchase_id,))


def create_purchase(supplier_name: str, items: list, payment_status: str = "unpaid", notes: str = "") -> int:
    """
    items: list of dicts {product_id, quantity, cost_price}
    Creates purchase header + items, increases stock for each item.
    """
    total = sum(it["quantity"] * it["cost_price"] for it in items)
    purchase_id = db.execute(
        """INSERT INTO purchases (supplier_name, total_amount, payment_status, notes)
           VALUES (?, ?, ?, ?)""",
        (supplier_name, total, payment_status, notes),
    )
    for it in items:
        subtotal = it["quantity"] * it["cost_price"]
        db.execute(
            """INSERT INTO purchase_items (purchase_id, product_id, quantity, cost_price, subtotal)
               VALUES (?, ?, ?, ?, ?)""",
            (purchase_id, it["product_id"], it["quantity"], it["cost_price"], subtotal),
        )
        inventory.adjust_stock(it["product_id"], it["quantity"], reason="purchase", ref_id=purchase_id)

    # log cash-out if paid
    if payment_status == "paid":
        db.execute(
            """INSERT INTO cash_transactions (txn_type, category, amount, description)
               VALUES ('out', 'purchase', ?, ?)""",
            (total, f"Purchase #{purchase_id} from {supplier_name}"),
        )
    return purchase_id


def update_payment_status(purchase_id: int, payment_status: str):
    db.execute(
        "UPDATE purchases SET payment_status = ? WHERE id = ?",
        (payment_status, purchase_id),
    )


def delete_purchase(purchase_id: int):
    """Reverse stock additions, then delete purchase (cascade removes items)."""
    items = get_purchase_items(purchase_id)
    # need product_id, fetch via items table before delete
    raw_items = db.run_query(
        "SELECT product_id, quantity FROM purchase_items WHERE purchase_id = ?",
        (purchase_id,),
    )
    for row in raw_items:
        inventory.adjust_stock(row["product_id"], -row["quantity"], reason="purchase_deleted", ref_id=purchase_id)
    db.execute("DELETE FROM purchases WHERE id = ?", (purchase_id,))
