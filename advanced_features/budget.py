"""
budgets.py - Monthly Budget Management System (per-user)

Features:
- Set monthly budget
- View usage and remaining balance for current month
- Data stored per user + month
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from core import data_manager, auth
from core.search_filter import round_money, safe_amount


BUDGET_FILE = "data/budgets.json"

# Load + decode into Decimal
raw_budgets = data_manager.load_json(BUDGET_FILE) or []
budgets: List[Dict[str, Any]] = [
    {
        "user_id": b.get("user_id"),
        "month": b.get("month"),
        "budget": Decimal(str(b.get("budget", "0")))
    }
    for b in raw_budgets
]


def _save_budgets():
    """Save budgets back to JSON with Decimal → string serialization."""
    serializable = [
        {
            "user_id": b["user_id"],
            "month": b["month"],
            "budget": str(b["budget"])
        }
        for b in budgets
    ]
    data_manager.save_json(BUDGET_FILE, serializable)


def clear_screen():
    print("\033c", end="")


def _current_month() -> str:
    """Return YYYY-MM for this month"""
    return datetime.now().strftime("%Y-%m")


def _get_user_id() -> str:
    """Return logged-in user's ID or None if not logged in."""
    return auth.current_user.get("user_id") if auth.current_user else None


def set_monthly_budget():
    clear_screen()
    if not auth.current_user:
        print("⚠️ Please login first.")
        input("Press Enter...")
        return

    month = _current_month()
    uid = _get_user_id()

    print(f"🎯 Set Budget for {month}")
    try:
        amount = Decimal(input("Enter monthly budget: ").strip())
        if amount <= 0:
            raise ValueError
    except Exception:
        print("❌ Invalid budget amount.")
        input("Press Enter...")
        return

    # Update if exists, else append
    found = False
    for b in budgets:
        if b["user_id"] == uid and b["month"] == month:
            b["budget"] = amount
            found = True
            break

    if not found:
        budgets.append({
            "user_id": uid,
            "month": month,
            "budget": amount
        })

    _save_budgets()
    print(f"✅ Budget set to {round_money(amount)}")
    input("Press Enter...")


def view_budget_status():
    clear_screen()
    if not auth.current_user:
        print("⚠️ Please login first.")
        input("Press Enter...")
        return

    month = _current_month()
    uid = _get_user_id()
    selected_budget = None

    # Find user’s budget record
    for b in budgets:
        if b["user_id"] == uid and b["month"] == month:
            selected_budget = b["budget"]
            break

    if selected_budget is None:
        print(f"⚠️ No budget set for {month}.")
        input("Press Enter...")
        return

    # Load expenses for this month
    all_txns = data_manager.load_transactions()
    total_spent = Decimal("0.00")

    for tx in all_txns:
        if tx.get("user_id") != uid:
            continue
        if tx.get("type") != "expense":
            continue

        try:
            date = datetime.strptime(tx["date"], "%Y-%m-%d")
            if date.strftime("%Y-%m") == month:
                total_spent += safe_amount(tx.get("amount"))
        except:
            continue

    remaining = round_money(selected_budget - total_spent)

    print("\n📊 MONTHLY BUDGET STATUS")
    print("-" * 35)
    print(f"Month: {month}")
    print(f"Budget: {round_money(selected_budget)}")
    print(f"Spent: {round_money(total_spent)}")

    if remaining >= 0:
        print(f"Remaining: ✅ {remaining}")
    else:
        print(f"Remaining: ❌ OVERSPENT by {abs(remaining)}")

    input("Press Enter...")


def budgets_menu():
    while True:
        clear_screen()
        print("💸 Monthly Budget Manager")
        print("-" * 35)
        print("1) Set Monthly Budget")
        print("2) View Budget Status")
        print("0) Back")
        choice = input("Select: ").strip()

        if choice == "1":
            set_monthly_budget()
        elif choice == "2":
            view_budget_status()
        elif choice == "0":
            return
        else:
            print("❌ Invalid option.")
            input("Press Enter...")
