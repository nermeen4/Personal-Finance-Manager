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
from decimal import Decimal

transactions = []
#next_id = 1

def clear_screen():
    #Clear console for this module.
    print("\033c", end="")

def pause():
    input("Press Enter to return")

def format_txn_id(n: int) -> str:
    return f"TXN{n:03d}"

def compute_next_id(txns):
    #return next numeric id based on transaction_id values.

    #handles integer IDs or strings like 'TXN001'. Keeps logic simple and easy to read.
    maxn = 0
    for tx in txns:
        tid = tx.get("transaction_id")
        if not tid:
            continue

        #if its an int, use it directly
        if isinstance(tid, int):
            n = tid
        else:
            #  extract digits and convert from TXN001
            digits = "".join(ch for ch in str(tid) if ch.isdigit())
            if not digits:
                continue
            try:
                n = int(digits)
            except ValueError:
                continue

        if n > maxn:
            maxn = n

    return maxn

def _save_transactions():
    #save transactions using data_manager.save_data by loading current users then saving both.
    try:
        data_manager.save_transactions(transactions)
    except Exception as e:
        print(f"[transactions] Warning: failed to save transactions ({e})")

# Load transactions on import
try:
    loaded_txns = data_manager.load_transactions()
    if loaded_txns:
        transactions = loaded_txns
except Exception:
    transactions = []

# init next id based on loaded transactions
next_id = compute_next_id(transactions) + 1

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

def add_transaction():
    global next_id, transactions
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
    except ValueError:
        print("Invalid amount.")
        pause()
        return



    user_id = auth.current_user.get("user_id") or auth.current_user.get("name")
    category = input("Category: ").strip() or "Uncategorized"
    tdate = input(f"Date (YYYY-MM-DD) [default {date.today()}]: ").strip()
    if not tdate:
        tdate = str(date.today())
    description = input("Description (optional): ").strip()
    payment_method = input("Payment method (e.g., Cash, Credit Card): ").strip() or "Unknown"

    tx = {
        "transaction_id": format_txn_id(next_id),
        "user_id": user_id,
        "type": ttype,
        "amount": float(amount),
        "category": category,
        "date": tdate,
        "description": description,
        "payment_method": payment_method,
    }
    transactions.append(tx)
    next_id += 1
    # persist transactions
    _save_transactions()
    print(f"Transaction added (ID: {tx['transaction_id']}).")
    pause()
def _current_user_id():
    return auth.current_user.get("user_id") if getattr(auth, "current_user", None) else None

def format_txn_id(n: int) -> str:
    return f"TXN{n:03d}"

def view_transactions():
    clear_screen()
    print("→ All transactions")
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
            print(
                f"[{tx['transaction_id']}] {tx['date']} {tx['type'].upper():7} "
                f"{tx['amount']:10.2f} {tx['category']:15} {tx['payment_method']:12} {tx.get('description','')}"
            )
    pause()

def _find_tx(txn_id, require_owner: bool = True):
    #Find transaction by transaction_id.
    #If require_owner is True, returns the tx only if it belongs to current user.
    for tx in transactions:
        if str(tx.get("transaction_id")) == str(txn_id):
            if require_owner:
                uid = _current_user_id()
                if uid is None or tx.get("user_id") != uid:
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
    if not txn_id:
        print("No ID entered.")
        pause()
        return
    tx = _find_tx(txn_id, require_owner=True)
    if not tx:
        print("Transaction not found or you don't have permission to edit it.")
        pause()
        return

    print("Leave blank to keep current value.")
    new_type = input(f"Type [{tx['type']}]: ").strip().lower()
    if new_type:
        if new_type in ("income", "expense"):
            tx["type"] = new_type
        else:
            print("Invalid type. keeping current.")
    new_amount = input(f"Amount [{tx['amount']}]: ").strip()
    if new_amount:
        try:
            tx["amount"] = float(new_amount)
        except ValueError:
            print("Invalid amount. keeping current.")
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
    if not txn_id:
        print("No ID entered.")
        pause()
        return
    tx = _find_tx(txn_id, require_owner=True)
    if not tx:
        print("Transaction not found.")
        pause()
        return
    confirm = input(f"Type 'yes' to confirm deletion of {txn_id}: ").strip().lower()
    if confirm == "yes":
        transactions.remove(tx)
        # persist transactions after deletion
        _save_transactions()
        print("Transaction deleted.")
    else:
        print("Deletion cancelled.")
        pause()
