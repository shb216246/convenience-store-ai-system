"""
Order Workflow API
Order creation, approval, and management
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db

router = APIRouter(prefix="/api/orders", tags=["orders"])


class OrderItem(BaseModel):
    product: str
    quantity: int


class CreateOrderRequest(BaseModel):
    items: List[OrderItem]
    notes: Optional[str] = None


class OrderApprovalRequest(BaseModel):
    approved_by: str
    notes: Optional[str] = None


@router.post("/create")
async def create_order(request: CreateOrderRequest) -> Dict:
    """새 발주 생성"""
    try:
        db = get_db()
        
        order_ids = []
        total_cost = 0
        
        for item in request.items:
            # 상품 정보 조회
            product_query = "SELECT unit_price FROM inventory WHERE product_name = %s"
            product = db.fetch_one(product_query, (item.product,))
            
            if not product:
                raise HTTPException(status_code=404, detail=f"상품을 찾을 수 없습니다: {item.product}")
            
            unit_cost = float(product['unit_price'])
            item_total = unit_cost * item.quantity
            total_cost += item_total
            
            # 발주 생성
            order_query = """
                INSERT INTO orders (product_name, quantity_ordered, unit_cost, total_cost, 
                                   order_date, delivery_date, status)
                VALUES (%s, %s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'pending')
            """
            db.execute_query(order_query, (item.product, item.quantity, unit_cost, item_total))
            
            # 마지막 삽입 ID 가져오기
            last_id_query = "SELECT LAST_INSERT_ID() as id"
            result = db.fetch_one(last_id_query)
            order_ids.append(result['id'])
        
        return {
            "success": True,
            "order_ids": order_ids,
            "total_items": len(request.items),
            "total_cost": total_cost,
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending")
async def get_pending_orders() -> List[Dict]:
    """대기 중인 발주 목록"""
    try:
        db = get_db()
        
        query = """
            SELECT 
                id,
                product_name,
                quantity_ordered,
                unit_cost,
                total_cost,
                order_date,
                delivery_date,
                status
            FROM orders
            WHERE status = 'pending'
            ORDER BY order_date DESC, id DESC
        """
        results = db.fetch_all(query)
        
        return [
            {
                "id": row['id'],
                "product": row['product_name'],
                "quantity": row['quantity_ordered'],
                "unit_cost": float(row['unit_cost']),
                "total_cost": float(row['total_cost']),
                "order_date": str(row['order_date']),
                "delivery_date": str(row['delivery_date']),
                "status": row['status']
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/approve")
async def approve_order(order_id: int, request: OrderApprovalRequest) -> Dict:
    """발주 승인"""
    try:
        db = get_db()
        
        # 발주 상태 업데이트
        update_query = """
            UPDATE orders
            SET status = 'approved'
            WHERE id = %s
        """
        db.execute_query(update_query, (order_id,))
        
        # 승인 기록 저장 (chat_history 테이블 활용)
        log_query = """
            INSERT INTO chat_history (session_id, user_message, assistant_message)
            VALUES (%s, %s, %s)
        """
        db.execute_query(log_query, (
            f"order_approval_{order_id}",
            f"Order #{order_id} approved by {request.approved_by}",
            request.notes or "No notes"
        ))
        
        return {
            "success": True,
            "order_id": order_id,
            "status": "approved",
            "approved_by": request.approved_by,
            "approved_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{order_id}/reject")
async def reject_order(order_id: int, request: OrderApprovalRequest) -> Dict:
    """발주 거부"""
    try:
        db = get_db()
        
        # 발주 상태 업데이트
        update_query = """
            UPDATE orders
            SET status = 'rejected'
            WHERE id = %s
        """
        db.execute_query(update_query, (order_id,))
        
        # 거부 기록 저장
        log_query = """
            INSERT INTO chat_history (session_id, user_message, assistant_message)
            VALUES (%s, %s, %s)
        """
        db.execute_query(log_query, (
            f"order_rejection_{order_id}",
            f"Order #{order_id} rejected by {request.approved_by}",
            request.notes or "No notes"
        ))
        
        return {
            "success": True,
            "order_id": order_id,
            "status": "rejected",
            "rejected_by": request.approved_by,
            "rejected_at": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_order_history(
    status: Optional[str] = None,
    days: int = 30
) -> List[Dict]:
    """발주 이력 조회"""
    try:
        db = get_db()
        
        if status:
            query = """
                SELECT *
                FROM orders
                WHERE status = %s
                AND order_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                ORDER BY order_date DESC, id DESC
            """
            results = db.fetch_all(query, (status, days))
        else:
            query = """
                SELECT *
                FROM orders
                WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                ORDER BY order_date DESC, id DESC
            """
            results = db.fetch_all(query, (days,))
        
        return [
            {
                "id": row['id'],
                "product": row['product_name'],
                "quantity": row['quantity_ordered'],
                "unit_cost": float(row['unit_cost']),
                "total_cost": float(row['total_cost']),
                "order_date": str(row['order_date']),
                "delivery_date": str(row['delivery_date']) if row['delivery_date'] else None,
                "status": row['status']
            }
            for row in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
