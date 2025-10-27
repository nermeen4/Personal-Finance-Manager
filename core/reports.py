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
from core import auth, data_manager  # Load transaction data
from core.search_filter import round_money # For rounding monetary values
#from core.auth import current_user_id # Current user context
from core.ascii_viz import category_barchart, monthly_barchart, trend_chart


#####DASHBOARD SUMMARY#####
def dashboard_summary(transactions: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    """Return a simple summary: total income, total expenses, and balance."""
    total_income = Decimal('0.00')
    total_expenses = Decimal('0.00')

    for txn in transactions:
        amount = Decimal(str(txn.get("amount", "0")))
        if txn.get("type") == "income" and txn.get("user_id") == auth.current_user.get("user_id"):
            total_income += amount
        elif txn.get("type") == "expense" and txn.get("user_id") == auth.current_user.get("user_id"):
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
            if txn.get("type") == "income" and txn.get("user_id") == auth.current_user.get("user_id"):
                monthly_data[month_key]["income"] += amount
            elif txn.get("type") == "expense" and txn.get("user_id") == auth.current_user.get("user_id"):
                monthly_data[month_key]["expense"] += amount

        except Exception:
            continue  # Skip malformed dates or amounts
   
    # Round amounts + calculate net
    for month in monthly_data:
        income = monthly_data[month]["income"]
        expense = monthly_data[month]["expense"]
        monthly_data[month]["net"] = round_money(income - expense)

    return dict(monthly_data)


########### category breakdown ###########
def category_breakdown(transactions: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    """Return total expenses grouped by category."""
    category_data = defaultdict(Decimal)

    for txn in transactions:
        if txn.get("type") == "expense" and txn.get("user_id") == auth.current_user.get("user_id"):
            category = txn.get("category", "Uncategorized")
            amount = Decimal(str(txn.get("amount", "0")))
            category_data[category] += amount

    # Round amounts
    for category in category_data:
        category_data[category] = round_money(category_data[category])


    return dict(category_data)


########### spending trends ###########
def spending_trends(transactions: List[Dict[str, Any]]) -> Dict[str, Decimal]:
    """Return monthly expense trend (for visualization or analysis)."""
    trends = defaultdict(Decimal)

    for txn in transactions:
        if txn.get("type") == "expense" and txn.get("user_id") == auth.current_user.get("user_id"):
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


    return dict(trends)

