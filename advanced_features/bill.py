"""
bill.py - Bill Reminder System (per-user)

Features:
- Add / list bills
- Mark bills as paid
- Show bills due within 5 days
- Uses core.data_manager for JSON persistence
"""

from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
from core import data_manager, auth

import os


BILLS_FILE = os.path.join(data_manager.DATA_DIR, "bills.json")


# ---------------- Data Loading & Saving ----------------
def _load_bills() -> List[Dict[str, Any]]:
    data_manager.ensure_data_dir()
    raw = data_manager.load_json(BILLS_FILE) or []
    bills = []
    for b in raw:
        bills.append({
            "bill_id": b.get("bill_id"),
            "user_id": b.get("user_id"),
            "name": b.get("name", ""),
            "amount": Decimal(str(b.get("amount", "0"))),
            "due_date": b.get("due_date"),
            "repeat": b.get("repeat", "none"),
            "payment_method": b.get("payment_method", ""),
            "notes": b.get("notes", ""),
            "paid": bool(b.get("paid", False))
        })
    return bills


def _save_bills():
    serializable = []
    for b in _bills:
        serializable.append({
            "bill_id": b["bill_id"],
            "user_id": b["user_id"],
            "name": b["name"],
            "amount": str(b["amount"]),
            "due_date": b["due_date"],
            "repeat": b["repeat"],
            "payment_method": b.get("payment_method", ""),
            "notes": b.get("notes", ""),
            "paid": b["paid"]
        })
    data_manager.save_json(BILLS_FILE, serializable)


_bills = _load_bills()


def _compute_next_id():
    maxn = 0
    for b in _bills:
        bid = b.get("bill_id", "")
        digits = "".join(ch for ch in bid if ch.isdigit())
        if digits.isdigit():
            maxn = max(maxn, int(digits))
    return maxn + 1


_next_id = _compute_next_id()


def clear_screen():
    print("\033c", end="")


def pause():
    input("Press Enter to return...")


def _format_bill_id(n: int) -> str:
    return f"BILL{n:03d}"


def _parse_date(s: str) -> Optional[date]:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None


# ---------------- Core Functions ----------------
def add_bill():
    global _next_id
    if not auth.current_user:
        print("⚠️ Login required.")
        pause()
        return

    clear_screen()
    print("➕ Add Bill")

    name = input("Bill name: ").strip() or "Unnamed Bill"

    try:
        amount = Decimal(input("Amount: ").strip())
        if amount <= 0:
            raise ValueError
    except Exception:
        print("❌ Invalid amount.")
        pause()
        return

    due_str = input("Due date (YYYY-MM-DD): ").strip()
    due_date = _parse_date(due_str)
    if not due_date:
        print("❌ Invalid date format.")
        pause()
        return

    repeat = input("Repeat (none/monthly/yearly): ").strip().lower()
    repeat = repeat if repeat in ("none", "monthly", "yearly") else "none"

    bill = {
        "bill_id": _format_bill_id(_next_id),
        "user_id": auth.current_user.get("user_id"),
        "name": name,
        "amount": amount,
        "due_date": due_date.isoformat(),
        "repeat": repeat,
        "payment_method": input("Payment method: ").strip() or "",
        "notes": input("Notes: ").strip() or "",
        "paid": False
    }

    _bills.append(bill)
    _next_id += 1
    _save_bills()

    print(f"✅ Bill added ({bill['bill_id']})")
    pause()


def list_bills():
    if not auth.current_user:
        print("⚠️ Login required.")
        pause()
        return

    clear_screen()
    uid = auth.current_user.get("user_id")
    user_bills = [b for b in _bills if b.get("user_id") == uid]

    if not user_bills:
        print("No bills found.")
        pause()
        return

    print("📋 Your Bills")
    print("-" * 45)
    for bill in sorted(user_bills, key=lambda b: b.get("due_date")):
        status = "✅ Paid" if bill["paid"] else "⚠️ Due"
        print(f"{bill['bill_id']} | {bill['due_date']} | {bill['name']} | {bill['amount']:.2f} | {status}")
    print("-" * 45)
    pause()


def mark_paid(bill_id: str):
    if not auth.current_user:
        print("⚠️ Login required.")
        pause()
        return

    uid = auth.current_user.get("user_id")

    for bill in _bills:
        if bill["bill_id"] == bill_id and bill["user_id"] == uid:
            bill["paid"] = True
            _save_bills()
            print(f"✅ Marked {bill_id} as paid.")
            pause()
            return

    print("❌ Bill not found.")
    pause()


def check_due_next_5_days():
    if not auth.current_user:
        return

    uid = auth.current_user.get("user_id")
    today = date.today()
    end_date = today + timedelta(days=5)
    due_list = []

    for bill in _bills:
        if bill["user_id"] != uid or bill["paid"]:
            continue

        d = _parse_date(bill["due_date"])
        if not d:
            continue

        if today <= d <= end_date:
            due_list.append(bill)

    if not due_list:
        print("✅ No upcoming bills!")
        return

    print("\n🔔 Bills Due Soon (Next 5 Days)")
    print("-" * 45)
    for bill in due_list:
        days = ( _parse_date(bill["due_date"]) - today ).days
        when = "today" if days == 0 else f"in {days} day(s)"
        print(f"{bill['bill_id']}: {bill['name']} — {bill['amount']:.2f} due {bill['due_date']} ({when})")
    print("-" * 45)


def bill_menu():
    while True:
        clear_screen()
        print("🔔 BILL REMINDERS")
        print("-" * 40)
        print("1) Add Bill")
        print("2) List Bills")
        print("3) Mark Bill Paid")
        print("4) View Due Soon")
        print("0) Back")
        choice = input("\nChoose: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            add_bill()
        elif choice == "2":
            list_bills()
        elif choice == "3":
            bid = input("Enter Bill ID: ").strip()
            mark_paid(bid)
        elif choice == "4":
            clear_screen()
            check_due_next_5_days()
            pause()
        else:
            print("❌ Invalid choice.")
            pause()
