import tempfile
import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from finance_tool import database


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_directory.name) / "test.db"

        self.database_patch = patch.object(
            database,
            "DATABASE",
            str(self.database_path),
        )
        self.database_patch.start()

        self.addCleanup(self.database_patch.stop)
        self.addCleanup(self.temp_directory.cleanup)

        database.create_database()

    def test_database_is_created(self):
        self.assertTrue(self.database_path.exists())

    def test_save_transactions(self):
        csv_path = Path(self.temp_directory.name) / "transactions.csv"
        csv_path.write_text("sample transaction data", encoding="utf-8")

        transactions = [
            {
                "transaction_id": "TX001",
                "date": "2026-01-05",
                "description": "Salary",
                "amount": Decimal(200000),
                "type": "income",
                "category": "Income",
                "currency": "NGN",
            }
        ]

        saved, duplicate = database.save_transactions(transactions, csv_path)

        self.assertEqual(saved, 1)
        self.assertFalse(duplicate)

    def test_same_file_cannot_be_imported_twice(self):
        csv_path = Path(self.temp_directory.name) / "transactions.csv"
        csv_path.write_text("sample transaction data", encoding="utf-8")

        transactions = [
            {
                "transaction_id": "TX001",
                "date": "2026-01-05",
                "description": "Salary",
                "amount": Decimal(200000),
                "type": "income",
                "category": "Income",
                "currency": "NGN",
            }
        ]

        database.save_transactions(transactions, csv_path)

        saved, duplicate = database.save_transactions(transactions, csv_path)

        self.assertEqual(saved, 0)
        self.assertTrue(duplicate)

    def test_get_all_transactions(self):
        csv_path = Path(self.temp_directory.name) / "transactions.csv"
        csv_path.write_text("sample transaction data", encoding="utf-8")

        transaction = {
            "transaction_id": "TX001",
            "date": "2026-01-05",
            "description": "Salary",
            "amount": Decimal(200000),
            "type": "income",
            "category": "Income",
            "currency": "NGN",
        }

        database.save_transactions([transaction], csv_path)

        result = database.get_all_transactions()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["description"], "Salary")

    def test_set_and_get_budget(self):
        database.set_budget(
            "2026-01",
            "Food & Groceries",
            "50000",
        )

        budgets = database.get_budgets("2026-01")

        self.assertEqual(
            budgets["Food & Groceries"],
            Decimal(50000),
        )

    def test_invalid_budget_month(self):
        with self.assertRaises(ValueError):
            database.set_budget("2026-15", "Food", "50000")

    def test_empty_budget_category(self):
        with self.assertRaises(ValueError):
            database.set_budget("2026-01", "  ", "50000")

    def test_negative_budget(self):
        with self.assertRaises(ValueError):
            database.set_budget("2026-01", "Food", "-500")

    def test_income_budget_is_rejected(self):
        with self.assertRaises(ValueError):
            database.set_budget("2026-01", "Income", "50000")

    def test_reset_database(self):
        csv_path = Path(self.temp_directory.name) / "transactions.csv"
        csv_path.write_text("sample transaction data", encoding="utf-8")

        transaction = {
            "transaction_id": "TX001",
            "date": "2026-01-05",
            "description": "Salary",
            "amount": Decimal(200000),
            "type": "income",
            "category": "Income",
            "currency": "NGN",
        }

        database.save_transactions([transaction], csv_path)
        database.set_budget("2026-01", "Food", "50000")

        database.reset_database()

        self.assertEqual(database.get_all_transactions(), [])
        self.assertEqual(database.get_budgets("2026-01"), {})


if __name__ == "__main__":
    unittest.main()
