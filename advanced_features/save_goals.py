"""
savings.py - Savings Goals Management

Features:
- Create savings goals
- View goals with progress bar
- Mark deposits toward a goal
- Auto-save goals data
"""


import os
from typing import List, Dict, Any
from decimal import Decimal
from core import data_manager

GOALS_FILE = os.path.join("data", "savings_goals.json")

# Load and convert to Decimal
raw_goals = data_manager.load_json(GOALS_FILE)
savings_goals: List[Dict[str, Any]] = [
    {
        "name": g.get("name", ""),
        "target": Decimal(str(g.get("target", "0"))),
        "saved": Decimal(str(g.get("saved", "0")))
    }
    for g in raw_goals
] if raw_goals else []


def _save_goals():
    """Save Decimal values as strings for JSON safety."""
    serializable_goals = []
    for g in savings_goals:
        serializable_goals.append({
            "name": g["name"],
            "target": str(g["target"]),
            "saved": str(g["saved"])
        })
    data_manager.save_json(GOALS_FILE, serializable_goals)



def clear_screen():
    print("\033c", end="")


def show_progress_bar(current: Decimal, target: Decimal) -> str:
    percentage = float((current / target) * 100) if target > 0 else 0
    filled = int(percentage // 5)
    return f"[{'█' * filled}{'.' * (20 - filled)}] {percentage:.1f}%"

def add_goal():
    clear_screen()
    print("➕ Add New Savings Goal")
    name = input("Goal name: ").strip()
    try:
        target = Decimal(input("Target amount: ").strip())
    except:
        print("❌ Invalid amount")
        input("Enter to return...")
        return

    goal = {"name": name, "target": target, "saved": Decimal("0.00")}
    savings_goals.append(goal)
    _save_goals()
    print("✅ Goal added!")
    input("Press Enter to continue...")


def view_goals():
    clear_screen()
    print("🎯 Your Savings Goals")
    print("-" * 50)

    if not savings_goals:
        print("No active goals yet!")
    else:
        for i, g in enumerate(savings_goals, start=1):
            bar = show_progress_bar(g["saved"], g["target"])
            print(f"{i}) {g['name']} - {g['saved']}/{g['target']} {bar}")

    input("Enter to return...")



def deposit_to_goal():
    clear_screen()
    if not savings_goals:
        print("No goals available.")
        input("Enter to return...")
        return

    print("💰 Deposit to a Goal\n")
    for i, g in enumerate(savings_goals, start=1):
        print(f"{i}) {g['name']} (Saved: {g['saved']}/{g['target']})")

    try:
        choice = int(input("Choose goal #: "))
        amount = Decimal(input("Deposit amount: "))
    except:
        print("❌ Invalid input")
        input("Enter to return...")
        return

    goal = savings_goals[choice - 1]
    goal["saved"] += amount
    _save_goals()

    print("✅ Deposit added!")
    input("Enter to return...")

def savings_menu():
    while True:
        clear_screen()
        print("💡 Savings Goals")
        print("-" * 30)
        print("1) Add goal")
        print("2) View goals")
        print("3) Deposit into goal")
        print("0) Back")
        choice = input("Select: ").strip()

        if choice == "1": add_goal()
        elif choice == "2": view_goals()
        elif choice == "3": deposit_to_goal()
        elif choice == "0": break
        else:
            print("❌ Invalid")
            input("Enter to continue...")