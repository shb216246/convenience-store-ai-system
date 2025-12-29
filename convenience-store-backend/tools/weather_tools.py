"""
날씨 기반 수요 예측 도구들
"""
from langchain.tools import tool
import json
from datetime import datetime, timedelta
from typing import Optional


@tool
def get_weather_forecast(days: int = 3, location: str = "서울") -> str:
    """
    날씨 예보를 조회합니다.
    
    Args:
        days: 예보 일수
        location: 지역
    
    Returns:
        날씨 예보 정보 (JSON 문자열)
    """
    # 실제로는 기상청 API 호출
    forecast = []
    weather_types = ["맑음", "흐림", "비", "눈"]
    
    for i in range(days):
        date = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
        forecast.append({
            "date": date,
            "weather": "비" if i == 1 else "맑음",  # 내일 비 예보
            "temperature": 15 + i,
            "precipitation_prob": 80 if i == 1 else 20,
            "humidity": 75 if i == 1 else 50
        })
    
    return json.dumps({"location": location, "forecast": forecast}, ensure_ascii=False)


@tool
def analyze_weather_impact(product_name: str, weather_condition: str) -> str:
    """
    날씨가 특정 상품 판매에 미치는 영향을 분석합니다.
    
    Args:
        product_name: 상품명
        weather_condition: 날씨 조건 ('비', '눈', '더위', '추위')
    
    Returns:
        날씨 영향 분석 결과
    """
    # 날씨별 상품 영향도 (실제로는 과거 데이터 기반)
    weather_impact = {
        "우산": {
            "비": {"impact": "매우 높음", "multiplier": 8.0, "description": "비올 때 필수품"},
            "눈": {"impact": "높음", "multiplier": 3.0},
            "더위": {"impact": "없음", "multiplier": 1.0},
            "추위": {"impact": "낮음", "multiplier": 1.2}
        },
        "아이스크림": {
            "비": {"impact": "낮음", "multiplier": 0.7},
            "눈": {"impact": "매우 낮음", "multiplier": 0.3},
            "더위": {"impact": "매우 높음", "multiplier": 3.5},
            "추위": {"impact": "낮음", "multiplier": 0.5}
        },
        "컵라면": {
            "비": {"impact": "높음", "multiplier": 1.5, "description": "비오는 날 따뜻한 음식 선호"},
            "눈": {"impact": "높음", "multiplier": 1.8},
            "더위": {"impact": "낮음", "multiplier": 0.8},
            "추위": {"impact": "높음", "multiplier": 1.6}
        },
        "음료수": {
            "비": {"impact": "보통", "multiplier": 1.0},
            "눈": {"impact": "낮음", "multiplier": 0.8},
            "더위": {"impact": "매우 높음", "multiplier": 2.5},
            "추위": {"impact": "낮음", "multiplier": 0.7}
        }
    }
    
    if product_name in weather_impact and weather_condition in weather_impact[product_name]:
        impact_data = weather_impact[product_name][weather_condition]
        result = {
            "product": product_name,
            "weather": weather_condition,
            "impact_level": impact_data["impact"],
            "sales_multiplier": impact_data["multiplier"],
            "description": impact_data.get("description", ""),
            "recommendation": f"{weather_condition} 날씨 시 평소 대비 {int((impact_data['multiplier'] - 1) * 100)}% 수요 변화 예상"
        }
    else:
        result = {
            "product": product_name,
            "weather": weather_condition,
            "impact_level": "보통",
            "sales_multiplier": 1.0,
            "description": "특별한 영향 없음"
        }
    
    return json.dumps(result, ensure_ascii=False)


@tool
def get_weather_based_recommendations(target_date: Optional[str] = None) -> str:
    """
    날씨 기반 발주 추천을 생성합니다.
    
    Args:
        target_date: 날짜 (없으면 내일)
    
    Returns:
        날씨 기반 추천 사항
    """
    if not target_date:
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # 날씨 예보 가져오기
    weather_data = json.loads(get_weather_forecast.invoke({}))
    tomorrow_weather = weather_data["forecast"][1] if len(weather_data["forecast"]) > 1 else weather_data["forecast"][0]
    
    recommendations = []
    
    # 날씨에 따른 추천
    if "비" in tomorrow_weather["weather"]:
        recommendations.extend([
            {"product": "우산", "action": "대폭 증량", "quantity": "+15개", "reason": "비 예보"},
            {"product": "우비", "action": "증량", "quantity": "+10개", "reason": "비 예보"},
            {"product": "컵라면", "action": "증량", "quantity": "+20개", "reason": "비 오는 날 따뜻한 음식 수요 증가"},
            {"product": "아이스크림", "action": "감량", "quantity": "-5개", "reason": "비 오는 날 수요 감소"}
        ])
    elif tomorrow_weather["temperature"] > 25:
        recommendations.extend([
            {"product": "음료수", "action": "대폭 증량", "quantity": "+30개", "reason": "더운 날씨"},
            {"product": "아이스크림", "action": "증량", "quantity": "+20개", "reason": "더운 날씨"},
            {"product": "컵라면", "action": "감량", "quantity": "-10개", "reason": "더운 날 뜨거운 음식 수요 감소"}
        ])
    
    result = {
        "target_date": target_date,
        "weather": tomorrow_weather,
        "recommendations": recommendations
    }
    
    return json.dumps(result, ensure_ascii=False)


@tool
def check_special_events(date: Optional[str] = None) -> str:
    """
    특정 날짜의 특별 이벤트/공휴일을 확인합니다.
    
    Args:
        date: 날짜 (YYYY-MM-DD)
    
    Returns:
        이벤트 정보
    """
    # 실제로는 공휴일 API 조회
    events = {
        "2024-12-25": {"name": "크리스마스", "type": "공휴일", "impact": "높음"},
        "2024-01-01": {"name": "신정", "type": "공휴일", "impact": "높음"},
        "2024-02-14": {"name": "밸런타인데이", "type": "기념일", "impact": "중간"},
    }
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    if date in events:
        return json.dumps(events[date], ensure_ascii=False)
    else:
        return json.dumps({"date": date, "events": "없음"}, ensure_ascii=False)