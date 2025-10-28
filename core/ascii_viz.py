"""
ascii_viz.py

ASCII visualization utilities for displaying financial reports directly in terminal.

Functions:
- draw_bar(label, value, max_value, width=40)
- category_barchart(category_data)
- monthly_barchart(monthly_data)
- trend_chart(trends_data)
"""


from typing import Dict
from decimal import Decimal, InvalidOperation
from core.search_filter import round_money



# ✅ Safe conversion for numeric visualization
def _to_decimal(value) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0.00")
    

def draw_bar(label: str, value, max_value: Decimal, width: int = 50) -> str:
    """
    Render bar as: Category     | ███████████ 1200.00
    - Safe Decimal conversion
    - Protects against zero max
    """
    value = _to_decimal(value)
    max_value = _to_decimal(max_value)

    if max_value <= 0:
        max_value = Decimal("1.00")

    ratio = value / max_value
    bar_len = int(ratio * width)
    bar = "█" * bar_len

    return f"{label:<15.15} | {bar} {value:.2f}"


# ========================== 📊 CATEGORY CHART ========================== #

def category_barchart(category_data: Dict[str, Decimal]) -> None:
    if not category_data:
        print("⚠️ No category data to display.")
        return

    max_value = max(category_data.values())
    print("\n📂 CATEGORY BREAKDOWN (Expenses)\n" + "-" * 60)

    for category, amount in sorted(category_data.items(), key=lambda x: x[1], reverse=True):
        print(draw_bar(category, amount, max_value))

    print("-" * 60 + "\n")


# ======================== 📅 MONTHLY NET BAR CHART ===================== #

def monthly_barchart(monthly_data: Dict[str, Dict[str, Decimal]]) -> None:
    if not monthly_data:
        print("⚠️ No monthly data to display.")
        return
    
    print("\n📅 Monthly Net Summary\n" + "-" * 60)

    # Ensure net values exist and rounded
    for m, vals in monthly_data.items():
        vals["net"] = round_money(vals.get("net", vals["income"] - vals["expense"]))

    max_net = max(vals["net"] for vals in monthly_data.values())

    for month in sorted(monthly_data.keys()):
        print(draw_bar(month, monthly_data[month]["net"], max_net))

    print("-" * 60 + "\n")


# ========================= 📈 TREND CHART ============================= #
def trend_chart(trends_data: Dict[str, Decimal]) -> None:
    if not trends_data:
        print("⚠️ No trend data available.")
        return

    max_val = max(trends_data.values())

    print("\n📈 Expense Trend\n" + "-" * 60)

    for month in sorted(trends_data.keys()):
        print(draw_bar(month, round_money(trends_data[month]), max_val))

    print("-" * 60 + "\n")