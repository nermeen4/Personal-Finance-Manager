# ...existing code...
"""
ascii_viz.py - ASCII-based data visualization.

Creates simple text-based charts for:
- Spending trends
- Category summaries
- Progress tracking (e.g. goals vs actual)

Designed to integrate with the project's transactions and auth modules:
- Uses transactions.TRANSACTIONS and transactions._current_user_id (if present)
- Uses auth.current_user to determine the active user (fallback)
"""
from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any, Optional
import transactions
import auth


def _parse_date(d: Optional[str]):
    if not d:
        return None
    try:
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
    """Return transactions for the current user (safe if helpers missing)."""
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


def monthly_bar_chart(txns: Optional[List[Dict[str, Any]]] = None, months: int = 6, width: int = 40) -> str:
    """
    Build an ASCII bar chart of monthly totals (last `months` months).
    Returns the chart as a string (useful for tests); printing is handled by helper below.
    """
    if txns is None:
        txns = _get_user_txns()
    monthly = defaultdict(float)
    for t in txns:
        d = _parse_date(t.get("date"))
        if not d:
            continue
        key = d.strftime("%Y-%m")
        monthly[key] += _safe_float(t.get("amount", 0))

    if not monthly:
        return "No monthly data available."

    keys = sorted(monthly.keys())[-months:]
    values = [monthly[k] for k in keys]
    maxv = max(values) if values else 1.0
    lines = ["Monthly totals (most recent last):", "-" * (width + 30)]
    for k in keys:
        v = monthly[k]
        filled = 0 if maxv == 0 else int((abs(v) / maxv) * width)
        bar = "█" * filled
        lines.append(f"{k} {v:12.2f} | {bar}")
    return "\n".join(lines)


def category_bar_chart(txns: Optional[List[Dict[str, Any]]] = None, top_n: int = 10, width: int = 40) -> str:
    """
    Build an ASCII bar chart summarizing totals per category.
    Returns chart as string.
    """
    if txns is None:
        txns = _get_user_txns()
    totals = defaultdict(float)
    overall = 0.0
    for t in txns:
        cat = t.get("category") or "Uncategorized"
        amt = _safe_float(t.get("amount", 0))
        totals[cat] += amt
        overall += amt

    if not totals:
        return "No category data available."

    items = sorted(totals.items(), key=lambda x: x[1], reverse=True)[:top_n]
    maxv = max(val for _, val in items) if items else 1.0
    lines = ["Category breakdown:", "-" * (width + 30)]
    for cat, val in items:
        filled = 0 if maxv == 0 else int((abs(val) / maxv) * width)
        bar = "█" * filled
        pct = (val / overall * 100) if overall else 0.0
        lines.append(f"{cat:20.20} {val:12.2f} {pct:6.2f}% | {bar}")
    return "\n".join(lines)


def progress_bar(current: float, goal: float, width: int = 40) -> str:
    """
    Return an ASCII progress bar showing current vs goal.
    If goal is zero or negative, shows a simple numeric summary.
    """
    current = _safe_float(current)
    goal = _safe_float(goal)
    if goal <= 0:
        return f"Goal must be > 0. Current: {current:.2f}, Goal: {goal:.2f}"
    pct = min(max(current / goal, 0.0), 1.0)
    filled = int(pct * width)
    bar = "█" * filled + "-" * (width - filled)
    return f"[{bar}] {pct*100:6.2f}% ({current:.2f} / {goal:.2f})"


# -- Interactive helpers for use from menus (print + wait) -------------------
def print_monthly_chart(months: int = 6, width: int = 40):
    print(monthly_bar_chart(months=months, width=width))
    input("\nPress Enter to return...")


def print_category_chart(top_n: int = 10, width: int = 40):
    print(category_bar_chart(top_n=top_n, width=width))
    input("\nPress Enter to return...")


def print_progress_demo():
    """
    Small interactive helper: ask user for a goal amount and compute progress from recent transactions.
    This is useful when integrating into the app's menus.
    """
    txns = _get_user_txns()
    if not txns:
        print("No transactions available to compute progress.")
        input("\nPress Enter to return...")
        return

    try:
        goal_s = input("Enter goal amount: ").strip()
        goal = float(goal_s)
    except Exception:
        print("Invalid goal amount.")
        input("\nPress Enter to return...")
        return

    # Use sum of recent month as 'current' progress example
    recent_month = sorted([_parse_date(t.get("date")) for t in txns if _parse_date(t.get("date"))])[-1]
    month_key = recent_month.strftime("%Y-%m")
    current = sum(_safe_float(t.get("amount", 0)) for t in txns if _parse_date(t.get("date")).strftime("%Y-%m") == month_key)

    print("Progress for month:", month_key)
    print(progress_bar(current, goal))
    input("\nPress Enter to return...")


def ascii_viz_menu():
    """Simple interactive menu to expose the ASCII visualizations."""
    while True:
        print("🖼️  ASCII VISUALS")
        print("-" * 30)
        print("1) Monthly bar chart")
        print("2) Category breakdown chart")
        print("3) Progress (demo)")
        print("0) Back")
        choice = input("\nSelect an option: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            months_s = input("Months to show [6]: ").strip()
            try:
                months = int(months_s) if months_s else 6
            except Exception:
                months = 6
            print_monthly_chart(months=months)
        elif choice == "2":
            top_s = input("Top categories to show [10]: ").strip()
            try:
                top_n = int(top_s) if top_s else 10
            except Exception:
                top_n = 10
            print_category_chart(top_n=top_n)
        elif choice == "3":
            print_progress_demo()
        else:
            print("❌ Invalid option.")
            input("Press Enter to continue...")
# ...existing code...