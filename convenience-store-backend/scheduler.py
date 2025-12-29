"""
자동 발주 스케줄러 (개선 버전)
매일 정해진 시간에 발주안을 자동으로 생성하고 order_items까지 저장
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import json
import logging
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class AutoOrderScheduler:
    """자동 발주 스케줄러"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(timezone='Asia/Seoul')
        self.coordinator = None
        self.is_running = False
        
    def set_coordinator(self, coordinator):
        """Coordinator Agent 설정"""
        self.coordinator = coordinator
        
    def get_db_connection(self):
        """DB 연결"""
        return pymysql.connect(
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE", "store_order"),
            charset='utf8mb4'
        )
    
    def create_tables(self):
        """필요한 테이블 생성"""
        db = self.get_db_connection()
        cursor = db.cursor()
        
        try:
            # order_recommendations 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_recommendations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    recommendation_date DATE NOT NULL,
                    inventory_analysis TEXT,
                    sales_analysis TEXT,
                    weather_analysis TEXT,
                    final_recommendation TEXT,
                    total_items INT DEFAULT 0,
                    total_cost DECIMAL(10,2) DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    executed_at TIMESTAMP NULL,
                    INDEX idx_date (recommendation_date),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # order_items 테이블
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    recommendation_id INT NOT NULL,
                    product_name VARCHAR(100) NOT NULL,
                    current_stock INT DEFAULT 0,
                    safe_stock INT DEFAULT 0,
                    order_quantity INT NOT NULL,
                    unit_price DECIMAL(10,2) DEFAULT 0,
                    total_cost DECIMAL(10,2) DEFAULT 0,
                    reason TEXT,
                    priority VARCHAR(20) DEFAULT 'medium',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    INDEX idx_recommendation (recommendation_id),
                    INDEX idx_product (product_name),
                    
                    FOREIGN KEY (recommendation_id) 
                        REFERENCES order_recommendations(id) 
                        ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            db.commit()
            logger.info("✅ 테이블 생성/확인 완료 (order_recommendations, order_items)")
        except Exception as e:
            logger.error(f"테이블 생성 오류: {e}")
        finally:
            cursor.close()
            db.close()
    
    def generate_and_save_recommendation(self):
        """발주 추천 생성 및 저장 (order_items 포함)"""
        try:
            logger.info("🤖 자동 발주 추천 생성 시작...")
            
            if not self.coordinator:
                logger.error("❌ Coordinator가 설정되지 않았습니다.")
                return
            
            # 발주 추천 생성
            result = self.coordinator.generate_order_recommendation(
                "내일 발주를 위한 자동 추천을 생성해주세요."
            )
            
            # DB에 저장
            db = self.get_db_connection()
            cursor = db.cursor()
            
            try:
                # 추천 내용 파싱
                inventory_analysis = result.get('inventory_analysis', '')
                sales_analysis = result.get('sales_analysis', '')
                weather_analysis = result.get('weather_analysis', '')
                final_recommendation = result.get('final_recommendation', '')
                
                # order_items에서 total_items와 total_cost 가져오기
                order_items = result.get('order_items', [])
                total_items = len(order_items)
                total_cost = sum(item.get('total_cost', 0) for item in order_items)
                
                # order_recommendations 저장
                cursor.execute("""
                    INSERT INTO order_recommendations 
                    (recommendation_date, inventory_analysis, sales_analysis, 
                     weather_analysis, final_recommendation, total_items, total_cost, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    datetime.now().date(),
                    inventory_analysis[:5000] if len(inventory_analysis) > 5000 else inventory_analysis,
                    sales_analysis[:5000] if len(sales_analysis) > 5000 else sales_analysis,
                    weather_analysis[:5000] if len(weather_analysis) > 5000 else weather_analysis,
                    final_recommendation[:5000] if len(final_recommendation) > 5000 else final_recommendation,
                    total_items,
                    total_cost,
                    'pending'
                ))
                
                recommendation_id = cursor.lastrowid
                
                # order_items 저장
                if order_items:
                    for item in order_items:
                        cursor.execute("""
                            INSERT INTO order_items
                            (recommendation_id, product_name, current_stock, safe_stock,
                             order_quantity, unit_price, total_cost, reason, priority)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            recommendation_id,
                            item.get('product_name', ''),
                            item.get('current_stock', 0),
                            item.get('safe_stock', 0),
                            item.get('order_quantity', 0),
                            item.get('unit_price', 0),
                            item.get('total_cost', 0),
                            item.get('reason', '')[:500],  # reason은 500자로 제한
                            item.get('priority', 'medium')
                        ))
                    
                    logger.info(f"✅ 발주 품목 {len(order_items)}개 저장 완료")
                
                db.commit()
                
                logger.info(f"✅ 발주 추천 저장 완료 (ID: {recommendation_id})")
                logger.info(f"📅 추천일: {datetime.now().date()}")
                logger.info(f"📦 총 품목: {total_items}개")
                logger.info(f"💰 총 금액: {total_cost:,.0f}원")
                
            except Exception as e:
                logger.error(f"❌ DB 저장 오류: {e}")
                db.rollback()
                import traceback
                traceback.print_exc()
            finally:
                cursor.close()
                db.close()
                
        except Exception as e:
            logger.error(f"❌ 발주 추천 생성 오류: {e}")
            import traceback
            traceback.print_exc()
    
    def start(self, schedule_time="06:00"):
        """스케줄러 시작"""
        if self.is_running:
            logger.warning("⚠️ 스케줄러가 이미 실행 중입니다.")
            return
        
        # 테이블 생성
        self.create_tables()
        
        # 스케줄 설정
        hour, minute = schedule_time.split(":")
        
        self.scheduler.add_job(
            self.generate_and_save_recommendation,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            id='auto_order_recommendation',
            name='자동 발주 추천 생성',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        
        logger.info(f"✅ 자동 발주 스케줄러 시작됨 (매일 {schedule_time})")
        logger.info("📋 다음 실행 시간: " + str(self.scheduler.get_job('auto_order_recommendation').next_run_time))
    
    def stop(self):
        """스케줄러 중지"""
        if not self.is_running:
            logger.warning("⚠️ 스케줄러가 실행 중이 아닙니다.")
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("⏹️ 자동 발주 스케줄러 중지됨")
    
    def get_status(self):
        """스케줄러 상태 조회"""
        if not self.is_running:
            return {
                "status": "stopped",
                "message": "스케줄러가 중지되어 있습니다."
            }
        
        job = self.scheduler.get_job('auto_order_recommendation')
        
        if job:
            return {
                "status": "running",
                "next_run": str(job.next_run_time),
                "message": f"다음 실행 예정: {job.next_run_time}"
            }
        else:
            return {
                "status": "error",
                "message": "스케줄 작업을 찾을 수 없습니다."
            }
    
    def run_now(self):
        """즉시 실행 (테스트용)"""
        logger.info("🚀 발주 추천 즉시 실행...")
        self.generate_and_save_recommendation()


# 전역 스케줄러 인스턴스
auto_scheduler = AutoOrderScheduler()