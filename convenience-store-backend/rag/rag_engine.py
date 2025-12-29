"""
RAG 엔진 - 통합 검색 및 컨텍스트 생성
"""
import os
from typing import List, Dict, Optional
import logging

from .vector_store import VectorStore
from .document_loader import DocumentLoader

logger = logging.getLogger(__name__)


class RAGEngine:
    """RAG 통합 엔진"""
    
    def __init__(
        self, 
        knowledge_base_path: str = "./knowledge_base",
        chromadb_path: str = "./chromadb"
    ):
        """
        Args:
            knowledge_base_path: 지식 베이스 디렉토리
            chromadb_path: ChromaDB 저장 경로
        """
        self.vector_store = VectorStore(persist_directory=chromadb_path)
        self.document_loader = DocumentLoader(base_path=knowledge_base_path)
        
        logger.info("✅ RAG 엔진 초기화 완료")
    
    def initialize_knowledge_base(self, reset: bool = False):
        """
        지식 베이스 초기화 (문서 → 벡터 DB)
        
        Args:
            reset: True면 기존 데이터 삭제 후 재생성
        """
        logger.info("📚 지식 베이스 초기화 시작...")
        
        if reset:
            logger.info("🗑️ 기존 컬렉션 삭제...")
            self.vector_store.delete_collection("convenience_store_kb")
        
        # 모든 문서 로드
        all_documents = self.document_loader.load_all()
        
        # 벡터 DB에 추가
        documents = []
        metadatas = []
        ids = []
        
        doc_id = 0
        for category, docs in all_documents.items():
            for doc in docs:
                documents.append(doc["content"])
                metadatas.append(doc["metadata"])
                ids.append(f"{category}_{doc_id}")
                doc_id += 1
        
        if documents:
            self.vector_store.add_documents(
                collection_name="convenience_store_kb",
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"✅ {len(documents)}개 문서 인덱싱 완료")
        else:
            logger.warning("⚠️ 로드된 문서가 없습니다")
    
    def search(self, query: str, n_results: int = 3) -> Dict:
        """
        질문에 대한 관련 문서 검색
        
        Args:
            query: 사용자 질문
            n_results: 검색할 문서 수
            
        Returns:
            {
                "context": "검색된 문서들의 내용",
                "sources": ["파일1.md", "파일2.md"],
                "num_sources": 2
            }
        """
        # 벡터 검색
        results = self.vector_store.search(
            collection_name="convenience_store_kb",
            query=query,
            n_results=n_results
        )
        
        # 결과 포맷팅
        if not results["documents"] or len(results["documents"][0]) == 0:
            return {
                "context": "",
                "sources": [],
                "num_sources": 0
            }
        
        # 컨텍스트 생성
        context_parts = []
        sources = []
        
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i]
            source = metadata.get("source", "unknown")
            
            context_parts.append(f"[출처: {source}]\n{doc}\n")
            sources.append(source)
        
        context = "\n---\n\n".join(context_parts)
        
        return {
            "context": context,
            "sources": sources,
            "num_sources": len(sources)
        }
    
    def search_products(self, query: str, n_results: int = 3) -> str:
        """상품 정보 검색"""
        result = self.search(query, n_results)
        return result["context"]
    
    def search_manuals(self, query: str, n_results: int = 2) -> str:
        """운영 매뉴얼 검색"""
        result = self.search(query, n_results)
        return result["context"]
    
    def search_patterns(self, query: str, n_results: int = 2) -> str:
        """판매 패턴 검색"""
        result = self.search(query, n_results)
        return result["context"]
    
    def get_statistics(self) -> Dict:
        """통계 정보"""
        doc_stats = self.document_loader.get_statistics()
        vector_count = self.vector_store.get_collection_count("convenience_store_kb")
        
        return {
            "vector_store": doc_stats,
            "total_indexed": vector_count
        }


# 전역 RAG 인스턴스
_rag_instance: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """RAG 엔진 싱글톤"""
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGEngine()
    return _rag_instance
