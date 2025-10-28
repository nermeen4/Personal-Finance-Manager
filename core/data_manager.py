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
import shutil  # used for safe copy backups
from decimal import Decimal  #for encoding/decoding
import re  #safer decimal detection

# === File paths ===
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

# === Global auto-save settings ===
AUTO_SAVE_INTERVAL = 60  # auto-saave every 60 seconds
_last_auto_save = 0      # tracks the last auto-save time
_save_counter = 0        # counts how many times auto-save occurred

# Better numeric detection
DECIMAL_PATTERN = re.compile(r"^-?\d+(\.\d+)?$")


# === Decimal Encoding/Decoding Helpers ===
def _encode_decimals(obj):
    """Recursively convert Decimals to strings for JSON serialization."""
    if isinstance(obj, list):
        return [_encode_decimals(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _encode_decimals(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return str(obj)  # <-- Decimal -> string
    return obj


def _decode_decimals(obj):
    """Recursively convert numeric-looking strings back to Decimal where appropriate."""
    if isinstance(obj, list):
        return [_decode_decimals(v) for v in obj]
    if isinstance(obj, dict):
        return {k: _decode_decimals(v) for k, v in obj.items()}
    if isinstance(obj, str):
        # convert only if it looks like a number (integers or decimals)
        s = obj.strip()
        if DECIMAL_PATTERN.match(s):
            try:
                return Decimal(s)
            except Exception:
                return obj
    return obj

# === Ensure data directories exist (helper)===
def ensure_data_dir():
    """Ensure the data and backup directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

#== Initialize data files if missing ===
def initialize_files():
    """Ensure data files exist and contain empty JSON lists if missing."""
    ensure_data_dir()
    for path in (USERS_FILE, TRANSACTIONS_FILE):
        if not os.path.exists(path):
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump([], f)
            except Exception as e:
                print(f"[Warning] Could not initialize {path}: {e}")


# === Load and Save JSON Data ===
def load_json(file_path: str) -> List[Dict[str, Any]]:
    """Load JSON data from a file."""
    ensure_data_dir()
    if not os.path.exists(file_path):
        return [] # Return empty list if file missing
    
    # handling JSON decode errors or file not found errors
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return _decode_decimals(json.load(f))  # << NEW: decode numeric strings to Decimal
    except (json.JSONDecodeError , FileNotFoundError):
        print (f"[Warning] could not read {file_path} Returning empty list.")
        return []
    

# Save JSON data to a file
def save_json(file_path: str, data: List[Dict[str, Any]]):  # takes two parameters: file_path (a string representing the path to the file where the data will be saved) and data (a list of dictionaries containing the  actual data to be saved).
    """Save JSON data to a file."""
    ensure_data_dir()
    # create a timestamped safe backup copy (do NOT move original)
    if os.path.exists(file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(file_path)
        backup_name = os.path.join(BACKUP_DIR, f"{filename}_{timestamp}.bak")
        try:
            shutil.copy2(file_path, backup_name)  # << SAFER: copy the file
        except Exception:
            # if backup copying fails, continue but log warning
            print(f"[Warning] Could not create pre-save backup for {file_path}")

    # write encoded JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(_encode_decimals(data), f, indent=4)




# === load and save users & transactions ===
def load_users(): # returns a
    """Load user data from users.json."""
    return load_json(USERS_FILE)

def save_users(users: List[Dict[str, Any]]):
    """Save user data to users.json."""
    save_json(USERS_FILE, users)

def load_transactions():
    """Load transaction data from transactions.json."""
    return load_json(TRANSACTIONS_FILE)

def save_transactions(transactions: List[Dict[str, Any]]):
    """Save transaction data to transactions.json."""
    save_json(TRANSACTIONS_FILE, transactions)


# === Auto-Save System ===
def auto_save(users: List[Dict[str, Any]], transactions: List[Dict[str, Any]], force: bool = False):
    """ Automatically save data at regular intervals or when forced."""
    global _last_auto_save, _save_counter
    now = time.time()

    if force or (now - _last_auto_save) >= AUTO_SAVE_INTERVAL:
        save_users(users)
        save_transactions(transactions)
        _last_auto_save = now
        _save_counter += 1
        print(f"[Auto-Save] Data saved automatically at {datetime.now().strftime('%H:%M:%S')}")

         # Create a timestamped backup every 5 auto-saves
        if _save_counter % 5 == 0:
            print("[Auto-Save] Creating periodic backup...")
            backup_all()

# === Shutdown Save ===
def shutdown_save(users, transactions):
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
            try:
                shutil.copy2(file, backup_name)  # << SAFER: copy original
                print(f"[Backup] Created {backup_name}")
            except Exception as e:
                print(f"[Backup] Failed to backup {file}: {e}")


def restore_backup(backup_file: str):
    """
    Restore a backup file to its original location.
    backup_file should be an existing file in the backups directory.
    """

    if not os.path.exists(backup_file):
        print(f"[Restore] Backup file not found: {backup_file}")
        return False
    
    basename = os.path.basename(backup_file)
    # Determine which file it maps to (users or transactions)
    if basename.startswith("users"):
        target = USERS_FILE
    elif basename.startswith("transactions"):
        target = TRANSACTIONS_FILE
    else:
        print("[Restore] Unknown backup type.")
        return False
    try:
        shutil.copy2(backup_file, target)
        print(f"[Restore] Restored {backup_file} => {target}")
        return True
    except Exception as e:
        print(f"[Restore] Failed: {e}")
        return False
