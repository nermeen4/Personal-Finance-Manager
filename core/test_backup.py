from data_manager import load_data, save_data
import os
import json

print("🔍 Testing backup system...\n")

# 1. Load existing data (creates files if missing)
users, txns = load_data()

# 2. Simulate new data
users.append({"id": len(users)+1, "name": "Backup Tester"})
txns.append({"id": len(txns)+1, "user_id": len(users), "amount": 50, "type": "deposit"})

# 3. Save the data (should trigger backup creation)
save_data(users, txns)

# 4. List all backups created
backup_dir = os.path.join("data", "backups")
backups = [f for f in os.listdir(backup_dir) if f.endswith(".json") or ".bak_" in f]

print("✅ Data saved successfully!")
print(f"📁 Backup files found in {backup_dir}:")
for b in backups:
    print(" -", b)

# 5. Verify JSON content
print("\n📘 Current users.json content:")
with open("data/users.json", "r", encoding="utf-8") as f:
    print(json.dumps(json.load(f), indent=2, ensure_ascii=False))
