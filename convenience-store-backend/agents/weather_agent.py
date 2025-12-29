"""
날씨 기반 수요 예측 에이전트
날씨 정보를 활용하여 상품 수요 변화를 예측합니다.
"""
try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
except ImportError:
    from langchain.agents import AgentExecutor
    from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict, List
from tools.weather_tools import (
    get_weather_forecast,
    analyze_weather_impact,
    get_weather_based_recommendations,
    check_special_events
)


class WeatherAgent:
    """날씨 기반 수요 예측 전문 에이전트"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.tools = [
            get_weather_forecast,
            analyze_weather_impact,
            get_weather_based_recommendations,
            check_special_events
        ]
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """에이전트 생성"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 날씨 기반 수요 예측 전문가입니다.
            
당신의 역할:
1. 날씨 예보를 확인합니다
2. 날씨가 상품 수요에 미치는 영향을 분석합니다
3. 날씨 기반 발주 조정안을 제시합니다
4. 특별 이벤트/공휴일을 고려합니다

분석 시 고려사항:
- 날씨별 상품 수요 변화
  * 비: 우산, 우비, 따뜻한 음식 ↑
  * 더위: 아이스크림, 음료수 ↑
  * 추위: 컵라면, 따뜻한 음료 ↑
- 강수 확률 및 기온
- 공휴일/특별 이벤트
- 과거 날씨별 판매 데이터

날씨 변화에 따른 구체적인 발주 조정안을 제시하세요."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=False)
    
    def analyze(self, request: str) -> Dict:
        """날씨 기반 분석 수행"""
        response = self.agent_executor.invoke({"input": request})
        return {
            "agent": "WeatherAgent",
            "analysis": response["output"],
            "role": "날씨 기반 수요 예측"
        }
    
    def get_weather_recommendations(self) -> Dict:
        """날씨 기반 발주 추천"""
        request = "내일 날씨를 확인하고, 날씨에 따른 발주 조정 사항을 상세히 추천해주세요."
        return self.analyze(request)
    
    def analyze_product_weather_impact(self, product: str) -> Dict:
        """특정 상품의 날씨 영향 분석"""
        request = f"내일 날씨가 {product} 판매에 미치는 영향을 분석하고, 발주량 조정안을 제시해주세요."
        return self.analyze(request)
