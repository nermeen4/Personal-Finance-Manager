"""
search_filter.py

Provides utilities to search and filter transaction lists.

Functions:
- parse_date_safe
- _safe_amount (Decimal)
- filter_by_date_range(transactions, start_date, end_date)
- filter_by_category(transactions, category)
- filter_by_amount_range(transactions, min_amount, max_amount)
- search_transactions(transactions, keyword)
- sort_transactions(transactions, key="date", reverse=False)
- apply_filters(transactions, *, start_date=None, end_date=None, category=None,
                min_amount=None, max_amount=None, keyword=None, sort_by="date", reverse=False)
"""


from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


DATE_FMT = "%Y-%m-%d"


# Helper function to parse dates safely
def parse_date_safe(s: Optional[str]) -> Optional[datetime.date]:
    """Parse YYYY-MM-DD to date object, return None on failure or if s is falsy."""
    if not s:
        return  None
    try:
        return datetime.strptime(s, DATE_FMT).date()
    except Exception:
        return None

# Helper function to safely convert to Decimal
def safe_amount(value) -> Decimal:
      """Convert numeric-like value to Decimal safely. Returns Decimal('0.00') on failure."""
      try:
          return Decimal(str(value))
      except (InvalidOperation, ValueError, TypeError):
            return Decimal('0.00')
      

# Helper function to get transaction date
def _txn_date(txn: Dict[str, Any]) -> Optional[datetime.date]:
    """Return date object for transaction or None."""
    date_str = txn.get("date")
    return parse_date_safe(date_str)

 # ROUND_HALF_UP helper
def round_money(d: Decimal) -> Decimal:
     """Round Decimal to 2 decimal places using ROUND_HALF_UP."""
     return d.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    
# Filter functions

def filter_by_date_range(transactions: List[Dict[str, Any]],
                         start_date: Optional[str]= None,
                         end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Filter transactions by date range [start_date, end_date]."""
    start = parse_date_safe(start_date)
    end = parse_date_safe(end_date)
    filtered = []
    for txn in transactions:
        txn_date = _txn_date(txn)
        if txn_date is None:
            continue
        if (start is None or txn_date >= start) and (end is None or txn_date <= end):
            filtered.append(txn)
    return filtered

def filter_by_category(transactions: List[Dict[str, Any]], category: Optional[str]) -> List[Dict[str, Any]]:
    """Filter transactions by category."""
    if not category:
        return list(transactions)
    category = category.strip().lower()
    return [txn for txn in transactions if (txn.get("category") or "").strip().lower() == category]


def filter_by_amount_range(transactions: List[Dict[str, Any]],
                           min_amount: Optional[Decimal] = None,
                           max_amount: Optional[Decimal] = None) -> List[Dict[str, Any]]:
    """Filter transactions by amount range [min_amount, max_amount]."""
    filtered = []
    for txn in transactions:
        amount = safe_amount(txn.get("amount"))
        if (min_amount is None or amount >= min_amount) and (max_amount is None or amount <= max_amount):
            filtered.append(txn)
    return filtered

# Search function
def search_transactions(transactions: List[Dict[str, Any]], keyword: Optional[str]) -> List[Dict[str, Any]]:
    """Search transactions by keyword in description."""
    if not keyword:
        return transactions
    keyword_lower = keyword.lower()
    return [txn for txn in transactions if keyword_lower in str(txn.get("description", "")).lower()]

# Sort function
def sort_transactions(transactions: List[Dict[str, Any]], key: str = "date", reverse: bool = False) -> List[Dict[str, Any]]:
    """Sort transactions by specified key."""
    if key == "date":
        return sorted(transactions, key=_txn_date, reverse=reverse)
    elif key == "amount":
        return sorted(transactions, key=lambda txn: safe_amount(txn.get("amount")), reverse=reverse)
    elif key == "category":
        return sorted(transactions, key=lambda txn: (txn.get("category") or "").lower(), reverse=reverse)
    elif key == "type":
        return sorted(transactions, key=lambda txn: (txn.get("type") or "").lower(), reverse=reverse)
    else:
        return transactions
    

    
# Combined filter function
def apply_filters(transactions: List[Dict[str, Any]], *,
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  category: Optional[str] = None,
                  min_amount: Optional[Decimal] = None,
                  max_amount: Optional[Decimal] = None,
                  keyword: Optional[str] = None,
                  sort_by: str = "date",
                  reverse: bool = False) -> List[Dict[str, Any]]:
    """Apply multiple filters and sorting to transactions."""
    filtered_txns = filter_by_date_range(transactions, start_date, end_date)
    filtered_txns = filter_by_category(filtered_txns, category)
    filtered_txns = filter_by_amount_range(filtered_txns, min_amount, max_amount)
    filtered_txns = search_transactions(filtered_txns, keyword)
    sorted_txns = sort_transactions(filtered_txns, key=sort_by, reverse=reverse)
    return sorted_txns

