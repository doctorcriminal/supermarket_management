"""
pages/accounting.py
Ledger CRUD + automatic Profit & Loss summary.
"""

import streamlit as st
from modules import accounting as accounting_module
import utils
import config


def render():
    st.title("📒 Accounting")

    tab_pl, tab_ledger, tab_add, tab_edit = st.tabs(
        ["📈 Profit & Loss", "📋 Ledger", "➕ Add Entry", "✏️ Edit / Delete"]
    )

    # ---------------- P&L ----------------
    with tab_pl:
        pl = accounting_module.profit_and_loss()
        utils.metric_row([
            ("Revenue", utils.money(pl["revenue"])),
            ("COGS", utils.money(pl["cogs"])),
            ("Gross Profit", utils.money(pl["gross_profit"])),
        ])
        utils.metric_row([
            ("Expenses", utils.money(pl["expenses"])),
            ("Net Profit", utils.money(pl["net_profit"])),
        ])

        st.divider()
        st.subheader("Account Balances")
        bal_df = accounting_module.account_balances()
        utils.show_dataframe(bal_df, "No ledger entries yet.")

    # ---------------- LEDGER LIST ----------------
    with tab_ledger:
        df = accounting_module.get_ledger()
        utils.show_dataframe(df, "No ledger entries recorded yet.")

    # ---------------- CREATE ----------------
    with tab_add:
        with st.form("add_ledger_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                entry_date = st.date_input("Date", value=utils.today_str())
                account = st.selectbox("Account", config.LEDGER_ACCOUNTS)
            with c2:
                debit = st.number_input("Debit", min_value=0.0, step=0.5)
                credit = st.number_input("Credit", min_value=0.0, step=0.5)
            description = st.text_area("Description")

            submitted = st.form_submit_button("Save Entry", type="primary", use_container_width=True)
            if submitted:
                accounting_module.create_entry(str(entry_date), account, description, debit, credit)
                utils.success("Ledger entry added.")
                st.rerun()

    # ---------------- EDIT / DELETE ----------------
    with tab_edit:
        df = accounting_module.get_ledger()
        if df.empty:
            st.info("No entries to edit.")
        else:
            options = {f"#{row.id} - {row['account']} - {row['entry_date']}": row.id
                       for _, row in df.iterrows()}
            selected_label = st.selectbox("Select ledger entry", list(options.keys()))
            selected_id = options[selected_label]
            entry = df[df["id"] == selected_id].iloc[0]

            with st.form("edit_ledger_form"):
                c1, c2 = st.columns(2)
                with c1:
                    entry_date = st.text_input("Date", value=entry["entry_date"])
                    acc_index = config.LEDGER_ACCOUNTS.index(entry["account"]) \
                        if entry["account"] in config.LEDGER_ACCOUNTS else 0
                    account = st.selectbox("Account", config.LEDGER_ACCOUNTS, index=acc_index)
                with c2:
                    debit = st.number_input("Debit", min_value=0.0, step=0.5, value=float(entry["debit"]))
                    credit = st.number_input("Credit", min_value=0.0, step=0.5, value=float(entry["credit"]))
                description = st.text_area("Description", value=entry["description"] or "")

                update_clicked = st.form_submit_button("💾 Update Entry", use_container_width=True)
                if update_clicked:
                    accounting_module.update_entry(selected_id, entry_date, account, description, debit, credit)
                    utils.success("Ledger entry updated.")
                    st.rerun()

            st.divider()
            if utils.confirm_delete(f"ledger_{selected_id}", "Delete this entry"):
                accounting_module.delete_entry(selected_id)
                utils.success("Ledger entry deleted.")
                st.rerun()
