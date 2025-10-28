"""
save_goals.py - Savings Goals Management (per-user)

Features:
- Create savings goals linked to current user
- View only user's goals w/ progress bar
- Deposit toward selected goal
- Auto-save using core.data_manager helpers
"""
import os
from typing import List, Dict, Any
from decimal import Decimal
from core import auth, data_manager
from core.search_filter import round_money

GOALS_FILE = os.path.join("data", "savings_goals.json")

# Load and decode
raw_goals = data_manager.load_json(GOALS_FILE)
savings_goals: List[Dict[str, Any]] = [
    {
        "user_id": g.get("user_id"),
        "name": g.get("name", ""),
        "target": Decimal(str(g.get("target", "0"))),
        "saved": Decimal(str(g.get("saved", "0")))
    }
    for g in raw_goals
] if raw_goals else []


def _save_goals():
    """Write updated goals back to JSON"""
    serializable = [
        {
            "user_id": g["user_id"],
            "name": g["name"],
            "target": str(g["target"]),
            "saved": str(g["saved"])
        }
        for g in savings_goals
    ]
    data_manager.save_json(GOALS_FILE, serializable)


def clear_screen():
    print("\033c", end="")


def show_progress_bar(current: Decimal, target: Decimal) -> str:
    percentage = float((current / target) * 100) if target > 0 else 0
    filled = int(percentage // 5)
    return f"[{'█' * filled}{'.' * (20 - filled)}] {percentage:.1f}%"


def _user_goals(user_id: str) -> List[Dict[str, Any]]:
    """Return only this user's goals"""
    return [g for g in savings_goals if g["user_id"] == user_id]


def add_goal():
    clear_screen()
    if not auth.current_user:
        print("⚠️ Please login first.")
        input("Enter to return...")
        return

    print("➕ Add New Savings Goal")

    name = input("Goal name: ").strip()
    if not name:
        print("❌ Name cannot be empty.")
        input("Enter to return...")
        return

    try:
        target = Decimal(input("Target amount: ").strip())
        if target <= 0:
            raise ValueError
    except Exception:
        print("❌ Invalid target amount.")
        input("Enter to return...")
        return

    goal = {
        "user_id": auth.current_user["user_id"],
        "name": name,
        "target": target,
        "saved": Decimal("0.00")
    }
    savings_goals.append(goal)
    _save_goals()
    print("✅ Goal added!")
    input("Press Enter...")


def view_goals():
    clear_screen()
    user = auth.current_user
    if not user:
        print("⚠️ Please login first.")
        input("Enter to return...")
        return

    print("🎯 Your Savings Goals")
    print("-" * 50)

    goals = _user_goals(user["user_id"])
    if not goals:
        print("No goals yet.")
    else:
        for i, g in enumerate(goals, start=1):
            bar = show_progress_bar(g["saved"], g["target"])
            print(f"{i}) {g['name']} → {round_money(g['saved'])}/{round_money(g['target'])} {bar}")

    input("Enter to return...")


def deposit_to_goal():
    clear_screen()
    user = auth.current_user
    if not user:
        print("⚠️ Please login first.")
        input("Enter to return...")
        return

    goals = _user_goals(user["user_id"])
    if not goals:
        print("No goals to deposit.")
        input("Enter to return...")
        return

    print("💰 Deposit to a Goal\n")
    for i, g in enumerate(goals, start=1):
        print(f"{i}) {g['name']} (Saved: {round_money(g['saved'])}/{round_money(g['target'])})")

    try:
        choice = int(input("Choose goal #: ")) - 1
        if choice < 0 or choice >= len(goals):
            raise IndexError
        amount = Decimal(input("Deposit amount: "))
        if amount <= 0:
            raise ValueError
    except Exception:
        print("❌ Invalid input")
        input("Enter to return...")
        return

    goals[choice]["saved"] += amount
    _save_goals()

    print("✅ Deposit recorded!")
    input("Enter to return...")


def savings_menu():
    while True:
        clear_screen()
        print("💡 Savings Goals")
        print("-" * 30)
        print("1) Add goal")
        print("2) View goals")
        print("3) Deposit to goal")
        print("0) Back")
        choice = input("Select: ").strip()

        if choice == "1": add_goal()
        elif choice == "2": view_goals()
        elif choice == "3": deposit_to_goal()
        elif choice == "0": break
        else:
            print("❌ Invalid")
            input("Enter to continue...")
