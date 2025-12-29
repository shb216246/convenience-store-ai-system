"""
재고 분석 에이전트
현재 재고 상태를 분석하고 부족한 상품을 파악합니다.
"""
try:
    from langchain.agents import AgentExecutor, create_openai_functions_agent
except ImportError:
    from langchain.agents import AgentExecutor
    from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import Dict, List
from tools.inventory_tools import (
    get_current_inventory,
    get_low_stock_items,
    get_expiring_products,
    calculate_stock_turnover
)


class InventoryAgent:
    """재고 관리 전문 에이전트"""
    
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.tools = [
            get_current_inventory,
            get_low_stock_items,
            get_expiring_products,
            calculate_stock_turnover
        ]
        self.agent_executor = self._create_agent()
    
    def _create_agent(self) -> AgentExecutor:
        """에이전트 생성"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """당신은 편의점 재고 관리 전문가입니다.
            
당신의 역할:
1. 현재 재고 상태를 정확히 파악합니다
2. 재고가 부족한 상품을 식별합니다
3. 유통기한이 임박한 상품을 관리합니다
4. 재고 회전율을 분석합니다

분석 시 고려사항:
- 안전 재고 수준 대비 현재 재고
- 유통기한 관리
- 재고 회전율
- 과잉/부족 재고 파악

항상 데이터 기반으로 객관적인 분석을 제공하세요."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=False)
    
    def analyze(self, request: str) -> Dict:
        """재고 분석 수행"""
        response = self.agent_executor.invoke({"input": request})
        return {
            "agent": "InventoryAgent",
            "analysis": response["output"],
            "role": "재고 상태 분석"
        }
    
    def get_low_stock_alert(self) -> Dict:
        """재고 부족 알림"""
        request = "현재 재고가 부족한 상품을 찾아서 상세히 분석해주세요. 각 상품의 현재 재고, 안전 재고, 부족량을 포함해주세요."
        return self.analyze(request)
    
    def check_expiring_items(self) -> Dict:
        """유통기한 임박 상품 확인"""
        request = "유통기한이 임박한 상품을 확인하고, 권장 조치사항을 알려주세요."
        return self.analyze(request)
