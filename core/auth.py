"""
auth.py - User authentication and management.
Provides:
- User registration
- Password/PIN hashing
- Login verification
- Profile switching
"""
# modules/user_management.py
# Handles user registration, login, and profile management (simple version — no getpass, no uuid, no hashing)

from core import data_manager

# Load users from disk (users only, no transactions)
try:
    users = data_manager.load_users() or []
except Exception:
    users = []

current_user = None

def _compute_next_user_id(u_list):
    if not u_list:
        return 1
    nums = []
    for u in u_list:
        uid = u.get("user_id", "")
        try:
            # accept formats like U001, u1, etc.
            nums.append(int(''.join(ch for ch in uid if ch.isdigit()) or 0))
        except Exception:
            continue
    return (max(nums) + 1) if nums else (len(u_list) + 1)

next_id = _compute_next_user_id(users)


def clear_screen():
    """Clear the console screen."""
    print("\033c", end="")


def _save_users():
    """Persist users list using data_manager.save_users."""
    try:
        data_manager.save_users(users)
    except Exception as e:
        print(f"[auth] Warning: failed to save users ({e})")


def user_management_menu():
    """Display and handle the User Management submenu."""
    global current_user

    while True:
        clear_screen()
        print("👤 USER MANAGEMENT")
        print("-" * 35)
        print(f"Current user: {current_user['name'] if current_user else 'None'}")
        print("\n1) Register new user")
        print("2) Login with password")
        print("3) View all users")
        print("4) Switch profile")
        print("0) Back to main menu")
        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            break
        elif choice == "1":
            register_user()
        elif choice == "2":
            login_user()
        elif choice == "3":
            list_users()
        elif choice == "4":
            switch_profile()
        else:
            print("❌ Invalid option.")
            input("Press Enter to continue...")


def register_user():
    """Register a new user with name, password, and currency."""
    global users, next_id
    clear_screen()
    print("➕ Register New User")
    print("-" * 30)

    name = input("Enter full name: ").strip()
    password = input("Enter password: ").strip()
    confirm = input("Confirm password: ").strip()

    if password != confirm:
        print("❌ Passwords do not match.")
        input("Press Enter to return...")
        return

    currency = input("Preferred currency (e.g., USD, EUR, EGP): ").strip().upper() or "USD"

    if any(u["name"].lower() == name.lower() for u in users):
        print("⚠️  A user with that name already exists.")
    else:
        user = {
            "user_id": f"U{next_id:03d}",
            "name": name,
            "password": password,  # plain text (consider hashing later)
            "currency": currency,
        }
        users.append(user)
        next_id += 1
        # persist users only
        _save_users()
        print(f"✅ User '{name}' registered successfully.")
    input("\nPress Enter to return...")


def login_user():
    """Authenticate existing user using plain password."""
    global current_user
    clear_screen()
    print("🔐 User Login")
    print("-" * 30)
    name = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    for u in users:
        if u["name"].lower() == name.lower() and u["password"] == password:
            current_user = u
            print(f"✅ Welcome, {u['name']} ({u['currency']})!")
            input("\nPress Enter to return...")
            return
    print("❌ Invalid username or password.")
    input("\nPress Enter to return...")


def list_users():
    """List all registered users."""
    clear_screen()
    print("👥 Registered Users")
    print("-" * 30)
    if not users:
        print("No users found.")
    else:
        for u in users:
            mark = "⭐ (current)" if current_user and u["user_id"] == current_user["user_id"] else ""
            print(f"ID: {u['user_id']} | Name: {u['name']} | Currency: {u['currency']} {mark}")
    input("\nPress Enter to return...")


# ...existing code...
def switch_profile():
    """Switch to another user profile (requires password)."""
    global current_user
    clear_screen()
    print("🔄 Switch Profile")
    print("-" * 30)
    if not users:
        print("No users available.")
        input("\nPress Enter to return...")
        return

    idx = 1
    for u in users:
        print(f"{idx}) {u['name']} ({u['currency']})")
        idx += 1

    try:
        choice = int(input("\nEnter the number of user to switch to: ").strip())
        if 1 <= choice <= len(users):
            candidate = users[choice - 1]
            pw = input(f"Enter password for {candidate['name']}: ").strip()
            if pw == candidate.get("password", ""):
                current_user = candidate
                print(f"✅ Switched to {current_user['name']}.")
            else:
                print("❌ Incorrect password. Profile not switched.")
        else:
            print("❌ Invalid selection.")
    except ValueError:
        print("❌ Invalid input.")
    input("\nPress Enter to return...")