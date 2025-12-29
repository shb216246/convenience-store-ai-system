"""
편의점 AI 시스템 도구 모음
"""
from .inventory_tools import (
    get_current_inventory,
    get_low_stock_items,
    get_expiring_products,
    calculate_stock_turnover,
    update_inventory
)

from .sales_tools import (
    get_sales_data,
    analyze_sales_pattern,
    get_trending_products,
    predict_daily_sales,
    analyze_sales_correlation
)

from .weather_tools import (
    get_weather_forecast,
    analyze_weather_impact,
    get_weather_based_recommendations,
    check_special_events
)

from .order_tools import (
    create_order,
    calculate_order_cost,
    optimize_order_quantity,
    get_order_history,
    validate_order
)

__all__ = [
    # Inventory tools
    "get_current_inventory",
    "get_low_stock_items",
    "get_expiring_products",
    "calculate_stock_turnover",
    "update_inventory",
    
    # Sales tools
    "get_sales_data",
    "analyze_sales_pattern",
    "get_trending_products",
    "predict_daily_sales",
    "analyze_sales_correlation",
    
    # Weather tools
    "get_weather_forecast",
    "analyze_weather_impact",
    "get_weather_based_recommendations",
    "check_special_events",
    
    # Order tools
    "create_order",
    "calculate_order_cost",
    "optimize_order_quantity",
    "get_order_history",
    "validate_order",
]
