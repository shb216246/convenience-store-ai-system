"""
판매 패턴 분석 에이전트
과거 판매 데이터를 분석하고 미래 수요를 예측합니다.
"""
try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
except ImportError:
    from langchain.agents import AgentExecutor
    from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict, List
from tools.sales_tools import (
    get_sales_data,
    analyze_sales_pattern,
    get_trending_products,
    predict_daily_sales,
    analyze_sales_correlation
)


class SalesAgent:
    """판매 분석 전문 에이전트"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.tools = [
            get_sales_data,
            analyze_sales_pattern,
            get_trending_products,
            predict_daily_sales,
            analyze_sales_correlation
        ]
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """에이전트 생성"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 편의점 판매 데이터 분석 전문가입니다.
            
당신의 역할:
1. 과거 판매 데이터를 분석합니다
2. 판매 패턴과 트렌드를 파악합니다
3. 미래 수요를 정확히 예측합니다
4. 상품 간 연관성을 발견합니다

분석 시 고려사항:
- 요일별/시간대별 판매 패턴
- 계절성 및 트렌드
- 인기 상품 변화
- 상품 간 교차 판매 기회
- 과거 데이터 기반 예측

통계적 근거를 바탕으로 명확한 인사이트를 제공하세요."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=False)
    
    def analyze(self, request: str) -> Dict:
        """판매 분석 수행"""
        response = self.agent_executor.invoke({"input": request})
        return {
            "agent": "SalesAgent",
            "analysis": response["output"],
            "role": "판매 패턴 분석 및 수요 예측"
        }
    
    def predict_tomorrow_sales(self, product: str) -> Dict:
        """내일 판매량 예측"""
        request = f"{product}의 내일 판매량을 예측하고, 예측 근거를 상세히 설명해주세요."
        return self.analyze(request)
    
    def find_sales_patterns(self, product: str) -> Dict:
        """판매 패턴 발견"""
        request = f"{product}의 판매 패턴을 분석해주세요. 주별, 시간대별 패턴과 트렌드를 포함해주세요."
        return self.analyze(request)
    
    def get_trending_analysis(self) -> Dict:
        """트렌딩 상품 분석"""
        request = "현재 인기 상승 중인 상품을 분석하고, 발주 전략을 제안해주세요."
        return self.analyze(request)
