"""
modules/returns.py
Handles sale returns (customer -> store, stock increases, cash refunded)
and purchase returns (store -> supplier, stock decreases, cash recovered).
"""

import pandas as pd
import database as db
from modules import inventory


def get_all_returns() -> pd.DataFrame:
    query = """
        SELECT r.id, r.return_type, r.ref_id, p.name AS product_name,
               r.quantity, r.amount, r.reason, r.return_date
        FROM returns r
        JOIN products p ON p.id = r.product_id
        ORDER BY r.id DESC
    """
    return db.run_query_df(query)


def create_return(return_type: str, ref_id, product_id: int, quantity: float,
                   amount: float, reason: str = "") -> int:
    """
    return_type: 'sale_return' (customer returns item -> stock +qty, cash out)
                 'purchase_return' (we return to supplier -> stock -qty, cash in)
    """
    return_id = db.execute(
        """INSERT INTO returns (return_type, ref_id, product_id, quantity, amount, reason)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (return_type, ref_id, product_id, quantity, amount, reason),
    )

    if return_type == "sale_return":
        inventory.adjust_stock(product_id, quantity, reason="sale_return", ref_id=return_id)
        db.execute(
            """INSERT INTO cash_transactions (txn_type, category, amount, description)
               VALUES ('out', 'other', ?, ?)""",
            (amount, f"Refund for sale return #{return_id}"),
        )
    else:  # purchase_return
        inventory.adjust_stock(product_id, -quantity, reason="purchase_return", ref_id=return_id)
        db.execute(
            """INSERT INTO cash_transactions (txn_type, category, amount, description)
               VALUES ('in', 'other', ?, ?)""",
            (amount, f"Refund from purchase return #{return_id}"),
        )
    return return_id


def delete_return(return_id: int):
    """Reverse stock/cash effects of a return, then delete it."""
    row = db.run_query("SELECT * FROM returns WHERE id = ?", (return_id,))
    if not row:
        return
    r = row[0]
    if r["return_type"] == "sale_return":
        inventory.adjust_stock(r["product_id"], -r["quantity"], reason="sale_return_deleted", ref_id=return_id)
    else:
        inventory.adjust_stock(r["product_id"], r["quantity"], reason="purchase_return_deleted", ref_id=return_id)
    db.execute("DELETE FROM returns WHERE id = ?", (return_id,))
