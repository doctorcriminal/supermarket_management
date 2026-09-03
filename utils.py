"""
utils.py
Shared helper functions used across pages/modules.
"""

import datetime
import pandas as pd
import streamlit as st
import config


def money(value) -> str:
    """Format a number as currency string."""
    try:
        return f"{config.CURRENCY}{float(value):,.2f}"
    except (TypeError, ValueError):
        return f"{config.CURRENCY}0.00"


def today_str() -> str:
    return datetime.date.today().isoformat()


def now_str() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def show_dataframe(df: pd.DataFrame, empty_msg: str = "No records found."):
    """Render a DataFrame nicely, or an info message if empty."""
    if df is None or df.empty:
        st.info(empty_msg)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def success(msg: str):
    st.success(msg, icon="✅")


def error(msg: str):
    st.error(msg, icon="⚠️")


def confirm_delete(key: str, label: str = "Delete") -> bool:
    """
    Simple two-step delete confirmation pattern.
    Returns True only once user has clicked delete then confirmed.
    """
    flag_key = f"confirm_{key}"
    if st.button(f"🗑️ {label}", key=f"btn_{key}"):
        st.session_state[flag_key] = True

    if st.session_state.get(flag_key):
        st.warning("Are you sure? This cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, delete", key=f"yes_{key}"):
                st.session_state[flag_key] = False
                return True
        with c2:
            if st.button("Cancel", key=f"no_{key}"):
                st.session_state[flag_key] = False
    return False


def sidebar_header():
    st.sidebar.markdown(f"## {config.APP_ICON} {config.APP_NAME}")
    st.sidebar.caption("Complete Supermarket CRUD & POS System")
    st.sidebar.divider()


def metric_row(items: list):
    """items: list of (label, value) tuples -> renders as st.metric columns."""
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)


def to_float(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
