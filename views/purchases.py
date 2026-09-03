"""
pages/purchases.py
CRUD UI for supplier purchases (multi-item purchase orders).
"""

import streamlit as st
from modules import purchases as purchases_module
from modules import products as products_module
import utils


def render():
    st.title("🚚 Purchases")

    if "purchase_cart" not in st.session_state:
        st.session_state.purchase_cart = []

    tab_new, tab_list = st.tabs(["➕ New Purchase", "📋 All Purchases"])

    # ---------------- NEW PURCHASE ----------------
    with tab_new:
        st.subheader("Create Purchase Order")
        prod_df = products_module.get_active_product_choices()

        if prod_df.empty:
            st.warning("Add products first before creating a purchase.")
        else:
            supplier_name = st.text_input("Supplier Name")

            st.markdown("#### Add Items")
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            prod_options = {f"{row['name']}": row for _, row in prod_df.iterrows()}
            with c1:
                selected_name = st.selectbox("Product", list(prod_options.keys()), key="purch_prod_select")
            with c2:
                qty = st.number_input("Qty", min_value=1.0, value=1.0, step=1.0, key="purch_qty")
            with c3:
                default_cost = float(prod_options[selected_name]["cost_price"]) if selected_name else 0.0
                cost_price = st.number_input("Cost Price", min_value=0.0, value=default_cost, step=0.5, key="purch_cost")
            with c4:
                st.write("")
                st.write("")
                if st.button("➕ Add to cart", key="add_purch_item"):
                    prod_row = prod_options[selected_name]
                    st.session_state.purchase_cart.append({
                        "product_id": int(prod_row["id"]),
                        "name": selected_name,
                        "quantity": qty,
                        "cost_price": cost_price,
                    })
                    st.rerun()

            if st.session_state.purchase_cart:
                st.markdown("#### Cart")
                cart_total = 0
                for idx, item in enumerate(st.session_state.purchase_cart):
                    subtotal = item["quantity"] * item["cost_price"]
                    cart_total += subtotal
                    cc1, cc2, cc3, cc4, cc5 = st.columns([3, 1, 1, 1, 1])
                    cc1.write(item["name"])
                    cc2.write(item["quantity"])
                    cc3.write(utils.money(item["cost_price"]))
                    cc4.write(utils.money(subtotal))
                    if cc5.button("Remove", key=f"rm_purch_{idx}"):
                        st.session_state.purchase_cart.pop(idx)
                        st.rerun()

                st.markdown(f"### Total: {utils.money(cart_total)}")

                payment_status = st.selectbox("Payment Status", ["unpaid", "paid", "partial"])
                notes = st.text_area("Notes (optional)")

                if st.button("✅ Save Purchase", use_container_width=True, type="primary"):
                    purchases_module.create_purchase(
                        supplier_name or "Unknown Supplier",
                        st.session_state.purchase_cart,
                        payment_status,
                        notes,
                    )
                    st.session_state.purchase_cart = []
                    utils.success("Purchase recorded and stock updated!")
                    st.rerun()
            else:
                st.info("Cart is empty. Add items above.")

    # ---------------- LIST / DELETE ----------------
    with tab_list:
        df = purchases_module.get_all_purchases()
        utils.show_dataframe(df, "No purchases recorded yet.")

        if not df.empty:
            st.divider()
            options = {f"#{row.id} - {row['supplier_name']} ({row['purchase_date']})": row.id
                       for _, row in df.iterrows()}
            selected_label = st.selectbox("View / manage a purchase", list(options.keys()))
            selected_id = options[selected_label]

            st.markdown("#### Items")
            items_df = purchases_module.get_purchase_items(selected_id)
            utils.show_dataframe(items_df)

            new_status = st.selectbox("Update Payment Status", ["unpaid", "paid", "partial"], key="upd_status")
            if st.button("Update Status"):
                purchases_module.update_payment_status(selected_id, new_status)
                utils.success("Payment status updated.")
                st.rerun()

            if utils.confirm_delete(f"purchase_{selected_id}", "Delete this purchase (reverses stock)"):
                purchases_module.delete_purchase(selected_id)
                utils.success("Purchase deleted and stock reversed.")
                st.rerun()
