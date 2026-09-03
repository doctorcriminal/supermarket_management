"""
modules/reports.py
Aggregated read-only queries used by the dashboard and reports pages.
"""

import pandas as pd
import database as db


def sales_by_day(days: int = 30) -> pd.DataFrame:
    query = """
        SELECT date(sale_date) AS day, SUM(total_amount) AS total, COUNT(*) AS txns
        FROM sales
        WHERE date(sale_date) >= date('now', ?)
        GROUP BY day
        ORDER BY day ASC
    """
    return db.run_query_df(query, (f"-{days} days",))


def top_selling_products(limit: int = 10) -> pd.DataFrame:
    query = """
        SELECT p.name, SUM(si.quantity) AS qty_sold, SUM(si.subtotal) AS revenue
        FROM sale_items si
        JOIN products p ON p.id = si.product_id
        GROUP BY p.id
        ORDER BY qty_sold DESC
        LIMIT ?
    """
    return db.run_query_df(query, (limit,))


def sales_by_category() -> pd.DataFrame:
    query = """
        SELECT p.category, SUM(si.subtotal) AS revenue
        FROM sale_items si
        JOIN products p ON p.id = si.product_id
        GROUP BY p.category
        ORDER BY revenue DESC
    """
    return db.run_query_df(query)


def purchases_by_day(days: int = 30) -> pd.DataFrame:
    query = """
        SELECT date(purchase_date) AS day, SUM(total_amount) AS total, COUNT(*) AS txns
        FROM purchases
        WHERE date(purchase_date) >= date('now', ?)
        GROUP BY day
        ORDER BY day ASC
    """
    return db.run_query_df(query, (f"-{days} days",))


def dashboard_kpis() -> dict:
    products_count = db.run_query("SELECT COUNT(*) AS c FROM products WHERE is_active=1")[0]["c"]
    employees_count = db.run_query("SELECT COUNT(*) AS c FROM employees WHERE status='active'")[0]["c"]
    today_sales = db.run_query(
        "SELECT COALESCE(SUM(total_amount),0) AS v FROM sales WHERE date(sale_date)=date('now')"
    )[0]["v"]
    month_sales = db.run_query(
        "SELECT COALESCE(SUM(total_amount),0) AS v FROM sales WHERE strftime('%Y-%m', sale_date)=strftime('%Y-%m','now')"
    )[0]["v"]
    low_stock_count = db.run_query(
        """SELECT COUNT(*) AS c FROM products p
           LEFT JOIN inventory i ON i.product_id = p.id
           WHERE p.is_active=1 AND COALESCE(i.quantity,0) <= p.reorder_level"""
    )[0]["c"]
    cash_balance = db.run_query(
        """SELECT COALESCE(SUM(CASE WHEN txn_type='in' THEN amount ELSE -amount END),0) AS v
           FROM cash_transactions"""
    )[0]["v"]

    return {
        "products_count": products_count,
        "employees_count": employees_count,
        "today_sales": today_sales,
        "month_sales": month_sales,
        "low_stock_count": low_stock_count,
        "cash_balance": cash_balance,
    }
