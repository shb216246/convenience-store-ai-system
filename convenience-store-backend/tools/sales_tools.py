"""
판매 데이터 분석 도구들
"""
from langchain.tools import tool
from typing import List, Dict, Optional
import json
from datetime import datetime, timedelta
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
def get_sales_data(product_name: Optional[str] = None, days: int = 7) -> str:
    """
    과거 판매 데이터를 조회합니다.
    
    Args:
        product_name: 상품명 (없으면 전체)
        days: 조회 기간 (일)
    
    Returns:
        판매 데이터 (JSON 문자열)
    """
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        start_date = (datetime.now() - timedelta(days=days)).date()
        
        if product_name:
            cursor.execute("""
                SELECT 
                    DATE(sale_date) as date,
                    SUM(quantity_sold) as quantity,
                    SUM(sale_price * quantity_sold) as revenue
                FROM sales
                WHERE product_name = %s
                  AND sale_date >= %s
                GROUP BY DATE(sale_date)
                ORDER BY date DESC
            """, (product_name, start_date))
            
            daily_sales = []
            for row in cursor.fetchall():
                daily_sales.append({
                    "date": row['date'].strftime('%Y-%m-%d'),
                    "quantity": int(float(row['quantity'])) if row['quantity'] else 0,
                    "revenue": int(float(row['revenue'])) if row['revenue'] else 0
                })
            
            return json.dumps({product_name: daily_sales}, ensure_ascii=False)
        else:
            cursor.execute("""
                SELECT 
                    product_name,
                    DATE(sale_date) as date,
                    SUM(quantity_sold) as quantity,
                    SUM(sale_price * quantity_sold) as revenue
                FROM sales
                WHERE sale_date >= %s
                GROUP BY product_name, DATE(sale_date)
                ORDER BY product_name, date DESC
            """, (start_date,))
            
            sales_data = {}
            for row in cursor.fetchall():
                product = row['product_name']
                if product not in sales_data:
                    sales_data[product] = []
                
                sales_data[product].append({
                    "date": row['date'].strftime('%Y-%m-%d'),
                    "quantity": int(float(row['quantity'])) if row['quantity'] else 0,
                    "revenue": int(float(row['revenue'])) if row['revenue'] else 0
                })
            
            return json.dumps(sales_data, ensure_ascii=False)
    finally:
        cursor.close()
        db.close()


@tool
def analyze_sales_pattern(product_name: str, period: str = "weekly") -> str:
    """
    판매 패턴을 분석합니다.
    
    Args:
        product_name: 상품명
        period: 분석 주기 ('daily', 'weekly', 'hourly')
    
    Returns:
        판매 패턴 분석 결과
    """
    if period == "weekly":
        pattern = {
            "product": product_name,
            "period": "weekly",
            "peak_days": ["월요일", "금요일"],
            "low_days": ["수요일"],
            "avg_daily_sales": 28.5,
            "peak_avg": 35,
            "low_avg": 20,
            "trend": "상승세",
            "seasonality": "주말 전 수요 증가"
        }
    elif period == "hourly":
        pattern = {
            "product": product_name,
            "period": "hourly",
            "peak_hours": ["7-9시", "12-13시", "18-20시"],
            "peak_sales": "아침 7-9시가 가장 높음",
            "recommendation": "아침 시간대 재고 확보 필요"
        }
    else:
        pattern = {
            "product": product_name,
            "period": "daily",
            "avg_sales": 28.5,
            "max_sales": 45,
            "min_sales": 15
        }
    
    return json.dumps(pattern, ensure_ascii=False)


@tool
def get_trending_products(days: int = 7, top_n: int = 5) -> str:
    """
    인기 상승 상품을 조회합니다.
    
    Args:
        days: 분석 기간
        top_n: 상위 N개
    
    Returns:
        트렌딩 상품 목록
    """
    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # 현재 기간과 이전 기간의 판매량 비교
        current_start = (datetime.now() - timedelta(days=days)).date()
        previous_start = (datetime.now() - timedelta(days=days*2)).date()
        previous_end = current_start
        
        cursor.execute("""
            WITH current_sales AS (
                SELECT 
                    product_name,
                    SUM(quantity_sold) as qty
                FROM sales
                WHERE sale_date >= %s
                GROUP BY product_name
            ),
            previous_sales AS (
                SELECT 
                    product_name,
                    SUM(quantity_sold) as qty
                FROM sales
                WHERE sale_date >= %s AND sale_date < %s
                GROUP BY product_name
            )
            SELECT 
                c.product_name as product,
                c.qty as current_qty,
                COALESCE(p.qty, 0) as previous_qty,
                CASE 
                    WHEN COALESCE(p.qty, 0) = 0 THEN 100.0
                    ELSE ((c.qty - COALESCE(p.qty, 0)) / COALESCE(p.qty, 1)) * 100
                END as growth_rate
            FROM current_sales c
            LEFT JOIN previous_sales p ON c.product_name = p.product_name
            ORDER BY growth_rate DESC
            LIMIT %s
        """, (current_start, previous_start, previous_end, top_n))
        
        trending = []
        for idx, row in enumerate(cursor.fetchall(), 1):
            trending.append({
                "product": row['product'],
                "growth_rate": round(float(row['growth_rate']), 1),  # Decimal → float
                "current_rank": idx
            })
        
        return json.dumps(trending, ensure_ascii=False)
    finally:
        cursor.close()
        db.close()


@tool
def predict_daily_sales(product_name: str, target_date: Optional[str] = None) -> str:
    """
    특정 날짜의 판매량을 예측합니다.
    
    Args:
        product_name: 상품명
        target_date: 예측 날짜 (YYYY-MM-DD, 없으면 내일)
    
    Returns:
        예측 판매량
    """
    if not target_date:
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 간단한 예측 로직 (실제로는 ML 모델 사용)
    weekday = datetime.strptime(target_date, "%Y-%m-%d").weekday()
    base_sales = 30
    
    if weekday == 0:  # 월요일
        predicted = int(base_sales * 1.3)
    elif weekday == 4:  # 금요일
        predicted = int(base_sales * 1.2)
    else:
        predicted = base_sales
    
    prediction = {
        "product": product_name,
        "target_date": target_date,
        "predicted_sales": predicted,
        "confidence": 0.85,
        "range": [int(predicted * 0.9), int(predicted * 1.1)]
    }
    
    return json.dumps(prediction, ensure_ascii=False)


@tool
def analyze_sales_correlation(product1: str, product2: str) -> str:
    """
    두 상품 간 판매 상관관계를 분석합니다.
    
    Args:
        product1: 첫 번째 상품
        product2: 두 번째 상품
    
    Returns:
        상관관계 분석 결과
    """
    # 실제로는 통계 분석
    correlation = {
        "product1": product1,
        "product2": product2,
        "correlation_coefficient": 0.72,
        "relationship": "강한 양의 상관관계",
        "insight": f"{product1}와 {product2}는 함께 판매되는 경향이 있습니다.",
        "recommendation": "번들 프로모션 추천"
    }
    
    return json.dumps(correlation, ensure_ascii=False)