"""
발주 최적화 에이전트 (긴급 수정 버전)
구조화된 JSON 형식으로 발주 품목 리스트 생성 + 숫자 검증 강화
"""
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from typing import Dict, List
import json
import re


class OrderAgent:
    """발주 최적화 전문 에이전트 - 구조화된 발주 데이터 생성"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
    
    def _safe_int(self, value, default=0):
        """안전한 정수 변환"""
        if value in [None, "", "N/A", "n/a", "null"]:
            return default
        try:
            return int(float(value))  # "10.0" 같은 경우 처리
        except (ValueError, TypeError):
            return default
    
    def _safe_float(self, value, default=0.0):
        """안전한 실수 변환"""
        if value in [None, "", "N/A", "n/a", "null"]:
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def analyze(self, integrated_analysis: str) -> Dict:
        """
        통합 분석 결과를 받아 구조화된 발주 품목 리스트 생성
        """
        
        system_prompt = """당신은 편의점 발주 최적화 전문가입니다.

재고 분석, 판매 분석, 날씨 분석 결과를 종합하여 **구조화된 발주 품목 리스트**를 생성하세요.

**중요**: 모든 숫자 필드는 반드시 숫자만 사용하세요. "N/A", "없음", "미정" 같은 문자열 절대 금지!

응답 형식 (반드시 이 JSON 형식으로만 응답):
```json
{
  "summary": "전체 발주 요약 (2-3문장)",
  "order_items": [
    {
      "product_name": "상품명",
      "current_stock": 0,
      "safe_stock": 20,
      "order_quantity": 50,
      "unit_price": 1500,
      "total_cost": 75000,
      "reason": "발주 이유 (1-2문장)",
      "priority": "high"
    }
  ]
}
```

**숫자 필드 규칙**:
- current_stock: 반드시 0 이상의 정수 (모르면 0)
- safe_stock: 반드시 0 이상의 정수 (모르면 20)
- order_quantity: 반드시 1 이상의 정수 (0이면 발주 안 함)
- unit_price: 반드시 0 이상의 숫자
- total_cost: order_quantity × unit_price

발주량 결정 기준:
- 재고 부족 상품: 안전재고의 150-200%
- 판매 증가 상품: 과거 7일 평균 + 20-30%
- 날씨 영향 상품: 추천 수량대로
- 재고 충분 상품: 발주 안 함

단가 기준 (추정):
- 삼각김밥/도시락: 1500
- 라면/컵라면: 1200
- 음료수: 1000
- 우유: 1800
- 빵: 2000
- 과자: 1500
- 아이스크림: 1200
- 우산: 5000
- 우비: 3000
- 생수: 500
- 커피: 2500

우선순위:
- high: 재고 0이거나 안전재고 50% 미만
- medium: 안전재고 50-80%
- low: 안전재고 80% 이상

**중요**: 반드시 유효한 JSON만 출력하세요. 모든 숫자는 정수 또는 실수로만!"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""다음은 각 에이전트의 분석 결과입니다:

{integrated_analysis}

위 분석을 바탕으로 구조화된 발주 품목 리스트를 JSON 형식으로 생성하세요.
재고가 부족하거나 판매가 증가한 상품, 날씨 영향을 받는 상품을 우선 발주하세요.
재고가 충분한 상품은 제외하세요.

**다시 한 번 강조**: 모든 숫자 필드는 반드시 숫자만! "N/A" 같은 문자열 금지!""")
        ]
        
        try:
            response = self.llm.invoke(messages)
            raw_content = response.content.strip()
            
            # JSON 추출 (마크다운 코드 블록 제거)
            json_match = re.search(r'```json\s*(.*?)\s*```', raw_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                # 코드 블록 없이 바로 JSON인 경우
                json_str = raw_content
            
            # JSON 파싱
            order_data = json.loads(json_str)
            
            # 검증 및 기본값 설정
            if "order_items" not in order_data:
                order_data["order_items"] = []
            
            if "summary" not in order_data:
                order_data["summary"] = "발주 품목 목록입니다."
            
            # 각 품목 검증 및 안전한 타입 변환
            validated_items = []
            for item in order_data["order_items"]:
                validated_item = {
                    "product_name": str(item.get("product_name", "미지정")),
                    "current_stock": self._safe_int(item.get("current_stock"), 0),
                    "safe_stock": self._safe_int(item.get("safe_stock"), 20),
                    "order_quantity": self._safe_int(item.get("order_quantity"), 0),
                    "unit_price": self._safe_float(item.get("unit_price"), 1000),
                    "reason": str(item.get("reason", "발주 필요"))[:500],
                    "priority": str(item.get("priority", "medium"))
                }
                
                # total_cost 재계산
                validated_item["total_cost"] = validated_item["order_quantity"] * validated_item["unit_price"]
                
                # order_quantity가 0이면 제외
                if validated_item["order_quantity"] > 0:
                    validated_items.append(validated_item)
            
            order_data["order_items"] = validated_items
            
            return {
                "agent": "OrderAgent",
                "analysis": order_data["summary"],
                "role": "발주 최적화 및 생성",
                "order_items": order_data["order_items"],
                "total_items": len(order_data["order_items"]),
                "total_cost": sum(item["total_cost"] for item in order_data["order_items"])
            }
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON 파싱 실패: {e}")
            print(f"원본 응답: {raw_content}")
            # 파싱 실패 시 빈 발주
            return {
                "agent": "OrderAgent",
                "analysis": "발주 데이터 생성 중 오류가 발생했습니다.",
                "role": "발주 최적화 및 생성",
                "order_items": [],
                "total_items": 0,
                "total_cost": 0
            }
        except Exception as e:
            print(f"❌ 발주 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return {
                "agent": "OrderAgent",
                "analysis": f"발주 생성 실패: {str(e)}",
                "role": "발주 최적화 및 생성",
                "order_items": [],
                "total_items": 0,
                "total_cost": 0
            }