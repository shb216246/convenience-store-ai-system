"""
재고 관리 도구들
"""
from langchain.tools import tool
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import json
import os
import pymysql
from dotenv import load_dotenv

load_dotenv()


def get_db_connection():
    """DB 연결"""
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE", "store_order"),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


@tool
def get_current_inventory(product_name: Optional[str] = None) -> str:
    """
    현재 재고를 조회합니다.
    
    Args:
        product_name: 특정 상품명 (없으면 전체 조회)
    
    Returns:
        현재 재고 정보 (JSON 문자열)
    """
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        if product_name:
            cursor.execute("""
                SELECT product_name, quantity, safe_stock, max_stock, unit_price
                FROM inventory
                WHERE product_name = %s
            """, (product_name,))
            result = cursor.fetchone()
            
            if result:
                return json.dumps({
                    result['product_name']: {
                        "quantity": int(result['quantity']),
                        "safe_stock": int(result['safe_stock']),
                        "max_stock": int(result['max_stock'])
                    }
                }, ensure_ascii=False)
            else:
                return f"상품 '{product_name}'을 찾을 수 없습니다."
        else:
            cursor.execute("""
                SELECT product_name, quantity, safe_stock, max_stock
                FROM inventory
            """)
            results = cursor.fetchall()
            
            inventory_data = {}
            for row in results:
                inventory_data[row['product_name']] = {
                    "quantity": int(row['quantity']),
                    "safe_stock": int(row['safe_stock']),
                    "max_stock": int(row['max_stock'])
                }
            
            return json.dumps(inventory_data, ensure_ascii=False)
    finally:
        cursor.close()
        db.close()


@tool
def get_low_stock_items(threshold: float = 0.8) -> str:
    """
    재고가 부족한 상품 목록을 반환합니다.
    
    Args:
        threshold: 안전재고 대비 비율 (기본값: 0.8 = 80%)
    
    Returns:
        재고 부족 상품 목록
    """
    inventory = json.loads(get_current_inventory.invoke({}))
    low_stock = {}
    
    for product, data in inventory.items():
        ratio = data["quantity"] / data["safe_stock"]
        if ratio < threshold:
            low_stock[product] = {
                "current": data["quantity"],
                "safe_stock": data["safe_stock"],
                "shortage": data["safe_stock"] - data["quantity"],
                "ratio": round(ratio, 2)
            }
    
    if not low_stock:
        return "모든 상품의 재고가 충분합니다."
    
    return json.dumps(low_stock, ensure_ascii=False)


@tool
def get_expiring_products(days: int = 3) -> str:
    """
    곧 유통기한이 만료되는 상품 목록을 반환합니다.
    
    Args:
        days: 며칠 이내 만료 (기본값: 3일)
    
    Returns:
        유통기한 임박 상품 목록
    """
    # 실제로는 DB에서 유통기한 데이터 조회
    expiring = {
        "삼각김밥": {"quantity": 5, "expiry_date": "2024-12-15"},
        "도시락": {"quantity": 3, "expiry_date": "2024-12-14"},
        "우유": {"quantity": 4, "expiry_date": "2024-12-16"},
    }
    
    return json.dumps(expiring, ensure_ascii=False)


@tool
def calculate_stock_turnover(product_name: str, period_days: int = 7) -> str:
    """
    상품의 재고 회전율을 계산합니다.
    
    Args:
        product_name: 상품명
        period_days: 분석 기간 (일)
    
    Returns:
        재고 회전율 정보
    """
    # 실제로는 판매 데이터 기반 계산
    turnover_data = {
        "product": product_name,
        "period_days": period_days,
        "avg_daily_sales": 8.5,
        "avg_inventory": 15,
        "turnover_rate": round(8.5 * period_days / 15, 2),
        "days_of_supply": round(15 / 8.5, 1)
    }
    
    return json.dumps(turnover_data, ensure_ascii=False)


@tool
def update_inventory(product_name: str, quantity: int, action: str = "set") -> str:
    """
    재고를 업데이트합니다.
    
    Args:
        product_name: 상품명
        quantity: 수량
        action: 'set' (설정), 'add' (추가), 'subtract' (차감)
    
    Returns:
        업데이트 결과
    """
    # 실제로는 DB 업데이트
    result = {
        "product": product_name,
        "action": action,
        "quantity": quantity,
        "timestamp": datetime.now().isoformat(),
        "success": True
    }
    
    return json.dumps(result, ensure_ascii=False)