import hashlib
import sqlite3
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

DATABASE = "data/finance.db"


def create_database():
    Path(DATABASE).parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount TEXT NOT NULL,
            type TEXT NOT NULL,
            category TEXT,
            currency TEXT NOT NULL,
            source_file TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS import_history (
            file_hash TEXT PRIMARY KEY,
            source_file TEXT,
            imported_count INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month TEXT NOT NULL,
            category TEXT NOT NULL,
            amount TEXT NOT NULL,
            UNIQUE(month, category)
        )
    """)

    connection.commit()
    connection.close()


def save_transactions(transactions, file_path):
    create_database()

    # Identify the file to prevent importing the same file twice
    with open(file_path, "rb") as file:
        file_hash = hashlib.sha256(file.read()).hexdigest()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT file_hash FROM import_history WHERE file_hash = ?", (file_hash,)
    )

    if cursor.fetchone():
        connection.close()
        return 0, True

    saved = 0

    for transaction in transactions:
        cursor.execute(
            """
            INSERT OR IGNORE INTO transactions
            (transaction_id, date, description, amount, type,
             category, currency, source_file)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                transaction.get("transaction_id"),
                transaction["date"],
                transaction["description"],
                str(transaction["amount"]),
                transaction["type"],
                transaction.get("category"),
                transaction.get("currency", "NGN"),
                Path(file_path).name,
            ),
        )

        saved += cursor.rowcount

    cursor.execute(
        """
        INSERT INTO import_history
        (file_hash, source_file, imported_count)
        VALUES (?, ?, ?)
    """,
        (file_hash, Path(file_path).name, saved),
    )

    connection.commit()
    connection.close()

    return saved, False


def get_all_transactions():
    create_database()

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()
    cursor.execute("SELECT * FROM transactions ORDER BY date")

    transactions = [dict(row) for row in cursor.fetchall()]

    connection.close()

    return transactions


def update_categories(transactions):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    for transaction in transactions:
        if transaction.get("transaction_id"):
            cursor.execute(
                """
                UPDATE transactions
                SET category = ?
                WHERE transaction_id = ?
            """,
                (transaction["category"], transaction["transaction_id"]),
            )

        else:
            cursor.execute(
                """
                UPDATE transactions
                SET category = ?
                WHERE date = ?
                AND description = ?
                AND amount = ?
                AND type = ?
            """,
                (
                    transaction["category"],
                    transaction["date"],
                    transaction["description"],
                    str(transaction["amount"]),
                    transaction["type"],
                ),
            )

    connection.commit()
    connection.close()


def set_budget(month, category, amount):

    # Validate the month
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        raise ValueError("Month must use YYYY-MM format.")

    category = category.strip()

    if not category:
        raise ValueError("Category cannot be empty.")

    if category.lower() in ["income", "refunds"]:
        raise ValueError("You cannot set a budget for income.")

    try:
        amount = Decimal(str(amount))
    except InvalidOperation:
        raise ValueError("Budget must be a number.")

    if not amount.is_finite() or amount <= 0:
        raise ValueError("Budget must be greater than zero.")

    create_database()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO budgets (month, category, amount)
        VALUES (?, ?, ?)
    """,
        (month, category, str(amount)),
    )

    connection.commit()
    connection.close()


def reset_database():
    create_database()
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    cursor.execute("DELETE FROM transactions")
    cursor.execute("DELETE FROM import_history")
    cursor.execute("DELETE FROM budgets")

    connection.commit()
    connection.close()


def get_budgets(month):
    create_database()

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT category, amount
        FROM budgets
        WHERE month = ?
    """,
        (month,),
    )

    rows = cursor.fetchall()
    connection.close()

    from decimal import Decimal

    budgets = {}

    for row in rows:
        budgets[row[0]] = Decimal(row[1])

    return budgets
