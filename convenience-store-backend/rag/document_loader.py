"""
문서 로더 - 마크다운 파일 로드
"""
import os
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class DocumentLoader:
    """마크다운 문서 로더"""
    
    def __init__(self, base_path: str = "./knowledge_base"):
        """
        Args:
            base_path: 지식 베이스 디렉토리
        """
        self.base_path = base_path
    
    def load_directory(self, subdirectory: str) -> List[Dict]:
        """
        디렉토리의 모든 마크다운 파일 로드
        
        Args:
            subdirectory: products, manuals, patterns 등
            
        Returns:
            [{"content": "...", "metadata": {...}}, ...]
        """
        directory = os.path.join(self.base_path, subdirectory)
        
        if not os.path.exists(directory):
            logger.warning(f"⚠️ 디렉토리 없음: {directory}")
            return []
        
        documents = []
        
        for filename in os.listdir(directory):
            if filename.endswith('.md'):
                filepath = os.path.join(directory, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 메타데이터
                    metadata = {
                        "source": filename,
                        "category": subdirectory,
                        "path": filepath
                    }
                    
                    documents.append({
                        "content": content,
                        "metadata": metadata
                    })
                    
                    logger.info(f"📄 로드: {filename}")
                    
                except Exception as e:
                    logger.error(f"❌ 파일 로드 실패 ({filename}): {e}")
        
        logger.info(f"✅ {len(documents)}개 문서 로드 완료: {subdirectory}")
        return documents
    
    def load_all(self) -> Dict[str, List[Dict]]:
        """
        모든 카테고리 문서 로드
        
        Returns:
            {
                "products": [...],
                "manuals": [...],
                "patterns": [...]
            }
        """
        categories = ["products", "manuals", "patterns"]
        all_documents = {}
        
        for category in categories:
            all_documents[category] = self.load_directory(category)
        
        total = sum(len(docs) for docs in all_documents.values())
        logger.info(f"✅ 전체 {total}개 문서 로드 완료")
        
        return all_documents
    
    def get_statistics(self) -> Dict:
        """통계 정보"""
        all_docs = self.load_all()
        
        return {
            "products": len(all_docs.get("products", [])),
            "manuals": len(all_docs.get("manuals", [])),
            "patterns": len(all_docs.get("patterns", [])),
            "total": sum(len(docs) for docs in all_docs.values())
        }
