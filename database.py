"""
database.py
Handles SQLite connection, initialization, and low-level query execution.
"""

import sqlite3
import pandas as pd
from contextlib import contextmanager
import config


def get_connection():
    """Create and return a new SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_cursor(commit=False):
    """Context manager yielding a cursor; commits/closes automatically."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        yield cur
        if commit:
            conn.commit()
    finally:
        conn.close()


def init_db():
    """Initialize the database using sql/schema.sql (idempotent)."""
    with open(config.SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn = get_connection()
    try:
        conn.executescript(schema_sql)
        conn.commit()
    finally:
        conn.close()


def run_query(query: str, params: tuple = ()):
    """SELECT query -> returns list of sqlite3.Row."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        conn.close()


def run_query_df(query: str, params: tuple = ()) -> pd.DataFrame:
    """SELECT query -> returns pandas DataFrame."""
    conn = get_connection()
    try:
        df = pd.read_sql_query(query, conn, params=params)
        return df
    finally:
        conn.close()


def execute(query: str, params: tuple = ()) -> int:
    """INSERT/UPDATE/DELETE -> returns lastrowid (for INSERT) or rowcount."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid if cur.lastrowid else cur.rowcount
    finally:
        conn.close()


def execute_many(query: str, param_list: list) -> None:
    """Bulk INSERT/UPDATE/DELETE."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.executemany(query, param_list)
        conn.commit()
    finally:
        conn.close()
