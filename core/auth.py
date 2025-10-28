"""
auth.py - User authentication and management.
Provides:
- User registration
- Password/PIN hashing
- Login verification
- Profile switching
"""

import uuid  #create UUIDs
import hashlib  #hashing
from core import data_manager

# Load users from disk (users only, no transactions)
try:
    users = data_manager.load_users() or []
except Exception:
    users = []

current_user = None


def clear_screen():
    #Clear the console screen.
    print("\033c", end="")

# === Password hashing ===
def _hash_password(password: str) -> str:
    """Return hex digest of sha256(password)."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def _sanitize_users():
    """
    Ensure all users have required fields.
    Fixes older-version users missing attributes.
    """
    changed = False
    for user in users:
        if "user_id" not in user:
            user["user_id"] = str(uuid.uuid4())
            changed = True
        if "currency" not in user:
            user["currency"] = "EGP"
            changed = True
        if "password" not in user:
            # Force password reset? For now: empty hash (account unusable)
            user["password"] = ""
            changed = True

    if changed:
        data_manager.save_users(users)
_sanitize_users() 

def _save_users():
    try:
        data_manager.save_users(users)
    except Exception:
        print("[auth] Warning: failed to save users.")


# === User Management Menu ===
def user_management_menu():
    # Display and handle the User Management submenu.
    global current_user

    while True:
        clear_screen()
        print("USER MANAGEMENT")
        print("-" * 40)
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
            input("Invalid option. Press Enter...")

# === Register User ===
def register_user():
    global users
    clear_screen()
    print("Register New User")
    print("-" * 40)

    name = input("Enter full name: ").strip()
    if not name:
        input("Name required. Enter to return.")
        return
    
    if any(u.get("name", "").lower() == name.lower() for u in users):
        input("User already exists. Enter to return.")
        return

    password = input("Enter password (min 4 chars): ").strip()
    if len(password) < 4:
        input("Too short. Enter to return.")
        return
    
    confirm = input("Confirm password: ").strip()
    if password != confirm:
        input("Mismatch. Enter to return.")
        return

    currency = input("Preferred currency (USD): ").strip().upper() or "EGP"

    user = {
        "user_id": str(uuid.uuid4()),  #use UUID
        "name": name,
        "password": _hash_password(password),  #store hashed
        "currency": currency
    }
    users.append(user)
    _save_users()
    # optionally call data_manager.auto_save(users, data_manager.load_transactions?) from main
    input(f"User {name} registered successfully. Press Enter...")
    

## login with hashed passwords ##
def login_user():
    global current_user
    clear_screen()
    print("User Login")
    print("-" * 40)

    name = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    hashed = _hash_password(password)

    for user in users:
        if user.get("name", "").lower() == name.lower() and user.get("password") == hashed:
            current_user = user
            input(f"Login successful. Welcome {user['name']}! Press Enter...")
            return user  #return object
        
    input("Invalid credentials. Press Enter...")
    return None


###list users######
def list_users():
    clear_screen()
    print("Registered Users")
    print("-" * 40)

    if not users:
        print("No users found.")
    else:
        for user in users:
            print(f"Name: {user['name']} | Currency: {user['currency']}")
    input("\nPress Enter to return...")


# === Switch Profile ===
def switch_profile():
    global current_user
    clear_screen()
    print("Switch Profile")
    print("-" * 30)

    # Check if there are any users to switch to
    if not users:
        input("No users available. Enter to return.")
        return  # Stop here if no users exist

    # display all users
    for idx, u in enumerate(users, start=1):
        print(f"{idx}) {u['name']} ({u['currency']})")
     
    # Ask the user to pick one of the listed profiles and convert input to a number
    choice_str = input("\nEnter the number of user to switch to: ").strip()

    # Validate input structure
    if not choice_str.isdigit():
        input("Invalid input! Please enter a number. Press Enter...")
        return

    idx = int(choice_str)

    # Validate range
    if idx < 1 or idx > len(users):
        input("Invalid selection! Press Enter...")
        return


    # Get the selected user (list index starts at 0)
    candidate = users[idx- 1]
    pwd = input(f"Enter password for {candidate['name']}: ").strip()

    #compare hashed password
    if _hash_password(pwd) == candidate.get("password", ""):
        current_user = candidate
        input(f"Switched to {candidate['name']}. Press Enter...")
    else:
        input("Incorrect password. Press Enter...")