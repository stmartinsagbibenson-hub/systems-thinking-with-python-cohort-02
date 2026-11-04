import csv
import sqlite3
from datetime import datetime

from finance_tool.calculations import (
    calculate_budget_status,
    calculate_savings_forecast,
    calculate_summary,
)
from finance_tool.database import (
    get_all_transactions,
    get_budgets,
    reset_database,
    save_transactions,
    set_budget,
    update_categories,
)
from finance_tool.importer import load_transactions
from finance_tool.reports import export_summary_report


def main():
    print("================================")
    print(" PERSONAL FINANCE AUTOMATION ")
    print("================================")

    while True:
        print("\nMAIN MENU")
        print("1. Import transactions")
        print("2. View financial summary")
        print("3. Manage monthly budgets")
        print("4. Savings forecast")
        print("5. Export financial report")
        print("6. View all transactions")
        print("7. Reset database")
        print("0. Exit")

        choice = input("\nChoose an option: ")
        if choice == "1":
            file_path = input("Enter CSV file path: ")

            try:
                transactions, errors, skipped = load_transactions(file_path)

                saved, already_imported = save_transactions(transactions, file_path)

                if already_imported:
                    print("This file has already been imported.")
                else:
                    update_categories(transactions)
                    print(f"Successfully imported: {saved}")

                    print(f"Invalid rows: {len(errors)}")
                    print(f"Skipped rows: {skipped}")

                    for error in errors:
                        print(error)

            except FileNotFoundError:
                print("File not found. Check the path and try again.")
            except (OSError, UnicodeError, csv.Error, sqlite3.Error) as error:
                print(f"Import failed: {error}")

        elif choice == "2":
            transactions = get_all_transactions()

            try:
                summary = calculate_summary(transactions)

                print("\nFINANCIAL SUMMARY")
                print("-------------------------")
                print(f"Currency: {summary['currency']}")
                print(f"Transactions: {summary['transaction_count']}")
                print(f"Total income: {summary['income']}")
                print(f"Total expenses: {summary['expenses']}")
                print(f"Net cash flow: {summary['net_cash_flow']}")

                print("\nSPENDING BY CATEGORY")

                for category, amount in summary["spending_by_category"].items():
                    print(f"{category}: {amount}")

                print("\nFIVE LARGEST EXPENSES")

                for transaction in summary["largest_expenses"]:
                    print(f"{transaction['description']}: " f"{transaction['amount']}")
            except ValueError as error:
                print(f"Could not calculate summary: {error}")

        elif choice == "3":
            month = input("Enter month (YYYY-MM): ")
            try:
                datetime.strptime(month, "%Y-%m")
            except ValueError:
                print("Invalid month. Please use YYYY-MM format.")
                continue
            try:
                budgets = get_budgets(month)
                if not budgets:
                    print("No budgets found for this month.")
                else:
                    transactions = get_all_transactions()
                    results = calculate_budget_status(transactions, budgets, month)
                    print(f"\nBUDGET STATUS — {month}")
                    for result in results:
                        print(f"\nCategory: {result['category']}")
                        print(f"Budget: {result['budget']}")
                        print(f"Spent: {result['spent']}")
                        print(f"Remaining: {result['remaining']}")
                        print(f"Status: {result['status']}")
                add_budget = input("\nAdd or update a budget? (yes/no): ")
                if add_budget.lower() == "yes":
                    category = input("Enter category: ")
                    amount = input("Enter budget amount: ")
                    set_budget(month, category, amount)
                    print("Budget saved successfully.")
            except ValueError as error:
                print(f"Error: {error}")

        elif choice == "4":
            try:
                starting_balance = input("Starting balance: ")
                monthly_contribution = input("Monthly contribution: ")
                months = int(input("Number of months: "))
                annual_interest = input("Annual interest rate (%): ")

                result = calculate_savings_forecast(
                    starting_balance, monthly_contribution, months, annual_interest
                )

                print("\nSAVINGS FORECAST")
                print(f"Projected savings: {result}")

            except ValueError as error:
                print(f"Invalid input: {error}")

        elif choice == "5":
            transactions = get_all_transactions()
            try:
                summary = calculate_summary(transactions)

                filename = "reports/financial_summary.csv"

                export_summary_report(summary, filename)
            except ValueError as error:
                print(f"Could not export report: {error}")

        elif choice == "6":
            transactions = get_all_transactions()
            if not transactions:
                print("No transactions found.")
            else:
                print("\nALL TRANSACTIONS")
                print("-------------------------")

                for transaction in transactions:
                    print(
                        f"{transaction['date']} | "
                        f"{transaction['description']} | "
                        f"{transaction['type']} | "
                        f"{transaction['amount']} | "
                        f"{transaction['category']}"
                    )
                print(f"\nTotal transactions: {len(transactions)}")

        elif choice == "7":
            print("\nWARNING: This will permanently delete:")
            print("- All saved transactions")
            print("- Import history")
            print("- All monthly budgets")

            confirmation = input("\nType YES to confirm: ")

            if confirmation.strip().upper() == "YES":
                try:
                    reset_database()
                    print("Database reset successfully.")
                except sqlite3.Error as error:
                    print(f"Database reset failed: {error}")
            else:
                print("Database reset cancelled.")

        elif choice == "0":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
