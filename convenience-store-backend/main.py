"""
편의점 AI 자동 발주 시스템 - FastAPI 백엔드
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv
import logging
import traceback

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,  # DEBUG → INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 외부 라이브러리 로그 레벨 조정
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

from agents import CoordinatorAgent
from scheduler import auto_scheduler
from rag import get_rag_engine  # RAG 엔진 import

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="편의점 AI 발주 시스템",
    description="멀티에이전트 기반 자동 발주 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 애플리케이션 시작/종료 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시"""
    logger.info("🚀 애플리케이션 시작 중...")
    
    # Coordinator 초기화
    coord = get_coordinator()
    
    # 스케줄러에 Coordinator 설정
    auto_scheduler.set_coordinator(coord)
    
    # 스케줄러 시작 (매일 아침 6시)
    auto_scheduler.start(schedule_time="06:00")
    
    logger.info("✅ 애플리케이션 시작 완료")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시"""
    logger.info("⏹️ 애플리케이션 종료 중...")
    auto_scheduler.stop()
    logger.info("✅ 애플리케이션 종료 완료")

# 전역 코디네이터 에이전트
coordinator = None

def get_coordinator():
    """코디네이터 에이전트 싱글톤"""
    global coordinator
    if coordinator is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        coordinator = CoordinatorAgent(api_key=api_key, model=model)
    return coordinator


# RAG 엔진
rag_engine = None

def get_rag():
    """RAG 엔진 싱글톤"""
    global rag_engine
    if rag_engine is None:
        try:
            rag_engine = get_rag_engine()
            logger.info("✅ RAG 엔진 로드 완료")
        except Exception as e:
            logger.warning(f"⚠️ RAG 엔진 로드 실패: {e}")
            rag_engine = None
    return rag_engine


# Pydantic 모델들
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    agent: Optional[str] = None

class OrderRecommendationResponse(BaseModel):
    timestamp: str
    final_recommendation: str
    agents_analysis: Dict

class ProductAnalysisRequest(BaseModel):
    product_name: str

class InventoryData(BaseModel):
    products: List[Dict]  # [{"name": "삼각김밥", "quantity": 15}, ...]


# API 엔드포인트들
@app.get("/")
async def root():
    """헬스 체크"""
    return {
        "status": "ok",
        "message": "편의점 AI 발주 시스템 API",
        "version": "1.0.0"
    }

@app.get("/api/health")
async def health_check():
    """시스템 상태 확인"""
    try:
        coord = get_coordinator()
        return {
            "status": "healthy",
            "agents": {
                "inventory": "active",
                "sales": "active",
                "weather": "active",
                "order": "active",
                "coordinator": "active"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    챗봇 인터페이스 (RAG 통합)
    사용자 메시지에 따라 적절한 에이전트가 응답
    """
    try:
        logger.info(f"Chat request: {request.message}")
        
        # RAG 검색
        rag_context = ""
        rag = get_rag()
        
        if rag:
            try:
                rag_result = rag.search(request.message, n_results=3)
                if rag_result["num_sources"] > 0:
                    rag_context = rag_result["context"]
                    logger.info(f"📚 RAG: {rag_result['num_sources']}개 문서 검색됨")
            except Exception as e:
                logger.warning(f"⚠️ RAG 검색 오류: {e}")
        
        # LLM에 컨텍스트 포함
        if rag_context:
            enhanced_message = f"""다음은 지식 베이스에서 검색한 관련 정보입니다:

{rag_context}

---

사용자 질문: {request.message}

위 정보를 참고하여 정확하고 구체적으로 답변해주세요."""
        else:
            enhanced_message = request.message
        
        # 코디네이터 에이전트 호출
        coord = get_coordinator()
        response = coord.chat(enhanced_message)
        logger.info(f"Chat response generated successfully")
        
        return ChatResponse(
            response=response,
            agent="coordinator"
        )
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/orders/recommend", response_model=OrderRecommendationResponse)
async def get_order_recommendation():
    """
    전체 워크플로우 실행하여 발주 추천 생성
    모든 에이전트가 순차적으로 분석
    """
    try:
        logger.info("Order recommendation request started")
        coord = get_coordinator()
        result = coord.generate_order_recommendation()
        logger.info("Order recommendation completed successfully")
        
        return OrderRecommendationResponse(
            timestamp=result["timestamp"],
            final_recommendation=result["final_recommendation"],
            agents_analysis=result["agents_analysis"]
        )
    except Exception as e:
        logger.error(f"Order recommendation error: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/products/{product_name}/analyze")
async def analyze_product(product_name: str):
    """
    특정 상품에 대한 심층 분석
    """
    try:
        coord = get_coordinator()
        result = coord.analyze_specific_product(product_name)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/inventory/upload")
async def upload_inventory(file: UploadFile = File(...)):
    """
    CSV 파일로 재고 데이터 업로드
    """
    try:
        # CSV 파일 읽기
        contents = await file.read()
        # 실제로는 DB에 저장
        
        return {
            "status": "success",
            "message": f"재고 데이터 업로드 완료: {file.filename}",
            "rows_processed": 10  # 예시
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/inventory")
async def get_inventory():
    """현재 재고 조회"""
    try:
        from tools.inventory_tools import get_current_inventory
        # @tool 데코레이터는 invoke() 사용
        inventory_str = get_current_inventory.invoke({})
        import json
        inventory = json.loads(inventory_str)
        
        return {
            "status": "success",
            "data": inventory
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sales/trends")
async def get_sales_trends(days: int = 7):
    """판매 트렌드 조회"""
    try:
        from tools.sales_tools import get_trending_products
        # @tool 데코레이터는 invoke() 사용
        trends_str = get_trending_products.invoke({"days": days})
        import json
        trends = json.loads(trends_str)
        
        return {
            "status": "success",
            "period_days": days,
            "data": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 통계 API (대시보드용)
# ============================================

@app.get("/api/stats/summary")
async def get_stats_summary():
    """대시보드 요약 통계"""
    try:
        import pymysql
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        # 오늘 매출
        cursor.execute("""
            SELECT COALESCE(SUM(sale_price * quantity_sold), 0) as total
            FROM sales
            WHERE DATE(sale_date) = CURDATE()
        """)
        today_sales = float(cursor.fetchone()[0])
        
        # 어제 매출
        cursor.execute("""
            SELECT COALESCE(SUM(sale_price * quantity_sold), 0) as total
            FROM sales
            WHERE DATE(sale_date) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        """)
        yesterday_sales = float(cursor.fetchone()[0])
        
        # 발주 대기
        cursor.execute("""
            SELECT COUNT(*) FROM order_recommendations
            WHERE status = 'pending' AND recommendation_date >= CURDATE()
        """)
        pending_orders = int(cursor.fetchone()[0])
        
        # 재고 부족 상품
        cursor.execute("""
            SELECT COUNT(*) FROM inventory
            WHERE quantity < safe_stock
        """)
        low_stock_count = int(cursor.fetchone()[0])
        
        cursor.close()
        db.close()
        
        # 변화율 계산
        sales_change = 0
        if yesterday_sales > 0:
            sales_change = ((today_sales - yesterday_sales) / yesterday_sales) * 100
        
        return {
            "today_sales": int(today_sales),
            "sales_change": round(sales_change, 1),
            "pending_orders": pending_orders,
            "low_stock_items": low_stock_count,
            "processing_speed": 1.2
        }
    except Exception as e:
        logger.error(f"Stats summary error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/sales/trend")
async def get_sales_trend(days: int = 7):
    """판매 트렌드"""
    try:
        import pymysql
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(sale_date) as date,
                SUM(quantity_sold) as orders,
                SUM(sale_price * quantity_sold) as sales
            FROM sales
            WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            GROUP BY DATE(sale_date)
            ORDER BY date ASC
        """, (days,))
        
        trend_data = []
        for row in cursor.fetchall():
            trend_data.append({
                "date": row[0].strftime('%m/%d'),
                "sales": int(float(row[2])) if row[2] else 0,
                "orders": int(row[1]) if row[1] else 0
            })
        
        cursor.close()
        db.close()
        
        return {"data": trend_data}
    except Exception as e:
        logger.error(f"Sales trend error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/products/top")
async def get_top_products(limit: int = 5):
    """인기 상품 TOP"""
    try:
        import pymysql
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                s.product_name,
                SUM(s.quantity_sold) as total_sales,
                i.quantity as current_stock
            FROM sales s
            LEFT JOIN inventory i ON s.product_name = i.product_name
            WHERE s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY s.product_name, i.quantity
            ORDER BY total_sales DESC
            LIMIT %s
        """, (limit,))
        
        products = []
        for row in cursor.fetchall():
            # 간단한 트렌드 계산
            trend = round((float(row[1]) / 100) * 10, 1) if row[1] else 0
            
            products.append({
                "name": row[0],
                "sales": int(row[1]) if row[1] else 0,
                "trend": trend,
                "stock": int(row[2]) if row[2] else 0
            })
        
        cursor.close()
        db.close()
        
        return {"products": products}
    except Exception as e:
        logger.error(f"Top products error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats/category/distribution")
async def get_category_distribution():
    """카테고리별 판매 분포"""
    try:
        import pymysql
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                i.category,
                SUM(s.sale_price * s.quantity_sold) as total
            FROM sales s
            JOIN inventory i ON s.product_name = i.product_name
            WHERE s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY i.category
            ORDER BY total DESC
        """)
        
        colors = ['#3b82f6', '#06b6d4', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981']
        categories = []
        
        for idx, row in enumerate(cursor.fetchall()):
            categories.append({
                "name": row[0],
                "value": int(float(row[1])) if row[1] else 0,
                "color": colors[idx % len(colors)]
            })
        
        cursor.close()
        db.close()
        
        return {"data": categories}
    except Exception as e:
        logger.error(f"Category distribution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/weather/forecast")
async def get_weather(days: int = 3):
    """날씨 예보 조회"""
    try:
        from tools.weather_tools import get_weather_forecast
        # @tool 데코레이터는 invoke() 사용
        weather_str = get_weather_forecast.invoke({"days": days})
        import json
        weather = json.loads(weather_str)
        
        return {
            "status": "success",
            "data": weather
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/status")
async def get_agents_status():
    """모든 에이전트의 상태 확인"""
    try:
        coord = get_coordinator()
        
        return {
            "status": "active",
            "agents": [
                {
                    "name": "InventoryAgent",
                    "role": "재고 상태 분석",
                    "tools": ["재고 조회", "부족 상품 파악", "유통기한 관리", "재고 회전율"]
                },
                {
                    "name": "SalesAgent",
                    "role": "판매 패턴 분석 및 수요 예측",
                    "tools": ["판매 데이터", "패턴 분석", "트렌드", "판매 예측", "상관관계"]
                },
                {
                    "name": "WeatherAgent",
                    "role": "날씨 기반 수요 예측",
                    "tools": ["날씨 예보", "날씨 영향", "이벤트 확인", "날씨 추천"]
                },
                {
                    "name": "OrderAgent",
                    "role": "발주 최적화 및 생성",
                    "tools": ["발주 생성", "비용 계산", "수량 최적화", "발주 검증"]
                },
                {
                    "name": "CoordinatorAgent",
                    "role": "전체 에이전트 조율 및 의사결정",
                    "workflow": ["재고분석 → 판매분석 → 날씨분석 → 발주생성"]
                }
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 자동 발주 스케줄러 API
# ============================================

@app.get("/api/scheduler/status")
async def get_scheduler_status():
    """스케줄러 상태 조회"""
    try:
        status = auto_scheduler.get_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scheduler/run-now")
async def run_scheduler_now():
    """발주 추천 즉시 실행 (테스트용)"""
    try:
        auto_scheduler.run_now()
        return {
            "status": "success",
            "message": "발주 추천이 실행되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations")
async def get_recommendations(limit: int = 10):
    """발주 추천 목록 조회"""
    try:
        import pymysql
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                recommendation_date,
                total_items,
                total_cost,
                status,
                created_at,
                executed_at
            FROM order_recommendations
            ORDER BY recommendation_date DESC, created_at DESC
            LIMIT %s
        """, (limit,))
        
        recommendations = []
        for row in cursor.fetchall():
            recommendations.append({
                "id": row[0],
                "recommendation_date": row[1].strftime('%Y-%m-%d'),
                "total_items": int(row[2]),
                "total_cost": float(row[3]) if row[3] else 0,
                "status": row[4],
                "created_at": row[5].strftime('%Y-%m-%d %H:%M:%S'),
                "executed_at": row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None
            })
        
        cursor.close()
        db.close()
        
        return {
            "recommendations": recommendations,
            "total": len(recommendations)
        }
    except Exception as e:
        logger.error(f"발주 추천 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations/{recommendation_id}")
async def get_recommendation_detail(recommendation_id: int):
    """발주 추천 상세 조회"""
    try:
        
        
        
        import pymysql
        db = pymysql.connect(host=os.getenv("MYSQL_HOST", "localhost"), port=int(os.getenv("MYSQL_PORT", 3306)), user=os.getenv("MYSQL_USER", "root"), password=os.getenv("MYSQL_PASSWORD"), database=os.getenv("MYSQL_DATABASE", "store_order"), charset="utf8mb4")
        cursor = db.cursor()
        cursor.execute("""
            SELECT 
                id,
                recommendation_date,
                inventory_analysis,
                sales_analysis,
                weather_analysis,
                final_recommendation,
                total_items,
                total_cost,
                status,
                created_at,
                executed_at
            FROM order_recommendations
            WHERE id = %s
        """, (recommendation_id,))
        
        row = cursor.fetchone()
        cursor.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="발주 추천을 찾을 수 없습니다.")
        
        return {
            "id": row[0],
            "recommendation_date": row[1].strftime('%Y-%m-%d'),
            "inventory_analysis": row[2],
            "sales_analysis": row[3],
            "weather_analysis": row[4],
            "final_recommendation": row[5],
            "total_items": int(row[6]),
            "total_cost": float(row[7]) if row[7] else 0,
            "status": row[8],
            "created_at": row[9].strftime('%Y-%m-%d %H:%M:%S'),
            "executed_at": row[10].strftime('%Y-%m-%d %H:%M:%S') if row[10] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"발주 추천 상세 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'db' in locals():
            db.close()


@app.post("/api/recommendations/{recommendation_id}/execute")
async def execute_recommendation(recommendation_id: int):
    """발주 추천 실행 - 실제 재고 업데이트 + 발주 기록 생성"""
    db = None
    cursor = None
    
    try:
        import pymysql
        from datetime import datetime, timedelta
        
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        # 1. 발주 추천 조회
        cursor.execute("""
            SELECT status FROM order_recommendations WHERE id = %s
        """, (recommendation_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="발주 추천을 찾을 수 없습니다.")
        
        if result[0] == 'executed':
            raise HTTPException(status_code=400, detail="이미 실행된 발주 추천입니다.")
        
        # 2. 발주 품목 조회
        cursor.execute("""
            SELECT 
                product_name,
                order_quantity,
                unit_price,
                total_cost
            FROM order_items
            WHERE recommendation_id = %s
        """, (recommendation_id,))
        
        items = cursor.fetchall()
        
        if not items:
            raise HTTPException(status_code=400, detail="발주 품목이 없습니다.")
        
        # 3. 각 품목 처리
        order_date = datetime.now().date()
        delivery_date = order_date + timedelta(days=2)  # 2일 후 도착
        
        for item in items:
            product_name = item[0]
            order_quantity = int(item[1])
            unit_price = float(item[2])
            total_cost = float(item[3])
            
            # 3-1. inventory 테이블 업데이트 (재고 증가)
            cursor.execute("""
                UPDATE inventory 
                SET 
                    quantity = quantity + %s,
                    last_updated = NOW()
                WHERE product_name = %s
            """, (order_quantity, product_name))
            
            # 3-2. orders 테이블에 발주 기록 추가
            cursor.execute("""
                INSERT INTO orders 
                (product_name, quantity_ordered, unit_cost, total_cost, 
                 order_date, delivery_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                product_name,
                order_quantity,
                unit_price,
                total_cost,
                order_date,
                delivery_date,
                'pending'  # 발주 완료, 배송 대기
            ))
        
        # 4. 발주 추천 상태 업데이트
        cursor.execute("""
            UPDATE order_recommendations 
            SET status = 'executed', executed_at = NOW()
            WHERE id = %s
        """, (recommendation_id,))
        
        db.commit()
        
        logger.info(f"✅ 발주 실행 완료 (ID: {recommendation_id})")
        logger.info(f"📦 {len(items)}개 품목 발주")
        logger.info(f"📦 재고 업데이트 완료")
        logger.info(f"📝 발주 기록 생성 완료")
        
        return {
            "status": "success",
            "message": f"발주가 실행되었습니다. {len(items)}개 품목이 발주되었습니다.",
            "recommendation_id": recommendation_id,
            "items_count": len(items),
            "delivery_date": delivery_date.strftime('%Y-%m-%d')
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"발주 실행 오류: {e}")
        if db:
            try:
                db.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 안전하게 연결 닫기
        try:
            if cursor:
                cursor.close()
        except:
            pass
        
        try:
            if db:
                db.close()
        except:
            pass


@app.get("/api/orders/pending")
async def get_pending_orders():
    """발주 대기 목록 조회 (pending 상태의 발주 추천)"""
    try:
        import pymysql
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                recommendation_date,
                total_items,
                total_cost,
                created_at
            FROM order_recommendations
            WHERE status = 'pending'
            ORDER BY recommendation_date DESC, created_at DESC
        """)
        
        pending_orders = []
        for row in cursor.fetchall():
            pending_orders.append({
                "id": row[0],
                "recommendation_date": row[1].strftime('%Y-%m-%d'),
                "total_items": int(row[2]),
                "total_cost": float(row[3]) if row[3] else 0,
                "created_at": row[4].strftime('%Y-%m-%d %H:%M:%S'),
                "status": "pending"
            })
        
        cursor.close()
        db.close()
        
        return {
            "orders": pending_orders,
            "total": len(pending_orders)
        }
    except Exception as e:
        logger.error(f"발주 대기 목록 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations/{recommendation_id}/items")
async def get_recommendation_items(recommendation_id: int):
    """발주 추천의 상세 품목 조회"""
    try:
        import pymysql
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        cursor.execute("""
            SELECT 
                id,
                product_name,
                current_stock,
                safe_stock,
                order_quantity,
                unit_price,
                total_cost,
                reason,
                priority
            FROM order_items
            WHERE recommendation_id = %s
            ORDER BY priority DESC, product_name ASC
        """, (recommendation_id,))
        
        items = []
        for row in cursor.fetchall():
            items.append({
                "id": row[0],
                "product_name": row[1],
                "current_stock": int(row[2]),
                "safe_stock": int(row[3]),
                "order_quantity": int(row[4]),
                "unit_price": float(row[5]) if row[5] else 0,
                "total_cost": float(row[6]) if row[6] else 0,
                "reason": row[7],
                "priority": row[8]
            })
        
        cursor.close()
        db.close()
        
        return {
            "items": items,
            "total": len(items)
        }
    except Exception as e:
        logger.error(f"발주 품목 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# 발주 수정 및 이력 관리 API
# ============================================

@app.put("/api/recommendations/{recommendation_id}/items/{item_id}")
async def update_order_item(recommendation_id: int, item_id: int, quantity: int):
    """발주 품목 수량 수정"""
    db = None
    cursor = None
    
    try:
        import pymysql
        
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        # 1. 품목 정보 조회
        cursor.execute("""
            SELECT unit_price FROM order_items
            WHERE id = %s AND recommendation_id = %s
        """, (item_id, recommendation_id))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="품목을 찾을 수 없습니다.")
        
        unit_price = float(result[0])
        new_total_cost = unit_price * quantity
        
        # 2. 품목 수량 및 금액 업데이트
        cursor.execute("""
            UPDATE order_items
            SET order_quantity = %s, total_cost = %s
            WHERE id = %s AND recommendation_id = %s
        """, (quantity, new_total_cost, item_id, recommendation_id))
        
        # 3. 전체 발주 금액 재계산
        cursor.execute("""
            SELECT SUM(total_cost) FROM order_items
            WHERE recommendation_id = %s
        """, (recommendation_id,))
        
        total_cost = float(cursor.fetchone()[0] or 0)
        
        # 4. 발주 추천 테이블 업데이트
        cursor.execute("""
            UPDATE order_recommendations
            SET total_cost = %s
            WHERE id = %s
        """, (total_cost, recommendation_id))
        
        db.commit()
        
        logger.info(f"✅ 발주 품목 수정: ID={item_id}, 수량={quantity}, 금액={new_total_cost:,.0f}원")
        
        return {
            "status": "success",
            "item_id": item_id,
            "quantity": quantity,
            "item_total_cost": new_total_cost,
            "order_total_cost": total_cost
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"발주 품목 수정 오류: {e}")
        if db:
            try:
                db.rollback()
            except:
                pass
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if db:
            try:
                db.close()
            except:
                pass


@app.get("/api/orders/history")
async def get_order_history(
    start_date: str = None,
    end_date: str = None,
    status: str = None,
    limit: int = 50
):
    """발주 이력 조회"""
    try:
        import pymysql
        
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        # 기본 쿼리
        query = """
            SELECT 
                id,
                recommendation_date,
                total_items,
                total_cost,
                status,
                created_at,
                executed_at
            FROM order_recommendations
            WHERE 1=1
        """
        params = []
        
        # 날짜 필터
        if start_date:
            query += " AND recommendation_date >= %s"
            params.append(start_date)
        if end_date:
            query += " AND recommendation_date <= %s"
            params.append(end_date)
        
        # 상태 필터
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY recommendation_date DESC, created_at DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        
        history = []
        for row in cursor.fetchall():
            history.append({
                "id": row[0],
                "recommendation_date": row[1].strftime('%Y-%m-%d'),
                "total_items": int(row[2]),
                "total_cost": float(row[3]) if row[3] else 0,
                "status": row[4],
                "created_at": row[5].strftime('%Y-%m-%d %H:%M:%S'),
                "executed_at": row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else None
            })
        
        cursor.close()
        db.close()
        
        return {
            "history": history,
            "total": len(history)
        }
    except Exception as e:
        logger.error(f"발주 이력 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/orders/statistics")
async def get_order_statistics(month: str = None):
    """발주 통계"""
    try:
        import pymysql
        from datetime import datetime
        
        # 기본값: 이번 달
        if not month:
            month = datetime.now().strftime('%Y-%m')
        
        db = pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
        cursor = db.cursor()
        
        # 월별 통계
        cursor.execute("""
            SELECT 
                COUNT(*) as total_orders,
                SUM(total_items) as total_items,
                SUM(total_cost) as total_cost,
                SUM(CASE WHEN status = 'executed' THEN 1 ELSE 0 END) as executed_count,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count
            FROM order_recommendations
            WHERE DATE_FORMAT(recommendation_date, '%%Y-%%m') = %s
        """, (month,))
        
        row = cursor.fetchone()
        
        # 일별 발주 금액
        cursor.execute("""
            SELECT 
                DATE(recommendation_date) as date,
                SUM(total_cost) as daily_cost,
                COUNT(*) as daily_count
            FROM order_recommendations
            WHERE DATE_FORMAT(recommendation_date, '%%Y-%%m') = %s
            GROUP BY DATE(recommendation_date)
            ORDER BY date
        """, (month,))

        
        daily_data = []
        for row2 in cursor.fetchall():
            daily_data.append({
                "date": row2[0].strftime('%Y-%m-%d'),
                "cost": float(row2[1]) if row2[1] else 0,
                "count": int(row2[2])
            })
        
        cursor.close()
        db.close()
        
        return {
            "month": month,
            "summary": {
                "total_orders": int(row[0]) if row[0] else 0,
                "total_items": int(row[1]) if row[1] else 0,
                "total_cost": float(row[2]) if row[2] else 0,
                "executed_count": int(row[3]) if row[3] else 0,
                "pending_count": int(row[4]) if row[4] else 0
            },
            "daily_data": daily_data
        }
    except Exception as e:
        logger.error(f"발주 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)