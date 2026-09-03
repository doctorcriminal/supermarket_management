-- ============================================================
-- Supermarket Management System - Database Schema (SQLite)
-- ============================================================

PRAGMA foreign_keys = ON;

-- ---------------- PRODUCTS ----------------
CREATE TABLE IF NOT EXISTS products (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    category        TEXT,
    unit            TEXT DEFAULT 'pcs',
    barcode         TEXT UNIQUE,
    cost_price      REAL NOT NULL DEFAULT 0,
    sale_price      REAL NOT NULL DEFAULT 0,
    reorder_level   INTEGER DEFAULT 10,
    is_active       INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- ---------------- INVENTORY ----------------
CREATE TABLE IF NOT EXISTS inventory (
    product_id      INTEGER PRIMARY KEY,
    quantity        REAL NOT NULL DEFAULT 0,
    updated_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS stock_movements (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id      INTEGER NOT NULL,
    change_qty      REAL NOT NULL,          -- positive = in, negative = out
    reason          TEXT,                    -- purchase / sale / return / adjustment
    ref_id          INTEGER,                 -- id of related record (purchase/sale/return)
    created_at      TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);

-- ---------------- PURCHASES ----------------
CREATE TABLE IF NOT EXISTS purchases (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_name   TEXT,
    purchase_date   TEXT DEFAULT (datetime('now')),
    total_amount    REAL DEFAULT 0,
    payment_status  TEXT DEFAULT 'unpaid',   -- paid / unpaid / partial
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS purchase_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    purchase_id     INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        REAL NOT NULL,
    cost_price      REAL NOT NULL,
    subtotal        REAL NOT NULL,
    FOREIGN KEY (purchase_id) REFERENCES purchases(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ---------------- SALES (POS) ----------------
CREATE TABLE IF NOT EXISTS sales (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_date       TEXT DEFAULT (datetime('now')),
    customer_name   TEXT DEFAULT 'Walk-in',
    total_amount    REAL DEFAULT 0,
    discount        REAL DEFAULT 0,
    payment_method  TEXT DEFAULT 'cash',     -- cash / card / credit
    cashier         TEXT
);

CREATE TABLE IF NOT EXISTS sale_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id         INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        REAL NOT NULL,
    sale_price      REAL NOT NULL,
    subtotal        REAL NOT NULL,
    FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ---------------- RETURNS ----------------
CREATE TABLE IF NOT EXISTS returns (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    return_type     TEXT NOT NULL,           -- sale_return / purchase_return
    ref_id          INTEGER,                 -- sale_id or purchase_id
    product_id      INTEGER NOT NULL,
    quantity        REAL NOT NULL,
    amount          REAL NOT NULL,
    reason          TEXT,
    return_date     TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- ---------------- CASH / EXPENSES ----------------
CREATE TABLE IF NOT EXISTS cash_transactions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    txn_type        TEXT NOT NULL,           -- in / out
    category        TEXT,                    -- sales/expense/salary/purchase/other
    amount          REAL NOT NULL,
    description     TEXT,
    txn_date        TEXT DEFAULT (datetime('now'))
);

-- ---------------- EMPLOYEES ----------------
CREATE TABLE IF NOT EXISTS employees (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    position        TEXT,
    phone           TEXT,
    email           TEXT,
    salary          REAL DEFAULT 0,
    hire_date       TEXT DEFAULT (date('now')),
    status          TEXT DEFAULT 'active'    -- active / inactive
);

-- ---------------- ATTENDANCE ----------------
CREATE TABLE IF NOT EXISTS attendance (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id     INTEGER NOT NULL,
    att_date        TEXT DEFAULT (date('now')),
    status          TEXT DEFAULT 'present',  -- present/absent/leave/half-day
    check_in        TEXT,
    check_out       TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
    UNIQUE(employee_id, att_date)
);

-- ---------------- ASSETS ----------------
CREATE TABLE IF NOT EXISTS assets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    category        TEXT,
    purchase_date   TEXT DEFAULT (date('now')),
    value           REAL DEFAULT 0,
    status          TEXT DEFAULT 'in_use',   -- in_use / maintenance / disposed
    notes           TEXT
);

-- ---------------- ACCOUNTING (LEDGER) ----------------
CREATE TABLE IF NOT EXISTS ledger (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date      TEXT DEFAULT (date('now')),
    account         TEXT NOT NULL,           -- e.g. Sales, Purchases, Salaries, Cash, Assets
    description     TEXT,
    debit           REAL DEFAULT 0,
    credit          REAL DEFAULT 0
);
