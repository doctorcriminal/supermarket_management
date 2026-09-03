"""
modules/cash.py
Cash-in / cash-out transaction ledger and balance calculation.
"""

import pandas as pd
import database as db


def get_all_transactions() -> pd.DataFrame:
    query = """
        SELECT id, txn_type, category, amount, description, txn_date
        FROM cash_transactions
        ORDER BY id DESC
    """
    return db.run_query_df(query)


def create_transaction(txn_type: str, category: str, amount: float, description: str = "") -> int:
    return db.execute(
        """INSERT INTO cash_transactions (txn_type, category, amount, description)
           VALUES (?, ?, ?, ?)""",
        (txn_type, category, amount, description),
    )


def update_transaction(txn_id: int, txn_type: str, category: str, amount: float, description: str):
    db.execute(
        """UPDATE cash_transactions
           SET txn_type=?, category=?, amount=?, description=?
           WHERE id=?""",
        (txn_type, category, amount, description, txn_id),
    )


def delete_transaction(txn_id: int):
    db.execute("DELETE FROM cash_transactions WHERE id = ?", (txn_id,))


def get_balance() -> float:
    row = db.run_query(
        """SELECT
               COALESCE(SUM(CASE WHEN txn_type='in' THEN amount ELSE 0 END), 0) -
               COALESCE(SUM(CASE WHEN txn_type='out' THEN amount ELSE 0 END), 0) AS balance
           FROM cash_transactions"""
    )[0]
    return row["balance"]


def get_totals() -> dict:
    row = db.run_query(
        """SELECT
               COALESCE(SUM(CASE WHEN txn_type='in' THEN amount ELSE 0 END), 0) AS total_in,
               COALESCE(SUM(CASE WHEN txn_type='out' THEN amount ELSE 0 END), 0) AS total_out
           FROM cash_transactions"""
    )[0]
    return {"total_in": row["total_in"], "total_out": row["total_out"]}
