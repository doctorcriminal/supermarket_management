"""
pages/inventory.py
View current stock levels, manually adjust stock, and inspect movement history.
"""

import streamlit as st
from modules import inventory as inventory_module
from modules import products as products_module
import utils


def render():
    st.title("📊 Inventory")

    tab_stock, tab_adjust, tab_history = st.tabs(["📦 Stock Levels", "⚙️ Adjust Stock", "🕒 Movement History"])

    # ---------------- STOCK LEVELS ----------------
    with tab_stock:
        df = inventory_module.get_inventory()
        utils.show_dataframe(df, "No inventory data. Add products first.")

        st.subheader("⚠️ Low Stock Items")
        low_df = inventory_module.get_low_stock()
        utils.show_dataframe(low_df, "All items are above reorder level. 🎉")

    # ---------------- ADJUST ----------------
    with tab_adjust:
        prod_df = products_module.get_active_product_choices()
        if prod_df.empty:
            st.info("No products available.")
        else:
            options = {f"{row['name']} (current: {row['stock_qty']:.0f})": row for _, row in prod_df.iterrows()}
            selected_label = st.selectbox("Select Product", list(options.keys()))
            selected = options[selected_label]

            mode = st.radio("Adjustment Mode", ["Add / Remove quantity", "Set exact quantity"], horizontal=True)

            if mode == "Add / Remove quantity":
                change = st.number_input("Change amount (use negative to remove)", value=0.0, step=1.0)
                reason = st.text_input("Reason", value="manual_adjustment")
                if st.button("Apply Adjustment", type="primary"):
                    if change == 0:
                        utils.error("Enter a non-zero amount.")
                    else:
                        inventory_module.adjust_stock(int(selected["id"]), change, reason=reason or "manual_adjustment")
                        utils.success("Stock adjusted successfully.")
                        st.rerun()
            else:
                new_qty = st.number_input("New quantity", min_value=0.0, value=float(selected["stock_qty"]), step=1.0)
                if st.button("Set Stock", type="primary"):
                    inventory_module.set_stock(int(selected["id"]), new_qty)
                    utils.success("Stock quantity set successfully.")
                    st.rerun()

    # ---------------- HISTORY ----------------
    with tab_history:
        prod_df = products_module.get_active_product_choices()
        filter_choice = st.selectbox(
            "Filter by product (optional)",
            ["All Products"] + list(prod_df["name"]) if not prod_df.empty else ["All Products"],
        )
        if filter_choice == "All Products" or prod_df.empty:
            movements_df = inventory_module.get_movements()
        else:
            product_id = int(prod_df[prod_df["name"] == filter_choice]["id"].iloc[0])
            movements_df = inventory_module.get_movements(product_id)

        utils.show_dataframe(movements_df, "No stock movements recorded yet.")
