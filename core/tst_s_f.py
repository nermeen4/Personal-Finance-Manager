# test_search_filter.py
from data_manager import save_transactions, load_transactions
from search_filter import apply_filters

sample = [
    {"transaction_id": "t1", "user_id": "U1", "type": "income", "amount": "1000.00", "category": "Salary", "date": "2025-08-01", "description": "August salary"},
    {"transaction_id": "t2", "user_id": "U1", "type": "expense", "amount": "120.50", "category": "Food", "date": "2025-08-02", "description": "Lunch with friends"},
    {"transaction_id": "t3", "user_id": "U1", "type": "expense", "amount": "15", "category": "Coffee", "date": "2025-07-30", "description": "Morning coffee"},
    {"transaction_id": "t4", "user_id": "U1", "type": "expense", "amount": "300", "category": "Rent", "date": "2025-08-01", "description": "Monthly rent"},
]

save_transactions(sample)
txns = load_transactions()

results = apply_filters(txns, category="Food", min_amount=10, max_amount=200, sort_by="amount", reverse=False)
print("Filtered results:")
for r in results:
    print(r)
