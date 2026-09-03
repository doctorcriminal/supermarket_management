"""
pages/cash.py
Cash-in / cash-out ledger CRUD.
"""

import streamlit as st
from modules import cash as cash_module
import utils
import config


def render():
    st.title("💵 Cash Management")

    totals = cash_module.get_totals()
    balance = cash_module.get_balance()
    utils.metric_row([
        ("Total Cash In", utils.money(totals["total_in"])),
        ("Total Cash Out", utils.money(totals["total_out"])),
        ("Current Balance", utils.money(balance)),
    ])

    st.divider()
    tab_add, tab_list, tab_edit = st.tabs(["➕ Add Transaction", "📋 All Transactions", "✏️ Edit / Delete"])

    # ---------------- CREATE ----------------
    with tab_add:
        with st.form("add_cash_form", clear_on_submit=True):
            txn_type = st.radio("Type", ["in", "out"], horizontal=True, format_func=lambda x: "Cash In" if x == "in" else "Cash Out")
            category = st.selectbox("Category", config.CASH_CATEGORIES)
            amount = st.number_input("Amount", min_value=0.0, step=0.5)
            description = st.text_area("Description")
            submitted = st.form_submit_button("Save Transaction", type="primary", use_container_width=True)
            if submitted:
                if amount <= 0:
                    utils.error("Amount must be greater than zero.")
                else:
                    cash_module.create_transaction(txn_type, category, amount, description)
                    utils.success("Transaction recorded.")
                    st.rerun()

    # ---------------- LIST ----------------
    with tab_list:
        df = cash_module.get_all_transactions()
        utils.show_dataframe(df, "No cash transactions recorded yet.")

    # ---------------- EDIT / DELETE ----------------
    with tab_edit:
        df = cash_module.get_all_transactions()
        if df.empty:
            st.info("No transactions to edit.")
        else:
            options = {f"#{row.id} - {row['category']} - {utils.money(row['amount'])}": row.id
                       for _, row in df.iterrows()}
            selected_label = st.selectbox("Select transaction", list(options.keys()))
            selected_id = options[selected_label]
            txn_row = df[df["id"] == selected_id].iloc[0]

            with st.form("edit_cash_form"):
                txn_type = st.radio("Type", ["in", "out"], horizontal=True,
                                     index=0 if txn_row["txn_type"] == "in" else 1,
                                     format_func=lambda x: "Cash In" if x == "in" else "Cash Out")
                cat_index = config.CASH_CATEGORIES.index(txn_row["category"]) \
                    if txn_row["category"] in config.CASH_CATEGORIES else 0
                category = st.selectbox("Category", config.CASH_CATEGORIES, index=cat_index)
                amount = st.number_input("Amount", min_value=0.0, step=0.5, value=float(txn_row["amount"]))
                description = st.text_area("Description", value=txn_row["description"] or "")

                update_clicked = st.form_submit_button("💾 Update", use_container_width=True)
                if update_clicked:
                    cash_module.update_transaction(selected_id, txn_type, category, amount, description)
                    utils.success("Transaction updated.")
                    st.rerun()

            st.divider()
            if utils.confirm_delete(f"cash_{selected_id}", "Delete this transaction"):
                cash_module.delete_transaction(selected_id)
                utils.success("Transaction deleted.")
                st.rerun()
