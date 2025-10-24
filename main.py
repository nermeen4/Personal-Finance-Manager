"""
main.py - Entry point for the Personal Finance Manager.

Handles the main menu system, user login, and navigation between
different modules (transactions, reports, savings goals, etc.).
"""
# main.py

def clear_screen():
    """Clears the console screen."""
    print("\033c", end="")

# ===== MODULE IMPORTS =====
from core.data_manager import load_transactions
from core import auth  # ✅ Import the real user management module
from core import transactions  # ✅ Import the real transactions module
from core.reports import dashboard_summary, monthly_reports, category_breakdown, spending_trends
from core.search_filter import apply_filters, round_money
from decimal import Decimal



# ========== TRANSACTIONS ==========
# Backward-compat shim in case other code calls it
def transactions_menu():
    transactions.transactions_menu()

# ========== REPORTS ==========
def reports_menu():
    transactions = load_transactions()

    print("\n📊 REPORTS MENU")
    print("📊 REPORTS")
    print("-" * 30)
    print("1) Dashboard summary")
    print("2) Monthly reports")
    print("3) Category breakdown")
    print("4) Spending trends")
    print("0) Back to main menu")
    choice = input("\nSelect an option: ").strip()

    if choice == "1":   
        summary = dashboard_summary(transactions)
        print(f"\nTotal Income: {summary['total_income']}")
        print(f"Total Expense: {summary['total_expense']}")
        print(f"Balance: {summary['balance']}")

    elif choice == "2":
        monthly = monthly_reports(transactions)
        print("\n📅 MONTHLY REPORTS")
        print("-" * 30)
        for month, data in sorted(monthly.items()):
            income = round_money(data['income'])
            expense = round_money(data['expense'])
            print(f"{month}: Income: {income}, Expense: {expense}")

    elif choice == "3":
        breakdown = category_breakdown(transactions)
        print("\n📂 CATEGORY BREAKDOWN")
        print("-" * 30)
        for category, amount in sorted(breakdown.items()):
            print(f"{category}: {round_money(amount)}")
    
    elif choice == "4":
        trends = spending_trends(transactions)
        print("\n📈 SPENDING TRENDS")
        print("-" * 30)
        for month, amount in sorted(trends.items()):
            print(f"{month}: {round_money(amount)}")

    elif choice == "0":
        return
    
    else:
        print("❌ Invalid choice.")
        input("\nPress Enter to continue...")


# ========== SEARCH & FILTER ==========
def search_and_filter_menu():
    transactions = load_transactions()
    print("\n🔍 Transaction Search & Filter")

    start_date = input("Start date (YYYY-MM-DD): ").strip()
    end_date = input("End date (YYYY-MM-DD): ").strip()
    category = input("Category: ").strip()
    min_amount = input("Min amount: ").strip()
    max_amount = input("Max amount: ").strip()
    keyword = input("Keyword: ").strip()
    sort_by = input("Sort by (date/amount/category/type): ").strip() or "date"
    reverse = input("Sort descending? (y/n): ").strip().lower() == "y"

    # Convert amounts safely
    min_amount = Decimal(min_amount) if min_amount else None
    max_amount = Decimal(max_amount) if max_amount else None

    # Apply all filters
    filtered_txns = apply_filters(
        transactions,
        start_date=start_date or None,
        end_date=end_date or None,
        category=category or None,
        min_amount=min_amount,
        max_amount=max_amount,
        keyword=keyword or None,
        sort_by=sort_by,
        reverse=reverse
    )

    # Show results
    if not filtered_txns:
        print("\n⚠️ No matching transactions found.")
    else:
        print(f"\n✅ Found {len(filtered_txns)} transactions:\n")
        for txn in filtered_txns:
            amount = round_money(Decimal(txn['amount']))  # ✅ formatted nicely
            print(f"{txn['date']} | {txn['category']} | {amount} | {txn['description']}")

    return filtered_txns  # ✅ makes it reusable for reports/export

# ========== MAIN MENU ==========
def main_menu():
    while True:
        clear_screen()
        print("=== PERSONAL FINANCE MANAGER ===")
        print(f"Current user: {auth.current_user['name'] if auth.current_user else 'None'}")
        print("-" * 35)
        print("1) 👤 User Management")
        print("2) 💳 Transactions")
        print("3) 📊 Reports")
        print("4) 🔍 Search & Filter")
        print("5) 🖼️ ASCII Visuals")
        print("0) Exit")
        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            print("\n👋 Exiting program. Goodbye!")
            break

        # call user management menu
        elif choice == "1":
            auth.user_management_menu()
        
        #call transactions menu
        elif choice == "2":
            transactions.transactions_menu()

        
        # call reports menu
        elif choice == "3":
            reports_menu()

        # call search & filter menu
        elif choice == "4":
            filtered = search_and_filter_menu()
            if filtered:
                print("\n✅ You can now generate a report or export these results.")
                # (later you could call a reports function here)
            else:
                print("\n⚠️ No data to report.")
            
        else:
            print("❌ Invalid choice.")
            input("Press Enter to continue...")

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    main_menu()
