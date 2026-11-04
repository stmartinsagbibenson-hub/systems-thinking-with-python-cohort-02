import csv
import tempfile
import unittest
from pathlib import Path

from finance_tool.importer import load_transactions


class TestTransactionImporter(unittest.TestCase):

    def create_csv(self, headers, rows):
        with tempfile.NamedTemporaryFile(
            mode="w",
            newline="",
            encoding="utf-8",
            suffix=".csv",
            delete=False,
        ) as temporary_file:
            writer = csv.writer(temporary_file)
            writer.writerow(headers)
            writer.writerows(rows)
            file_path = temporary_file.name

        self.addCleanup(Path(file_path).unlink, missing_ok=True)

        return file_path

    def test_import_valid_transactions(self):
        file_path = self.create_csv(
            ["date", "description", "amount", "type"],
            [
                ["2026-01-05", "Salary", "200000", "income"],
                ["2026-01-06", "Grocery shopping", "30000", "expense"],
            ],
        )
        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 2)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(_skipped), 0)

    def test_invalid_amount_is_rejected(self):
        file_path = self.create_csv(
            ["date", "description", "amount", "type"],
            [["2026-01-05", "Groceries", "abc", "expense"]],
        )

        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 0)
        self.assertEqual(len(errors), 1)

    def test_invalid_date_is_rejected(self):
        file_path = self.create_csv(
            ["date", "description", "amount", "type"],
            [["not-a-date", "Groceries", "30000", "expense"]],
        )

        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 0)
        self.assertEqual(len(errors), 1)

    def test_invalid_transaction_type_is_rejected(self):
        file_path = self.create_csv(
            ["date", "description", "amount", "type"],
            [["2026-01-05", "Payment", "30000", "unknown"]],
        )

        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 0)
        self.assertEqual(len(errors), 1)

    def test_duplicate_rows_are_detected(self):
        file_path = self.create_csv(
            ["date", "description", "amount", "type"],
            [
                ["2026-01-05", "Groceries", "30000", "expense"],
                ["2026-01-05", "Groceries", "30000", "expense"],
            ],
        )

        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 1)
        self.assertEqual(len(errors), 1)

    def test_empty_file_raises_error(self):
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            delete=False,
        ) as temporary_file:
            file_path = temporary_file.name

        self.addCleanup(Path(file_path).unlink, missing_ok=True)

        with self.assertRaisesRegex(ValueError, "no headers"):
            load_transactions(file_path)

    def test_missing_required_column(self):
        file_path = self.create_csv(
            ["date", "description", "amount"],
            [["2026-01-05", "Groceries", "30000"]],
        )

        with self.assertRaisesRegex(ValueError, "Missing column"):
            load_transactions(file_path)

    def test_partial_success(self):
        file_path = self.create_csv(
            ["date", "description", "amount", "type"],
            [
                ["2026-01-05", "Salary", "200000", "income"],
                ["invalid-date", "Groceries", "30000", "expense"],
                ["2026-01-06", "Electricity", "15000", "expense"],
            ],
        )

        transactions, errors, skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 2)
        self.assertEqual(len(errors), 1)
        self.assertEqual(len(skipped), 0)

    def test_bank_format_skips_pending_transactions(self):
        file_path = self.create_csv(
            [
                "transaction_id",
                "transaction_date",
                "transaction_type",
                "description",
                "amount",
                "currency",
                "status",
            ],
            [
                [
                    "TX001",
                    "2026-01-05",
                    "credit",
                    "Salary",
                    "200000",
                    "NGN",
                    "completed",
                ],
                [
                    "TX002",
                    "2026-01-06",
                    "debit",
                    "Groceries",
                    "30000",
                    "NGN",
                    "pending",
                ],
            ],
        )

        transactions, errors, skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["type"], "income")
        self.assertEqual(len(skipped), 1)
        self.assertEqual(len(errors), 0)

    def test_non_positive_amount_is_rejected(self):
        file_path = self.create_csv(
            ["date", "description", "amount", "type"],
            [
                ["2026-01-05", "Groceries", "0", "expense"],
                ["2026-01-06", "Transport", "-500", "expense"],
            ],
        )
        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 0)
        self.assertEqual(len(errors), 2)

    def test_bank_salary_credit_is_income(self):
        file_path = self.create_csv(
            [
                "transaction_id",
                "transaction_date",
                "transaction_type",
                "description",
                "amount",
                "currency",
                "status",
            ],
            [["TX003", "2026-01-05", "credit", "Salary", "200000", "NGN", "completed"]],
        )

        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0]["type"], "income")
        self.assertEqual(len(errors), 0)

    def test_bank_grocery_debit_is_expense(self):
        file_path = self.create_csv(
            [
                "transaction_id",
                "transaction_date",
                "transaction_type",
                "description",
                "amount",
                "currency",
                "status",
            ],
            [
                [
                    "TX004",
                    "2026-01-05",
                    "debit",
                    "Grocery shopping",
                    "30000",
                    "NGN",
                    "completed",
                ]
            ],
        )

        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(transactions[0]["type"], "expense")
        self.assertEqual(len(errors), 0)

    def test_bank_refund_is_classified_correctly(self):
        file_path = self.create_csv(
            [
                "transaction_id",
                "transaction_date",
                "transaction_type",
                "description",
                "amount",
                "currency",
                "status",
            ],
            [
                [
                    "TX005",
                    "2026-01-05",
                    "credit",
                    "Refund for groceries",
                    "5000",
                    "NGN",
                    "completed",
                ]
            ],
        )

        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(transactions[0]["type"], "refund")
        self.assertEqual(len(errors), 0)

    def test_bank_transfer_is_classified_correctly(self):
        file_path = self.create_csv(
            [
                "transaction_id",
                "transaction_date",
                "transaction_type",
                "description",
                "amount",
                "currency",
                "status",
            ],
            [
                [
                    "TX006",
                    "2026-01-05",
                    "debit",
                    "Transfer to savings",
                    "20000",
                    "NGN",
                    "completed",
                ]
            ],
        )

        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(transactions[0]["type"], "transfer")
        self.assertEqual(len(errors), 0)

    def test_csv_accepts_refund_and_transfer_types(self):
        file_path = self.create_csv(
            ["date", "description", "amount", "type"],
            [
                ["2026-01-05", "Grocery refund", "5000", "refund"],
                ["2026-01-06", "Transfer to savings", "20000", "transfer"],
            ],
        )

        transactions, errors, _skipped = load_transactions(file_path)

        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]["type"], "refund")
        self.assertEqual(transactions[1]["type"], "transfer")
        self.assertEqual(len(errors), 0)


if __name__ == "__main__":
    unittest.main()
