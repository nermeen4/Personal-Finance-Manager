"""
data_manager.py - Handles data persistence and backup.

Responsible for:
- Saving/loading user and transaction data to/from JSON or CSV
- Automatic backups
- Ensuring data consistency on startup and shutdown
"""

import json
import os
from datetime import datetime
from typing import Tuple, List

# constant filepath's name 
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.json")
TXNS_FILE = os.path.join(DATA_DIR, "transactions.json")


# build ensure_data_files() => for check if data/ or two files of json don't exist.
def ensure_data_files() ->None:

    """Ensure the data directory and base JSON files exist.
    If the files do not exist, create them with an empty JSON list []"""

    os.makedirs(DATA_DIR, exist_ok=True)
    
    for path in (USERS_FILE, TXNS_FILE):
        if not os.path.exists(path):

           # write a valid empty JSON array
           try:
               with open(path, "w", encoding="utf-8") as f:
                   json.dump([], f, indent=2)
           except OSError as e:
               # If creating file fails, raise with a readable message
                raise RuntimeError(f"Failed to create data file{path}: {e}")
               
#build load_data() to read both files and return (users, transactions) lists. Handle JSON errors and fallback safely.
def load_data() -> Tuple[List[dict], List[dict]]:
    """
    Load and return (users, transactions) from JSON files.
    If files are missing or corrupted, returns two empty lists.
    """
    ensure_data_files()
    try:
        with open(USERS_FILE, "r", encoding="UTF-8") as uf:
            users = json.load(uf)
        with open(TXNS_FILE, "r", encoding="utf-8") as tf:
            transactions = json.load(tf)

        # Basic sanity: ensure lists
        if not isinstance(users, list):
            raise ValueError("users.json does not contain a list")
        if not isinstance(transactions, list):
            raise ValueError("transactions.json does not contain a list")
        return users, transactions
    except (OSError, json.JSONDecodeError, ValueError) as e:
        # Print friendly message and return empty stores (caller should handle)
        print(f"[data_manager] Warning: failed to load data ({e}). Starting with empty data.")
        return [], []
    

# build save_data() when saving, create a timestamped backup of current files, then write new data.
def save_data(users: List[dict], transactions: List[dict]) -> None:
    """
    Save users and transactions to JSON files.
    Creates timestamped backups of existing files before writing.
    Writes atomically by writing to a temporary file then replacing the original.
    """
    ensure_data_files()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # backup current files if they exist
    for file_path in (USERS_FILE, TXNS_FILE):
        if os.path.exists(file_path):
            try:
                backup_path = f"{file_path}.bak_{ts}"
                os.replace(file_path, backup_path)
            except OSError as e:
                # If backup fails, warn but continue (you can change to raise)
                print(f"[data_manager] Warning: could not create backup {backup_path}: {e}")

    # Now write new files atomically (to tmp then replace)
    try:
        # users
        tmp_users = f"{USERS_FILE}.tmp"
        with open(tmp_users, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        os.replace(tmp_users, USERS_FILE)

        # transactions
        tmp_tx = f"{TXNS_FILE}.tmp"
        with open(tmp_tx, "w", encoding="utf-8") as f:
            json.dump(transactions, f, indent=2, ensure_ascii=False)
        os.replace(tmp_tx, TXNS_FILE)
    except OSError as e:
        # If writing fails, you might want to restore backups or alert the user
        raise RuntimeError(f"Failed to save data files: {e}")
