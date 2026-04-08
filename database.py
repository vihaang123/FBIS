"""
database.py - SQLite database management for FBIS
Handles all database operations: creation, insertion, and retrieval.
"""

import sqlite3
import pandas as pd
import json
import os

DB_PATH = "fbis_data.db"


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # enables column name access
    return conn


def initialize_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_type         TEXT,
            name              TEXT,
            user_type_other   TEXT,
            age               INTEGER,
            income            REAL,
            expenses          REAL,
            savings           REAL,
            daily_spending    REAL,
            weekly_spending   REAL,
            expense_categories TEXT,     -- JSON list
            spending_habit    TEXT,
            tracking          TEXT,
            discipline        TEXT,
            overspending      TEXT,
            investment        TEXT,
            investment_amount REAL,
            investment_types  TEXT,      -- JSON list
            emergency_fund    TEXT,
            stress            INTEGER,
            goal              TEXT
        )
    """)
    conn.commit()
    conn.close()


def insert_user(data: dict) -> int:
    """
    Insert a new user record.
    Returns the new row id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Serialize list fields to JSON strings
    data["expense_categories"] = json.dumps(data.get("expense_categories", []))
    data["investment_types"] = json.dumps(data.get("investment_types", []))

    cursor.execute("""
        INSERT INTO user_data (
            user_type, user_type_other, name, age, income, expenses, savings,
            daily_spending, weekly_spending, expense_categories,
            spending_habit, tracking, discipline, overspending,
            investment, investment_amount, investment_types,
            emergency_fund, stress, goal
        ) VALUES (
            :user_type, :user_type_other, :name, :age, :income, :expenses, :savings,
            :daily_spending, :weekly_spending, :expense_categories,
            :spending_habit, :tracking, :discipline, :overspending,
            :investment, :investment_amount, :investment_types,
            :emergency_fund, :stress, :goal
        )
    """, data)

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def fetch_all_users() -> pd.DataFrame:
    """
    Retrieve all user records as a DataFrame.
    Deserializes JSON list columns automatically.
    """
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM user_data ORDER BY created_at DESC", conn)
    conn.close()

    if df.empty:
        return df

    # Deserialize JSON columns
    df["expense_categories"] = df["expense_categories"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else []
    )
    df["investment_types"] = df["investment_types"].apply(
        lambda x: json.loads(x) if isinstance(x, str) else []
    )

    return df


def fetch_user_by_id(user_id: int) -> pd.Series | None:
    """Fetch a single user record by id."""
    df = fetch_all_users()
    if df.empty:
        return None
    row = df[df["id"] == user_id]
    return row.iloc[0] if not row.empty else None


def get_user_count() -> int:
    """Return total number of user records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_data")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def clear_all_data():
    """Delete all records (for dev/testing)."""
    conn = get_connection()
    conn.execute("DELETE FROM user_data")
    conn.commit()
    conn.close()