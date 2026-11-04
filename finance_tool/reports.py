import csv


def export_report(transactions, filename):
    if not transactions:
        print("No transactions available for the report.")
        return

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=transactions[0].keys())

        writer.writeheader()
        writer.writerows(transactions)

    print(f"Report exported successfully: {filename}")


def export_summary_report(summary, filename):
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow(["Financial Summary"])
        writer.writerow(["Currency", summary["currency"]])
        writer.writerow(["Reporting Period", summary["reporting_period"]])
        writer.writerow(["Transaction Count", summary["transaction_count"]])
        writer.writerow(["Total Income", summary["income"]])
        writer.writerow(["Total Expenses", summary["expenses"]])
        writer.writerow(["Net Cash Flow", summary["net_cash_flow"]])

        writer.writerow([])
        writer.writerow(["Category", "Amount"])

        for category, amount in summary["spending_by_category"].items():
            writer.writerow([category, amount])

        writer.writerow([])
        writer.writerow(["Five Largest Expenses"])
        writer.writerow(["Date", "Description", "Category", "Amount"])

        for transaction in summary["largest_expenses"]:
            writer.writerow(
                [
                    transaction["date"],
                    transaction["description"],
                    transaction["category"],
                    transaction["amount"],
                ]
            )

    print(f"Summary report exported: {filename}")
