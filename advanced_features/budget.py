"""
budgets.py - Monthly Budget Management System

Features:
- Set monthly budget
- View current month's usage and remaining
- Save budgets by user and month
"""
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any
from core import data_manager, auth, transactions
from core.search_filter import round_money, safe_amount



# Load existing budget data or start new
BUDGET_FILE = "data/budgets.json"
try:
    budgets = data_manager.load_json(BUDGET_FILE) or []
except Exception:
    budgets = []



def _save_budgets():
    try:
        data_manager.save_json(BUDGET_FILE, budgets)
    except Exception as e:
        print(f"[budgets] Warning: failed to save budgets ({e})")


def _current_month():
    return datetime.now().strftime("%Y-%m")


def _get_user_id():
    return auth.current_user.get("user_id") if auth.current_user else None


def set_monthly_budget():
    if not auth.current_user:
        print("⚠️ Please login first.")
        input("Press Enter...")
        return

    month = _current_month()
    uid = _get_user_id()

    try:
        amount = Decimal(input(f"Enter budget for {month}: ").strip())
    except Exception:
        print("❌ Invalid amount.")
        input("Press Enter...")
        return
    

    # Update existing or create new
    for b in budgets:
        if b["user_id"] == uid and b["month"] == month:
            b["budget"] = str(amount)
            break
    else:
        budgets.append({
            "user_id": uid,
            "month": month,
            "budget": str(amount),
        })

    _save_budgets()
    print(f"✅ Budget set: {amount}")
    input("Press Enter...")




def view_budget_status():
    if not auth.current_user:
        print("⚠️ Please login first.")
        input("Press Enter...")
        return

    month = _current_month()
    uid = _get_user_id()
    selected_budget = None

    # Find user's current month budget
    for b in budgets:
        if b["user_id"] == uid and b["month"] == month:
            selected_budget = Decimal(b["budget"])
            break

    if not selected_budget:
        print("⚠️ No budget set for this month.")
        input("Press Enter...")
        return

    # Load all transactions from disk
    all_txns = data_manager.load_transactions()

    # Filter only current month expenses of this user
    total_spent = Decimal("0.00")
    for tx in all_txns:
        if tx.get("user_id") == uid and tx.get("type") == "expense":
            try:
                date = datetime.strptime(tx["date"], "%Y-%m-%d")
                if date.strftime("%Y-%m") == month:
                    total_spent += safe_amount(tx.get("amount"))
            except:
                continue

    remaining = selected_budget - total_spent
    remaining = round_money(remaining)

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
        print("\n💸 Monthly Budget Manager")
        print("-" * 35)
        print("1) Set Monthly Budget")
        print("2) View Budget & Remaining")
        print("0) Back")
        choice = input("Select an option: ").strip()

        if choice == "1":
            set_monthly_budget()
        elif choice == "2":
            view_budget_status()
        elif choice == "0":
            return
        else:
            print("❌ Invalid option.")
            input("Press Enter to continue...")