"""
Statistics API
Real-time statistics endpoints for dashboard
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db

router = APIRouter(prefix="/api/stats", tags=["statistics"])


@router.get("/summary")
async def get_summary_stats() -> Dict:
    """대시보드 요약 통계"""
    try:
        db = get_db()
        
        # 오늘 매출
        today_sales_query = """
            SELECT COALESCE(SUM(quantity_sold * sale_price), 0) as total_sales
            FROM sales
            WHERE sale_date = CURDATE()
        """
        today_sales = db.fetch_one(today_sales_query)
        
        # 어제 매출 (비교용)
        yesterday_sales_query = """
            SELECT COALESCE(SUM(quantity_sold * sale_price), 0) as total_sales
            FROM sales
            WHERE sale_date = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        """
        yesterday_sales = db.fetch_one(yesterday_sales_query)
        
        # 발주 대기
        pending_orders_query = """
            SELECT COUNT(*) as count
            FROM orders
            WHERE status = 'pending'
        """
        pending_orders = db.fetch_one(pending_orders_query)
        
        # 재고 부족 알림
        low_stock_query = """
            SELECT COUNT(*) as count
            FROM inventory
            WHERE quantity < 20
        """
        low_stock = db.fetch_one(low_stock_query)
        
        # 변화율 계산
        today_amount = float(today_sales['total_sales']) if today_sales else 0
        yesterday_amount = float(yesterday_sales['total_sales']) if yesterday_sales else 1
        sales_change = ((today_amount - yesterday_amount) / yesterday_amount * 100) if yesterday_amount > 0 else 0
        
        return {
            "today_sales": {
                "value": int(today_amount),
                "change": round(sales_change, 1)
            },
            "pending_orders": {
                "value": pending_orders['count'] if pending_orders else 0,
                "change": 0
            },
            "low_stock_alerts": {
                "value": low_stock['count'] if low_stock else 0,
                "change": 0
            },
            "ai_processing_time": {
                "value": 1.2,
                "change": -0.3
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales/trend")
async def get_sales_trend(days: int = 7) -> List[Dict]:
    """판매 트렌드 데이터"""
    try:
        db = get_db()
        
        query = """
            SELECT 
                DATE_FORMAT(sale_date, '%m/%d') as date,
                SUM(quantity_sold * sale_price) as sales,
                SUM(quantity_sold) as orders
            FROM sales
            WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY sale_date
            ORDER BY sale_date ASC
        """
        results = db.fetch_all(query, (days,))
        
        return [
            {
                "date": row['date'],
                "sales": int(row['sales']) if row['sales'] else 0,
                "orders": int(row['orders']) if row['orders'] else 0
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products/top")
async def get_top_products(limit: int = 5) -> List[Dict]:
    """인기 상품 TOP N"""
    try:
        db = get_db()
        
        query = """
            SELECT 
                s.product_name,
                SUM(s.quantity_sold) as total_sales,
                i.quantity as current_stock,
                (
                    SELECT SUM(quantity_sold) 
                    FROM sales 
                    WHERE product_name = s.product_name 
                    AND sale_date >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
                    AND sale_date < DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                ) as prev_week_sales
            FROM sales s
            LEFT JOIN inventory i ON s.product_name = i.product_name
            WHERE s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY s.product_name, i.quantity
            ORDER BY total_sales DESC
            LIMIT %s
        """
        results = db.fetch_all(query, (limit,))
        
        products = []
        for row in results:
            current_sales = int(row['total_sales']) if row['total_sales'] else 0
            prev_sales = int(row['prev_week_sales']) if row['prev_week_sales'] else 1
            trend = ((current_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
            
            products.append({
                "name": row['product_name'],
                "sales": current_sales,
                "trend": round(trend, 1),
                "stock": int(row['current_stock']) if row['current_stock'] else 0
            })
        
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/category/distribution")
async def get_category_distribution() -> List[Dict]:
    """카테고리별 매출 분포"""
    try:
        db = get_db()
        
        query = """
            SELECT 
                i.category as name,
                SUM(s.quantity_sold * s.sale_price) as value
            FROM sales s
            JOIN inventory i ON s.product_name = i.product_name
            WHERE s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY i.category
            ORDER BY value DESC
        """
        results = db.fetch_all(query)
        
        # 색상 매핑
        colors = ['#3b82f6', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
        
        return [
            {
                "name": row['name'] if row['name'] else '기타',
                "value": int(row['value']) if row['value'] else 0,
                "color": colors[i % len(colors)]
            }
            for i, row in enumerate(results)
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/alerts")
async def get_alerts() -> List[Dict]:
    """재고 부족 알림"""
    try:
        db = get_db()
        
        query = """
            SELECT 
                product_name,
                category,
                quantity,
                expiry_date,
                DATEDIFF(expiry_date, CURDATE()) as days_until_expiry
            FROM inventory
            WHERE quantity < 20 OR expiry_date <= DATE_ADD(CURDATE(), INTERVAL 7 DAY)
            ORDER BY quantity ASC, expiry_date ASC
        """
        results = db.fetch_all(query)
        
        alerts = []
        for row in results:
            if row['quantity'] < 20:
                alerts.append({
                    "type": "low_stock",
                    "severity": "warning" if row['quantity'] < 10 else "info",
                    "product": row['product_name'],
                    "message": f"{row['product_name']} 재고 부족 ({row['quantity']}개)",
                    "quantity": row['quantity']
                })
            
            if row['days_until_expiry'] is not None and row['days_until_expiry'] <= 7:
                alerts.append({
                    "type": "expiry",
                    "severity": "error" if row['days_until_expiry'] <= 3 else "warning",
                    "product": row['product_name'],
                    "message": f"{row['product_name']} 유통기한 임박 ({row['days_until_expiry']}일)",
                    "days_left": row['days_until_expiry']
                })
        
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
