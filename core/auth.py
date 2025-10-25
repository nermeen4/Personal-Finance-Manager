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

def _compute_next_user_id(user_list):
    # If the user list is empty, start IDs from 1
    if not user_list:
        return 1
    # store all the numeric parts of user IDs
    nums = []  

    # Go through each user in the list
    for user in user_list:
        # Get the user_id value, or empty string if missing
        uid = user.get("user_id", "")  

        digits = ""  # To collect digits from the user_id

        # Loop through each character in the user_id
        for ch in uid:
            if ch.isdigit():  # Check if it's a number
                digits += ch  # Add the number character to the digits string

        # Convert digits to an integer, or use 0 if there were no digits
        if digits == "":
            number = 0
        else:
            number = int(digits)
        # Add this number to our list
        nums.append(number)  

    # If found any numbers get the next one after the highest
    if nums:
        next_id = max(nums) + 1
    else:
        # If no numbers found use the list length + 1
        next_id = len(user_list) + 1

    # Return the next available userid number
    return next_id


next_id = _compute_next_user_id(users)


def clear_screen():
    #Clear the console screen.
    print("\033c", end="")


def _save_users():
    try:
        data_manager.save_users(users)
    except Exception:
        print("[auth] Warning: failed to save users.")


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
            print("Invalid option.")
            input("Press Enter to continue...")


def register_user():
    #Register a new user with name password currency.
    global users, next_id
    clear_screen()
    print("Register New User")
    print("-" * 40)

    name = input("Enter full name: ").strip()
    password = input("Enter password: ").strip()
    confirm = input("Confirm password: ").strip()

    if password != confirm:
        print("Password doesn't match.")
        input("Press Enter to return.")
        return

    currency = input("Preferred currency: ").strip().upper() or "EGP"

    # Check if a user with the same name already exists
    user_exists = False

    for user in users:
        # Compare names without worrying about uppercase/lowercase
        if user["name"].lower() == name.lower():
            user_exists = True
            break  # No need to keep checking once we find a match

    if user_exists:
        print("A user with that name already exists.")
    else:
        # Create a new user dictionary
        user = {
            # Format ID like U001, U002, etc.
            "user_id": "U" + str(next_id).zfill(3),  
            "name": name,
            "password": password,
            "currency": currency
        }

        # Add the new user to the list
        users.append(user)

        # Increase the ID counter for the next user
        next_id = next_id + 1


        # Save the updated users list
        _save_users()

        print(f"User {name} registered successfully.")

    # Pause before going back to the main menu
    input("\n Press Enter to return.")



def login_user():
    #login user by name and password

    global current_user

    clear_screen()

    print("User Login")
    print("-" * 40)
    name = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    # check for a user with this name and password
    for user in users:
        if user["name"].lower() == name.lower() and user["password"] == password:
            #if found, set as current user instead of none
            current_user = user
            print(f"Welcome, {user['name']}!")
            input("\n Press Enter to return.")
            return
    print("Invalid username or password.")
    input("\n Press Enter to return.")


def list_users():
    # list all registered users.
    clear_screen()
    print("Registered Users")
    print("-" * 40)
    if not users:
        print("No users found.")
    else:
        for user in users:
            print(f"ID: {user['user_id']} | Name: {user['name']} | Currency: {user['currency']}")
    input("\nPress Enter to return...")


def switch_profile():
    # Switch to a different user profile.
    global current_user

    # Clear the screen for better readability
    clear_screen()
    print("Switch Profile")
    print("-" * 30)

    # Check if there are any users to switch to
    if not users:
        print("No users available.")
        input("\nPress Enter to return...")
        return  # Stop here if no users exist

    # display all users
    index = 1
    for u in users:
        print(f"{index}) {u['name']} ({u['currency']})")
        index += 1

    # Ask the user to pick one of the listed profiles and convert input to a number
    choice_input = input("\nEnter the number of user to switch to: ").strip()
    try:
        choice = int(choice_input)
    except ValueError:
        print("Invalid input. Please enter a number.")
        input("\nPress Enter to return...")
        return

    # Check if the chosen number is within the valid range
    if choice < 1 or choice > len(users):
        print("Invalid selection.")
        input("\nPress Enter to return...")
        return

    # Get the selected user (list index starts at 0)
    candidate = users[choice - 1]


    # ask for that user's password and check it
    password = input(f"Enter password for {candidate['name']}: ").strip()
    if password == candidate.get("password", ""):
        current_user = candidate
        print(f"Switched to {current_user['name']}.")
    else:
        print("Incorrect password.")

    # Pause before returning
    input("\n Press Enter to return.")