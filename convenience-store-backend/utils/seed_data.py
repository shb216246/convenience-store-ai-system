"""
샘플 데이터 생성 스크립트
MySQL 데이터베이스와 벡터 스토어에 테스트 데이터를 추가합니다.
"""
import sys
import os
from datetime import datetime, timedelta
import random

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from rag import get_rag


def seed_inventory_data():
    """재고 데이터 생성"""
    db = get_db()
    
    products = [
        ("삼각김밥", "즉석식품", 15, 1500, "2024-12-20"),
        ("도시락", "즉석식품", 8, 5000, "2024-12-18"),
        ("컵라면", "라면", 25, 1200, "2025-03-15"),
        ("우유", "유제품", 12, 2500, "2024-12-25"),
        ("빵", "베이커리", 18, 2000, "2024-12-22"),
        ("음료수", "음료", 35, 1500, "2025-06-30"),
        ("과자", "스낵", 28, 1800, "2025-04-20"),
        ("라면", "라면", 45, 900, "2025-05-10"),
        ("아이스크림", "냉동", 22, 2000, "2025-08-15"),
        ("우산", "생활용품", 3, 5000, "2026-12-31"),
    ]
    
    print("📦 재고 데이터 생성 중...")
    for product_name, category, quantity, unit_price, expiry_date in products:
        query = """
            INSERT INTO inventory (product_name, category, quantity, unit_price, expiry_date)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                quantity = VALUES(quantity),
                unit_price = VALUES(unit_price),
                expiry_date = VALUES(expiry_date)
        """
        db.execute_query(query, (product_name, category, quantity, unit_price, expiry_date))
    
    print(f"✅ {len(products)}개 상품 재고 데이터 생성 완료")
    
    # 벡터 스토어에 인덱싱
    inventory_data = db.fetch_all("SELECT * FROM inventory")
    rag = get_rag()
    rag.index_inventory_data(inventory_data)
    print("✅ 재고 데이터 벡터 인덱싱 완료")


def seed_sales_data():
    """판매 데이터 생성 (최근 30일)"""
    db = get_db()
    rag = get_rag()
    
    products = ["삼각김밥", "도시락", "컵라면", "우유", "빵", "음료수", "과자", "라면"]
    days_of_week = ["월", "화", "수", "목", "금", "토", "일"]
    
    print("📊 판매 데이터 생성 중...")
    sales_count = 0
    
    for i in range(30):  # 최근 30일
        sale_date = datetime.now() - timedelta(days=i)
        weekday = sale_date.weekday()
        day_name = days_of_week[weekday]
        
        for product in products:
            # 요일별 판매 패턴
            base_sales = random.randint(20, 40)
            
            if weekday == 0:  # 월요일
                quantity = int(base_sales * 1.3)
            elif weekday == 4:  # 금요일
                quantity = int(base_sales * 1.2)
            elif weekday in [5, 6]:  # 주말
                quantity = int(base_sales * 0.8)
            else:
                quantity = base_sales
            
            # 시간대별 판매 (아침, 점심, 저녁)
            for hour in [8, 12, 19]:
                sale_time = f"{hour:02d}:{random.randint(0, 59):02d}:00"
                sale_price = random.choice([1500, 2000, 2500, 5000])
                
                query = """
                    INSERT INTO sales (product_name, quantity_sold, sale_price, sale_date, sale_time, day_of_week)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                db.execute_query(query, (
                    product,
                    random.randint(1, 5),
                    sale_price,
                    sale_date.strftime("%Y-%m-%d"),
                    sale_time,
                    day_name
                ))
                sales_count += 1
    
    print(f"✅ {sales_count}개 판매 데이터 생성 완료")
    
    # 벡터 스토어에 인덱싱
    sales_data = db.fetch_all("SELECT * FROM sales ORDER BY sale_date DESC LIMIT 500")
    rag.index_sales_data(sales_data)
    print("✅ 판매 데이터 벡터 인덱싱 완료")


def seed_order_data():
    """발주 데이터 생성"""
    db = get_db()
    rag = get_rag()
    
    products = ["삼각김밥", "도시락", "컵라면", "우유", "빵"]
    
    print("📋 발주 데이터 생성 중...")
    
    for i in range(10):  # 최근 10건의 발주
        order_date = datetime.now() - timedelta(days=i*3)
        delivery_date = order_date + timedelta(days=1)
        
        for product in random.sample(products, 3):
            quantity = random.randint(20, 50)
            unit_cost = random.choice([1000, 1500, 2000])
            total_cost = quantity * unit_cost
            status = random.choice(["completed", "completed", "pending"])
            
            query = """
                INSERT INTO orders (product_name, quantity_ordered, unit_cost, total_cost, order_date, delivery_date, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            db.execute_query(query, (
                product,
                quantity,
                unit_cost,
                total_cost,
                order_date.strftime("%Y-%m-%d"),
                delivery_date.strftime("%Y-%m-%d"),
                status
            ))
    
    print("✅ 발주 데이터 생성 완료")
    
    # 벡터 스토어에 인덱싱
    order_data = db.fetch_all("SELECT * FROM orders ORDER BY order_date DESC")
    rag.index_order_data(order_data)
    print("✅ 발주 데이터 벡터 인덱싱 완료")


def seed_weather_data():
    """날씨 데이터 생성"""
    db = get_db()
    
    weather_conditions = ["맑음", "흐림", "비", "눈", "흐림"]
    
    print("🌤️ 날씨 데이터 생성 중...")
    
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        
        query = """
            INSERT INTO weather_history (date, temperature, weather_condition, precipitation_probability, humidity)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                temperature = VALUES(temperature),
                weather_condition = VALUES(weather_condition)
        """
        db.execute_query(query, (
            date.strftime("%Y-%m-%d"),
            random.randint(5, 25),
            random.choice(weather_conditions),
            random.randint(0, 100),
            random.randint(40, 80)
        ))
    
    print("✅ 날씨 데이터 생성 완료")


def main():
    """메인 실행 함수"""
    print("\n" + "="*60)
    print("🚀 편의점 AI 발주 시스템 - 샘플 데이터 생성")
    print("="*60 + "\n")
    
    try:
        # 데이터베이스 연결 확인
        db = get_db()
        if not db.connection or not db.connection.is_connected():
            print("❌ MySQL 연결 실패. .env 파일의 데이터베이스 설정을 확인하세요.")
            return
        
        print("✅ MySQL 연결 성공\n")
        
        # 샘플 데이터 생성
        seed_inventory_data()
        print()
        seed_sales_data()
        print()
        seed_order_data()
        print()
        seed_weather_data()
        
        print("\n" + "="*60)
        print("✨ 모든 샘플 데이터 생성 완료!")
        print("="*60)
        print("\n데이터베이스와 벡터 스토어가 준비되었습니다.")
        print("이제 백엔드 서버를 실행할 수 있습니다: python main.py\n")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.disconnect()


if __name__ == "__main__":
    main()
