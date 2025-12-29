"""
발주 생성 및 관리 도구들
"""
from langchain.tools import tool
import json
from datetime import datetime, timedelta
from typing import Dict, List


@tool
def create_order(orders: str) -> str:
    """
    발주서를 생성합니다.
    
    Args:
        orders: 발주 항목 JSON 문자열
            예: '[{"product": "삼각김밥", "quantity": 30}]'
    
    Returns:
        생성된 발주서 정보
    """
    try:
        order_items = json.loads(orders)
    except:
        return "발주 정보 형식이 올바르지 않습니다."
    
    order_id = f"ORD-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    total_items = len(order_items)
    total_quantity = sum(item.get("quantity", 0) for item in order_items)
    
    order_document = {
        "order_id": order_id,
        "created_at": datetime.now().isoformat(),
        "status": "대기중",
        "items": order_items,
        "summary": {
            "total_items": total_items,
            "total_quantity": total_quantity
        },
        "estimated_delivery": (datetime.now().date() + timedelta(days=1)).isoformat()
    }
    
    return json.dumps(order_document, ensure_ascii=False)


@tool
def calculate_order_cost(orders: str) -> str:
    """
    발주 비용을 계산합니다.
    
    Args:
        orders: 발주 항목 JSON 문자열
    
    Returns:
        비용 계산 결과
    """
    try:
        order_items = json.loads(orders)
    except:
        return "발주 정보 형식이 올바르지 않습니다."
    
    # 상품별 도매가 (실제로는 DB에서 조회)
    wholesale_prices = {
        "삼각김밥": 1000,
        "도시락": 3000,
        "컵라면": 800,
        "우유": 1500,
        "빵": 1200,
        "음료수": 700,
        "과자": 900,
        "라면": 600,
        "아이스크림": 1100,
        "우산": 5000,
    }
    
    total_cost = 0
    item_costs = []
    
    for item in order_items:
        product = item.get("product")
        quantity = item.get("quantity", 0)
        unit_price = wholesale_prices.get(product, 1000)
        item_total = unit_price * quantity
        
        total_cost += item_total
        item_costs.append({
            "product": product,
            "quantity": quantity,
            "unit_price": unit_price,
            "total": item_total
        })
    
    result = {
        "items": item_costs,
        "subtotal": total_cost,
        "tax": int(total_cost * 0.1),
        "total": int(total_cost * 1.1)
    }
    
    return json.dumps(result, ensure_ascii=False)


@tool
def optimize_order_quantity(product: str, predicted_sales: int, current_stock: int, 
                           lead_time_days: int = 1) -> str:
    """
    최적 발주량을 계산합니다.
    
    Args:
        product: 상품명
        predicted_sales: 예상 판매량
        current_stock: 현재 재고
        lead_time_days: 배송 소요일
    
    Returns:
        최적 발주량 계산 결과
    """
    # 안전 재고 계수 (판매량의 20%)
    safety_stock_factor = 0.2
    
    # 필요 재고 = (예상 판매량 * 배송일) + 안전재고
    required_stock = (predicted_sales * lead_time_days) + (predicted_sales * safety_stock_factor)
    
    # 최적 발주량 = 필요 재고 - 현재 재고
    optimal_order = max(0, int(required_stock - current_stock))
    
    result = {
        "product": product,
        "current_stock": current_stock,
        "predicted_daily_sales": predicted_sales,
        "lead_time_days": lead_time_days,
        "required_stock": int(required_stock),
        "safety_stock": int(predicted_sales * safety_stock_factor),
        "optimal_order_quantity": optimal_order,
        "rationale": f"{lead_time_days}일 소요 + 안전재고 20% 고려"
    }
    
    return json.dumps(result, ensure_ascii=False)


@tool
def get_order_history(days: int = 30, product: str = None) -> str:
    """
    과거 발주 내역을 조회합니다.
    
    Args:
        days: 조회 기간
        product: 특정 상품 (없으면 전체)
    
    Returns:
        발주 내역
    """
    # 실제로는 DB에서 조회
    from datetime import timedelta
    
    history = []
    for i in range(5):
        date = (datetime.now() - timedelta(days=i*7)).strftime("%Y-%m-%d")
        history.append({
            "order_id": f"ORD-{date.replace('-', '')}",
            "date": date,
            "product": product if product else "삼각김밥",
            "quantity": 50 - i*5,
            "status": "완료"
        })
    
    return json.dumps(history, ensure_ascii=False)


@tool
def validate_order(orders: str) -> str:
    """
    발주 가능 여부를 검증합니다.
    
    Args:
        orders: 발주 항목 JSON 문자열
    
    Returns:
        검증 결과
    """
    try:
        order_items = json.loads(orders)
    except:
        return json.dumps({"valid": False, "error": "잘못된 형식"}, ensure_ascii=False)
    
    issues = []
    warnings = []
    
    for item in order_items:
        product = item.get("product")
        quantity = item.get("quantity", 0)
        
        # 수량 검증
        if quantity <= 0:
            issues.append(f"{product}: 수량이 0 이하입니다.")
        elif quantity > 200:
            warnings.append(f"{product}: 수량이 매우 많습니다 ({quantity}개)")
        
        # 상품 존재 여부 (간단한 체크)
        if not product:
            issues.append("상품명이 없습니다.")
    
    result = {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "can_proceed": len(issues) == 0
    }
    
    return json.dumps(result, ensure_ascii=False)
