"""
pages/products.py
Full CRUD UI for the products catalog.
"""

import streamlit as st
from modules import products as products_module
import utils
import config


def render():
    st.title("📦 Products")
    tab_list, tab_add, tab_edit = st.tabs(["📋 All Products", "➕ Add Product", "✏️ Edit / Delete"])

    # ---------------- LIST ----------------
    with tab_list:
        search = st.text_input("🔍 Search by name / barcode / category", key="prod_search")
        if search:
            df = products_module.search_products(search)
        else:
            df = products_module.get_all_products()
        utils.show_dataframe(df, "No products yet. Add one from the 'Add Product' tab.")

    # ---------------- CREATE ----------------
    with tab_add:
        st.subheader("Add a new product")
        with st.form("add_product_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Product Name *")
                category = st.selectbox("Category", config.PRODUCT_CATEGORIES)
                unit = st.text_input("Unit", value="pcs")
                barcode = st.text_input("Barcode (optional)")
            with c2:
                cost_price = st.number_input("Cost Price", min_value=0.0, step=0.5)
                sale_price = st.number_input("Sale Price", min_value=0.0, step=0.5)
                reorder_level = st.number_input("Reorder Level", min_value=0, value=config.DEFAULT_REORDER_LEVEL)

            submitted = st.form_submit_button("Save Product", use_container_width=True)
            if submitted:
                if not name.strip():
                    utils.error("Product name is required.")
                else:
                    products_module.create_product(
                        name.strip(), category, unit.strip() or "pcs",
                        barcode.strip(), cost_price, sale_price, reorder_level
                    )
                    utils.success(f"Product '{name}' added successfully!")
                    st.rerun()

    # ---------------- UPDATE / DELETE ----------------
    with tab_edit:
        df = products_module.get_all_products()
        if df.empty:
            st.info("No products available to edit.")
        else:
            options = {f"#{row.id} - {row['name']}": row.id for _, row in df.iterrows()}
            selected_label = st.selectbox("Select a product", list(options.keys()))
            selected_id = options[selected_label]
            prod = products_module.get_product(selected_id)

            if prod:
                with st.form("edit_product_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        name = st.text_input("Product Name *", value=prod["name"])
                        cat_index = config.PRODUCT_CATEGORIES.index(prod["category"]) \
                            if prod["category"] in config.PRODUCT_CATEGORIES else 0
                        category = st.selectbox("Category", config.PRODUCT_CATEGORIES, index=cat_index)
                        unit = st.text_input("Unit", value=prod["unit"] or "pcs")
                        barcode = st.text_input("Barcode", value=prod["barcode"] or "")
                    with c2:
                        cost_price = st.number_input("Cost Price", min_value=0.0, step=0.5, value=float(prod["cost_price"]))
                        sale_price = st.number_input("Sale Price", min_value=0.0, step=0.5, value=float(prod["sale_price"]))
                        reorder_level = st.number_input("Reorder Level", min_value=0, value=int(prod["reorder_level"]))
                        is_active = st.checkbox("Active", value=bool(prod["is_active"]))

                    update_clicked = st.form_submit_button("💾 Update Product", use_container_width=True)
                    if update_clicked:
                        products_module.update_product(
                            selected_id, name.strip(), category, unit.strip(),
                            barcode.strip(), cost_price, sale_price, reorder_level, is_active
                        )
                        utils.success("Product updated successfully!")
                        st.rerun()

                st.divider()
                if utils.confirm_delete(f"product_{selected_id}", "Delete this product"):
                    products_module.delete_product(selected_id)
                    utils.success("Product deleted.")
                    st.rerun()
