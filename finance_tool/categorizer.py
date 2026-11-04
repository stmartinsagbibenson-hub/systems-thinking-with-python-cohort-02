# Keywords and their categories.

CATEGORY_RULES = {
    "grocery": "Food & Groceries",
    "restaurant": "Dining",
    "electricity": "Utilities",
    "water bill": "Utilities",
    "internet": "Utilities",
    "fuel": "Transport",
    "transport": "Transport",
    "airtime": "Communication",
    "pharmacy": "Healthcare",
    "online purchase": "Shopping",
    "transfer to savings": "Savings",
    "funds received": "Income",
    "cash deposit": "Income",
    "salary": "Income",
    "freelance": "Income",
    "interest": "Income",
    "refund": "Refunds",
}


def categorize_transaction(transaction):
    # Keep a category already supplied in the CSV.
    if transaction.get("category"):
        return transaction["category"]

    description = transaction["description"].lower()

    # Find a matching keyword.
    for keyword, category in CATEGORY_RULES.items():
        if keyword in description:
            return category

    return "Uncategorized"


def categorize_transactions(transactions):
    for transaction in transactions:
        transaction["category"] = categorize_transaction(transaction)

    return transactions
