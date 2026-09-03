"""
pages/employees.py
CRUD UI for employees, plus a linked attendance-marking tab.
"""

import streamlit as st
from modules import employees as employees_module
from modules import attendance as attendance_module
import utils
import config


def render():
    st.title("👥 Employees")

    tab_list, tab_add, tab_edit, tab_attendance = st.tabs(
        ["📋 All Employees", "➕ Add Employee", "✏️ Edit / Delete", "🕒 Attendance"]
    )

    # ---------------- LIST ----------------
    with tab_list:
        df = employees_module.get_all_employees()
        utils.show_dataframe(df, "No employees yet. Add one from the 'Add Employee' tab.")

    # ---------------- CREATE ----------------
    with tab_add:
        with st.form("add_employee_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name *")
                position = st.selectbox("Position", config.EMPLOYEE_POSITIONS)
                phone = st.text_input("Phone")
            with c2:
                email = st.text_input("Email")
                salary = st.number_input("Salary", min_value=0.0, step=100.0)
                hire_date = st.date_input("Hire Date", value=utils.today_str())

            submitted = st.form_submit_button("Save Employee", type="primary", use_container_width=True)
            if submitted:
                if not name.strip():
                    utils.error("Employee name is required.")
                else:
                    employees_module.create_employee(
                        name.strip(), position, phone, email, salary, str(hire_date)
                    )
                    utils.success(f"Employee '{name}' added successfully!")
                    st.rerun()

    # ---------------- UPDATE / DELETE ----------------
    with tab_edit:
        df = employees_module.get_all_employees()
        if df.empty:
            st.info("No employees available to edit.")
        else:
            options = {f"#{row.id} - {row['name']}": row.id for _, row in df.iterrows()}
            selected_label = st.selectbox("Select employee", list(options.keys()))
            selected_id = options[selected_label]
            emp = employees_module.get_employee(selected_id)

            if emp:
                with st.form("edit_employee_form"):
                    c1, c2 = st.columns(2)
                    with c1:
                        name = st.text_input("Full Name *", value=emp["name"])
                        pos_index = config.EMPLOYEE_POSITIONS.index(emp["position"]) \
                            if emp["position"] in config.EMPLOYEE_POSITIONS else 0
                        position = st.selectbox("Position", config.EMPLOYEE_POSITIONS, index=pos_index)
                        phone = st.text_input("Phone", value=emp["phone"] or "")
                    with c2:
                        email = st.text_input("Email", value=emp["email"] or "")
                        salary = st.number_input("Salary", min_value=0.0, step=100.0, value=float(emp["salary"]))
                        status = st.selectbox("Status", ["active", "inactive"],
                                               index=0 if emp["status"] == "active" else 1)

                    update_clicked = st.form_submit_button("💾 Update Employee", use_container_width=True)
                    if update_clicked:
                        employees_module.update_employee(
                            selected_id, name.strip(), position, phone, email,
                            salary, emp["hire_date"], status
                        )
                        utils.success("Employee updated successfully!")
                        st.rerun()

                st.divider()
                if utils.confirm_delete(f"employee_{selected_id}", "Delete this employee"):
                    employees_module.delete_employee(selected_id)
                    utils.success("Employee deleted.")
                    st.rerun()

    # ---------------- ATTENDANCE ----------------
    with tab_attendance:
        st.subheader("Mark Attendance")
        emp_df = employees_module.get_all_employees(active_only=True)
        if emp_df.empty:
            st.info("No active employees.")
        else:
            emp_options = {row["name"]: row["id"] for _, row in emp_df.iterrows()}
            c1, c2, c3 = st.columns(3)
            with c1:
                selected_emp = st.selectbox("Employee", list(emp_options.keys()))
            with c2:
                att_date = st.date_input("Date", value=utils.today_str(), key="att_date_input")
            with c3:
                status = st.selectbox("Status", config.ATTENDANCE_STATUSES)

            c4, c5 = st.columns(2)
            with c4:
                check_in = st.text_input("Check-in time (optional)", placeholder="09:00")
            with c5:
                check_out = st.text_input("Check-out time (optional)", placeholder="17:00")

            if st.button("✅ Mark Attendance", type="primary"):
                attendance_module.mark_attendance(
                    emp_options[selected_emp], str(att_date), status, check_in, check_out
                )
                utils.success("Attendance marked.")
                st.rerun()

            st.divider()
            st.subheader("📋 Attendance Records")
            att_df = attendance_module.get_attendance()
            utils.show_dataframe(att_df, "No attendance records yet.")

            if not att_df.empty:
                del_options = {f"#{row.id} - {row['employee_name']} ({row['att_date']})": row.id
                               for _, row in att_df.iterrows()}
                selected_att_label = st.selectbox("Select record to delete", list(del_options.keys()))
                selected_att_id = del_options[selected_att_label]
                if utils.confirm_delete(f"attendance_{selected_att_id}", "Delete this attendance record"):
                    attendance_module.delete_attendance(selected_att_id)
                    utils.success("Attendance record deleted.")
                    st.rerun()
