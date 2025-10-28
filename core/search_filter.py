"""
search_filter.py

Utilities for filtering, searching, sorting transaction lists.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

DATE_FMT = "%Y-%m-%d"


# ✅ Safe date parsing
def parse_date_safe(s: Optional[str]) -> Optional[date]:
    """Parse YYYY-MM-DD into date, None if invalid."""
    if not s:
        return None
    try:
        return datetime.strptime(s, DATE_FMT).date()
    except Exception:
        return None


# ✅ Safe Decimal conversion
def safe_amount(value: Any) -> Decimal:
    """Convert to Decimal safely, fallback to 0.00."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0.00")


# ✅ Money rounding: Uniform system-wide rule
def round_money(d: Decimal) -> Decimal:
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ✅ Extract transaction date uniformly
def _txn_date(txn: Dict[str, Any]) -> Optional[date]:
    return parse_date_safe(txn.get("date"))


# ========================= 🔹 FILTERING 🔹 ========================= #

def filter_by_date_range(
    transactions: List[Dict[str, Any]],
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Filter by date range [start_date, end_date]."""
    start = parse_date_safe(start_date)
    end = parse_date_safe(end_date)

    return [
        tx for tx in transactions
        if _txn_date(tx) is not None
        and (start is None or _txn_date(tx) >= start)
        and (end is None or _txn_date(tx) <= end)
    ]


def filter_by_category(transactions: List[Dict[str, Any]], category: Optional[str]) -> List[Dict[str, Any]]:
    """Exact match category filter."""
    if not category:
        return list(transactions)
    category = category.strip().lower()

    return [
        tx for tx in transactions
        if str(tx.get("category", "")).strip().lower() == category
    ]


def filter_by_amount_range(
    transactions: List[Dict[str, Any]],
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None
) -> List[Dict[str, Any]]:
    """Filter by amount boundaries."""
    return [
        tx for tx in transactions
        if ((min_amount is None or safe_amount(tx.get("amount")) >= min_amount)
            and (max_amount is None or safe_amount(tx.get("amount")) <= max_amount))
    ]


# ========================= 🔹 SEARCH 🔹 ========================= #

def search_transactions(transactions: List[Dict[str, Any]], keyword: Optional[str]) -> List[Dict[str, Any]]:
    """Search keyword in description or category."""
    if not keyword:
        return transactions
    keyword = keyword.lower()

    return [
        tx for tx in transactions
        if keyword in str(tx.get("description", "")).lower()
        or keyword in str(tx.get("category", "")).lower()
    ]


# ========================= 🔹 SORTING 🔹 ========================= #

def sort_transactions(
    transactions: List[Dict[str, Any]],
    key: str = "date",
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """Sort transactions (fallback safe for missing values)."""
    try:
        if key == "date":
            return sorted(transactions, key=_txn_date, reverse=reverse)
        if key == "amount":
            return sorted(transactions, key=lambda tx: safe_amount(tx.get("amount")), reverse=reverse)
        if key == "category":
            return sorted(transactions, key=lambda tx: (tx.get("category") or "").lower(), reverse=reverse)
        if key == "type":
            return sorted(transactions, key=lambda tx: (tx.get("type") or "").lower(), reverse=reverse)
    except Exception:
        pass

    return transactions


# ========================= 🔹 MASTER FILTER PIPELINE 🔹 ========================= #

def apply_filters(
    transactions: List[Dict[str, Any]], *,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    keyword: Optional[str] = None,
    sort_by: str = "date",
    reverse: bool = False
) -> List[Dict[str, Any]]:
    """Chain all filters and sorting in correct order."""
    txns = filter_by_date_range(transactions, start_date, end_date)
    txns = filter_by_category(txns, category)
    txns = filter_by_amount_range(txns, min_amount, max_amount)
    txns = search_transactions(txns, keyword)
    return sort_transactions(txns, key=sort_by, reverse=reverse)
