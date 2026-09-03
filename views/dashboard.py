"""
pages/dashboard.py
Overview dashboard: KPIs, sales trend, top products, low-stock alerts.
"""

import streamlit as st
from modules import reports, inventory
import utils


def render():
    st.title("📊 Dashboard")
    st.caption("Live overview of your supermarket's performance")

    kpis = reports.dashboard_kpis()

    utils.metric_row([
        ("Today's Sales", utils.money(kpis["today_sales"])),
        ("This Month", utils.money(kpis["month_sales"])),
        ("Cash Balance", utils.money(kpis["cash_balance"])),
    ])
    utils.metric_row([
        ("Active Products", kpis["products_count"]),
        ("Active Employees", kpis["employees_count"]),
        ("Low Stock Items", kpis["low_stock_count"]),
    ])

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Sales Trend (30 days)")
        df = reports.sales_by_day(30)
        if not df.empty:
            st.line_chart(df.set_index("day")["total"])
        else:
            st.info("No sales recorded yet.")

    with col2:
        st.subheader("🏆 Top Selling Products")
        df = reports.top_selling_products(10)
        if not df.empty:
            st.bar_chart(df.set_index("name")["qty_sold"])
        else:
            st.info("No sales recorded yet.")

    st.divider()

    st.subheader("⚠️ Low Stock Alerts")
    low_stock_df = inventory.get_low_stock()
    utils.show_dataframe(low_stock_df, "All products are sufficiently stocked. 🎉")

    st.subheader("🧾 Revenue by Category")
    cat_df = reports.sales_by_category()
    if not cat_df.empty:
        st.bar_chart(cat_df.set_index("category")["revenue"])
    else:
        st.info("No sales data yet to break down by category.")
