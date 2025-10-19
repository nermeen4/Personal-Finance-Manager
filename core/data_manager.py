# ...existing code...
"""
data_manager.py - Handles data persistence and backup.

Responsible for:
- Saving/loading user and transaction data to/from JSON or CSV
- Automatic backups
- Ensuring data consistency on startup and shutdown
"""

import json
import os
import shutil
import glob
from datetime import datetime
from typing import Tuple, List, Optional

# constant filepath's name 
DATA_DIR = "data"
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
TXNS_FILE = os.path.join(DATA_DIR, "transactions.json")
_BACKUP_KEEP = 5  # number of backups to keep per file


def ensure_data_files() -> None:
    """Ensure the data directory and base JSON files exist.
    If the files do not exist, create them with an empty JSON list []"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for path in (USERS_FILE, TXNS_FILE):
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump([], f, indent=2)
            except OSError as e:
                raise RuntimeError(f"Failed to create data file {path}: {e}")

###########################backup parts ###########################
def _backup_filename(file_path: str, ts: Optional[str] = None) -> str:
    base = os.path.basename(file_path)
    ts = ts or datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(BACKUP_DIR, f"{base}.bak_{ts}")


def _rotate_backups(file_path: str, keep: int = _BACKUP_KEEP) -> None:
    """Keep only the most recent `keep` backups for the given file (by filename prefix)."""
    base = os.path.basename(file_path)
    pattern = os.path.join(BACKUP_DIR, f"{base}.bak_*")
    files = sorted(glob.glob(pattern))
    # older first; remove until length == keep
    while len(files) > keep:
        old = files.pop(0)
        try:
            os.remove(old)
        except OSError:
            pass


def _make_backup(file_path: str, keep: int = _BACKUP_KEEP) -> Optional[str]:
    """Create a timestamped copy of file_path into BACKUP_DIR. Return backup path or None."""
    if not os.path.exists(file_path):
        return None
    try:
        backup_path = _backup_filename(file_path)
        shutil.copy2(file_path, backup_path)
        _rotate_backups(file_path, keep=keep)
        return backup_path
    except OSError as e:
        # warn and continue; caller can decide how to handle
        print(f"[data_manager] Warning: could not create backup for {file_path}: {e}")
        return None


def _latest_backup_for(file_path: str) -> Optional[str]:
    base = os.path.basename(file_path)
    pattern = os.path.join(BACKUP_DIR, f"{base}.bak_*")
    files = sorted(glob.glob(pattern), reverse=True)
    return files[0] if files else None


def restore_latest_backup(file_path: str) -> bool:
    """Restore the latest available backup for file_path -> file_path. Returns True if restored."""
    latest = _latest_backup_for(file_path)
    if not latest:
        return False
    try:
        shutil.copy2(latest, file_path)
        return True
    except OSError:
        return False

####################save/load data parts ####################
def load_data() -> Tuple[List[dict], List[dict]]:
    """
    Load and return (users, transactions) from JSON files.
    If files are missing or corrupted, returns two empty lists.
    """
    ensure_data_files()
    try:
        with open(USERS_FILE, "r", encoding="UTF-8") as uf:
            users = json.load(uf)
        with open(TXNS_FILE, "r", encoding="UTF-8") as tf:
            transactions = json.load(tf)

        # Basic sanity: ensure lists
        if not isinstance(users, list):
            raise ValueError("users.json does not contain a list")
        if not isinstance(transactions, list):
            raise ValueError("transactions.json does not contain a list")
        return users, transactions
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"[data_manager] Warning: failed to load data ({e}). Attempting restore from backups...")
        # Try to restore from latest backups (users then transactions)
        restored_users = restored_txns = False
        try:
            restored_users = restore_latest_backup(USERS_FILE)
            restored_txns = restore_latest_backup(TXNS_FILE)
        except Exception:
            restored_users = restored_txns = False

        if restored_users or restored_txns:
            # Try loading again after restore
            try:
                with open(USERS_FILE, "r", encoding="UTF-8") as uf:
                    users = json.load(uf)
                with open(TXNS_FILE, "r", encoding="UTF-8") as tf:
                    transactions = json.load(tf)
                if not isinstance(users, list) or not isinstance(transactions, list):
                    raise ValueError("Restored files invalid")
                print("[data_manager] Restored data from backups.")
                return users, transactions
            except Exception as e2:
                print(f"[data_manager] Restore failed ({e2}). Starting with empty data.")
                return [], []
        else:
            return [], []


def save_data(users: List[dict], transactions: List[dict]) -> None:
    """
    Save users and transactions to JSON files.
    Creates timestamped backups of existing files before writing.
    Writes atomically by writing to a temporary file then replacing the original.
    On write failure, attempts to restore the latest backups.
    """
    ensure_data_files()

    # create backups (copy, not move) so originals remain until new files succeed
    _make_backup(USERS_FILE)
    _make_backup(TXNS_FILE)

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
        # Attempt to restore latest backups if writing failed
        print(f"[data_manager] Error saving data ({e}). Attempting to restore backups...")
        users_restored = restore_latest_backup(USERS_FILE)
        txns_restored = restore_latest_backup(TXNS_FILE)
        if users_restored or txns_restored:
            print("[data_manager] Restore from backups completed (partial ok).")
        else:
            print("[data_manager] Failed to restore backups; data files may be inconsistent.")
        raise RuntimeError(f"Failed to save data files: {e}")


# --- New: save/load users only (no transactions) ---
def load_users() -> List[dict]:
    """
    Load and return users list from USERS_FILE.
    Returns [] on error (prints a warning).
    """
    ensure_data_files()
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as uf:
            users = json.load(uf)
        if not isinstance(users, list):
            raise ValueError("users.json does not contain a list")
        return users
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"[data_manager] Warning: failed to load users ({e}). Attempting restore from backup...")
        if restore_latest_backup(USERS_FILE):
            try:
                with open(USERS_FILE, "r", encoding="utf-8") as uf:
                    users = json.load(uf)
                if isinstance(users, list):
                    return users
            except Exception:
                pass
        print(f"[data_manager] Warning: failed to load users after restore. Returning empty list.")
        return []


def save_users(users: List[dict]) -> None:
    """
    Save users list to USERS_FILE only.
    Creates a timestamped backup of users.json, writes atomically.
    """
    ensure_data_files()
    _make_backup(USERS_FILE)

    try:
        tmp_users = f"{USERS_FILE}.tmp"
        with open(tmp_users, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        os.replace(tmp_users, USERS_FILE)
    except OSError as e:
        print(f"[data_manager] Error saving users ({e}). Attempting to restore backup...")
        restore_latest_backup(USERS_FILE)
        raise RuntimeError(f"Failed to save users file: {e}")
# ...existing code...