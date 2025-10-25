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
from decimal import Decimal


def draw_bar(label: str, value: Decimal, max_value: Decimal, width: int = 40) -> str:
    """Return a formatted bar like: label | ███████████ 1200.00"""
    if max_value <= 0:
        max_value = Decimal("1.00")
    ratio = Decimal(value / max_value)
    bar_len = int(ratio * width)
    bar = "█" * bar_len
    return f"{label:<12} | {bar} {value}"




def category_barchart(category_data: Dict[str, Decimal]) -> None:
    """Print a bar chart for category breakdown.""" 
    if not category_data:
        print("No category data to display.")
        return

    max_value = max(category_data.values())
    print("📂 CATEGORY BREAKDOWN (Bar Chart)")
    print("-" * 50)
    for category, amount in sorted(category_data.items(), key=lambda x: x[1], reverse=True):
        print(draw_bar(category, amount, max_value))
    print("-" * 50)
    print()




def monthly_barchart(monthly_data: Dict[str, Dict[str, Decimal]]) -> None:
    """Print a bar chart of net totals per month."""
    if not monthly_data:
        print("⚠️ No monthly data to display.")
        return

    print("\n📅 Monthly Spending Trend\n")
    max_net = max(v["net"] for v in monthly_data.values())

    # Sort months so they appear in order
    for month in sorted(monthly_data.keys()):
        net = monthly_data[month]["net"]
        print(draw_bar(month, net, max_net))



def trend_chart(trends_data: Dict[str, Decimal]) -> None:
    """Print trend chart for expenses over months."""
    if not trends_data:
        print("⚠️ No trend data available.")
        return

    max_val = max(trends_data.values())
    print("\n📈 Spending Trend\n")
    for month in sorted(trends_data.keys()):
        print(draw_bar(month, trends_data[month], max_val))