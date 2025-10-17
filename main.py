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
import transactions
import auth  # ✅ Import the real user management module

# ========== TRANSACTIONS ==========
# Backward-compat shim in case other code calls it
def transactions_menu():
    transactions.transactions_menu()

# ========== REPORTS ==========
def reports_menu():
    while True:
        clear_screen()
        print("📊 REPORTS")
        print("-" * 30)
        print("1) Dashboard summary")
        print("2) Monthly reports")
        print("3) Category breakdown")
        print("4) Spending trends")
        print("0) Back to main menu")
        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            dashboard_summary()
        elif choice == "2":
            monthly_reports()
        elif choice == "3":
            category_breakdown()
        elif choice == "4":
            spending_trends()
        else:
            print("❌ Invalid option.")
            input("Press Enter to continue...")

def dashboard_summary():
    print("→ [Placeholder] Show dashboard summary.")
    input("Press Enter to return...")

def monthly_reports():
    print("→ [Placeholder] Generate monthly reports.")
    input("Press Enter to return...")

def category_breakdown():
    print("→ [Placeholder] Show category breakdown report.")
    input("Press Enter to return...")

def spending_trends():
    print("→ [Placeholder] Display spending trends.")
    input("Press Enter to return...")

# ========== SEARCH & FILTER ==========
def search_filter_menu():
    while True:
        clear_screen()
        print("🔍 SEARCH & FILTER")
        print("-" * 30)
        print("1) Search by date range")
        print("2) Filter by category")
        print("3) Amount range filter")
        print("4) Sort results")
        print("0) Back to main menu")
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

def search_by_date():
    print("→ [Placeholder] Search transactions by date range.")
    input("Press Enter to return...")

def filter_by_category():
    print("→ [Placeholder] Filter transactions by category.")
    input("Press Enter to return...")

def amount_range_filter():
    print("→ [Placeholder] Filter transactions by amount range.")
    input("Press Enter to return...")

def sort_results():
    print("→ [Placeholder] Sort transactions (by date, amount, etc.).")
    input("Press Enter to return...")

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
        print("0) Exit")
        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            print("\n👋 Exiting program. Goodbye!")
            break
        elif choice == "1":
            # ✅ Call the real user management menu
            auth.user_management_menu()
        elif choice == "2":
            transactions.transactions_menu()
        elif choice == "3":
            reports_menu()
        elif choice == "4":
            search_filter_menu()
        else:
            print("❌ Invalid choice.")
            input("Press Enter to continue...")

# ========== ENTRY POINT ==========
if __name__ == "__main__":
    main_menu()
