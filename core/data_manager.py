"""
data_manager.py - Handles data persistence and backups.

Responsible for:
- Loading and saving JSON files (users, transactions)
- Ensuring data directory exists
- Auto-save functionality
- Shutdown save operations
- Basic backup and restore operations
"""
import os   # handle existing file paths and directories
import json # read and write JSON files
from typing import Any, Dict, List  # used to import type hints classes that describe what types of data your functions expect or return
from datetime import datetime # used to create timestamps for backup files
import time # used for auto-save timing
 
# === File paths ===
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")


# === Global auto-save settings ===
AUTO_SAVE_INTERVAL = 60  # auto-saave every 60 seconds
_last_auto_save = 0      # tracks the last auto-save time
_save_counter = 0        # counts how many times auto-save occurred


# === Ensure data directories exist (helper)===
def ensure_data_dir():
    """Ensure the data and backup directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)


   

# === Load and Save JSON Data ===
def load_json(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON data from a file."""
    ensure_data_dir()
    if not os.path.exists(file_path):
        return [] # Return empty list if file missing
    
    # handling JSON decode errors or file not found errors
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError , FileNotFoundError):
        print (f"[Warning] could not read {file_path} Returning empty list.")
        return []
    

    
# Save JSON data to a file
def save_json(file_path: str, data: List[Dict[str, Any]]):  # takes two parameters: file_path (a string representing the path to the file where the data will be saved) and data (a list of dictionaries containing the  actual data to be saved).
    """Save JSON data to a file."""
    ensure_data_dir()
    #create backup before saving
    if os.path.exists(file_path):
        backup_file = f"{file_path}.bak"  # create a backup copy before saving to ensure there is no data missed.
        os.replace(file_path, backup_file)  # move the copy of original file.
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4) #Converts your Python data into JSON text and writes it into the file.



# === Specialized functions ===
#load and save users
def load_users() -> List[Dict[str, Any]]: # returns a list of dictionaries, where each dictionary represents a user and contains key-value pairs for user attributes.
    """Load user data from users.json."""
    return load_json(USERS_FILE)
def save_users(users: List[Dict[str, Any]]):
    """Save user data to users.json."""
    save_json(USERS_FILE, users)


#load and save transactions
def load_transactions() -> List[Dict[str, Any]]:
    """Load transaction data from transactions.json."""
    return load_json(TRANSACTIONS_FILE)
def save_transactions(transactions: List[Dict[str, Any]]):
    """Save transaction data to transactions.json."""
    save_json(TRANSACTIONS_FILE, transactions)


# === Auto-Save System ===
def auto_save(users: List[Dict[str, Any]], transactions: List[Dict[str, Any]], force: bool = False):
    """
    Automatically save data at regular intervals or when forced.
    - users: list of user dictionaries
    - transactions: list of transaction dictionaries
    - force: True forces save immediately
    """

    global _last_auto_save, _save_counter
    current_time = time.time()
    if force or (current_time - _last_auto_save) >= AUTO_SAVE_INTERVAL:
        save_users(users)
        save_transactions(transactions)
        _last_auto_save = current_time
        _save_counter += 1
        print(f"[Auto-Save] Data saved automatically at {datetime.now().strftime('%H:%M:%S')}")

         # Create a timestamped backup every 5 auto-saves
        if _save_counter % 5 == 0:
            print("[Auto-Save] Creating periodic backup...")
            backup_all()

# === Shutdown Save ===
def shutdown_save(users: List[Dict[str, Any]], transactions: List[Dict[str, Any]]):
    """Force save everything before exiting the program."""
    print("[Shutdown] Saving all data before exit...")
    auto_save(users, transactions, force=True)
    print("[Shutdown] All data saved successfully.")


# === Backup and Restore ===
def backup_all():
    """Backup both JSON files with timestamps."""
    ensure_data_dir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # Generate timestamp for backup filenames (string format time like "20240615_123456")
    for file in [USERS_FILE, TRANSACTIONS_FILE]:   # Iterate over both files to back up
        if os.path.exists(file):
            filename = os.path.basename(file) # returns just the file’s name, without the folder part to store the backup inside another folder (data/backups/)
            backup_name = os.path.join(BACKUP_DIR, f"{filename}_{timestamp}.bak") #creates the full file path for unique names and safe locations 
            os.replace(file, backup_name) # Move original file to backup location
            print(f"[Backup] Created {backup_name}")