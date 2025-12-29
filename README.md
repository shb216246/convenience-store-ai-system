# 🏪 편의점 AI 자동 발주 시스템

> 멀티에이전트 시스템과 RAG 기반 AI를 활용한 지능형 재고 관리 및 자동 발주 시스템

[![React](https://img.shields.io/badge/React-18.3.1-blue)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6.2-blue)](https://www.typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-green)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green)](https://www.python.org/)

## 📌 프로젝트 소개

편의점 운영자를 위한 AI 기반 자동 발주 시스템입니다. 
판매 데이터, 재고 현황, 날씨 정보 등을 종합 분석하여 최적의 발주 추천을 제공합니다.

### 🎯 주요 기능

- **🤖 AI 챗봇**: RAG 기반 대화형 인터페이스로 재고 관리 질문 응답
- **📊 실시간 대시보드**: 판매 통계, 재고 현황, 트렌드 분석 시각화
- **🎯 자동 발주 추천**: 멀티에이전트 시스템이 최적의 발주량 계산
- **📈 데이터 분석**: 판매 패턴 분석 및 예측
- **📋 발주 이력 관리**: 과거 발주 내역 조회 및 통계

### 🏗️ 시스템 아키텍처

```
Frontend (React + TypeScript)
    ↓
Backend (FastAPI)
    ↓
Multi-Agent System
    ├── Coordinator Agent (조정)
    ├── Data Analysis Agent (데이터 분석)
    ├── Inventory Agent (재고 관리)
    └── Order Agent (발주 실행)
    ↓
RAG System (LangChain + ChromaDB)
    ↓
OpenAI GPT-4
```

## 🛠️ 기술 스택

### Frontend
- **React 18** - UI 프레임워크
- **TypeScript** - 타입 안전성
- **Tailwind CSS** - 스타일링
- **Framer Motion** - 애니메이션
- **React Query** - 데이터 캐싱
- **Recharts** - 데이터 시각화
- **React Hot Toast** - 알림 시스템

### Backend
- **FastAPI** - 웹 프레임워크
- **Python 3.11+** - 백엔드 언어
- **LangChain** - AI 체인 구축
- **ChromaDB** - 벡터 데이터베이스
- **OpenAI API** - GPT-4 모델

### AI/ML
- **Multi-Agent System** - 역할 기반 에이전트 협업
- **RAG (Retrieval-Augmented Generation)** - 문서 기반 답변 생성
- **Vector Embeddings** - 의미 기반 검색

## 🚀 설치 및 실행

### 사전 요구사항
- Node.js 18+
- Python 3.11+
- OpenAI API Key

### 1. 저장소 클론
```bash
git clone https://github.com/YOUR_USERNAME/convenience-store-ai-system.git
cd convenience-store-ai-system
```

### 2. 백엔드 설정
```bash
cd convenience-store-backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt

# .env 파일 생성
echo OPENAI_API_KEY=your_api_key_here > .env

# 서버 실행
uvicorn main:app --reload --port 8000
```

### 3. 프론트엔드 설정
```bash
cd convenience-store-frontend
npm install
npm run dev
```

### 4. 브라우저에서 접속
```
http://localhost:3000
```

## 📸 스크린샷

### 대시보드
실시간 판매 통계, 재고 현황, 트렌드 분석을 한눈에 확인할 수 있습니다.

### AI 챗봇
RAG 기반 AI가 재고 관리, 발주 관련 질문에 정확하게 답변합니다.

### 발주 추천
멀티에이전트 시스템이 분석한 최적의 발주 추천을 제공합니다.

### 발주 이력
과거 발주 내역과 통계를 확인하고 분석할 수 있습니다.

## 🎓 배운 점 및 성과

### 기술적 성과
- ✅ 멀티에이전트 시스템 설계 및 구현
- ✅ RAG 기반 AI 챗봇 구축
- ✅ React Query를 활용한 효율적인 상태 관리
- ✅ TypeScript로 타입 안전성 확보
- ✅ FastAPI로 고성능 백엔드 구축

### 문제 해결 경험

#### 1. 멀티에이전트 간 데이터 동기화
**문제**: 여러 에이전트가 동시에 작업할 때 데이터 일관성 유지 어려움  
**해결**: Coordinator 패턴을 도입하여 중앙 집중식 관리 구현

#### 2. RAG 시스템 응답 속도 개선
**문제**: 벡터 검색 및 응답 생성에 시간 소요  
**해결**: 벡터 인덱싱 최적화 및 캐싱 전략 적용으로 응답 속도 50% 개선

#### 3. 사용자 경험 개선
**문제**: API 오류 시 사용자 피드백 부족  
**해결**: Toast 알림 시스템 도입 및 로딩 스켈레톤 UI 적용

### 향후 개선 계획
- [ ] 다크 모드 지원
- [ ] 모바일 반응형 디자인 개선
- [ ] 실시간 알림 기능 추가
- [ ] 데이터 내보내기 (PDF, Excel)
- [ ] 다국어 지원 (i18n)

## 📁 프로젝트 구조

```
convenience-store-ai-system/
├── convenience-store-frontend/    # React 프론트엔드
│   ├── src/
│   │   ├── components/           # React 컴포넌트
│   │   ├── hooks/               # 커스텀 훅
│   │   ├── config.ts            # 환경 설정
│   │   └── App.tsx              # 메인 앱
│   └── package.json
├── convenience-store-backend/     # FastAPI 백엔드
│   ├── agents/                   # 멀티에이전트 시스템
│   ├── rag/                      # RAG 시스템
│   ├── main.py                   # FastAPI 앱
│   └── requirements.txt
└── README.md
```

## 🔒 환경 변수

### 백엔드 (.env)
```env
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4
```

### 프론트엔드 (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=편의점 AI 자동 발주 시스템
```

## 📝 라이선스
MIT License

## 👤 개발자
**Your Name**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- Email: your.email@example.com
- Portfolio: https://your-portfolio.com

## 🙏 감사의 말
이 프로젝트는 실제 편의점 운영의 어려움을 해결하기 위해 시작되었습니다.
AI 기술을 활용하여 소상공인의 업무 효율을 높이는 것이 목표입니다.
