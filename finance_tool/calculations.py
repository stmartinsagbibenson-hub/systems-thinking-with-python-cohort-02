from datetime import date
from decimal import Decimal


def calculate_summary(transactions, start_date=None, end_date=None):
    if start_date:
        start_date = date.fromisoformat(start_date).isoformat()

    if end_date:
        end_date = date.fromisoformat(end_date).isoformat()

    if start_date and end_date and start_date > end_date:
        raise ValueError("Start date cannot be after end date.")

    filtered = []

    for transaction in transactions:
        transaction_date = transaction["date"]

        if start_date and transaction_date < start_date:
            continue

        if end_date and transaction_date > end_date:
            continue

        filtered.append(transaction)

    currencies = {transaction.get("currency", "NGN") for transaction in filtered}

    if len(currencies) > 1:
        raise ValueError(
            "Transactions contain multiple currencies. "
            "Calculate each currency separately."
        )

    currency = next(iter(currencies), "NGN")
    transaction_dates = [transaction["date"] for transaction in filtered]

    if transaction_dates:
        first_date = min(transaction_dates)
        last_date = max(transaction_dates)

        reporting_period = (
            first_date if first_date == last_date else f"{first_date} to {last_date}"
        )
    else:
        reporting_period = "No transactions"

    income = Decimal(0)
    expenses = Decimal(0)
    spending_by_category = {}
    expense_transactions = []

    for transaction in filtered:
        amount = Decimal(str(transaction["amount"]))
        transaction_type = transaction["type"]

        category = transaction.get("category") or "Uncategorized"

        if transaction_type == "income":
            income += amount

        elif transaction_type == "expense":
            expenses += amount
            spending_by_category[category] = (
                spending_by_category.get(category, Decimal(0)) + amount
            )
            expense_transactions.append(transaction)

        elif transaction_type == "refund":
            expenses -= amount
            spending_by_category[category] = (
                spending_by_category.get(category, Decimal(0)) - amount
            )

    net_cash_flow = income - expenses

    largest_expenses = sorted(
        expense_transactions,
        key=lambda transaction: Decimal(str(transaction["amount"])),
        reverse=True,
    )[:5]

    return {
        "currency": currency,
        "reporting_period": reporting_period,
        "transaction_count": len(filtered),
        "income": income,
        "expenses": expenses,
        "net_cash_flow": net_cash_flow,
        "spending_by_category": spending_by_category,
        "largest_expenses": largest_expenses,
    }


def calculate_budget_status(transactions, budgets, month):
    results = []

    for category, budget in budgets.items():
        spent = Decimal(0)

        for transaction in transactions:
            if (
                transaction["date"].startswith(month)
                and transaction.get("category", "").strip().lower()
                == category.strip().lower()
            ):
                amount = Decimal(str(transaction["amount"]))

                if transaction["type"] == "expense":
                    spent += amount

                elif transaction["type"] == "refund":
                    spent -= amount

        remaining = budget - spent

        status = "Over budget" if remaining < 0 else "Within budget"

        results.append(
            {
                "category": category,
                "budget": budget,
                "spent": spent,
                "remaining": remaining,
                "status": status,
            }
        )

    return results


def calculate_savings_forecast(
    starting_balance, monthly_contribution, months, annual_interest=0
):
    starting_balance = Decimal(str(starting_balance))
    monthly_contribution = Decimal(str(monthly_contribution))
    annual_interest = Decimal(str(annual_interest))

    if months < 0:
        raise ValueError("Months cannot be negative.")

    if not starting_balance.is_finite() or starting_balance < 0:
        raise ValueError("Starting balance must be non-negative.")

    if not monthly_contribution.is_finite() or monthly_contribution < 0:
        raise ValueError("Monthly contribution must be non-negative.")

    if not annual_interest.is_finite() or annual_interest < 0:
        raise ValueError("Annual interest must be non-negative.")

    balance = starting_balance
    monthly_interest = annual_interest / Decimal(100) / Decimal(12)

    for month in range(months):
        balance += monthly_contribution
        balance += balance * monthly_interest

    return balance.quantize(Decimal("0.01"))
