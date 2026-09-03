"""
pages/pos.py
Point-of-Sale screen for creating new sales, plus sales history/CRUD.
"""

import streamlit as st
from modules import sales as sales_module
from modules import products as products_module
import utils
import config


def render():
    st.title("🧾 Point of Sale")

    if "sale_cart" not in st.session_state:
        st.session_state.sale_cart = []

    tab_new, tab_history = st.tabs(["🛒 New Sale", "📋 Sales History"])

    # ---------------- NEW SALE ----------------
    with tab_new:
        prod_df = products_module.get_active_product_choices()
        if prod_df.empty:
            st.warning("Add products first before making a sale.")
        else:
            customer_name = st.text_input("Customer Name", value="Walk-in")

            st.markdown("#### Add Items")
            c1, c2, c3, c4 = st.columns([3, 1, 1, 1])
            prod_options = {f"{row['name']} (stock: {row['stock_qty']:.0f})": row for _, row in prod_df.iterrows()}
            with c1:
                selected_name = st.selectbox("Product", list(prod_options.keys()), key="pos_prod_select")
            with c2:
                qty = st.number_input("Qty", min_value=1.0, value=1.0, step=1.0, key="pos_qty")
            with c3:
                prod_row = prod_options[selected_name]
                default_price = float(prod_row["sale_price"])
                sale_price = st.number_input("Price", min_value=0.0, value=default_price, step=0.5, key="pos_price")
            with c4:
                st.write("")
                st.write("")
                if st.button("➕ Add to cart", key="add_sale_item"):
                    if qty > prod_row["stock_qty"]:
                        utils.error(f"Insufficient stock! Only {prod_row['stock_qty']:.0f} available.")
                    else:
                        st.session_state.sale_cart.append({
                            "product_id": int(prod_row["id"]),
                            "name": selected_name.split(" (stock:")[0],
                            "quantity": qty,
                            "sale_price": sale_price,
                        })
                        st.rerun()

            if st.session_state.sale_cart:
                st.markdown("#### Cart")
                cart_total = 0
                for idx, item in enumerate(st.session_state.sale_cart):
                    subtotal = item["quantity"] * item["sale_price"]
                    cart_total += subtotal
                    cc1, cc2, cc3, cc4, cc5 = st.columns([3, 1, 1, 1, 1])
                    cc1.write(item["name"])
                    cc2.write(item["quantity"])
                    cc3.write(utils.money(item["sale_price"]))
                    cc4.write(utils.money(subtotal))
                    if cc5.button("Remove", key=f"rm_sale_{idx}"):
                        st.session_state.sale_cart.pop(idx)
                        st.rerun()

                discount = st.number_input("Discount", min_value=0.0, value=0.0, step=0.5)
                payment_method = st.selectbox("Payment Method", config.PAYMENT_METHODS)
                cashier = st.text_input("Cashier Name (optional)")

                final_total = max(cart_total - discount, 0)
                st.markdown(f"### Total: {utils.money(final_total)}")

                if st.button("✅ Complete Sale", use_container_width=True, type="primary"):
                    sales_module.create_sale(
                        customer_name, st.session_state.sale_cart,
                        discount, payment_method, cashier
                    )
                    st.session_state.sale_cart = []
                    utils.success("Sale completed! Stock and cash updated.")
                    st.rerun()
            else:
                st.info("Cart is empty. Add items above.")

    # ---------------- HISTORY ----------------
    with tab_history:
        today = sales_module.sales_summary_today()
        utils.metric_row([
            ("Today's Transactions", today["count"]),
            ("Today's Revenue", utils.money(today["total"])),
        ])

        df = sales_module.get_all_sales()
        utils.show_dataframe(df, "No sales recorded yet.")

        if not df.empty:
            st.divider()
            options = {f"#{row.id} - {row['customer_name']} ({row['sale_date']})": row.id
                       for _, row in df.iterrows()}
            selected_label = st.selectbox("View / delete a sale", list(options.keys()))
            selected_id = options[selected_label]

            st.markdown("#### Items")
            items_df = sales_module.get_sale_items(selected_id)
            utils.show_dataframe(items_df)

            if utils.confirm_delete(f"sale_{selected_id}", "Delete this sale (reverses stock)"):
                sales_module.delete_sale(selected_id)
                utils.success("Sale deleted and stock reversed.")
                st.rerun()
