"""
MySQL 데이터베이스 연결 및 관리 모듈
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
import logging

load_dotenv()
logger = logging.getLogger(__name__)


class DatabaseManager:
    """MySQL 데이터베이스 연결 관리자"""
    
    def __init__(self):
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = int(os.getenv("MYSQL_PORT", "3306"))
        self.user = os.getenv("MYSQL_USER", "root")
        self.password = os.getenv("MYSQL_PASSWORD", "")
        self.database = os.getenv("MYSQL_DATABASE", "convenience_store")
        self.connection: Optional[mysql.connector.MySQLConnection] = None
    
    def connect(self) -> bool:
        """데이터베이스 연결"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                logger.info(f"MySQL 데이터베이스 연결 성공: {self.database}")
                return True
        except Error as e:
            logger.error(f"MySQL 연결 오류: {e}")
            return False
    
    def disconnect(self):
        """데이터베이스 연결 종료"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL 연결 종료")
    
    def execute_query(self, query: str, params: tuple = None) -> bool:
        """쿼리 실행 (INSERT, UPDATE, DELETE)"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            self.connection.commit()
            cursor.close()
            return True
        except Error as e:
            logger.error(f"쿼리 실행 오류: {e}")
            return False
    
    def fetch_all(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """쿼리 실행 및 모든 결과 반환"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"쿼리 조회 오류: {e}")
            return []
    
    def fetch_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """쿼리 실행 및 단일 결과 반환"""
        try:
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchone()
            cursor.close()
            return result
        except Error as e:
            logger.error(f"쿼리 조회 오류: {e}")
            return None
    
    def create_tables(self):
        """데이터베이스 테이블 생성"""
        tables = {
            "inventory": """
                CREATE TABLE IF NOT EXISTS inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    product_name VARCHAR(100) NOT NULL,
                    category VARCHAR(50),
                    quantity INT NOT NULL DEFAULT 0,
                    unit_price DECIMAL(10, 2),
                    expiry_date DATE,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_product_name (product_name),
                    INDEX idx_category (category)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            "sales": """
                CREATE TABLE IF NOT EXISTS sales (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    product_name VARCHAR(100) NOT NULL,
                    quantity_sold INT NOT NULL,
                    sale_price DECIMAL(10, 2),
                    sale_date DATE NOT NULL,
                    sale_time TIME,
                    day_of_week VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_product_name (product_name),
                    INDEX idx_sale_date (sale_date),
                    INDEX idx_day_of_week (day_of_week)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            "orders": """
                CREATE TABLE IF NOT EXISTS orders (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    product_name VARCHAR(100) NOT NULL,
                    quantity_ordered INT NOT NULL,
                    unit_cost DECIMAL(10, 2),
                    total_cost DECIMAL(10, 2),
                    order_date DATE NOT NULL,
                    delivery_date DATE,
                    status VARCHAR(20) DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_product_name (product_name),
                    INDEX idx_order_date (order_date),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            "weather_history": """
                CREATE TABLE IF NOT EXISTS weather_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    date DATE NOT NULL,
                    temperature DECIMAL(5, 2),
                    weather_condition VARCHAR(50),
                    precipitation_probability INT,
                    humidity INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_date (date),
                    INDEX idx_weather_condition (weather_condition)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """,
            "chat_history": """
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL,
                    user_message TEXT NOT NULL,
                    assistant_message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_session_id (session_id),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
        }
        
        for table_name, create_query in tables.items():
            if self.execute_query(create_query):
                logger.info(f"테이블 생성/확인 완료: {table_name}")
            else:
                logger.error(f"테이블 생성 실패: {table_name}")


# 전역 데이터베이스 인스턴스
_db_instance: Optional[DatabaseManager] = None


def get_db() -> DatabaseManager:
    """데이터베이스 인스턴스 싱글톤"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager()
        if _db_instance.connect():
            _db_instance.create_tables()
    return _db_instance
