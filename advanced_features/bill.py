"""
bill.py - Simple bill reminder system.

Features:
- Add / list bills (per-user)
- Persist bills to data/bills.json (uses core.data_manager)
- Check due bills for current user and print reminders
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from core import data_manager, auth
from decimal import Decimal

import os
# create new bills file to put the bills data
BILLS_FILE = os.path.join(data_manager.DATA_DIR, "bills.json")

def _ensure_data_dir():
    data_manager.ensure_data_dir()

def load_bills() -> List[Dict[str, Any]]:
    _ensure_data_dir()
    try:
        return data_manager.load_json(BILLS_FILE)
    except Exception:
        return []

def save_bills(bills: List[Dict[str, Any]]):
    _ensure_data_dir()
    #create new bills file to put the bills data
    try:
        data_manager.save_json(BILLS_FILE, bills)
    except Exception as e:
        print(f"[bill] Warning: failed to save bills ({e})")

#put in in bill formate BILLxxx
def _format_bill_id(n: int) -> str:
    return f"BILL{n:03d}"

def _compute_next_id(bills: List[Dict[str, Any]]) -> int:
    maxn = 0
    for b in bills:
        bid = b.get("bill_id")
        if not bid:
            continue
        s = str(bid)
        digits = "".join(ch for ch in s if ch.isdigit())
        if not digits:
            continue
        try:
            n = int(digits)
        except ValueError:
            continue
        if n > maxn:
            maxn = n
    return maxn + 1

# load the bills 
_bills = load_bills()
_next_id = _compute_next_id(_bills)

# clears the screen for the next text
def clear_screen():
    print("\033c", end="")

#pause the screen 
def pause():
    input("Press Enter to return...")

def add_bill():
    global _next_id, _bills
    if not auth.current_user:
        print("You must be logged in to add a bill.")
        pause()
        return

    clear_screen()
    print("Add Bill")
    #get bill info from user
    name = input("Bill name: ").strip() or "Unnamed Bill"

    #validate amount and date
    try:
        amount = Decimal(input("Amount: ").strip())
    except Exception:
        print("Invalid amount.")
        pause()
        return
    due = input("Due date (YYYY-MM-DD): ").strip()
    try:
        # validate date format
        due_date = datetime.strptime(due, "%Y-%m-%d").date()
        due = due_date.isoformat()
    except Exception:
        print("Invalid date format.")
        pause()
        return
    

    repeat = input("Repeat (monthly/yearly): ").strip().lower() or "none"
    payment_method = input("Payment method (optional): ").strip() or ""
    notes = input("Notes (optional): ").strip() or ""

    #bill dictionary format
    bill = {
        "bill_id": _format_bill_id(_next_id),
        "user_id": auth.current_user.get("user_id"),
        "name": name,
        "amount": float(amount),
        "due_date": due,
        "repeat": repeat if repeat in ("none", "monthly", "yearly") else "none",
        "payment_method": payment_method,
        "notes": notes,
        "paid": False
    }
    # append bill to bills list and save and add another id for next bill
    _bills.append(bill)
    _next_id += 1
    save_bills(_bills)
    #show user bill added and its id
    print(f"Bill added ({bill['bill_id']}).")
    pause()

#list all the bill of the user logged in
def list_bills(show_all: bool = False):
    clear_screen()
    #if user isnt logged in
    if not auth.current_user:
        print("You must be logged in to view bills.")
        pause()
        return
    
    #if user is logged in
    uid = auth.current_user.get("user_id")
    user_bills = [b for b in _bills if b.get("user_id") == uid]


    #if no bills found for user
    if not user_bills:
        print("No bills found for current user.")
        pause()
        return
    
    print("Your bills:")
    print("-" * 40)


    # list all bills for user logged in
    for bill in user_bills:
        status = "Paid" if bill.get("paid") else "Due"
        print(f"{bill['bill_id']} | {bill['due_date']} | {bill['name']} | {bill['amount']:.2f} | {status} | {bill.get('notes','')}")
    pause()

def mark_paid(bill_id: str):
    global _bills

    #if user isnt logged in
    if not auth.current_user:
        print("You must be logged in to mark bills.")
        pause()
        return
    
    
    uid = auth.current_user.get("user_id")
    for bill in _bills:
        if bill.get("bill_id") == bill_id and bill.get("user_id") == uid:
            bill["paid"] = True
            save_bills(_bills)
            print(f"{bill_id} marked as paid.")
            pause()
            return
    print("Bill not found or not permitted.")
    pause()

def _parse_date(s: str) -> Optional[date]:
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except Exception:
        return None



def check_due_next_5_days():
    #return unpaid bills for the current user due within the next 5 days."""
    if not auth.current_user:
        return []
    uid = auth.current_user.get("user_id")
    today = date.today()
    end_date = today + timedelta(days=5)
    due: List[Dict[str, Any]] = []

    for bill in _bills:
        if bill.get("user_id") != uid:
            continue
        d = _parse_date(bill.get("due_date", ""))
        if not d:
            continue
        if today <= d <= end_date and not bill["paid"]:
            due.append(bill)

    if due:
        print("\n Bills due in the next 5 days")
        print("-" * 40)
        for bill in due:
            days = (_parse_date(bill["due_date"]) - today).days
            when = "today" if days == 0 else f"in {days} day(s)" if days > 0 else f"{-days} day(s) overdue"
            print(f"{bill['bill_id']}: {bill['name']} — {bill['amount']:.2f} due {bill['due_date']} ({when})")
        print("-" * 40)
    


def bill_menu():
    while True:
        clear_screen()
        print("🔔 BILLS & REMINDERS")
        print("-" * 40)
        print("1) Add bill")
        print("2) List my bills")
        print("3) Mark bill paid")
        print("4) Check due bills")
        print("0) Back")
        choice = input("\nChoose: ").strip()
        if choice == "0":
            break
        if choice == "1":
            add_bill()
        elif choice == "2":
            list_bills()
        elif choice == "3":
            bid = input("Enter bill id (e.g. BILL001): ").strip()
            mark_paid(bid)
        elif choice == "4":
            clear_screen()
            check_due_next_5_days()
            pause()
        else:
            print("Invalid choice.")
            pause()