"""
pages/returns.py
CRUD UI for sale returns and purchase returns.
"""

import streamlit as st
from modules import returns as returns_module
from modules import products as products_module
import utils


def render():
    st.title("↩️ Returns")

    tab_new, tab_list = st.tabs(["➕ New Return", "📋 All Returns"])

    # ---------------- NEW RETURN ----------------
    with tab_new:
        return_type_label = st.radio(
            "Return Type",
            ["Customer Return (Sale Return)", "Return to Supplier (Purchase Return)"],
            horizontal=True,
        )
        return_type = "sale_return" if "Sale Return" in return_type_label else "purchase_return"

        prod_df = products_module.get_active_product_choices()
        if prod_df.empty:
            st.info("No products available.")
        else:
            options = {row["name"]: row for _, row in prod_df.iterrows()}
            with st.form("return_form", clear_on_submit=True):
                selected_name = st.selectbox("Product", list(options.keys()))
                ref_id = st.number_input("Reference Sale/Purchase ID (optional)", min_value=0, value=0, step=1)
                quantity = st.number_input("Quantity", min_value=1.0, value=1.0, step=1.0)
                amount = st.number_input("Refund / Recovery Amount", min_value=0.0, step=0.5)
                reason = st.text_area("Reason")

                submitted = st.form_submit_button("Save Return", type="primary", use_container_width=True)
                if submitted:
                    prod_row = options[selected_name]
                    returns_module.create_return(
                        return_type,
                        ref_id if ref_id > 0 else None,
                        int(prod_row["id"]),
                        quantity,
                        amount,
                        reason,
                    )
                    utils.success("Return recorded and stock/cash updated.")
                    st.rerun()

    # ---------------- LIST ----------------
    with tab_list:
        df = returns_module.get_all_returns()
        utils.show_dataframe(df, "No returns recorded yet.")

        if not df.empty:
            st.divider()
            options = {f"#{row.id} - {row['product_name']} ({row['return_type']})": row.id
                       for _, row in df.iterrows()}
            selected_label = st.selectbox("Select a return to delete", list(options.keys()))
            selected_id = options[selected_label]

            if utils.confirm_delete(f"return_{selected_id}", "Delete this return"):
                returns_module.delete_return(selected_id)
                utils.success("Return deleted and effects reversed.")
                st.rerun()
