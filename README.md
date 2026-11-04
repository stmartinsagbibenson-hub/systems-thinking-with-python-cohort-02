# Personal & Small-Business Finance Automation CLI

A Python command-line application that helps individuals, freelancers, and small-business owners understand where their money comes from, where it goes, and how their saving habits may affect future balances.

## Features

- Import financial transactions from CSV files.
- Validate transaction data and detect duplicates.
- Automatically categorize transactions using keyword rules.
- Calculate income, expenses, and net cash flow.
- Generate financial summaries.
- Create and manage monthly budgets.
- Track spending against budgets.
- Calculate savings projections with optional interest.
- Export financial summaries and transaction reports to CSV.
- View saved transactions.
- Store financial data locally using SQLite.

## Requirements

- Python 3.10 or later.
- No external packages required to run the application.

## Setup

Clone the repository:

```bash
git clone https://github.com/stmartinsagbibenson-hub/systems-thinking-with-python-cohort-02

cd Finance-Automation-CLI
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it.

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source .venv/bin/activate
```

Run the application:

```bash
python -m finance_tool.main
```

## CSV Import Format

The standard CSV format uses the following columns:

| Column | Description |
|---|---|
| `date` | Transaction date (YYYY-MM-DD) |
| `description` | Transaction description |
| `amount` | Positive transaction amount |
| `type` | income, expense, refund, or transfer |
| `category` | Optional transaction category |
| `currency` | Optional currency; defaults to NGN |

Example:

```csv
date,description,amount,type,category,currency
2026-01-05,Monthly salary,250000,income,Income,NGN
2026-01-07,Grocery shopping,15000,expense,Food & Groceries,NGN
2026-01-10,Internet subscription,8000,expense,Utilities,NGN
```

A sample bank transaction file is available at:

`data/bank_transactions.csv`

The application also supports the bank-export format used by the sample file. Only completed transactions are imported.

Invalid rows are reported, while valid rows can still be imported.

### Special Transaction Handling

- Refunds reduce recorded expenses.
- Transfers are excluded from income and expense totals.
- Bank-format refund and transfer classification uses description keywords and may require review.

## Application Menu

The interactive menu provides these operations:

1. Import transactions.
2. View financial summaries.
3. Manage monthly budgets.
4. Calculate savings forecasts.
5. Export financial reports.
6. View saved transactions.
7. Reset the database.
0. Exit.

## Reports

Generated reports are saved in the `reports/` directory.

The financial summary report includes:

- Currency and reporting period.
- Transaction count.
- Total income and expenses.
- Net cash flow.
- Spending by category.
- Five largest expenses.

## Database and Privacy

The application uses SQLite for local storage.

Database location:

`data/finance.db`

Transaction records, import history, and budgets are stored locally. The application does not connect directly to bank accounts.

Keep your database private because it may contain sensitive financial information.

## Development and Testing

Install optional development tools:

```bash
python -m pip install ruff black
```

Run linting:

```bash
ruff check finance_tool tests
```

Check formatting:

```bash
black --check finance_tool tests
```

Run automated tests:

```bash
python -m unittest discover -s tests -v
```

Check Python compilation:

```bash
python -m compileall -q finance_tool tests
```

## Project Status

The core application features have been implemented.

The automated test suite contains 40 passing tests. Ruff, Black, and Python compilation checks have also passed.

## Limitations

- No direct bank account integration.
- Currency conversion is not supported.
- Automatic categorization depends on configured keywords.
- Savings projections are estimates and do not guarantee actual future returns.
