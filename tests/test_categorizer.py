import unittest

from finance_tool.categorizer import categorize_transaction, categorize_transactions


class TestCategorizer(unittest.TestCase):

    def test_grocery_transaction(self):
        transaction = {"description": "Grocery shopping"}

        result = categorize_transaction(transaction)

        self.assertEqual(result, "Food & Groceries")

    def test_case_insensitive_matching(self):
        transaction = {"description": "ELECTRICITY BILL"}

        result = categorize_transaction(transaction)

        self.assertEqual(result, "Utilities")

    def test_unknown_transaction(self):
        transaction = {"description": "Random payment"}

        result = categorize_transaction(transaction)

        self.assertEqual(result, "Uncategorized")

    def test_existing_category_is_preserved(self):
        transaction = {"description": "Grocery shopping", "category": "Personal"}

        result = categorize_transaction(transaction)

        self.assertEqual(result, "Personal")

    def test_categorize_multiple_transactions(self):
        transactions = [
            {"description": "Grocery shopping"},
            {"description": "Electricity bill"},
        ]

        result = categorize_transactions(transactions)

        self.assertEqual(result[0]["category"], "Food & Groceries")
        self.assertEqual(result[1]["category"], "Utilities")


if __name__ == "__main__":
    unittest.main()
