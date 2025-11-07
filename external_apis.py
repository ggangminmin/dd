"""
외부 API 연동 모듈
날씨 API (OpenWeatherMap), 뉴스 API (NewsAPI) 통합
"""
import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class WeatherAPI:
    """
    OpenWeatherMap API 연동
    현재 날씨 정보 조회 (한국 지역명 지원)
    """

    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "http://api.openweathermap.org/data/2.5/forecast"

        # 한국 주요 도시 영문명 매핑
        self.korean_cities = {
            '서울': 'Seoul',
            '부산': 'Busan',
            '인천': 'Incheon',
            '대구': 'Daegu',
            '대전': 'Daejeon',
            '광주': 'Gwangju',
            '울산': 'Ulsan',
            '수원': 'Suwon',
            '창원': 'Changwon',
            '성남': 'Seongnam',
            '고양': 'Goyang',
            '용인': 'Yongin',
            '부천': 'Bucheon',
            '안산': 'Ansan',
            '안양': 'Anyang',
            '남양주': 'Namyangju',
            '천안': 'Cheonan',
            '전주': 'Jeonju',
            '제주': 'Jeju',
            '평택': 'Pyeongtaek',
            '시흥': 'Siheung',
            '파주': 'Paju',
            '의정부': 'Uijeongbu',
            '김해': 'Gimhae',
            '청주': 'Cheongju',
            '포항': 'Pohang',
            '춘천': 'Chuncheon',
            '강릉': 'Gangneung',
            '은평구': 'Seoul',  # 서울 구는 서울로 매핑
            '강남구': 'Seoul',
            '송파구': 'Seoul',
            '강서구': 'Seoul',
            '마포구': 'Seoul',
            '광명': 'Seoul',  # 광명시는 서울 인근으로 서울 날씨 제공
            '철산동': 'Seoul',  # 철산동(광명시)은 서울로 매핑
            '하남': 'Seoul',
            '과천': 'Seoul',
            '구리': 'Seoul'
        }

    def is_available(self) -> bool:
        """API 키가 설정되어 있는지 확인"""
        return self.api_key is not None and self.api_key != ""

    def parse_korean_location(self, location_text: str) -> tuple:
        """
        한국어 지역명에서 도시명 추출

        Args:
            location_text: 지역명 (예: "서울시 은평구", "경기도 광명시 철산동")

        Returns:
            (영문 도시명, 원본 지역명)
        """
        # 공백 및 특수문자 제거
        location_text = location_text.replace(' ', '').replace(',', '')

        # 시/도/군/구/동 제거
        for suffix in ['특별시', '광역시', '특별자치시', '도', '시', '군', '구', '읍', '면', '동']:
            location_text = location_text.replace(suffix, ' ')

        # 분리된 단어들
        parts = location_text.split()

        # 매핑 테이블에서 찾기
        for part in parts:
            if part in self.korean_cities:
                return self.korean_cities[part], part

        # 기본값
        return 'Seoul', '서울'

    def get_weather(self, location_input: str = "서울", lang: str = "kr") -> Optional[str]:
        """
        현재 날씨 정보 조회 (한국 지역명 지원)

        Args:
            location_input: 지역명 (한글/영문 모두 지원)
            lang: 언어 (kr=한국어, en=영어)

        Returns:
            날씨 정보 텍스트 또는 None (오류 시)
        """
        if not self.is_available():
            return "⚠️ 날씨 API 키가 설정되지 않았습니다. .env 파일에 OPENWEATHER_API_KEY를 추가해주세요."

        try:
            # 한국어 지역명 처리
            if any(ord(char) > 127 for char in location_input):  # 한글 포함 여부
                city_en, city_kr = self.parse_korean_location(location_input)
            else:
                city_en = location_input
                city_kr = location_input

            # 현재 날씨 조회
            weather_params = {
                'q': f"{city_en},KR",
                'appid': self.api_key,
                'units': 'metric',
                'lang': lang
            }

            weather_response = requests.get(self.base_url, params=weather_params, timeout=5)
            weather_response.raise_for_status()
            weather_data = weather_response.json()

            # 5일 예보 조회 (3시간 단위) - 강수확률 정보 포함
            forecast_params = {
                'q': f"{city_en},KR",
                'appid': self.api_key,
                'units': 'metric',
                'lang': lang,
                'cnt': 1  # 가장 최근 예보만
            }

            forecast_response = requests.get(self.forecast_url, params=forecast_params, timeout=5)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # 현재 날씨 정보 추출
            weather_desc = weather_data['weather'][0]['description']
            temp = weather_data['main']['temp']
            feels_like = weather_data['main']['feels_like']
            humidity = weather_data['main']['humidity']
            wind_speed = weather_data['wind']['speed']
            pressure = weather_data['main']['pressure']

            # 강수 정보
            rain_1h = weather_data.get('rain', {}).get('1h', 0)
            snow_1h = weather_data.get('snow', {}).get('1h', 0)

            # 강수확률 (예보 데이터에서)
            rain_prob = 0
            if forecast_data.get('list') and len(forecast_data['list']) > 0:
                rain_prob = forecast_data['list'][0].get('pop', 0) * 100  # 0~1 값을 퍼센트로

            # 구름 양
            cloudiness = weather_data.get('clouds', {}).get('all', 0)

            # 상세 정보 포맷팅
            weather_text = f"""🌤️ **{location_input} 실시간 날씨**

📍 위치: {city_kr} ({city_en})
🌡️ 기온: {temp}°C (체감: {feels_like}°C)
💧 습도: {humidity}%
🌧️ 강수확률: {rain_prob:.0f}%
💨 풍속: {wind_speed}m/s
☁️ 구름: {cloudiness}%
🔽 기압: {pressure}hPa
☔ 강수량: {rain_1h}mm/h
❄️ 적설량: {snow_1h}mm/h

날씨 상태: {weather_desc}"""

            return weather_text

        except requests.exceptions.RequestException as e:
            print(f"날씨 API 오류: {e}")
            return f"⚠️ '{location_input}' 지역의 날씨 정보를 가져오는 중 오류가 발생했습니다."
        except KeyError as e:
            print(f"날씨 데이터 파싱 오류: {e}")
            return "⚠️ 날씨 데이터를 처리하는 중 오류가 발생했습니다."

    def get_weather_by_location(self, lat: float, lon: float, lang: str = "kr") -> Optional[str]:
        """
        위도/경도로 날씨 정보 조회

        Args:
            lat: 위도
            lon: 경도
            lang: 언어

        Returns:
            날씨 정보 텍스트 또는 None
        """
        if not self.is_available():
            return "⚠️ 날씨 API 키가 설정되지 않았습니다."

        try:
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'lang': lang
            }

            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            weather_desc = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']

            weather_text = f"""🌤️ **현재 위치 날씨**

날씨: {weather_desc}
온도: {temp}°C (체감: {feels_like}°C)
습도: {humidity}%"""

            return weather_text

        except Exception as e:
            print(f"위치 기반 날씨 조회 오류: {e}")
            return "⚠️ 날씨 정보를 가져오는 중 오류가 발생했습니다."


class NewsAPI:
    """
    NewsAPI 연동
    최신 뉴스 헤드라인 조회
    """

    def __init__(self):
        self.api_key = os.getenv('NEWS_API_KEY')
        self.base_url = "https://newsapi.org/v2/top-headlines"

    def is_available(self) -> bool:
        """API 키가 설정되어 있는지 확인"""
        return self.api_key is not None and self.api_key != ""

    def get_top_news(self, country: str = "kr", category: Optional[str] = None, count: int = 1) -> Optional[str]:
        """
        최신 뉴스 헤드라인 조회 (한국 뉴스는 Everything API 사용)

        Args:
            country: 국가 코드 (kr=한국, us=미국 등)
            category: 카테고리 (business, entertainment, health, science, sports, technology)
            count: 가져올 뉴스 개수

        Returns:
            뉴스 정보 텍스트 또는 None
        """
        if not self.is_available():
            return "⚠️ 뉴스 API 키가 설정되지 않았습니다. .env 파일에 NEWS_API_KEY를 추가해주세요."

        try:
            # 한국 뉴스는 Everything API 사용 (Top Headlines에 한국 뉴스가 없음)
            if country == "kr":
                everything_url = "https://newsapi.org/v2/everything"
                params = {
                    'q': '한국',  # 한국 관련 뉴스 검색
                    'language': 'ko',  # 한국어
                    'sortBy': 'publishedAt',  # 최신순
                    'apiKey': self.api_key,
                    'pageSize': count
                }
                response = requests.get(everything_url, params=params, timeout=5)
            else:
                # 다른 국가는 Top Headlines 사용
                params = {
                    'country': country,
                    'apiKey': self.api_key,
                    'pageSize': count
                }
                if category:
                    params['category'] = category
                response = requests.get(self.base_url, params=params, timeout=5)

            response.raise_for_status()
            data = response.json()

            if data['status'] != 'ok' or not data.get('articles'):
                return "📰 현재 표시할 뉴스가 없습니다."

            # 첫 번째 뉴스만 가져오기
            article = data['articles'][0]

            title = article.get('title', '제목 없음')
            description = article.get('description', '내용 없음')
            source = article.get('source', {}).get('name', '출처 불명')
            url = article.get('url', '')
            published_at = article.get('publishedAt', '')

            # 날짜 포맷팅
            if published_at:
                from datetime import datetime
                try:
                    dt = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
                    published_at = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass

            news_text = f"""📰 **최신 뉴스**

제목: {title}

{description}

출처: {source}
시간: {published_at}
링크: {url}"""

            return news_text

        except requests.exceptions.RequestException as e:
            print(f"뉴스 API 오류: {e}")
            return "⚠️ 뉴스 정보를 가져오는 중 오류가 발생했습니다."
        except Exception as e:
            print(f"뉴스 데이터 파싱 오류: {e}")
            return "⚠️ 뉴스 데이터를 처리하는 중 오류가 발생했습니다."

    def search_news(self, query: str, language: str = "kr", count: int = 1) -> Optional[str]:
        """
        키워드로 뉴스 검색

        Args:
            query: 검색 키워드
            language: 언어 코드
            count: 가져올 뉴스 개수

        Returns:
            뉴스 정보 텍스트
        """
        if not self.is_available():
            return "⚠️ 뉴스 API 키가 설정되지 않았습니다."

        try:
            search_url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': language,
                'apiKey': self.api_key,
                'pageSize': count,
                'sortBy': 'publishedAt'
            }

            response = requests.get(search_url, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()

            if data['status'] != 'ok' or not data.get('articles'):
                return f"📰 '{query}' 관련 뉴스를 찾을 수 없습니다."

            article = data['articles'][0]
            title = article.get('title', '제목 없음')
            description = article.get('description', '내용 없음')
            source = article.get('source', {}).get('name', '출처 불명')

            news_text = f"""📰 **'{query}' 검색 결과**

제목: {title}

{description}

출처: {source}"""

            return news_text

        except Exception as e:
            print(f"뉴스 검색 오류: {e}")
            return "⚠️ 뉴스 검색 중 오류가 발생했습니다."


class ExternalAPIManager:
    """
    외부 API 관리자
    날씨와 뉴스 API를 통합 관리
    """

    def __init__(self):
        self.weather_api = WeatherAPI()
        self.news_api = NewsAPI()

    def check_availability(self) -> Dict[str, bool]:
        """API 사용 가능 여부 확인"""
        return {
            'weather': self.weather_api.is_available(),
            'news': self.news_api.is_available()
        }

    def process_command(self, message: str) -> Optional[str]:
        """
        사용자 메시지에서 명령 감지 및 처리

        Args:
            message: 사용자 메시지

        Returns:
            API 응답 또는 None (명령이 없을 경우)
        """
        message_lower = message.lower()

        # 날씨 명령 감지
        if any(keyword in message_lower for keyword in ['날씨', '기온', '날씨알려줘', '날씨어때']):
            # 지역명 추출 (더 정교한 패턴)
            location = "서울"  # 기본값

            # '날씨' 키워드 이전의 텍스트를 지역명으로 추출
            for keyword in ['날씨', '기온']:
                if keyword in message:
                    parts = message.split(keyword)[0].strip()
                    if parts:
                        # 불필요한 단어 제거
                        parts = parts.replace('의', '').replace('은', '').replace('는', '').strip()
                        if parts:
                            location = parts
                            break

            # 명시적인 지역명이 포함된 경우
            if not location or location == "서울":
                if '부산' in message:
                    location = "부산"
                elif '인천' in message:
                    location = "인천"
                elif '대구' in message:
                    location = "대구"
                elif '대전' in message:
                    location = "대전"
                elif '광주' in message:
                    location = "광주"
                elif '울산' in message:
                    location = "울산"
                elif '제주' in message:
                    location = "제주"
                elif '은평구' in message:
                    location = "서울시 은평구"
                elif '광명' in message or '철산동' in message:
                    location = "경기도 광명시"

            return self.weather_api.get_weather(location)

        # 뉴스 명령 감지
        if any(keyword in message_lower for keyword in ['뉴스', '최신뉴스', '뉴스알려줘', '헤드라인']):
            return self.news_api.get_top_news()

        return None
