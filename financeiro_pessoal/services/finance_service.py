from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from financeiro_pessoal.config import DB_PATH

DEFAULT_CATEGORIES = [
    "Salário",
    "Trabalho extra",
    "Freelance",
    "Benefícios",
    "Reembolsos",
    "Outros",
    "Moradia",
    "Água",
    "Energia elétrica",
    "Internet",
    "Telefone",
    "Alimentação",
    "Mercado",
    "Transporte",
    "Saúde",
    "Educação",
    "Lazer",
    "Assinaturas",
    "Compras",
    "Impostos e taxas",
    "Dívidas",
    "Outros",
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_db() -> None:
    db_path = Path(DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incomes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                value_cents INTEGER NOT NULL,
                category TEXT NOT NULL,
                expected_date TEXT NOT NULL,
                received_date TEXT,
                status TEXT NOT NULL,
                payment_method TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                value_cents INTEGER NOT NULL,
                category TEXT NOT NULL,
                due_date TEXT NOT NULL,
                paid_date TEXT,
                payment_method TEXT,
                status TEXT NOT NULL,
                recurrence TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )

        conn.commit()
    finally:
        conn.close()

    ensure_default_categories()


def ensure_default_categories() -> None:
    conn = get_connection()
    try:
        for name in DEFAULT_CATEGORIES:
            conn.execute(
                "INSERT OR IGNORE INTO categories (name) VALUES (?)",
                (name,),
            )
        conn.commit()
    finally:
        conn.close()


def add_income(data: Dict[str, Any]) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO incomes (
                description, value_cents, category, expected_date,
                received_date, status, payment_method, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["description"],
                int(data["value_cents"]),
                data["category"],
                data["expected_date"],
                data.get("received_date"),
                data["status"],
                data.get("payment_method"),
                data.get("notes"),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def list_incomes(year: Optional[int] = None, month: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        query = "SELECT * FROM incomes"
        params: List[Any] = []
        filters: List[str] = []

        if year is not None:
            filters.append("strftime('%Y', expected_date) = ?")
            params.append(str(year))
        if month is not None:
            filters.append("strftime('%m', expected_date) = ?")
            params.append(f"{month:02d}")

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY expected_date DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_income(income_id: int, data: Dict[str, Any]) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE incomes
            SET description = ?, value_cents = ?, category = ?, expected_date = ?,
                received_date = ?, status = ?, payment_method = ?, notes = ?
            WHERE id = ?
            """,
            (
                data["description"],
                int(data["value_cents"]),
                data["category"],
                data["expected_date"],
                data.get("received_date"),
                data["status"],
                data.get("payment_method"),
                data.get("notes"),
                income_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def delete_income(income_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM incomes WHERE id = ?", (income_id,))
        conn.commit()
    finally:
        conn.close()


def add_expense(data: Dict[str, Any]) -> int:
    conn = get_connection()
    try:
        cursor = conn.execute(
            """
            INSERT INTO expenses (
                description, value_cents, category, due_date, paid_date,
                payment_method, status, recurrence, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["description"],
                int(data["value_cents"]),
                data["category"],
                data["due_date"],
                data.get("paid_date"),
                data.get("payment_method"),
                data["status"],
                data.get("recurrence"),
                data.get("notes"),
            ),
        )
        conn.commit()
        return int(cursor.lastrowid)
    finally:
        conn.close()


def list_expenses(year: Optional[int] = None, month: Optional[int] = None) -> List[Dict[str, Any]]:
    conn = get_connection()
    try:
        query = "SELECT * FROM expenses"
        params: List[Any] = []
        filters: List[str] = []

        if year is not None:
            filters.append("strftime('%Y', due_date) = ?")
            params.append(str(year))
        if month is not None:
            filters.append("strftime('%m', due_date) = ?")
            params.append(f"{month:02d}")

        if filters:
            query += " WHERE " + " AND ".join(filters)

        query += " ORDER BY due_date DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_expense(expense_id: int, data: Dict[str, Any]) -> None:
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE expenses
            SET description = ?, value_cents = ?, category = ?, due_date = ?,
                paid_date = ?, payment_method = ?, status = ?, recurrence = ?, notes = ?
            WHERE id = ?
            """,
            (
                data["description"],
                int(data["value_cents"]),
                data["category"],
                data["due_date"],
                data.get("paid_date"),
                data.get("payment_method"),
                data["status"],
                data.get("recurrence"),
                data.get("notes"),
                expense_id,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def delete_expense(expense_id: int) -> None:
    conn = get_connection()
    try:
        conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
    finally:
        conn.close()


def get_categories() -> List[str]:
    conn = get_connection()
    try:
        rows = conn.execute("SELECT name FROM categories ORDER BY name").fetchall()
        return [row["name"] for row in rows]
    finally:
        conn.close()


def set_setting(key: str, value: str) -> None:
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value),
        )
        conn.commit()
    finally:
        conn.close()


def get_setting(key: str, default: str = "") -> str:
    conn = get_connection()
    try:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default
    finally:
        conn.close()


initialize_db()
