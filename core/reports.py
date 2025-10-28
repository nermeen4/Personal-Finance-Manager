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

from core import auth # Load transaction data
from core.search_filter import round_money # For rounding monetary values
from core.ascii_viz import category_barchart, monthly_barchart, trend_chart

#####DASHBOARD SUMMARY#####
def dashboard_summary(transactions: List[Dict[str, Any]], user_id: Optional[str]) -> Dict[str, Decimal]:
    """Return totals for the specified user_id. caller should pass filtered transactions OR supply user_id."""
    user_txns = [tx for tx in transactions if tx.get("user_id") == user_id]

    total_income = Decimal('0.00')
    total_expenses = Decimal('0.00')

    for tx in user_txns:
        amt = Decimal(str(tx.get("amount", "0")))
        if tx.get("type") == "income":
            total_income += amt
        elif tx.get("type") == "expense":
            total_expenses += amt

    balance = total_income - total_expenses

    return {
        "total_income": round_money(total_income),
        "total_expense": round_money(total_expenses),
        "balance": round_money(balance)
    }

########### monthly reports ###########
def monthly_reports(transactions: List[Dict[str, Any]], user_id: Optional[str]) -> Dict[str, Dict[str, Decimal]]:
    """Summarize transactions by month."""
    user_txns = [tx for tx in transactions if tx.get("user_id") == user_id]
    monthly_data = defaultdict(lambda: {"income": Decimal('0.00'), "expense": Decimal('0.00')})

    for tx in user_txns:
        try:
            date_obj = datetime.strptime(tx.get("date"), "%Y-%m-%d")
            month_key = date_obj.strftime("%Y-%m")
            amt = Decimal(str(tx.get("amount", "0")))
            if tx.get("type") == "income":
                monthly_data[month_key]["income"] += amt
            elif tx.get("type") == "expense":
                monthly_data[month_key]["expense"] += amt
        except Exception:
            continue

    # Round all values + compute net
    result = {}
    for month, values in sorted(monthly_data.items()):
        income = round_money(values["income"])
        expense = round_money(values["expense"])
        result[month] = {
            "income": income,
            "expense": expense,
            "net": round_money(income - expense)
        }

    return result


########### category breakdown ###########
def category_breakdown(transactions: List[Dict[str, Any]], user_id: Optional[str]) -> Dict[str, Decimal]:
 
    """Return total expenses grouped by category."""
    user_txns = [tx for tx in transactions if tx.get("user_id") == user_id]
    category_data = defaultdict(Decimal)

    for tx in user_txns:
        if tx.get("type") != "expense":
            continue
        category = tx.get("category", "Uncategorized")
        amt = Decimal(str(tx.get("amount", "0")))
        category_data[category] += amt


    return {cat: round_money(total) for cat, total in category_data.items()}


########### spending trends ###########
def spending_trends(transactions: List[Dict[str, Any]], user_id: Optional[str]) -> Dict[str, Decimal]:
    """Return monthly expense trend (for visualization or analysis)."""
    user_txns = [tx for tx in transactions if tx.get("user_id") == user_id]

    trends = defaultdict(Decimal)

    for tx in user_txns:
        if tx.get("type") != "expense":
            continue
        try:
            date_obj = datetime.strptime(tx.get("date"), "%Y-%m-%d")
            month_key = date_obj.strftime("%Y-%m")
            trends[month_key] += Decimal(str(tx.get("amount")))
        except Exception:
            continue

    return {m: round_money(v) for m, v in sorted(trends.items())}