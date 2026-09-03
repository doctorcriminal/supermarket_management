"""
app.py
Streamlit entry point for the Supermarket Management System.
Handles DB initialization and sidebar navigation between pages.
"""

import streamlit as st
import config
import database as db
import utils

# Page modules
from views import (
    dashboard,
    products,
    purchases,
    pos,
    inventory,
    returns,
    cash,
    employees,
    assets,
    accounting,
    reports,
)

st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize the database once per session (creates tables if not present)
if "db_initialized" not in st.session_state:
    db.init_db()
    st.session_state.db_initialized = True

utils.sidebar_header()

PAGES = {
    "📊 Dashboard": dashboard,
    "📦 Products": products,
    "🚚 Purchases": purchases,
    "🧾 POS / Sales": pos,
    "📈 Inventory": inventory,
    "↩️ Returns": returns,
    "💵 Cash": cash,
    "👥 Employees": employees,
    "🏢 Assets": assets,
    "📒 Accounting": accounting,
    "📑 Reports": reports,
}

selection = st.sidebar.radio("Navigate", list(PAGES.keys()), label_visibility="collapsed")

st.sidebar.divider()
st.sidebar.caption(f"{config.APP_NAME} — Built with Streamlit & SQLite")

# Render the selected page
PAGES[selection].render()
