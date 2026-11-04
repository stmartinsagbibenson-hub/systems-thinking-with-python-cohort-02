import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation

from finance_tool.categorizer import categorize_transactions


def load_transactions(file_path):
    transactions = []
    errors = []
    skipped = []

    seen_ids = set()
    seen_rows = set()

    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file has no headers.")

        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]

        bank_format = "transaction_id" in reader.fieldnames

        if bank_format:
            required = [
                "transaction_id",
                "transaction_date",
                "transaction_type",
                "description",
                "amount",
                "currency",
                "status",
            ]
        else:
            required = ["date", "description", "amount", "type"]

        for column in required:
            if column not in reader.fieldnames:
                raise ValueError(f"Missing column: {column}")

        for row_number, row in enumerate(reader, start=2):
            try:
                if bank_format:
                    transaction_id = row["transaction_id"].strip()
                    status = row["status"].strip().lower()

                    if status != "completed":
                        skipped.append(f"Row {row_number}: {status} transaction")
                        continue

                    if not transaction_id:
                        raise ValueError("Missing transaction ID")

                    if transaction_id in seen_ids:
                        raise ValueError("Duplicate transaction ID")

                    raw_type = row["transaction_type"].strip().lower()
                    description = row["description"].strip().lower()

                    if "refund" in description:
                        transaction_type = "refund"
                    elif "transfer" in description:
                        transaction_type = "transfer"
                    elif raw_type == "credit":
                        transaction_type = "income"
                    elif raw_type == "debit":
                        transaction_type = "expense"
                    else:
                        raise ValueError("Invalid transaction type")

                    transaction_date = row["transaction_date"]
                    currency = row["currency"].strip().upper()

                else:
                    transaction_id = None
                    transaction_type = row["type"].strip().lower()
                    transaction_date = row["date"]
                    currency = row.get("currency") or "NGN"

                    if transaction_type not in [
                        "income",
                        "expense",
                        "refund",
                        "transfer",
                    ]:
                        raise ValueError("Invalid transaction type")

                transaction_date = (
                    datetime.fromisoformat(transaction_date.strip()).date().isoformat()
                )

                description = row["description"].strip()

                if not description:
                    raise ValueError("Missing description")

                amount = Decimal(row["amount"].strip())

                if not amount.is_finite() or amount <= 0:
                    raise ValueError("Amount must be positive")

                category = row.get("category") or None

                duplicate_key = (
                    transaction_date,
                    description.lower(),
                    str(amount),
                    transaction_type,
                )

                if not bank_format and duplicate_key in seen_rows:
                    errors.append(f"Row {row_number}: Duplicate transaction")
                    continue

                seen_rows.add(duplicate_key)

                if transaction_id:
                    seen_ids.add(transaction_id)

                transactions.append(
                    {
                        "transaction_id": transaction_id,
                        "date": transaction_date,
                        "description": description,
                        "amount": amount,
                        "type": transaction_type,
                        "category": category,
                        "currency": currency,
                    }
                )

            except (ValueError, InvalidOperation, AttributeError) as error:
                errors.append(f"Row {row_number}: {error}")

    categorize_transactions(transactions)
    return transactions, errors, skipped
