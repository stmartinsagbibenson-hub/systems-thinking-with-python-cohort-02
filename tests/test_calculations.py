import unittest
from decimal import Decimal

from finance_tool.calculations import (
    calculate_budget_status,
    calculate_savings_forecast,
    calculate_summary,
)


class TestFinancialSummary(unittest.TestCase):

    def setUp(self):
        self.transactions = [
            {
                "date": "2026-01-05",
                "description": "Salary",
                "amount": Decimal(200000),
                "type": "income",
                "category": "Income",
                "currency": "NGN",
            },
            {
                "date": "2026-01-10",
                "description": "Groceries",
                "amount": Decimal(30000),
                "type": "expense",
                "category": "Food & Groceries",
                "currency": "NGN",
            },
            {
                "date": "2026-01-15",
                "description": "Electricity",
                "amount": Decimal(15000),
                "type": "expense",
                "category": "Utilities",
                "currency": "NGN",
            },
        ]


def test_refund_reduces_expenses(self):
    transactions = [
        {
            "date": "2026-01-05",
            "amount": Decimal(30000),
            "type": "expense",
            "category": "Food & Groceries",
        },
        {
            "date": "2026-01-06",
            "amount": Decimal(5000),
            "type": "refund",
            "category": "Food & Groceries",
        },
    ]

    result = calculate_summary(transactions)

    self.assertEqual(result["expenses"], Decimal(25000))
    self.assertEqual(
        result["spending_by_category"]["Food & Groceries"],
        Decimal(25000),
    )


def test_transfers_are_excluded_from_summary(self):
    transactions = [
        {
            "date": "2026-01-05",
            "amount": Decimal(20000),
            "type": "transfer",
            "category": "Savings",
        },
    ]

    result = calculate_summary(transactions)

    self.assertEqual(result["income"], Decimal(0))
    self.assertEqual(result["expenses"], Decimal(0))
    self.assertEqual(result["net_cash_flow"], Decimal(0))

    def test_calculates_income(self):
        result = calculate_summary(self.transactions)
        self.assertEqual(result["income"], Decimal(200000))

    def test_calculates_expenses(self):
        result = calculate_summary(self.transactions)
        self.assertEqual(result["expenses"], Decimal(45000))

    def test_calculates_net_cash_flow(self):
        result = calculate_summary(self.transactions)
        self.assertEqual(result["net_cash_flow"], Decimal(155000))

    def test_transaction_count(self):
        result = calculate_summary(self.transactions)
        self.assertEqual(result["transaction_count"], 3)

    def test_spending_by_category(self):
        result = calculate_summary(self.transactions)

        self.assertEqual(
            result["spending_by_category"]["Food & Groceries"],
            Decimal(30000),
        )

    def test_date_filter(self):
        result = calculate_summary(
            self.transactions,
            start_date="2026-01-10",
            end_date="2026-01-15",
        )

        self.assertEqual(result["transaction_count"], 2)
        self.assertEqual(result["expenses"], Decimal(45000))

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            calculate_summary(self.transactions, start_date="invalid-date")

    def test_start_date_after_end_date(self):
        with self.assertRaises(ValueError):
            calculate_summary(
                self.transactions,
                start_date="2026-01-20",
                end_date="2026-01-10",
            )

    def test_empty_transactions(self):
        result = calculate_summary([])

        self.assertEqual(result["income"], Decimal(0))
        self.assertEqual(result["expenses"], Decimal(0))
        self.assertEqual(result["transaction_count"], 0)
        self.assertEqual(result["reporting_period"], "No transactions")

    def test_multiple_currencies_are_rejected(self):
        transactions = self.transactions + [
            {
                "date": "2026-01-20",
                "description": "Foreign payment",
                "amount": Decimal(100),
                "type": "income",
                "category": "Income",
                "currency": "USD",
            }
        ]

        with self.assertRaises(ValueError):
            calculate_summary(transactions)

    def test_largest_expenses(self):
        result = calculate_summary(self.transactions)

        self.assertEqual(
            result["largest_expenses"][0]["amount"],
            Decimal(30000),
        )


class TestBudgetCalculations(unittest.TestCase):

    def test_within_budget(self):
        transactions = [
            {
                "date": "2026-01-10",
                "type": "expense",
                "category": "Food & Groceries",
                "amount": Decimal(30000),
            }
        ]

        budgets = {"Food & Groceries": Decimal(50000)}

        result = calculate_budget_status(transactions, budgets, "2026-01")

        self.assertEqual(result[0]["remaining"], Decimal(20000))
        self.assertEqual(result[0]["status"], "Within budget")

    def test_over_budget(self):
        transactions = [
            {
                "date": "2026-01-10",
                "type": "expense",
                "category": "Food & Groceries",
                "amount": Decimal(60000),
            }
        ]

        budgets = {"Food & Groceries": Decimal(50000)}

        result = calculate_budget_status(transactions, budgets, "2026-01")

        self.assertEqual(result[0]["remaining"], Decimal(-10000))
        self.assertEqual(result[0]["status"], "Over budget")

    def test_budget_ignores_other_months(self):
        transactions = [
            {
                "date": "2026-02-10",
                "type": "expense",
                "category": "Food & Groceries",
                "amount": Decimal(30000),
            }
        ]

        budgets = {"Food & Groceries": Decimal(50000)}

        result = calculate_budget_status(transactions, budgets, "2026-01")

        self.assertEqual(result[0]["spent"], Decimal(0))


class TestSavingsForecast(unittest.TestCase):

    def test_forecast_without_interest(self):
        result = calculate_savings_forecast(50000, 10000, 6)

        self.assertEqual(result, Decimal("110000.00"))

    def test_forecast_with_interest(self):
        result = calculate_savings_forecast(50000, 10000, 6, 12)

        self.assertEqual(result, Decimal("115211.36"))

    def test_zero_months(self):
        result = calculate_savings_forecast(50000, 10000, 0)

        self.assertEqual(result, Decimal("50000.00"))

    def test_negative_months(self):
        with self.assertRaises(ValueError):
            calculate_savings_forecast(50000, 10000, -1)

    def test_negative_starting_balance(self):
        with self.assertRaises(ValueError):
            calculate_savings_forecast(-5000, 10000, 6)

    def test_negative_monthly_contribution(self):
        with self.assertRaises(ValueError):
            calculate_savings_forecast(50000, -1000, 6)

    def test_negative_interest(self):
        with self.assertRaises(ValueError):
            calculate_savings_forecast(50000, 10000, 6, -5)


if __name__ == "__main__":
    unittest.main()
