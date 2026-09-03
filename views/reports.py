"""
pages/reports.py
Read-only business reports: sales trends, top products, category breakdown,
purchase trends.
"""

import streamlit as st
from modules import reports as reports_module
import utils


def render():
    st.title("📑 Reports")

    period = st.slider("Period (days)", min_value=7, max_value=180, value=30, step=1)

    st.subheader("📈 Sales Trend")
    sales_df = reports_module.sales_by_day(period)
    if not sales_df.empty:
        st.line_chart(sales_df.set_index("day")["total"])
        utils.show_dataframe(sales_df)
    else:
        st.info("No sales data for this period.")

    st.divider()
    st.subheader("🚚 Purchases Trend")
    purch_df = reports_module.purchases_by_day(period)
    if not purch_df.empty:
        st.line_chart(purch_df.set_index("day")["total"])
        utils.show_dataframe(purch_df)
    else:
        st.info("No purchase data for this period.")

    st.divider()
    st.subheader("🏆 Top Selling Products")
    top_n = st.slider("Show top N products", min_value=5, max_value=30, value=10)
    top_df = reports_module.top_selling_products(top_n)
    if not top_df.empty:
        st.bar_chart(top_df.set_index("name")["qty_sold"])
        utils.show_dataframe(top_df)
    else:
        st.info("No sales data yet.")

    st.divider()
    st.subheader("🧾 Revenue by Category")
    cat_df = reports_module.sales_by_category()
    if not cat_df.empty:
        st.bar_chart(cat_df.set_index("category")["revenue"])
        utils.show_dataframe(cat_df)
    else:
        st.info("No category sales data yet.")
