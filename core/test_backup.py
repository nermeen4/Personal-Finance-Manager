from data_manager import (
    load_users, save_users,
    load_transactions, save_transactions,
    auto_save, shutdown_save,
    backup_all
)
import time
import os

print("\n=== Test: Personal Finance Data Manager ===")

# Step 1 — Prepare test data
users = [
    {"user_id": "U001", "name": "Nermeen", "password": "1234"},
    {"user_id": "U002", "name": "Mohamed", "password": "abcd"}
]

transactions = [
    {"transaction_id": "T001", "user_id": "U001", "type": "expense", "amount": 50.0, "category": "Food", "date": "2025-10-21"},
    {"transaction_id": "T002", "user_id": "U002", "type": "income", "amount": 300.0, "category": "Salary", "date": "2025-10-21"}
]

# Step 2 — Test saving
print("\n[TEST] Saving users and transactions...")
save_users(users)
save_transactions(transactions)

# Step 3 — Test loading
print("\n[TEST] Loading data back...")
loaded_users = load_users()
loaded_txns = load_transactions()
print("Loaded users:", loaded_users)
print("Loaded transactions:", loaded_txns)

# Step 4 — Test auto-save (force mode)
print("\n[TEST] Testing auto-save (forced)...")
auto_save(loaded_users, loaded_txns, force=True)

# Step 5 — Wait a few seconds, then test periodic auto-save
print("\n[TEST] Waiting to test timed auto-save...")
time.sleep(2)  # wait a bit for readability
auto_save(loaded_users, loaded_txns)  # normal (will skip if interval < 60s)

# Step 6 — Test backup creation manually
print("\n[TEST] Creating timestamped backup manually...")
backup_all()

# Step 7 — Test shutdown save (simulates program exit)
print("\n[TEST] Testing shutdown save...")
shutdown_save(loaded_users, loaded_txns)

print("\n✅ All tests completed!")
