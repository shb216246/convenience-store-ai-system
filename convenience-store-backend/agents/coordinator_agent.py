"""
코디네이터 에이전트
모든 전문 에이전트들을 조율하여 최종 발주 결정을 내립니다.
"""
from langchain_openai import ChatOpenAI
from typing import Dict, List
import json
import logging

from .inventory_agent import InventoryAgent
from .sales_agent import SalesAgent
from .weather_agent import WeatherAgent
from .order_agent import OrderAgent

logger = logging.getLogger(__name__)


class CoordinatorAgent:
    """
    멀티에이전트 시스템의 코디네이터
    
    워크플로우:
    1. InventoryAgent: 재고 상태 확인
    2. SalesAgent: 판매 패턴 분석 및 수요 예측
    3. WeatherAgent: 날씨 기반 수요 조정
    4. OrderAgent: 최종 발주안 생성
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key  # 추가
        self.model = model      # 추가
        
        self.llm = ChatOpenAI(
            temperature=0,
            model=model,
            openai_api_key=api_key
        )
        
        # 전문 에이전트들 초기화
        self.inventory_agent = InventoryAgent(self.llm)
        self.sales_agent = SalesAgent(self.llm)
        self.weather_agent = WeatherAgent(self.llm)
        self.order_agent = OrderAgent(self.llm)
    
    def generate_order_recommendation(self, user_request: str = None) -> Dict:
        """
        전체 워크플로우 실행하여 발주 추천 생성
        
        Returns:
            Dict: 각 에이전트의 분석 결과와 최종 발주 추천
        """
        print("\n" + "="*80)
        print("🤖 멀티에이전트 발주 시스템 시작")
        print("="*80 + "\n")
        
        workflow_results = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "user_request": user_request,
            "agents_analysis": {},
            "final_recommendation": None
        }
        
        # Step 1: 재고 분석
        print("\n📦 Step 1: 재고 상태 분석 (InventoryAgent)")
        print("-" * 80)
        inventory_analysis = self.inventory_agent.get_low_stock_alert()
        workflow_results["agents_analysis"]["inventory"] = inventory_analysis
        print(f"✅ 완료: {inventory_analysis['analysis'][:200]}...")
        
        # Step 2: 판매 패턴 분석
        print("\n📊 Step 2: 판매 패턴 분석 (SalesAgent)")
        print("-" * 80)
        sales_analysis = self.sales_agent.get_trending_analysis()
        workflow_results["agents_analysis"]["sales"] = sales_analysis
        print(f"✅ 완료: {sales_analysis['analysis'][:200]}...")
        
        # Step 3: 날씨 기반 수요 예측
        print("\n🌤️ Step 3: 날씨 기반 수요 예측 (WeatherAgent)")
        print("-" * 80)
        weather_analysis = self.weather_agent.get_weather_recommendations()
        workflow_results["agents_analysis"]["weather"] = weather_analysis
        print(f"✅ 완료: {weather_analysis['analysis'][:200]}...")
        
        # Step 4: 최종 발주안 생성
        print("\n📋 Step 4: 최적 발주안 생성 (OrderAgent)")
        print("-" * 80)
        
        # 모든 분석 결과를 종합
        combined_insights = f"""
다음은 각 전문 에이전트의 분석 결과입니다:

[재고 분석 - InventoryAgent]
{inventory_analysis['analysis']}

[판매 분석 - SalesAgent]
{sales_analysis['analysis']}

[날씨 분석 - WeatherAgent]
{weather_analysis['analysis']}

위 모든 분석을 종합하여 최적의 발주안을 생성해주세요.
각 상품별로:
1. 현재 재고 상태
2. 예상 판매량
3. 날씨 영향
4. 최종 추천 발주량
을 포함해주세요.
"""
        
        final_order = self.order_agent.analyze(combined_insights)
        workflow_results["agents_analysis"]["order"] = final_order
        workflow_results["final_recommendation"] = final_order["analysis"]
        
        # order_items 추가 (OrderAgent에서 생성한 구조화된 데이터)
        workflow_results["order_items"] = final_order.get("order_items", [])
        workflow_results["total_items"] = final_order.get("total_items", 0)
        workflow_results["total_cost"] = final_order.get("total_cost", 0)
        
        # 각 에이전트 분석을 텍스트로 저장 (DB 저장용)
        workflow_results["inventory_analysis"] = inventory_analysis.get("analysis", "")
        workflow_results["sales_analysis"] = sales_analysis.get("analysis", "")
        workflow_results["weather_analysis"] = weather_analysis.get("analysis", "")
        
        print(f"✅ 완료: 최종 발주안 생성 완료")
        print(f"📦 발주 품목: {len(workflow_results['order_items'])}개")
        print(f"💰 총 금액: {workflow_results['total_cost']:,.0f}원")
        
        # 요약
        print("\n" + "="*80)
        print("✨ 멀티에이전트 분석 완료")
        print("="*80)
        print(f"\n참여 에이전트: {len(workflow_results['agents_analysis'])}개")
        print("- InventoryAgent: 재고 상태 분석")
        print("- SalesAgent: 판매 패턴 및 수요 예측")
        print("- WeatherAgent: 날씨 기반 조정")
        print("- OrderAgent: 최적 발주안 생성")
        print("\n" + "="*80 + "\n")
        
        return workflow_results
    
    def analyze_specific_product(self, product_name: str) -> Dict:
        """
        특정 상품에 대한 심층 분석
        """
        print(f"\n🔍 '{product_name}' 상품 심층 분석 시작\n")
        
        results = {
            "product": product_name,
            "analyses": {}
        }
        
        # 각 에이전트의 분석
        results["analyses"]["inventory"] = self.inventory_agent.analyze(
            f"{product_name}의 현재 재고 상태와 회전율을 분석해주세요."
        )
        
        results["analyses"]["sales"] = self.sales_agent.predict_tomorrow_sales(product_name)
        
        results["analyses"]["weather"] = self.weather_agent.analyze_product_weather_impact(product_name)
        
        # 통합 분석
        integrated_analysis = f"""
{product_name}에 대한 모든 분석 결과:

재고: {results["analyses"]["inventory"]["analysis"]}
판매: {results["analyses"]["sales"]["analysis"]}
날씨: {results["analyses"]["weather"]["analysis"]}

이를 바탕으로 {product_name}의 최적 발주량을 계산해주세요.
"""
        
        results["final_recommendation"] = self.order_agent.analyze(integrated_analysis)
        
        return results
    
    def chat(self, user_message: str) -> str:
        """
        사용자와의 대화형 인터페이스 (자연스러운 대화)
        """
        from langchain_openai import ChatOpenAI
        from langchain.schema import HumanMessage, SystemMessage
        
        # 대화형 LLM (temperature 높여서 자연스럽게)
        chat_llm = ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            temperature=0.7  # 자연스러운 대화를 위해 높임
        )
        
        # 친근한 편의점 직원 스타일 시스템 프롬프트
        system_prompt = """당신은 편의점 AI 어시스턴트입니다. 친근하고 유연하게 대화하세요.

**대화 스타일:**
- 친근한 편의점 직원처럼 말하기
- 존댓말 사용하되 너무 딱딱하지 않게
- 이모지 적절히 사용 (📦, 🔥, ☔ 등)
- 간결하고 핵심만 전달
- 불필요한 나열 금지

**답변 방식:**
1. 먼저 질문에 직접 답변
2. 필요한 정보만 간단히 설명
3. 추가 도움 제안

**예시:**
❌ 나쁜 답변: "다음 기능을 제공합니다: • 재고 확인 • 판매 분석..."
✅ 좋은 답변: "안녕하세요! 😊 재고 확인, 판매 분석, 날씨 예측 도와드려요. 뭐가 궁금하세요?"

**중요:** 
- 지식 베이스 정보가 제공되면 자연스럽게 녹여서 답변
- 리스트 나열보다는 문장으로 설명
- 사용자가 물어본 것에만 집중"""

        try:
            # 간단한 인사 처리
            message_lower = user_message.lower()
            if any(word in message_lower for word in ["안녕", "hello", "hi"]):
                return "안녕하세요! 😊 편의점 AI 어시스턴트예요.\n\n재고 확인, 판매 분석, 날씨 예측, 발주 정보 등 도와드릴게요. 뭐가 궁금하세요?"
            
            # LLM으로 자연스럽게 답변
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_message)
            ]
            
            response = chat_llm.invoke(messages).content
            return response
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "죄송해요, 일시적인 오류가 발생했어요. 😅 다시 한 번 물어봐주시겠어요?"
    
    def _simple_response(self, message: str) -> str:
        """간단한 인사나 질문에 대한 직접 응답 (Agent 호출 없음)"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["안녕", "hello", "hi", "헬로"]):
            return "안녕하세요! 😊 편의점 AI 어시스턴트예요.\n\n재고 확인, 판매 분석, 날씨 예측 도와드릴게요. 뭐가 궁금하세요?"
        elif any(word in message_lower for word in ["도움", "help", "기능", "뭐", "할수"]):
            return "이런 걸 도와드릴 수 있어요! 😊\n\n• 재고 확인 - \"재고 부족한 거 뭐야?\"\n• 판매 분석 - \"어제 뭐 많이 팔렸어?\"\n• 날씨 예측 - \"내일 날씨 어때?\"\n• 상품 정보 - \"삼각김밥 발주 기준이 뭐야?\"\n\n편하게 물어보세요!"
        elif any(word in message_lower for word in ["고마", "감사", "thank"]):
            return "천만에요! 😊 더 궁금한 거 있으면 언제든 물어보세요!"
        else:
            return "음... 잘 이해하지 못했어요. 😅\n\n재고, 판매, 날씨, 상품 정보 같은 걸 물어보시면 도와드릴게요!"