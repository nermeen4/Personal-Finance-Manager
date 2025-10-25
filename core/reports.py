"""
reports.py - Generates financial reports from transaction data.

Includes:
- Dashboard summary
- Monthly report
- Category breakdown
- Spending trends
"""

from collections import defaultdict # For category breakdown
from datetime import datetime # For date handling
from decimal import Decimal, ROUND_HALF_UP  # For monetary calculations
from typing import List, Dict, Any, Optional # Type hints
from data_manager import load_transactions  # Load transaction data
from search_filter import round_money # For rounding monetary values
#from core.auth import current_user_id # Current user context
from ascii_viz import category_barchart, monthly_barchart, trend_chart


#####DASHBOARD SUMMARY#####
def dashboard_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    """Return a simple summary: total income, total expenses, and balance."""
    total_income = Decimal('0.00')
    total_expenses = Decimal('0.00')

    for txn in transactions:
        amount = Decimal(str(txn.get("amount", "0")))
        if txn.get("type") == "income":
            total_income += amount
        elif txn.get("type") == "expense":
            total_expenses += amount

    balance = total_income - total_expenses

    print("📊 DASHBOARD SUMMARY")
    print("-" * 30)
    return {
        "total_income": round_money(total_income),
        "total_expense": round_money(total_expenses),
        "balance": round_money(balance)
    }


########### monthly reports ###########
def monthly_reports(transactions: List[Dict[str, Any]]) -> Dict[str, Dict[str, Decimal]]:
    """Summarize transactions by month."""
    monthly_data = defaultdict(lambda: {"income": Decimal('0.00'), "expense": Decimal('0.00')})

    for txn in transactions:
        try:
            date_obj = datetime.strptime(txn.get("date"), "%Y-%m-%d")
            month_key = date_obj.strftime("%Y-%m")
            amount = Decimal(str(txn.get("amount", "0")))
            if txn.get("type") == "income":
                monthly_data[month_key]["income"] += amount
            elif txn.get("type") == "expense":
                monthly_data[month_key]["expense"] += amount

        except Exception:
            continue  # Skip malformed dates or amounts
   
    # Round amounts
    for month in monthly_data:
        monthly_data[month]["income"] = round_money(monthly_data[month]["income"])
        monthly_data[month]["expense"] = round_money(monthly_data[month]["expense"])

    print("📅 MONTHLY REPORTS")
    print("-" * 30)
    return dict(monthly_data)


########### category breakdown ###########
def category_breakdown(transactions: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    """Return total expenses grouped by category."""
    category_data = defaultdict(Decimal)

    for txn in transactions:
        if txn.get("type") == "expense":
            category = txn.get("category", "Uncategorized")
            amount = Decimal(str(txn.get("amount", "0")))
            category_data[category] += amount

    # Round amounts
    for category in category_data:
        category_data[category] = round_money(category_data[category])

    print("📂 CATEGORY BREAKDOWN")
    print("-" * 30)
    return dict(category_data)


########### spending trends ###########
def spending_trends(transactions: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    """Return monthly expense trend (for visualization or analysis)."""
    trends = defaultdict(Decimal)

    for txn in transactions:
        if txn.get("type") == "expense":
            try:
                date_obj = datetime.strptime(txn.get("date"), "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                #amount = Decimal(str(txn.get("amount", "0")))
                trends[month_key] += Decimal(str(txn.get("amount")))
            except Exception:
                continue  # Skip malformed dates or amounts

    # Round amounts
    for month in trends:
        trends[month] = round_money(trends[month])

    print("📈 SPENDING TRENDS")
    print("-" * 30)
    return dict(trends)


######## testing the reports output ########
if __name__ == "__main__":
    from decimal import Decimal

    # 🧪 Example transaction data to test all reports
    sample_transactions = [
        {"date": "2025-01-15", "type": "income", "amount": "5000.00", "category": "Salary"},
        {"date": "2025-01-18", "type": "expense", "amount": "1200.00", "category": "Rent"},
        {"date": "2025-01-20", "type": "expense", "amount": "400.00", "category": "Food"},
        {"date": "2025-02-10", "type": "income", "amount": "4800.00", "category": "Salary"},
        {"date": "2025-02-15", "type": "expense", "amount": "300.00", "category": "Transport"},
        {"date": "2025-02-18", "type": "expense", "amount": "700.00", "category": "Shopping"},
        {"date": "2025-03-05", "type": "expense", "amount": "350.00", "category": "Food"},
    ]

    # === Test 1: Dashboard summary ===
    print("\n=== Dashboard Summary ===")
    from reports import dashboard_summary
    summary = dashboard_summary(sample_transactions)
    for key, val in summary.items():
        print(f"{key}: {val}")

    # === Test 2: Monthly Report ===
    print("\n=== Monthly Report ===")
    from reports import monthly_reports
    monthly = monthly_reports(sample_transactions)
    for month, data in monthly.items():
        print(f"{month}: {data}")

    # === Test 3: Category Breakdown ===
    print("\n=== Category Breakdown ===")
    from reports import category_breakdown
    cats = category_breakdown(sample_transactions)
    for cat, amt in cats.items():
        print(f"{cat}: {amt}")

    # === Test 4: Spending Trends ===
    print("\n=== Spending Trends ===")
    from reports import spending_trends
    trends = spending_trends(sample_transactions)
    for month, total in trends.items():
        print(f"{month}: {total}")


##############ASCII VISUALIZATION UTILITIES##############
    print("\n=== ASCII Charts ===")

    category_barchart(category_breakdown(sample_transactions))
    monthly_barchart(monthly_reports(sample_transactions))
    trend_chart(spending_trends(sample_transactions))