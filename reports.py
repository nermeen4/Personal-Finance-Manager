# ...existing code...
"""
reports.py - Generate reports and summaries.

Handles:
- Monthly spending reports
- Category breakdowns
- Dashboard summaries
- Spending trends analysis
"""
from collections import defaultdict, Counter
from datetime import datetime
import transactions
import auth
from typing import List, Dict, Any, Optional


def _parse_date(d: Optional[str]):
    if not d:
        return None
    try:
        # Accept ISO-like strings or plain YYYY-MM-DD
        return datetime.fromisoformat(str(d)).date()
    except Exception:
        try:
            return datetime.strptime(str(d), "%Y-%m-%d").date()
        except Exception:
            return None


def _safe_float(v):
    try:
        return float(v)
    except Exception:
        return 0.0


def _get_user_txns() -> List[Dict[str, Any]]:
    """Return transactions for the current user (safe if auth/transactions helpers missing)."""
    uid = None
    try:
        uid = transactions._current_user_id()
    except Exception:
        pass
    if uid is None and getattr(auth, "current_user", None):
        uid = auth.current_user.get("user_id")
    if uid is None:
        return []
    return [tx for tx in transactions.TRANSACTIONS if tx.get("user_id") == uid]


def _format_amount(a: float) -> str:
    return f"{a:,.2f}"


def dashboard_summary():
    """Print a simple dashboard: totals, counts, top categories, last transactions."""
    txns = _get_user_txns()
    clear = lambda: None
    total_income = 0.0
    total_expense = 0.0
    for t in txns:
        amt = _safe_float(t.get("amount", 0))
        ttype = str(t.get("type", "")).lower()
        # treat "income" as positive, others as expense if type specified
        if ttype == "income":
            total_income += amt
        else:
            # if type is "expense" or unknown, consider negative flow towards expenses
            total_expense += amt

    net = total_income - total_expense
    count = len(txns)
    avg = (sum(_safe_float(t.get("amount", 0)) for t in txns) / count) if count else 0.0

    # top categories
    cat_sums = defaultdict(float)
    for t in txns:
        cat = t.get("category") or "Uncategorized"
        cat_sums[cat] += _safe_float(t.get("amount", 0))

    top_categories = sorted(cat_sums.items(), key=lambda x: x[1], reverse=True)[:5]

    print("📊 DASHBOARD SUMMARY")
    print("-" * 40)
    print(f"Transactions: {count}")
    print(f"Total income : { _format_amount(total_income)}")
    print(f"Total expense: { _format_amount(total_expense)}")
    print(f"Net          : { _format_amount(net)}")
    print(f"Average txn  : { _format_amount(avg)}")
    print()
    print("Top categories:")
    if top_categories:
        for cat, val in top_categories:
            print(f" - {cat:20} { _format_amount(val)}")
    else:
        print(" No categories to show.")
    print()
    print("Most recent transactions:")
    recent = sorted(txns, key=lambda x: _parse_date(x.get("date")) or datetime.min.date(), reverse=True)[:5]
    if recent:
        for t in recent:
            d = _parse_date(t.get("date"))
            print(f"[{t.get('transaction_id')}] {d or ''} {str(t.get('type','')).upper():7} "
                  f"{_format_amount(_safe_float(t.get('amount',0))):>12} {t.get('category','')}")
    else:
        print(" No transactions.")
    input("\nPress Enter to return...")


def monthly_reports(last_n: int = 12):
    """Show monthly totals for the last_n months (income, expense, net)."""
    txns = _get_user_txns()
    by_month = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for t in txns:
        d = _parse_date(t.get("date"))
        if not d:
            continue
        key = d.strftime("%Y-%m")
        amt = _safe_float(t.get("amount", 0))
        ttype = str(t.get("type", "")).lower()
        if ttype == "income":
            by_month[key]["income"] += amt
        else:
            by_month[key]["expense"] += amt

    months = sorted(by_month.keys(), reverse=True)[:last_n]
    if not months:
        print("No monthly data available.")
        input("Press Enter to return...")
        return

    print("📅 MONTHLY REPORTS")
    print("-" * 50)
    print(f"{'Month':10} {'Income':>12} {'Expense':>12} {'Net':>12}")
    for m in sorted(months):
        inc = by_month[m]["income"]
        exp = by_month[m]["expense"]
        net = inc - exp
        print(f"{m:10} { _format_amount(inc):>12} { _format_amount(exp):>12} { _format_amount(net):>12}")
    input("\nPress Enter to return...")


def category_breakdown():
    """Show spend/income breakdown by category (totals and percentage)."""
    txns = _get_user_txns()
    totals = defaultdict(float)
    overall = 0.0
    for t in txns:
        cat = t.get("category") or "Uncategorized"
        amt = _safe_float(t.get("amount", 0))
        totals[cat] += amt
        overall += amt

    if not totals:
        print("No category data available.")
        input("Press Enter to return...")
        return

    breakdown = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    print("📂 CATEGORY BREAKDOWN")
    print("-" * 50)
    print(f"{'Category':25} {'Amount':>12} {'% of total':>12}")
    for cat, val in breakdown:
        pct = (val / overall * 100) if overall else 0.0
        print(f"{cat:25} { _format_amount(val):>12} {pct:11.2f}%")
    input("\nPress Enter to return...")


def spending_trends(months: int = 6):
    """Show a simple trend (monthly totals) for the last `months` months."""
    txns = _get_user_txns()
    monthly = defaultdict(float)
    for t in txns:
        d = _parse_date(t.get("date"))
        if not d:
            continue
        key = d.strftime("%Y-%m")
        monthly[key] += _safe_float(t.get("amount", 0))

    if not monthly:
        print("No trend data available.")
        input("Press Enter to return...")
        return

    keys = sorted(monthly.keys())[-months:]
    values = [monthly[k] for k in keys]
    maxv = max(values) if values else 1.0

    def bar(v, width=40):
        if maxv == 0:
            return ""
        filled = int((v / maxv) * width)
        return "█" * filled

    print("📈 SPENDING TRENDS")
    print("-" * 60)
    for k in keys:
        v = monthly[k]
        print(f"{k} { _format_amount(v):>12} | {bar(v)}")
    input("\nPress Enter to return...")
# ...existing code...