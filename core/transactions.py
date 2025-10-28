"""
transactions.py - Manage all user transactions.

Includes:
- Add income or expense
- Edit and delete transactions
- View and search by filters
- Input validation and categorization
"""
from datetime import datetime, date
from core import data_manager, auth
from decimal import Decimal
from core.search_filter import round_money 

# === Load existing transactions ===
try:
    transactions = data_manager.load_transactions() or []
except Exception:
    transactions = []

transactions = [tx for tx in transactions if tx.get("user_id")]

# === Utility Functions ===
def clear_screen():
    print("\033c", end="")

def pause():
    input("Press Enter to return")

def format_txn_id(n: int) -> str:
    return f"TXN{n:03d}"

def compute_next_id(txns):
    """Return next numeric ID based on existing transaction IDs."""
    maxn = 0
    for tx in txns:
        tid = tx.get("transaction_id")
        if not tid:
            continue
        digits = "".join(ch for ch in str(tid) if ch.isdigit())
        if digits.isdigit():
            maxn = max(maxn, int(digits))
    return maxn + 1

#Always recompute next ID safely
def refresh_next_id():
    return compute_next_id(transactions)


def _save_transactions():
    """Emergency save — REAL auto-save happens in main.py."""
    try:
        data_manager.save_transactions(transactions)
    except Exception as e:
        print(f"[transactions] Warning: failed to save transactions ({e})")


# === Transactions Menu ===
def transactions_menu():
    while True:
        clear_screen()
        print("transactions")
        print("-" * 40)
        print("1) Add income/expenses")
        print("2) View all transactions")
        print("3) Edit transactions")
        print("4) Delete with confirmation")
        print("0) Back to main menu")
        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            add_transaction()
        elif choice == "2":
            view_transactions()
        elif choice == "3":
            edit_transaction()
        elif choice == "4":
            delete_transaction()
        else:
            print("Invalid option")
            pause()


# === CRUD Operations ===
def add_transaction():
    global transactions
    clear_screen()
    print("Add income or expense")

    if not auth.current_user:
        print("You must be logged in to add a transaction.")
        pause()
        return
    
    ttype = input("Type (income/expense): ").strip().lower()
    if ttype not in ("income", "expense"):
        print("Invalid type. must be 'income' or 'expense'.")
        pause()
        return
    
    try:
        amount = Decimal(input("Amount: ").strip())
        if amount <= 0:       # handle for zero or negative amounts
            raise ValueError("Amount must be > 0")
    except Exception:
        print("Invalid amount.")
        pause()
        return

    user_id = auth.current_user.get("user_id") 
    if not user_id: #check for user_id presence
        print("Error: Missing user ID. Login again.")
        pause()
        return

    category = input("Category: ").strip() or "Uncategorized"
    tdate = input(f"Date (YYYY-MM-DD) [default {date.today()}]: ").strip()
    if not tdate:
        tdate = str(date.today())

    # validate date format new addition
    try:
        datetime.strptime(tdate, "%Y-%m-%d")
    except Exception:
        print("Invalid date format. Use YYYY-MM-DD.")
        pause()
        return
  
    description = input("Description (optional): ").strip()
    payment_method = input("Payment method (e.g., Cash, Credit Card): ").strip() or "Unknown"

    tx = {
        "transaction_id": format_txn_id(refresh_next_id()),
        "user_id": user_id,
        "type": ttype,
        "amount": amount,
        "category": category,
        "date": tdate,
        "description": description,
        "payment_method": payment_method,
    }
    transactions.append(tx)
    _save_transactions()

    print(f"Transaction added (ID: {tx['transaction_id']}).")
    pause()


def _current_user_id():
    return auth.current_user.get("user_id") if auth.current_user else None


def view_transactions(sort_by: str = "date", reverse: bool = True):
    clear_screen()
    print("→ Your transactions")

    if not auth.current_user:
        print("You must be logged in to view transactions.")
        pause()
        return

    user_id = _current_user_id()
    # show only transactions belonging to current user
    user_txns = [tx for tx in transactions if tx.get("user_id") == user_id]

    if not user_txns:
        print("No transactions found for the current user.")
    else:
        for tx in user_txns:
            amount_str = f"{round_money(tx['amount']):.2f}"
            print(
                f"[{tx['transaction_id']}] {tx['date']} {tx['type'].upper():7} "
                f"{amount_str:10} {tx['category']:15} "
                f"{tx['payment_method']:12} {tx.get('description','')}"
            )
    pause()


def _find_tx(txn_id, require_owner = True):
    #Find transaction by transaction_id.
    #If require_owner is True, returns the tx only if it belongs to current user.
    for tx in transactions:
        if str(tx.get("transaction_id")) == str(txn_id):
            if require_owner:
                if tx.get("user_id") != _current_user_id():
                    return None
            return tx
    return None


def edit_transaction():
    global transactions
    clear_screen()
    print("Edit transaction")

    if not auth.current_user:
        print("You must be logged in to edit transactions.")
        pause()
        return

    txn_id = input("Enter transaction ID to edit (e.g. TXN001): ").strip()
    tx = _find_tx(txn_id, require_owner=True)
    if not tx:
        print("Not found or no permission.")
        pause()
        return

    print("Leave blank to keep current value.")
    new_type = input(f"Type [{tx['type']}]: ").strip().lower()
    if new_type in ("income", "expense"):
        tx["type"] = new_type
    
    new_amount = input(f"Amount [{tx['amount']}]: ").strip()
    if new_amount:
        try:  #rehandle amount input
            dec = Decimal(new_amount)
            if dec > 0:
                tx["amount"] = dec
        except Exception:
            print("Invalid amount. keeping current.")

    new_category = input(f"Category [{tx['category']}]: ").strip()
    if new_category:
        tx["category"] = new_category

    new_date = input(f"Date [{tx['date']}]: ").strip()
    if new_date:
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            tx["date"] = new_date
        except Exception:
            print("Invalid date. keeping current.")

    new_description = input(f"Description [{tx.get('description','')}]: ").strip()
    if new_description:
        tx["description"] = new_description

    new_payment = input(f"Payment method [{tx.get('payment_method','')}]: ").strip()
    if new_payment:
        tx["payment_method"] = new_payment

    # persist transactions after edit
    _save_transactions()
    print("✔ Transaction updated.")
    pause()



def delete_transaction():
    global transactions
    clear_screen()
    print("Delete transaction")

    if not auth.current_user:
        print("You must be logged in to delete transactions.")
        pause()
        return

    txn_id = input("Enter transaction ID to delete (e.g. TXN001): ").strip()
    tx = _find_tx(txn_id, require_owner=True)
    if not tx:
        print("Not found.")
        pause()
        return
    ###confirm deletion
    if input("Type YES to confirm: ").strip().lower() == "yes":
        transactions.remove(tx)
        _save_transactions()
        print("Deleted.")
    else:
        print("Cancelled.")
    pause()