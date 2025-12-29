"""
Data Upload API
CSV upload and data management
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import csv
import io
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from rag import get_rag

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("/upload/sales")
async def upload_sales_csv(file: UploadFile = File(...)) -> Dict:
    """판매 데이터 CSV 업로드"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")
        
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')  # BOM 처리
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        db = get_db()
        rag = get_rag()
        
        rows_processed = 0
        errors = []
        
        # 디버깅: 헤더 출력
        first_row = True
        
        for row in csv_reader:
            try:
                # 첫 번째 행에서 헤더 확인
                if first_row:
                    print(f"CSV Headers: {list(row.keys())}")
                    first_row = False
                
                # 필드 매핑 (한글/영문 모두 지원, 공백 제거)
                product_name = (row.get('product_name') or row.get('product_name ') or 
                               row.get(' product_name') or row.get('상품명') or row.get('제품명'))
                quantity_sold = (row.get('quantity_sold') or row.get('quantity_sold ') or 
                                row.get(' quantity_sold') or row.get('판매수량') or row.get('수량'))
                sale_price = (row.get('sale_price') or row.get('sale_price ') or 
                             row.get(' sale_price') or row.get('판매가격') or row.get('가격'))
                sale_date = (row.get('sale_date') or row.get('sale_date ') or 
                            row.get(' sale_date') or row.get('판매날짜') or row.get('날짜'))
                sale_time = (row.get('sale_time') or row.get('sale_time ') or 
                            row.get(' sale_time') or row.get('판매시간') or row.get('시간') or '12:00:00')
                
                # 필수 필드 확인
                if not all([product_name, quantity_sold, sale_price, sale_date]):
                    errors.append(f"Row {rows_processed + 1}: 필수 필드 누락 (상품명, 판매수량, 판매가격, 판매날짜 필요)")
                    continue
                
                # 날짜 파싱
                try:
                    sale_date_obj = datetime.strptime(sale_date, '%Y-%m-%d').date()
                except:
                    errors.append(f"Row {rows_processed + 1}: 날짜 형식 오류 (YYYY-MM-DD 형식 필요)")
                    continue
                
                # 요일 계산
                days_of_week = ["월", "화", "수", "목", "금", "토", "일"]
                day_of_week = days_of_week[sale_date_obj.weekday()]
                
                # DB에 삽입
                query = """
                    INSERT INTO sales (product_name, quantity_sold, sale_price, sale_date, 
                                      sale_time, day_of_week)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                db.execute_query(query, (
                    product_name,
                    int(quantity_sold),
                    float(sale_price),
                    sale_date_obj,
                    sale_time,
                    day_of_week
                ))
                
                rows_processed += 1
            except Exception as e:
                errors.append(f"Row {rows_processed + 1}: {str(e)}")
        
        # 벡터 스토어 업데이트
        if rows_processed > 0:
            sales_data = db.fetch_all("SELECT * FROM sales ORDER BY sale_date DESC LIMIT 500")
            rag.index_sales_data(sales_data)
        
        return {
            "success": True,
            "rows_processed": rows_processed,
            "errors": errors[:10],  # 최대 10개 에러만 반환
            "total_errors": len(errors)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload/inventory")
async def upload_inventory_csv(file: UploadFile = File(...)) -> Dict:
    """재고 데이터 CSV 업로드"""
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="CSV 파일만 업로드 가능합니다.")
        
        contents = await file.read()
        decoded = contents.decode('utf-8-sig')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        db = get_db()
        rag = get_rag()
        
        rows_processed = 0
        errors = []
        
        for row in csv_reader:
            try:
                # 필드 매핑 (한글/영문 모두 지원)
                product_name = row.get('product_name') or row.get('상품명') or row.get('제품명')
                category = row.get('category') or row.get('카테고리') or row.get('분류')
                quantity = row.get('quantity') or row.get('수량') or row.get('재고')
                unit_price = row.get('unit_price') or row.get('단가') or row.get('가격')
                expiry_date = row.get('expiry_date') or row.get('유통기한') or row.get('만료일') or None
                
                # 필수 필드 확인
                if not all([product_name, category, quantity, unit_price]):
                    errors.append(f"Row {rows_processed + 1}: 필수 필드 누락 (상품명, 카테고리, 수량, 단가 필요)")
                    continue
                
                # DB에 삽입 또는 업데이트
                query = """
                    INSERT INTO inventory (product_name, category, quantity, unit_price, expiry_date)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        quantity = VALUES(quantity),
                        unit_price = VALUES(unit_price),
                        expiry_date = VALUES(expiry_date)
                """
                db.execute_query(query, (
                    product_name,
                    category,
                    int(quantity),
                    float(unit_price),
                    expiry_date
                ))
                
                rows_processed += 1
            except Exception as e:
                errors.append(f"Row {rows_processed + 1}: {str(e)}")
        
        # 벡터 스토어 업데이트
        if rows_processed > 0:
            inventory_data = db.fetch_all("SELECT * FROM inventory")
            rag.index_inventory_data(inventory_data)
        
        return {
            "success": True,
            "rows_processed": rows_processed,
            "errors": errors[:10],
            "total_errors": len(errors)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
