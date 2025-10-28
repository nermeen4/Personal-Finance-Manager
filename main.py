
"""
main.py - Entry point for the Personal Finance Manager.

Responsibilities:
- Initialize data storage
- Handle user login and main navigation
- Manage transactions, reports, filtering, and advanced features
- Centralize auto-save and shutdown save operations
"""
from decimal import Decimal
from core import data_manager
from core.data_manager import initialize_files, shutdown_save
from core import auth
from core import transactions
from core.reports import (
    dashboard_summary,
    monthly_reports,
    category_breakdown,
    spending_trends
)
from core.search_filter import apply_filters, round_money
from core.ascii_viz import monthly_barchart, category_barchart, trend_chart
from advanced_features import save_goals, budget, bill

# Ensure required files and folders exist before any interaction
initialize_files()


def clear_screen():
    """Clear console screen using ANSI escape."""
    print("\033c", end="")


# =================================================================
# REPORTS (Merged Text + ASCII Visualizations)
# =================================================================
def reports_menu():
    while True:
        clear_screen()
        user = auth.current_user
        if not user:
            print("⚠️  Please login first (User Management).")
            input("Press Enter to return...")
            return

        txns = transactions.transactions
        user_id = user.get("user_id")

        print("\n📊 REPORTS MENU")
        print("-" * 35)
        print("1) Dashboard Summary")
        print("2) Monthly Reports + Chart")
        print("3) Category Breakdown + Chart")
        print("4) Spending Trends + Chart")
        print("0) Back to Main Menu")
        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            return

        elif choice == "1":
            summary = dashboard_summary(txns, user_id)
            print("\n📌 DASHBOARD SUMMARY")
            print(f"Total Income : {summary['total_income']}")
            print(f"Total Expense: {summary['total_expense']}")
            print(f"Balance      : {summary['balance']}")
            input("\nPress Enter to return...")

        elif choice == "2":
            data = monthly_reports(txns, user_id)
            print("\n📅 MONTHLY REPORTS")
            for month, vals in sorted(data.items()):
                print(f"{month}: Income: {vals['income']} | Expense: {vals['expense']}")
            monthly_barchart(data)
            input("\nPress Enter to return...")

        elif choice == "3":
            data = category_breakdown(txns, user_id)
            print("\n📂 CATEGORY BREAKDOWN")
            for category, amount in sorted(data.items(), key=lambda x: x[1], reverse=True):
                print(f"{category}: {amount}")
            category_barchart(data)
            input("\nPress Enter to return...")

        elif choice == "4":
            data = spending_trends(txns, user_id)
            print("\n📈 SPENDING TRENDS")
            for month, amount in sorted(data.items()):
                print(f"{month}: {amount}")
            trend_chart(data)
            input("\nPress Enter to return...")

        else:
            print("❌ Invalid selection.")
            input("Press Enter to continue...")


# =================================================================
# SEARCH & FILTER
# =================================================================
def search_and_filter_menu():
    if not auth.current_user:
        print("⚠️  Please login first.")
        input("Press Enter to continue...")
        return []

    txns = transactions.transactions
    clear_screen()
    print("\n🔍 Transaction Search & Filter")

    start_date = input("Start date (YYYY-MM-DD): ").strip()
    end_date = input("End date (YYYY-MM-DD): ").strip()
    category = input("Category: ").strip()
    min_amount = input("Min amount: ").strip()
    max_amount = input("Max amount: ").strip()
    keyword = input("Keyword: ").strip()
    sort_by = input("Sort by (date/amount/category/type): ").strip() or "date"
    reverse = input("Sort descending? (y/n): ").strip().lower() == "y"

    min_amount = Decimal(min_amount) if min_amount else None
    max_amount = Decimal(max_amount) if max_amount else None

    filtered = apply_filters(
        txns,
        start_date=start_date or None,
        end_date=end_date or None,
        category=category or None,
        min_amount=min_amount,
        max_amount=max_amount,
        keyword=keyword or None,
        sort_by=sort_by,
        reverse=reverse
    )

    if not filtered:
        print("\n⚠️ No matching transactions found.")
        input("\nPress Enter to return...")
        return []

    print(f"\n✅ {len(filtered)} matching transactions:\n")
    for tx in filtered:
        amount = round_money(Decimal(tx.get("amount", "0")))
        print(f"{tx['date']} | {tx['category']} | {amount} | {tx.get('description','')}")
        print("-" * 50)

    input("\nPress Enter to return...")
    return filtered

# =================================================================
# ADVANCED FEATURES MENU
# =================================================================
# ========== ADVANCED FEATURES MENU ==========
def advanced_features_menu():
    while True:
        clear_screen()
        print("⚙️ ADVANCED FEATURES")
        print("-" * 35)
        print("1) 🎯 Savings Goals")
        print("2) 💸 Monthly Budget Manager")
        print("3) ⏰ Bill Reminders")
        print("0) Back to Main Menu")
        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            save_goals.savings_menu()

        elif choice == "2":
            budget.budgets_menu()

        elif choice == "3":
           bill.bill_menu()

        elif choice == "0":
            return
        
        else:
            print("❌ Invalid choice.")
            input("Press Enter to continue...")

# =================================================================
# MAIN MENU + AUTO-SAVE ON RETURN
# =================================================================
def main_menu():
    while True:
        clear_screen()
        print("=== PERSONAL FINANCE MANAGER ===")
        print(f"Current user: {auth.current_user['name'] if auth.current_user else 'None'}")
        print("-" * 40)
        print("1) 👤 User Management")
        print("2) 💳 Transactions")
        print("3) 📊 Reports + Charts")
        print("4) 🔍 Search & Filter")
        print("5) ⚙️ Advanced Features")
        print("0) Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "0":
            shutdown_save(auth.users, transactions.transactions)  # ✅ Safety save
            print("\n👋 Exiting program. Goodbye!")
            break

        elif choice == "1":
            auth.user_management_menu()

        elif choice == "2":
            transactions.transactions_menu()

        elif choice == "3":
            reports_menu()

        elif choice == "4":
            search_and_filter_menu()

        elif choice == "5":
            advanced_features_menu()

        else:
            print("❌ Invalid choice.")
            input("Press Enter...")

        # ✅ Auto-save every time user returns here
        shutdown_save(auth.users, transactions.transactions)


# =================================================================
# ENTRY POINT
# =================================================================
if __name__ == "__main__":
    main_menu()