"""
Chroma DB 벡터 스토어 관리
"""
import os
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """ChromaDB 벡터 스토어"""
    
    def __init__(self, persist_directory: str = "./chromadb"):
        """
        Args:
            persist_directory: ChromaDB 저장 경로
        """
        self.persist_directory = persist_directory
        
        # 디렉토리 생성
        os.makedirs(persist_directory, exist_ok=True)
        
        # ChromaDB 클라이언트 초기화 (PersistentClient 사용)
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # 임베딩 모델 (한국어 지원)
        self.embedding_model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        
        logger.info(f"✅ VectorStore 초기화: {persist_directory}")

    
    def get_or_create_collection(self, name: str):
        """컬렉션 가져오기 또는 생성"""
        try:
            collection = self.client.get_collection(name)
            logger.info(f"📚 기존 컬렉션 로드: {name}")
        except:
            collection = self.client.create_collection(name)
            logger.info(f"📚 새 컬렉션 생성: {name}")
        
        return collection
    
    def add_documents(
        self, 
        collection_name: str, 
        documents: List[str], 
        metadatas: List[Dict],
        ids: List[str]
    ):
        """문서 추가"""
        collection = self.get_or_create_collection(collection_name)
        
        # 임베딩 생성
        embeddings = self.embedding_model.encode(documents).tolist()
        
        # 문서 추가
        collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        logger.info(f"✅ {len(documents)}개 문서 추가 → {collection_name}")
    
    def search(
        self, 
        collection_name: str, 
        query: str, 
        n_results: int = 3
    ) -> Dict:
        """유사 문서 검색"""
        try:
            collection = self.client.get_collection(collection_name)
        except:
            logger.warning(f"⚠️ 컬렉션 없음: {collection_name}")
            return {"documents": [], "metadatas": [], "distances": []}
        
        # 쿼리 임베딩
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # 검색
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        return results
    
    def get_collection_count(self, collection_name: str) -> int:
        """컬렉션 문서 수"""
        try:
            collection = self.client.get_collection(collection_name)
            return collection.count()
        except:
            return 0
    
    def delete_collection(self, collection_name: str):
        """컬렉션 삭제"""
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"🗑️ 컬렉션 삭제: {collection_name}")
        except:
            logger.warning(f"⚠️ 컬렉션 없음: {collection_name}")
