"""
transactions.py - Manage all user transactions.

Includes:
- Add income or expense
- Edit and delete transactions
- View and search by filters
- Input validation and categorization
"""
from datetime import date
from core import data_manager, auth

TRANSACTIONS = []
_next_id = 1

def _clear_screen():
    """Clear console for this module."""
    print("\033c", end="")

def _pause():
    input("Press Enter to return...")

def _format_txn_id(n: int) -> str:
    return f"TXN{n:03d}"

def _compute_next_id(txns):
    """Compute next numeric id from existing transaction_id values (supports 'TXN001' or integers)."""
    maxn = 0
    for tx in txns:
        tid = tx.get("transaction_id")
        if isinstance(tid, int):
            n = tid
        elif isinstance(tid, str):
            digits = ''.join(ch for ch in tid if ch.isdigit())
            n = int(digits) if digits else 0
        else:
            n = 0
        if n > maxn:
            maxn = n
    return maxn + 1

def _save_transactions():
    """Persist transactions using data_manager.save_data by loading current users then saving both."""
    try:
        users = data_manager.load_users() or []
        data_manager.save_data(users, TRANSACTIONS)
    except Exception as e:
        print(f"[transactions] Warning: failed to save transactions ({e})")

# Load transactions on import
try:
    _loaded_users, _loaded_txns = data_manager.load_data()
    if _loaded_txns:
        TRANSACTIONS = _loaded_txns
except Exception:
    TRANSACTIONS = []

# init next id based on loaded transactions
_next_id = _compute_next_id(TRANSACTIONS)

def transactions_menu():
    while True:
        _clear_screen()
        print("💳 TRANSACTIONS")
        print("-" * 30)
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
            print("❌ Invalid option.")
            _pause()

def add_transaction():
    global _next_id, TRANSACTIONS
    _clear_screen()
    print("→ Add income or expense")
    if not auth.current_user:
        print("You must be logged in to add a transaction.")
        _pause()
        return
    ttype = input("Type (income/expense): ").strip().lower()
    if ttype not in ("income", "expense"):
        print("❌ Invalid type; must be 'income' or 'expense'.")
        _pause()
        return
    try:
        amount = float(input("Amount: ").strip())
    except ValueError:
        print("❌ Invalid amount.")
        _pause()
        return



    user_id = auth.current_user.get("user_id") or auth.current_user.get("name")
    category = input("Category: ").strip() or "Uncategorized"
    tdate = input(f"Date (YYYY-MM-DD) [default {date.today()}]: ").strip()
    if not tdate:
        tdate = str(date.today())
    description = input("Description (optional): ").strip()
    payment_method = input("Payment method (e.g., Cash, Credit Card): ").strip() or "Unknown"

    tx = {
        "transaction_id": _format_txn_id(_next_id),
        "user_id": user_id,
        "type": ttype,
        "amount": amount,
        "category": category,
        "date": tdate,
        "description": description,
        "payment_method": payment_method,
    }
    TRANSACTIONS.append(tx)
    _next_id += 1
    # persist transactions
    _save_transactions()
    print(f"✔ Transaction added (ID: {tx['transaction_id']}).")
    _pause()
def _current_user_id():
    return auth.current_user.get("user_id") if getattr(auth, "current_user", None) else None

def _format_txn_id(n: int) -> str:
    return f"TXN{n:03d}"
# ...existing code...

def view_transactions():
    _clear_screen()
    print("→ All transactions")
    if not auth.current_user:
        print("You must be logged in to view transactions.")
        _pause()
        return

    user_id = _current_user_id()
    # show only transactions belonging to current user
    user_txns = [tx for tx in TRANSACTIONS if tx.get("user_id") == user_id]

    if not user_txns:
        print("No transactions found for the current user.")
    else:
        for tx in user_txns:
            print(
                f"[{tx['transaction_id']}] {tx['date']} {tx['type'].upper():7} "
                f"{tx['amount']:10.2f} {tx['category']:15} {tx['payment_method']:12} {tx.get('description','')}"
            )
    _pause()

def _find_tx(txn_id, require_owner: bool = True):
    """
    Find transaction by transaction_id.
    If require_owner is True, returns the tx only if it belongs to current user.
    """
    for tx in TRANSACTIONS:
        if str(tx.get("transaction_id")) == str(txn_id):
            if require_owner:
                uid = _current_user_id()
                if uid is None or tx.get("user_id") != uid:
                    return None
            return tx
    return None
# ...existing code...

def edit_transaction():
    global TRANSACTIONS
    _clear_screen()
    print("→ Edit transaction")
    if not auth.current_user:
        print("You must be logged in to edit transactions.")
        _pause()
        return

    txn_id = input("Enter transaction ID to edit (e.g. TXN001): ").strip()
    if not txn_id:
        print("❌ No ID entered.")
        _pause()
        return
    tx = _find_tx(txn_id, require_owner=True)
    if not tx:
        print("❌ Transaction not found or you don't have permission to edit it.")
        _pause()
        return

    print("Leave blank to keep current value.")
    new_type = input(f"Type [{tx['type']}]: ").strip().lower()
    if new_type:
        if new_type in ("income", "expense"):
            tx["type"] = new_type
        else:
            print("❌ Invalid type; keeping current.")
    new_amount = input(f"Amount [{tx['amount']}]: ").strip()
    if new_amount:
        try:
            tx["amount"] = float(new_amount)
        except ValueError:
            print("❌ Invalid amount; keeping current.")
    new_category = input(f"Category [{tx['category']}]: ").strip()
    if new_category:
        tx["category"] = new_category
    new_date = input(f"Date [{tx['date']}]: ").strip()
    if new_date:
        tx["date"] = new_date
    new_description = input(f"Description [{tx.get('description','')}]: ").strip()
    if new_description:
        tx["description"] = new_description
    new_payment = input(f"Payment method [{tx.get('payment_method','')}]: ").strip()
    if new_payment:
        tx["payment_method"] = new_payment

    # persist transactions after edit
    _save_transactions()
    print("✔ Transaction updated.")
    _pause()

def delete_transaction():
    global TRANSACTIONS
    _clear_screen()
    print("→ Delete transaction")
    if not auth.current_user:
        print("You must be logged in to delete transactions.")
        _pause()
        return

    txn_id = input("Enter transaction ID to delete (e.g. TXN001): ").strip()
    if not txn_id:
        print("❌ No ID entered.")
        _pause()
        return
    tx = _find_tx(txn_id, require_owner=True)
    if not tx:
        print("❌ Transaction not found or you don't have permission to delete it.")
        _pause()
        return
    confirm = input(f"Type 'yes' to confirm deletion of {txn_id}: ").strip().lower()
    if confirm == "yes":
        TRANSACTIONS.remove(tx)
        # persist transactions after deletion
        _save_transactions()
        print("✔ Transaction deleted.")
    else:
        print("✖ Deletion cancelled.")
    _pause()
# ...existing code...