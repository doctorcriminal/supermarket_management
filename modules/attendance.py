"""
modules/attendance.py
CRUD for daily employee attendance (one record per employee per day).
"""

import pandas as pd
import database as db


def get_attendance(att_date: str = None) -> pd.DataFrame:
    query = """
        SELECT a.id, e.name AS employee_name, a.att_date, a.status,
               a.check_in, a.check_out, a.employee_id
        FROM attendance a
        JOIN employees e ON e.id = a.employee_id
    """
    params = ()
    if att_date:
        query += " WHERE a.att_date = ?"
        params = (att_date,)
    query += " ORDER BY a.att_date DESC, e.name ASC"
    return db.run_query_df(query, params)


def mark_attendance(employee_id: int, att_date: str, status: str, check_in: str = "", check_out: str = "") -> int:
    """Upsert: one attendance record per employee per date."""
    existing = db.run_query(
        "SELECT id FROM attendance WHERE employee_id=? AND att_date=?",
        (employee_id, att_date),
    )
    if existing:
        db.execute(
            """UPDATE attendance SET status=?, check_in=?, check_out=?
               WHERE employee_id=? AND att_date=?""",
            (status, check_in, check_out, employee_id, att_date),
        )
        return existing[0]["id"]
    else:
        return db.execute(
            """INSERT INTO attendance (employee_id, att_date, status, check_in, check_out)
               VALUES (?, ?, ?, ?, ?)""",
            (employee_id, att_date, status, check_in, check_out),
        )


def delete_attendance(att_id: int):
    db.execute("DELETE FROM attendance WHERE id = ?", (att_id,))


def monthly_summary(employee_id: int, year_month: str) -> pd.DataFrame:
    """year_month format: 'YYYY-MM'"""
    query = """
        SELECT status, COUNT(*) AS days
        FROM attendance
        WHERE employee_id = ? AND strftime('%Y-%m', att_date) = ?
        GROUP BY status
    """
    return db.run_query_df(query, (employee_id, year_month))
