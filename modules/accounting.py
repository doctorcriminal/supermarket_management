"""
modules/accounting.py
Simple ledger (debit/credit) CRUD + profit & loss helper calculations
built from sales, purchases, cash and returns data.
"""

import pandas as pd
import database as db


def get_ledger() -> pd.DataFrame:
    query = """
        SELECT id, entry_date, account, description, debit, credit
        FROM ledger
        ORDER BY id DESC
    """
    return db.run_query_df(query)


def create_entry(entry_date, account, description, debit=0, credit=0) -> int:
    return db.execute(
        """INSERT INTO ledger (entry_date, account, description, debit, credit)
           VALUES (?, ?, ?, ?, ?)""",
        (entry_date, account, description, debit, credit),
    )


def update_entry(entry_id, entry_date, account, description, debit, credit):
    db.execute(
        """UPDATE ledger
           SET entry_date=?, account=?, description=?, debit=?, credit=?
           WHERE id=?""",
        (entry_date, account, description, debit, credit, entry_id),
    )


def delete_entry(entry_id):
    db.execute("DELETE FROM ledger WHERE id = ?", (entry_id,))


def account_balances() -> pd.DataFrame:
    query = """
        SELECT account,
               COALESCE(SUM(debit), 0) AS total_debit,
               COALESCE(SUM(credit), 0) AS total_credit,
               COALESCE(SUM(credit), 0) - COALESCE(SUM(debit), 0) AS net
        FROM ledger
        GROUP BY account
        ORDER BY account ASC
    """
    return db.run_query_df(query)


def profit_and_loss() -> dict:
    """
    Basic P&L derived from actual transaction tables:
    Revenue = total sales (net of discount)
    COGS    = sum(quantity * cost_price) for items sold
    Expenses = cash 'out' transactions in category expense/salary
    """
    revenue = db.run_query(
        "SELECT COALESCE(SUM(total_amount), 0) AS v FROM sales"
    )[0]["v"]

    cogs = db.run_query(
        """SELECT COALESCE(SUM(si.quantity * p.cost_price), 0) AS v
           FROM sale_items si JOIN products p ON p.id = si.product_id"""
    )[0]["v"]

    expenses = db.run_query(
        """SELECT COALESCE(SUM(amount), 0) AS v
           FROM cash_transactions
           WHERE txn_type='out' AND category IN ('expense','salary')"""
    )[0]["v"]

    gross_profit = revenue - cogs
    net_profit = gross_profit - expenses

    return {
        "revenue": revenue,
        "cogs": cogs,
        "gross_profit": gross_profit,
        "expenses": expenses,
        "net_profit": net_profit,
    }
