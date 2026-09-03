"""
modules/employees.py
CRUD for employee records.
"""

import pandas as pd
import database as db


def get_all_employees(active_only: bool = False) -> pd.DataFrame:
    query = "SELECT id, name, position, phone, email, salary, hire_date, status FROM employees"
    if active_only:
        query += " WHERE status = 'active'"
    query += " ORDER BY id DESC"
    return db.run_query_df(query)


def get_employee(employee_id: int):
    rows = db.run_query("SELECT * FROM employees WHERE id = ?", (employee_id,))
    return rows[0] if rows else None


def create_employee(name, position, phone, email, salary, hire_date, status="active") -> int:
    return db.execute(
        """INSERT INTO employees (name, position, phone, email, salary, hire_date, status)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (name, position, phone, email, salary, hire_date, status),
    )


def update_employee(employee_id, name, position, phone, email, salary, hire_date, status):
    db.execute(
        """UPDATE employees
           SET name=?, position=?, phone=?, email=?, salary=?, hire_date=?, status=?
           WHERE id=?""",
        (name, position, phone, email, salary, hire_date, status, employee_id),
    )


def delete_employee(employee_id):
    db.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
