"""
RAG (Retrieval-Augmented Generation) 시스템
ChromaDB를 사용한 벡터 스토어 및 임베딩 관리
"""
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

load_dotenv()
logger = logging.getLogger(__name__)


class RAGManager:
    """RAG 시스템 관리자"""
    
    def __init__(self):
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./vector_store")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        
        # OpenAI 임베딩 초기화
        self.embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # 컬렉션별 벡터 스토어
        self.vector_stores: Dict[str, Chroma] = {}
        self._initialize_vector_stores()
    
    def _initialize_vector_stores(self):
        """벡터 스토어 초기화"""
        collections = ["sales_patterns", "inventory_history", "order_history", "weather_patterns"]
        
        for collection in collections:
            try:
                self.vector_stores[collection] = Chroma(
                    collection_name=collection,
                    embedding_function=self.embeddings,
                    persist_directory=os.path.join(self.vector_store_path, collection)
                )
                logger.info(f"벡터 스토어 초기화 완료: {collection}")
            except Exception as e:
                logger.error(f"벡터 스토어 초기화 실패 ({collection}): {e}")
    
    def add_documents(self, collection: str, documents: List[Dict[str, Any]]):
        """문서를 벡터 스토어에 추가"""
        if collection not in self.vector_stores:
            logger.error(f"존재하지 않는 컬렉션: {collection}")
            return
        
        try:
            # Document 객체로 변환
            docs = [
                Document(
                    page_content=doc["content"],
                    metadata=doc.get("metadata", {})
                )
                for doc in documents
            ]
            
            # 벡터 스토어에 추가
            self.vector_stores[collection].add_documents(docs)
            logger.info(f"{len(docs)}개 문서를 {collection}에 추가")
        except Exception as e:
            logger.error(f"문서 추가 실패 ({collection}): {e}")
    
    def search_similar(
        self, 
        collection: str, 
        query: str, 
        k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Document]:
        """유사한 문서 검색"""
        if collection not in self.vector_stores:
            logger.error(f"존재하지 않는 컬렉션: {collection}")
            return []
        
        try:
            if filter_metadata:
                results = self.vector_stores[collection].similarity_search(
                    query, 
                    k=k,
                    filter=filter_metadata
                )
            else:
                results = self.vector_stores[collection].similarity_search(query, k=k)
            
            logger.info(f"{collection}에서 {len(results)}개 유사 문서 검색")
            return results
        except Exception as e:
            logger.error(f"문서 검색 실패 ({collection}): {e}")
            return []
    
    def index_sales_data(self, sales_data: List[Dict[str, Any]]):
        """판매 데이터를 벡터 스토어에 인덱싱"""
        documents = []
        for sale in sales_data:
            content = f"""
상품명: {sale['product_name']}
판매량: {sale['quantity_sold']}개
판매일: {sale['sale_date']}
요일: {sale.get('day_of_week', 'N/A')}
가격: {sale.get('sale_price', 0)}원
"""
            documents.append({
                "content": content,
                "metadata": {
                    "product_name": sale['product_name'],
                    "sale_date": str(sale['sale_date']),
                    "quantity": sale['quantity_sold'],
                    "type": "sales"
                }
            })
        
        self.add_documents("sales_patterns", documents)
    
    def index_inventory_data(self, inventory_data: List[Dict[str, Any]]):
        """재고 데이터를 벡터 스토어에 인덱싱"""
        documents = []
        for item in inventory_data:
            content = f"""
상품명: {item['product_name']}
카테고리: {item.get('category', 'N/A')}
재고량: {item['quantity']}개
단가: {item.get('unit_price', 0)}원
유통기한: {item.get('expiry_date', 'N/A')}
"""
            documents.append({
                "content": content,
                "metadata": {
                    "product_name": item['product_name'],
                    "category": item.get('category', ''),
                    "quantity": item['quantity'],
                    "type": "inventory"
                }
            })
        
        self.add_documents("inventory_history", documents)
    
    def index_order_data(self, order_data: List[Dict[str, Any]]):
        """발주 데이터를 벡터 스토어에 인덱싱"""
        documents = []
        for order in order_data:
            content = f"""
상품명: {order['product_name']}
발주량: {order['quantity_ordered']}개
발주일: {order['order_date']}
배송일: {order.get('delivery_date', 'N/A')}
총 비용: {order.get('total_cost', 0)}원
상태: {order.get('status', 'pending')}
"""
            documents.append({
                "content": content,
                "metadata": {
                    "product_name": order['product_name'],
                    "order_date": str(order['order_date']),
                    "quantity": order['quantity_ordered'],
                    "type": "order"
                }
            })
        
        self.add_documents("order_history", documents)
    
    def get_relevant_sales_context(self, product_name: str, days: int = 30) -> str:
        """특정 상품의 관련 판매 컨텍스트 검색"""
        query = f"{product_name}의 최근 판매 패턴과 트렌드"
        results = self.search_similar("sales_patterns", query, k=10)
        
        if not results:
            return "관련 판매 데이터가 없습니다."
        
        context = f"{product_name}의 과거 판매 데이터:\n\n"
        for doc in results:
            context += f"{doc.page_content}\n---\n"
        
        return context
    
    def get_relevant_inventory_context(self, product_name: str) -> str:
        """특정 상품의 관련 재고 컨텍스트 검색"""
        query = f"{product_name}의 재고 이력과 변화"
        results = self.search_similar("inventory_history", query, k=5)
        
        if not results:
            return "관련 재고 데이터가 없습니다."
        
        context = f"{product_name}의 재고 이력:\n\n"
        for doc in results:
            context += f"{doc.page_content}\n---\n"
        
        return context
    
    def get_similar_order_patterns(self, context: str) -> str:
        """유사한 발주 패턴 검색"""
        results = self.search_similar("order_history", context, k=5)
        
        if not results:
            return "유사한 발주 이력이 없습니다."
        
        patterns = "유사한 과거 발주 사례:\n\n"
        for doc in results:
            patterns += f"{doc.page_content}\n---\n"
        
        return patterns


# 전역 RAG 인스턴스
_rag_instance: Optional[RAGManager] = None


def get_rag() -> RAGManager:
    """RAG 인스턴스 싱글톤"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGManager()
    return _rag_instance
