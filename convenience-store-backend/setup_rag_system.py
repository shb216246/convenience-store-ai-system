"""
RAG 시스템 자동 설치 스크립트
모든 설정을 자동으로 처리합니다
"""
import subprocess
import sys
import os


def install_packages():
    """필요한 패키지 설치"""
    print("📦 패키지 설치 중...")
    
    packages = [
        "chromadb",
        "sentence-transformers",
        "torch"  # sentence-transformers 의존성
    ]
    
    for package in packages:
        print(f"  - {package} 설치 중...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"  ✅ {package} 설치 완료")
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️ {package} 설치 실패: {e}")
            print(f"  수동 설치: pip install {package}")


def create_directories():
    """필요한 디렉토리 생성"""
    print("\n📁 디렉토리 생성 중...")
    
    directories = [
        "./knowledge_base",
        "./knowledge_base/products",
        "./knowledge_base/manuals",
        "./knowledge_base/patterns",
        "./chromadb"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}")


def generate_knowledge_base():
    """지식 베이스 생성"""
    print("\n📚 지식 베이스 생성 중...")
    
    scripts = [
        ("create_knowledge_base.py", "상품 문서"),
        ("create_manuals.py", "운영 매뉴얼"),
        ("create_patterns.py", "판매 패턴")
    ]
    
    for script, name in scripts:
        if os.path.exists(script):
            print(f"\n  {name} 생성 중...")
            try:
                subprocess.check_call([sys.executable, script])
            except subprocess.CalledProcessError as e:
                print(f"  ⚠️ {name} 생성 실패: {e}")
        else:
            print(f"  ⚠️ {script} 파일이 없습니다")


def initialize_vector_db():
    """벡터 DB 초기화"""
    print("\n🔧 벡터 DB 초기화 중...")
    
    try:
        from rag.rag_engine import RAGEngine
        
        rag = RAGEngine()
        rag.initialize_knowledge_base(reset=True)
        
        # 통계 출력
        stats = rag.get_statistics()
        print(f"\n✅ 벡터 DB 초기화 완료!")
        print(f"  - 상품: {stats['vector_store']['products']}개")
        print(f"  - 매뉴얼: {stats['vector_store']['manuals']}개")
        print(f"  - 패턴: {stats['vector_store']['patterns']}개")
        print(f"  - 총 인덱싱: {stats['total_indexed']}개 문서")
        
    except Exception as e:
        print(f"⚠️ 벡터 DB 초기화 실패: {e}")
        print("수동으로 초기화하세요:")
        print("  python")
        print("  >>> from rag.rag_engine import RAGEngine")
        print("  >>> rag = RAGEngine()")
        print("  >>> rag.initialize_knowledge_base(reset=True)")


def test_rag_system():
    """RAG 시스템 테스트"""
    print("\n🧪 RAG 시스템 테스트 중...")
    
    try:
        from rag.rag_engine import RAGEngine
        
        rag = RAGEngine()
        
        # 테스트 쿼리
        test_queries = [
            "삼각김밥 발주 기준이 뭐야?",
            "비 오는 날 뭐 많이 팔려?",
            "재고 관리 어떻게 해?"
        ]
        
        for query in test_queries:
            print(f"\n  질문: {query}")
            result = rag.search(query, n_results=1)
            
            if result["num_sources"] > 0:
                print(f"  ✅ 검색 성공 ({result['num_sources']}개 문서)")
                print(f"  출처: {result['sources'][0]}")
            else:
                print(f"  ⚠️ 검색 결과 없음")
        
        print("\n✅ RAG 시스템 테스트 완료!")
        
    except Exception as e:
        print(f"⚠️ 테스트 실패: {e}")


def main():
    """메인 실행"""
    print("=" * 60)
    print("🎉 RAG 시스템 자동 설치 시작")
    print("=" * 60)
    
    # 1. 패키지 설치
    install_packages()
    
    # 2. 디렉토리 생성
    create_directories()
    
    # 3. 지식 베이스 생성
    generate_knowledge_base()
    
    # 4. 벡터 DB 초기화
    initialize_vector_db()
    
    # 5. 테스트
    test_rag_system()
    
    print("\n" + "=" * 60)
    print("🎉 RAG 시스템 설치 완료!")
    print("=" * 60)
    print("\n다음 단계:")
    print("1. main.py의 /chat 엔드포인트에 RAG 통합")
    print("2. 백엔드 재시작: uvicorn main:app --reload")
    print("3. 챗봇에서 테스트")
    print("\n예시 질문:")
    print('  - "삼각김밥 발주 기준이 뭐야?"')
    print('  - "비 오는 날 뭐 많이 팔려?"')
    print('  - "재고 관리 어떻게 해?"')


if __name__ == "__main__":
    main()
