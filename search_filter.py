# ...existing code...
from datetime import datetime
import transactions
import auth


def _parse_date(s: str):
    if not s:
        return None
    try:
        # accept YYYY-MM-DD
        return datetime.fromisoformat(s).date()
    except Exception:
        return None


def _get_user_txns():
    """Return transactions for the current user (uses transactions.TRANSACTIONS)."""
    uid = None
    # prefer transaction module helper if available
    try:
        uid = transactions._current_user_id()
    except Exception:
        pass
    if uid is None and getattr(auth, "current_user", None):
        uid = auth.current_user.get("user_id")
    if uid is None:
        return []
    return [tx for tx in transactions.TRANSACTIONS if tx.get("user_id") == uid]


def _display_txns(txns):
    if not txns:
        print("No transactions found.")
        input("Press Enter to return...")
        return
    for tx in txns:
        print(
            f"[{tx.get('transaction_id')}] {tx.get('date')} {tx.get('type','').upper():7} "
            f"{float(tx.get('amount',0)):10.2f} {tx.get('category',''):15} "
            f"{tx.get('payment_method',''):12} {tx.get('description','')}"
        )
    input("\nPress Enter to return...")


def search_by_date():
    """Search current user's transactions by date range."""
    print("→ Search by date range (YYYY-MM-DD). Leave blank for open-ended.")
    start_s = input("Start date: ").strip()
    end_s = input("End date: ").strip()
    start = _parse_date(start_s)
    end = _parse_date(end_s)

    if start_s and start is None:
        print("❌ Invalid start date format.")
        input("Press Enter to return...")
        return
    if end_s and end is None:
        print("❌ Invalid end date format.")
        input("Press Enter to return...")
        return

    txns = _get_user_txns()
    def in_range(tx):
        try:
            d = _parse_date(str(tx.get("date")))
        except Exception:
            return False
        if d is None:
            return False
        if start and d < start:
            return False
        if end and d > end:
            return False
        return True

    results = [t for t in txns if in_range(t)]
    _display_txns(sorted(results, key=lambda x: x.get("date") or ""))


def filter_by_category():
    """Filter current user's transactions by category (case-insensitive substring)."""
    cat = input("Category to filter by (partial match allowed): ").strip().lower()
    if not cat:
        print("❌ No category entered.")
        input("Press Enter to return...")
        return
    txns = _get_user_txns()
    results = [t for t in txns if cat in (str(t.get("category","")).lower())]
    _display_txns(sorted(results, key=lambda x: x.get("date") or ""))


def amount_range_filter():
    """Filter current user's transactions by amount range."""
    print("→ Amount range filter. Leave blank to omit a bound.")
    min_s = input("Minimum amount: ").strip()
    max_s = input("Maximum amount: ").strip()
    try:
        min_a = float(min_s) if min_s else None
    except ValueError:
        print("❌ Invalid minimum amount.")
        input("Press Enter to return...")
        return
    try:
        max_a = float(max_s) if max_s else None
    except ValueError:
        print("❌ Invalid maximum amount.")
        input("Press Enter to return...")
        return
    txns = _get_user_txns()

    def in_amount_range(tx):
        try:
            a = float(tx.get("amount", 0))
        except Exception:
            return False
        if min_a is not None and a < min_a:
            return False
        if max_a is not None and a > max_a:
            return False
        return True

    results = [t for t in txns if in_amount_range(t)]
    _display_txns(sorted(results, key=lambda x: float(x.get("amount", 0))))


def sort_results():
    """Sort current user's transactions by a chosen key."""
    choices = {"1": "date", "2": "amount", "3": "category", "4": "type"}
    print("Sort by:")
    print("1) Date")
    print("2) Amount")
    print("3) Category")
    print("4) Type")
    choice = input("Choose sort key: ").strip()
    key = choices.get(choice)
    if not key:
        print("❌ Invalid choice.")
        input("Press Enter to return...")
        return
    order = input("Order (asc/desc) [asc]: ").strip().lower() or "asc"
    reverse = order == "desc"

    txns = _get_user_txns()

    def key_fn(tx):
        val = tx.get(key)
        if key == "amount":
            try:
                return float(val)
            except Exception:
                return 0.0
        if key == "date":
            d = _parse_date(str(val))
            return d.isoformat() if d else ""
        return str(val or "").lower()

    results = sorted(txns, key=key_fn, reverse=reverse)
    _display_txns(results)


def search_filter_menu():
    """Interactive menu (can be used by main instead of the placeholder)."""
    while True:
        print("🔍 SEARCH & FILTER")
        print("-" * 30)
        print("1) Search by date range")
        print("2) Filter by category")
        print("3) Amount range filter")
        print("4) Sort results")
        print("0) Back")
        choice = input("\nSelect an option: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            search_by_date()
        elif choice == "2":
            filter_by_category()
        elif choice == "3":
            amount_range_filter()
        elif choice == "4":
            sort_results()
        else:
            print("❌ Invalid option.")
            input("Press Enter to continue...")
# ...existing code...