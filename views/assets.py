"""
pages/assets.py
CRUD UI for fixed assets.
"""

import streamlit as st
from modules import assets as assets_module
import utils
import config


def render():
    st.title("🏢 Assets")

    st.metric("Total Asset Value", utils.money(assets_module.total_asset_value()))
    st.divider()

    tab_list, tab_add, tab_edit = st.tabs(["📋 All Assets", "➕ Add Asset", "✏️ Edit / Delete"])

    # ---------------- LIST ----------------
    with tab_list:
        df = assets_module.get_all_assets()
        utils.show_dataframe(df, "No assets recorded yet.")

    # ---------------- CREATE ----------------
    with tab_add:
        with st.form("add_asset_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Asset Name *")
                category = st.selectbox("Category", config.ASSET_CATEGORIES)
                purchase_date = st.date_input("Purchase Date", value=utils.today_str())
            with c2:
                value = st.number_input("Value", min_value=0.0, step=100.0)
                status = st.selectbox("Status", config.ASSET_STATUSES)
                notes = st.text_area("Notes")

            submitted = st.form_submit_button("Save Asset", type="primary", use_container_width=True)
            if submitted:
                if not name.strip():
                    utils.error("Asset name is required.")
                else:
                    assets_module.create_asset(name.strip(), category, str(purchase_date), value, status, notes)
                    utils.success(f"Asset '{name}' added successfully!")
                    st.rerun()

    # ---------------- UPDATE / DELETE ----------------
    with tab_edit:
        df = assets_module.get_all_assets()
        if df.empty:
            st.info("No assets available to edit.")
        else:
            options = {f"#{row.id} - {row['name']}": row.id for _, row in df.iterrows()}
            selected_label = st.selectbox("Select asset", list(options.keys()))
            selected_id = options[selected_label]
            asset = assets_module.get_asset(selected_id)

            if asset:
                with st.form("edit_asset_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        name = st.text_input("Asset Name *", value=asset["name"])
                        cat_index = config.ASSET_CATEGORIES.index(asset["category"]) \
                            if asset["category"] in config.ASSET_CATEGORIES else 0
                        category = st.selectbox("Category", config.ASSET_CATEGORIES, index=cat_index)
                        purchase_date = st.text_input("Purchase Date", value=asset["purchase_date"])
                    with c2:
                        value = st.number_input("Value", min_value=0.0, step=100.0, value=float(asset["value"]))
                        status_index = config.ASSET_STATUSES.index(asset["status"]) \
                            if asset["status"] in config.ASSET_STATUSES else 0
                        status = st.selectbox("Status", config.ASSET_STATUSES, index=status_index)
                        notes = st.text_area("Notes", value=asset["notes"] or "")

                    update_clicked = st.form_submit_button("💾 Update Asset", use_container_width=True)
                    if update_clicked:
                        assets_module.update_asset(
                            selected_id, name.strip(), category, purchase_date, value, status, notes
                        )
                        utils.success("Asset updated successfully!")
                        st.rerun()

                st.divider()
                if utils.confirm_delete(f"asset_{selected_id}", "Delete this asset"):
                    assets_module.delete_asset(selected_id)
                    utils.success("Asset deleted.")
                    st.rerun()
