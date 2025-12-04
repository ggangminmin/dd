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

        # 작은 도시를 가까운 큰 도시로 매핑 (OpenWeatherMap이 인식하지 못하는 경우)
        self.city_fallback = {
            # 경기도 - 서울 인근
            '광명': '서울',
            '광명시': '서울',
            '과천': '서울',
            '과천시': '서울',
            '구리': '서울',
            '구리시': '서울',
            '군포': '수원',
            '군포시': '수원',
            '하남': '서울',
            '하남시': '서울',
            '의왕': '수원',
            '의왕시': '수원',
            '오산': '수원',
            '오산시': '수원',
            '안성': '평택',
            '안성시': '평택',
            '이천': '수원',
            '이천시': '수원',
            '여주': '수원',
            '여주시': '수원',
            '양평': '수원',
            '양평군': '수원',
            '가평': '춘천',
            '가평군': '춘천',
            '연천': '서울',
            '연천군': '서울',
            '포천': '서울',
            '포천시': '서울',
            '동두천': '서울',
            '동두천시': '서울',
            '의정부': '서울',
            '의정부시': '서울',

            # 강원도
            '태백': '강릉',
            '태백시': '강릉',
            '삼척': '강릉',
            '삼척시': '강릉',
            '속초': '강릉',
            '속초시': '강릉',
            '동해': '강릉',
            '동해시': '강릉',

            # 충청도
            '제천': '청주',
            '제천시': '청주',
            '계룡': '대전',
            '계룡시': '대전',

            # 경상도
            '상주': '구미',
            '상주시': '구미',
            '문경': '구미',
            '문경시': '구미',
            '영천': '경주',
            '영천시': '경주',
            '경산': '대구',
            '경산시': '대구',
            '밀양': '창원',
            '밀양시': '창원',
            '사천': '진주',
            '사천시': '진주',
            '거제': '부산',
            '거제시': '부산',
            '통영': '부산',
            '통영시': '부산',

            # 전라도
            '정읍': '전주',
            '정읍시': '전주',
            '남원': '전주',
            '남원시': '전주',
            '김제': '전주',
            '김제시': '전주',
            '나주': '광주',
            '나주시': '광주',

            # 제주도
            '서귀포': '제주',
            '서귀포시': '제주',
        }

        # 도시 영문명 매핑 (한국 + 해외 주요 도시)
        self.korean_cities = {
            # 한국 광역시/특별시 (다양한 표현)
            '서울특별시': 'Seoul',
            '서울시': 'Seoul',
            '서울': 'Seoul',
            '부산광역시': 'Busan',
            '부산시': 'Busan',
            '부산': 'Busan',
            '인천광역시': 'Incheon',
            '인천시': 'Incheon',
            '인천': 'Incheon',
            '대구광역시': 'Daegu',
            '대구시': 'Daegu',
            '대구': 'Daegu',
            '대전광역시': 'Daejeon',
            '대전시': 'Daejeon',
            '대전': 'Daejeon',
            '광주광역시': 'Gwangju',
            '광주시': 'Gwangju',
            '광주': 'Gwangju',
            '울산광역시': 'Ulsan',
            '울산시': 'Ulsan',
            '울산': 'Ulsan',
            '세종특별자치시': 'Sejong',
            '세종시': 'Sejong',
            '세종': 'Sejong',

            # 서울특별시 25개 구
            '종로구': 'Jongno-gu,Seoul',
            '중구': 'Jung-gu,Seoul',
            '용산구': 'Yongsan-gu,Seoul',
            '성동구': 'Seongdong-gu,Seoul',
            '광진구': 'Gwangjin-gu,Seoul',
            '동대문구': 'Dongdaemun-gu,Seoul',
            '중랑구': 'Jungnang-gu,Seoul',
            '성북구': 'Seongbuk-gu,Seoul',
            '강북구': 'Gangbuk-gu,Seoul',
            '도봉구': 'Dobong-gu,Seoul',
            '노원구': 'Nowon-gu,Seoul',
            '은평구': 'Eunpyeong-gu,Seoul',
            '서대문구': 'Seodaemun-gu,Seoul',
            '마포구': 'Mapo-gu,Seoul',
            '양천구': 'Yangcheon-gu,Seoul',
            '강서구': 'Gangseo-gu,Seoul',
            '구로구': 'Guro-gu,Seoul',
            '금천구': 'Geumcheon-gu,Seoul',
            '영등포구': 'Yeongdeungpo-gu,Seoul',
            '동작구': 'Dongjak-gu,Seoul',
            '관악구': 'Gwanak-gu,Seoul',
            '서초구': 'Seocho-gu,Seoul',
            '강남구': 'Gangnam-gu,Seoul',
            '송파구': 'Songpa-gu,Seoul',
            '강동구': 'Gangdong-gu,Seoul',

            # 부산광역시 16개 구/군
            '중구부산': 'Jung-gu,Busan',
            '서구부산': 'Seo-gu,Busan',
            '동구부산': 'Dong-gu,Busan',
            '영도구': 'Yeongdo-gu,Busan',
            '부산진구': 'Busanjin-gu,Busan',
            '동래구': 'Dongnae-gu,Busan',
            '남구부산': 'Nam-gu,Busan',
            '북구부산': 'Buk-gu,Busan',
            '해운대구': 'Haeundae-gu,Busan',
            '사하구': 'Saha-gu,Busan',
            '금정구': 'Geumjeong-gu,Busan',
            '강서구부산': 'Gangseo-gu,Busan',
            '연제구': 'Yeonje-gu,Busan',
            '수영구': 'Suyeong-gu,Busan',
            '사상구': 'Sasang-gu,Busan',
            '기장군': 'Gijang-gun,Busan',

            # 인천광역시 10개 구/군
            '중구인천': 'Jung-gu,Incheon',
            '동구인천': 'Dong-gu,Incheon',
            '미추홀구': 'Michuhol-gu,Incheon',
            '연수구': 'Yeonsu-gu,Incheon',
            '남동구': 'Namdong-gu,Incheon',
            '부평구': 'Bupyeong-gu,Incheon',
            '계양구': 'Gyeyang-gu,Incheon',
            '서구인천': 'Seo-gu,Incheon',
            '강화군': 'Ganghwa-gun,Incheon',
            '옹진군': 'Ongjin-gun,Incheon',

            # 대구광역시 8개 구/군
            '중구대구': 'Jung-gu,Daegu',
            '동구대구': 'Dong-gu,Daegu',
            '서구대구': 'Seo-gu,Daegu',
            '남구대구': 'Nam-gu,Daegu',
            '북구대구': 'Buk-gu,Daegu',
            '수성구': 'Suseong-gu,Daegu',
            '달서구': 'Dalseo-gu,Daegu',
            '달성군': 'Dalseong-gun,Daegu',

            # 대전광역시 5개 구
            '동구대전': 'Dong-gu,Daejeon',
            '중구대전': 'Jung-gu,Daejeon',
            '서구대전': 'Seo-gu,Daejeon',
            '유성구': 'Yuseong-gu,Daejeon',
            '대덕구': 'Daedeok-gu,Daejeon',

            # 광주광역시 5개 구
            '동구광주': 'Dong-gu,Gwangju',
            '서구광주': 'Seo-gu,Gwangju',
            '남구광주': 'Nam-gu,Gwangju',
            '북구광주': 'Buk-gu,Gwangju',
            '광산구': 'Gwangsan-gu,Gwangju',

            # 울산광역시 5개 구/군
            '중구울산': 'Jung-gu,Ulsan',
            '남구울산': 'Nam-gu,Ulsan',
            '동구울산': 'Dong-gu,Ulsan',
            '북구울산': 'Buk-gu,Ulsan',
            '울주군': 'Ulju-gun,Ulsan',

            # 경기도 주요 도시
            '경기도수원시': 'Suwon',
            '경기수원시': 'Suwon',
            '수원시': 'Suwon',
            '수원': 'Suwon',
            '경기도성남시': 'Seongnam',
            '경기성남시': 'Seongnam',
            '성남시': 'Seongnam',
            '성남': 'Seongnam',
            '경기도고양시': 'Goyang',
            '경기고양시': 'Goyang',
            '고양시': 'Goyang',
            '고양': 'Goyang',
            '경기도용인시': 'Yongin',
            '경기용인시': 'Yongin',
            '용인시': 'Yongin',
            '용인': 'Yongin',
            '경기도부천시': 'Bucheon',
            '경기부천시': 'Bucheon',
            '부천시': 'Bucheon',
            '부천': 'Bucheon',
            '경기도안산시': 'Ansan',
            '경기안산시': 'Ansan',
            '안산시': 'Ansan',
            '안산': 'Ansan',
            '경기도안양시': 'Anyang',
            '경기안양시': 'Anyang',
            '안양시': 'Anyang',
            '안양': 'Anyang',
            '경기도남양주시': 'Namyangju',
            '경기남양주시': 'Namyangju',
            '남양주시': 'Namyangju',
            '남양주': 'Namyangju',
            '경기도평택시': 'Pyeongtaek',
            '경기평택시': 'Pyeongtaek',
            '평택시': 'Pyeongtaek',
            '평택': 'Pyeongtaek',
            '경기도시흥시': 'Siheung',
            '경기시흥시': 'Siheung',
            '시흥시': 'Siheung',
            '시흥': 'Siheung',
            '경기도파주시': 'Paju',
            '경기파주시': 'Paju',
            '파주시': 'Paju',
            '파주': 'Paju',
            '경기도의정부시': 'Uijeongbu',
            '경기의정부시': 'Uijeongbu',
            '의정부시': 'Uijeongbu',
            '의정부': 'Uijeongbu',
            '경기도김포시': 'Gimpo',
            '경기김포시': 'Gimpo',
            '김포시': 'Gimpo',
            '김포': 'Gimpo',
            '경기도광명시': 'Gwangmyeong',
            '경기광명시': 'Gwangmyeong',
            '광명시': 'Gwangmyeong',
            '광명': 'Gwangmyeong',
            '경기도광주시': 'Gwangju,Gyeonggi',
            '경기광주시': 'Gwangju,Gyeonggi',
            '광주경기': 'Gwangju,Gyeonggi',
            '경기도군포시': 'Gunpo',
            '경기군포시': 'Gunpo',
            '군포시': 'Gunpo',
            '군포': 'Gunpo',
            '경기도하남시': 'Hanam',
            '경기하남시': 'Hanam',
            '하남시': 'Hanam',
            '하남': 'Hanam',
            '경기도오산시': 'Osan',
            '경기오산시': 'Osan',
            '오산시': 'Osan',
            '오산': 'Osan',
            '경기도양주시': 'Yangju',
            '경기양주시': 'Yangju',
            '양주시': 'Yangju',
            '양주': 'Yangju',
            '경기도이천시': 'Icheon',
            '경기이천시': 'Icheon',
            '이천시': 'Icheon',
            '이천': 'Icheon',
            '경기도구리시': 'Guri',
            '경기구리시': 'Guri',
            '구리시': 'Guri',
            '구리': 'Guri',
            '경기도안성시': 'Anseong',
            '경기안성시': 'Anseong',
            '안성시': 'Anseong',
            '안성': 'Anseong',
            '경기도포천시': 'Pocheon',
            '경기포천시': 'Pocheon',
            '포천시': 'Pocheon',
            '포천': 'Pocheon',
            '경기도의왕시': 'Uiwang',
            '경기의왕시': 'Uiwang',
            '의왕시': 'Uiwang',
            '의왕': 'Uiwang',
            '경기도양평군': 'Yangpyeong',
            '경기양평군': 'Yangpyeong',
            '양평군': 'Yangpyeong',
            '양평': 'Yangpyeong',
            '경기도여주시': 'Yeoju',
            '경기여주시': 'Yeoju',
            '여주시': 'Yeoju',
            '여주': 'Yeoju',
            '경기도동두천시': 'Dongducheon',
            '경기동두천시': 'Dongducheon',
            '동두천시': 'Dongducheon',
            '동두천': 'Dongducheon',
            '경기도과천시': 'Gwacheon',
            '경기과천시': 'Gwacheon',
            '과천시': 'Gwacheon',
            '과천': 'Gwacheon',
            '경기도가평군': 'Gapyeong',
            '경기가평군': 'Gapyeong',
            '가평군': 'Gapyeong',
            '가평': 'Gapyeong',
            '경기도연천군': 'Yeoncheon',
            '경기연천군': 'Yeoncheon',
            '연천군': 'Yeoncheon',
            '연천': 'Yeoncheon',

            # 강원도
            '강원도춘천시': 'Chuncheon',
            '강원춘천시': 'Chuncheon',
            '춘천시': 'Chuncheon',
            '춘천': 'Chuncheon',
            '강원도원주시': 'Wonju',
            '강원원주시': 'Wonju',
            '원주시': 'Wonju',
            '원주': 'Wonju',
            '강원도강릉시': 'Gangneung',
            '강원강릉시': 'Gangneung',
            '강릉시': 'Gangneung',
            '강릉': 'Gangneung',
            '강원도동해시': 'Donghae',
            '강원동해시': 'Donghae',
            '동해시': 'Donghae',
            '동해': 'Donghae',
            '강원도태백시': 'Taebaek',
            '강원태백시': 'Taebaek',
            '태백시': 'Taebaek',
            '태백': 'Taebaek',
            '강원도속초시': 'Sokcho',
            '강원속초시': 'Sokcho',
            '속초시': 'Sokcho',
            '속초': 'Sokcho',
            '강원도삼척시': 'Samcheok',
            '강원삼척시': 'Samcheok',
            '삼척시': 'Samcheok',
            '삼척': 'Samcheok',

            # 충청북도
            '충청북도청주시': 'Cheongju',
            '충북청주시': 'Cheongju',
            '청주시': 'Cheongju',
            '청주': 'Cheongju',
            '충청북도충주시': 'Chungju',
            '충북충주시': 'Chungju',
            '충주시': 'Chungju',
            '충주': 'Chungju',
            '충청북도제천시': 'Jecheon',
            '충북제천시': 'Jecheon',
            '제천시': 'Jecheon',
            '제천': 'Jecheon',

            # 충청남도
            '충청남도천안시': 'Cheonan',
            '충남천안시': 'Cheonan',
            '천안시': 'Cheonan',
            '천안': 'Cheonan',
            '충청남도공주시': 'Gongju',
            '충남공주시': 'Gongju',
            '공주시': 'Gongju',
            '공주': 'Gongju',
            '충청남도보령시': 'Boryeong',
            '충남보령시': 'Boryeong',
            '보령시': 'Boryeong',
            '보령': 'Boryeong',
            '충청남도아산시': 'Asan',
            '충남아산시': 'Asan',
            '아산시': 'Asan',
            '아산': 'Asan',
            '충청남도서산시': 'Seosan',
            '충남서산시': 'Seosan',
            '서산시': 'Seosan',
            '서산': 'Seosan',
            '충청남도논산시': 'Nonsan',
            '충남논산시': 'Nonsan',
            '논산시': 'Nonsan',
            '논산': 'Nonsan',
            '충청남도계룡시': 'Gyeryong',
            '충남계룡시': 'Gyeryong',
            '계룡시': 'Gyeryong',
            '계룡': 'Gyeryong',
            '충청남도당진시': 'Dangjin',
            '충남당진시': 'Dangjin',
            '당진시': 'Dangjin',
            '당진': 'Dangjin',

            # 전라북도
            '전라북도전주시': 'Jeonju',
            '전북전주시': 'Jeonju',
            '전주시': 'Jeonju',
            '전주': 'Jeonju',
            '전라북도군산시': 'Gunsan',
            '전북군산시': 'Gunsan',
            '군산시': 'Gunsan',
            '군산': 'Gunsan',
            '전라북도익산시': 'Iksan',
            '전북익산시': 'Iksan',
            '익산시': 'Iksan',
            '익산': 'Iksan',
            '전라북도정읍시': 'Jeongeup',
            '전북정읍시': 'Jeongeup',
            '정읍시': 'Jeongeup',
            '정읍': 'Jeongeup',
            '전라북도남원시': 'Namwon',
            '전북남원시': 'Namwon',
            '남원시': 'Namwon',
            '남원': 'Namwon',
            '전라북도김제시': 'Gimje',
            '전북김제시': 'Gimje',
            '김제시': 'Gimje',
            '김제': 'Gimje',

            # 전라남도
            '전라남도목포시': 'Mokpo',
            '전남목포시': 'Mokpo',
            '목포시': 'Mokpo',
            '목포': 'Mokpo',
            '전라남도여수시': 'Yeosu',
            '전남여수시': 'Yeosu',
            '여수시': 'Yeosu',
            '여수': 'Yeosu',
            '전라남도순천시': 'Suncheon',
            '전남순천시': 'Suncheon',
            '순천시': 'Suncheon',
            '순천': 'Suncheon',
            '전라남도나주시': 'Naju',
            '전남나주시': 'Naju',
            '나주시': 'Naju',
            '나주': 'Naju',
            '전라남도광양시': 'Gwangyang',
            '전남광양시': 'Gwangyang',
            '광양시': 'Gwangyang',
            '광양': 'Gwangyang',

            # 경상북도
            '경상북도포항시': 'Pohang',
            '경북포항시': 'Pohang',
            '포항시': 'Pohang',
            '포항': 'Pohang',
            '경상북도경주시': 'Gyeongju',
            '경북경주시': 'Gyeongju',
            '경주시': 'Gyeongju',
            '경주': 'Gyeongju',
            '경상북도김천시': 'Gimcheon',
            '경북김천시': 'Gimcheon',
            '김천시': 'Gimcheon',
            '김천': 'Gimcheon',
            '경상북도안동시': 'Andong',
            '경북안동시': 'Andong',
            '안동시': 'Andong',
            '안동': 'Andong',
            '경상북도구미시': 'Gumi',
            '경북구미시': 'Gumi',
            '구미시': 'Gumi',
            '구미': 'Gumi',
            '경상북도영주시': 'Yeongju',
            '경북영주시': 'Yeongju',
            '영주시': 'Yeongju',
            '영주': 'Yeongju',
            '경상북도영천시': 'Yeongcheon',
            '경북영천시': 'Yeongcheon',
            '영천시': 'Yeongcheon',
            '영천': 'Yeongcheon',
            '경상북도상주시': 'Sangju',
            '경북상주시': 'Sangju',
            '상주시': 'Sangju',
            '상주': 'Sangju',
            '경상북도문경시': 'Mungyeong',
            '경북문경시': 'Mungyeong',
            '문경시': 'Mungyeong',
            '문경': 'Mungyeong',
            '경상북도경산시': 'Gyeongsan',
            '경북경산시': 'Gyeongsan',
            '경산시': 'Gyeongsan',
            '경산': 'Gyeongsan',

            # 경상남도
            '경상남도창원시': 'Changwon',
            '경남창원시': 'Changwon',
            '창원시': 'Changwon',
            '창원': 'Changwon',
            '경상남도김해시': 'Gimhae',
            '경남김해시': 'Gimhae',
            '김해시': 'Gimhae',
            '김해': 'Gimhae',
            '경상남도진주시': 'Jinju',
            '경남진주시': 'Jinju',
            '진주시': 'Jinju',
            '진주': 'Jinju',
            '경상남도양산시': 'Yangsan',
            '경남양산시': 'Yangsan',
            '양산시': 'Yangsan',
            '양산': 'Yangsan',
            '경상남도거제시': 'Geoje',
            '경남거제시': 'Geoje',
            '거제시': 'Geoje',
            '거제': 'Geoje',
            '경상남도통영시': 'Tongyeong',
            '경남통영시': 'Tongyeong',
            '통영시': 'Tongyeong',
            '통영': 'Tongyeong',
            '경상남도사천시': 'Sacheon',
            '경남사천시': 'Sacheon',
            '사천시': 'Sacheon',
            '사천': 'Sacheon',
            '경상남도밀양시': 'Miryang',
            '경남밀양시': 'Miryang',
            '밀양시': 'Miryang',
            '밀양': 'Miryang',

            # 제주특별자치도
            '제주특별자치도제주시': 'Jeju',
            '제주도제주시': 'Jeju',
            '제주시': 'Jeju',
            '제주': 'Jeju',
            '제주특별자치도서귀포시': 'Seogwipo',
            '제주도서귀포시': 'Seogwipo',
            '서귀포시': 'Seogwipo',
            '서귀포': 'Seogwipo',

            # 아시아
            '도쿄': 'Tokyo',
            '오사카': 'Osaka',
            '교토': 'Kyoto',
            '베이징': 'Beijing',
            '상하이': 'Shanghai',
            '홍콩': 'Hong Kong',
            '타이베이': 'Taipei',
            '방콕': 'Bangkok',
            '싱가포르': 'Singapore',
            '하노이': 'Hanoi',
            '호치민': 'Ho Chi Minh City',
            '마닐라': 'Manila',
            '자카르타': 'Jakarta',
            '뉴델리': 'New Delhi',
            '뭄바이': 'Mumbai',

            # 유럽
            '런던': 'London',
            '파리': 'Paris',
            '베를린': 'Berlin',
            '로마': 'Rome',
            '마드리드': 'Madrid',
            '바르셀로나': 'Barcelona',
            '암스테르담': 'Amsterdam',
            '빈': 'Vienna',
            '취리히': 'Zurich',
            '프라하': 'Prague',
            '부다페스트': 'Budapest',
            '바르샤바': 'Warsaw',
            '모스크바': 'Moscow',
            '상트페테르부르크': 'Saint Petersburg',

            # 미주
            '뉴욕': 'New York',
            '로스앤젤레스': 'Los Angeles',
            '샌프란시스코': 'San Francisco',
            '시카고': 'Chicago',
            '워싱턴': 'Washington',
            '보스턴': 'Boston',
            '라스베이거스': 'Las Vegas',
            '시애틀': 'Seattle',
            '토론토': 'Toronto',
            '밴쿠버': 'Vancouver',
            '멕시코시티': 'Mexico City',

            # 오세아니아
            '시드니': 'Sydney',
            '멜버른': 'Melbourne',
            '오클랜드': 'Auckland',

            # 중동/아프리카
            '두바이': 'Dubai',
            '카이로': 'Cairo',
            '이스탄불': 'Istanbul',
            '텔아비브': 'Tel Aviv',
            '리야드': 'Riyadh',
            '도하': 'Doha',
            '아부다비': 'Abu Dhabi',

            # 추가 아시아 도시
            '타이페이': 'Taipei',
            '쿠알라룸푸르': 'Kuala Lumpur',
            '방콕': 'Bangkok',
            '델리': 'Delhi',
            '서울': 'Seoul',
            '부산': 'Busan',

            # 추가 유럽 도시
            '리스본': 'Lisbon',
            '아테네': 'Athens',
            '코펜하겐': 'Copenhagen',
            '오슬로': 'Oslo',
            '스톡홀름': 'Stockholm',
            '헬싱키': 'Helsinki',
            '더블린': 'Dublin',
            '브뤼셀': 'Brussels',

            # 추가 미주 도시
            '마이애미': 'Miami',
            '댈러스': 'Dallas',
            '휴스턴': 'Houston',
            '애틀랜타': 'Atlanta',
            '덴버': 'Denver',
            '피닉스': 'Phoenix',
            '샌디에이고': 'San Diego',
            '포틀랜드': 'Portland',
            '몬트리올': 'Montreal',
            '상파울루': 'Sao Paulo',
            '부에노스아이레스': 'Buenos Aires',
            '리우데자네이루': 'Rio de Janeiro',

            # 추가 오세아니아
            '브리즈번': 'Brisbane',
            '퍼스': 'Perth',
            '웰링턴': 'Wellington'
        }

        # 한국 도시 목록 (KR 국가 코드가 필요한 도시들)
        self.korean_city_names = {
            # 광역시/특별시
            '서울', '부산', '인천', '대구', '대전', '광주', '울산', '세종',

            # 서울 25개 구
            '종로구', '중구', '용산구', '성동구', '광진구', '동대문구', '중랑구',
            '성북구', '강북구', '도봉구', '노원구', '은평구', '서대문구', '마포구',
            '양천구', '강서구', '구로구', '금천구', '영등포구', '동작구', '관악구',
            '서초구', '강남구', '송파구', '강동구',

            # 부산 16개 구/군
            '중구부산', '서구부산', '동구부산', '영도구', '부산진구', '동래구',
            '남구부산', '북구부산', '해운대구', '사하구', '금정구', '강서구부산',
            '연제구', '수영구', '사상구', '기장군',

            # 인천 10개 구/군
            '중구인천', '동구인천', '미추홀구', '연수구', '남동구', '부평구',
            '계양구', '서구인천', '강화군', '옹진군',

            # 대구 8개 구/군
            '중구대구', '동구대구', '서구대구', '남구대구', '북구대구',
            '수성구', '달서구', '달성군',

            # 대전 5개 구
            '동구대전', '중구대전', '서구대전', '유성구', '대덕구',

            # 광주 5개 구
            '동구광주', '서구광주', '남구광주', '북구광주', '광산구',

            # 울산 5개 구/군
            '중구울산', '남구울산', '동구울산', '북구울산', '울주군',

            # 경기도
            '수원', '성남', '고양', '용인', '부천', '안산', '안양', '남양주',
            '평택', '시흥', '파주', '의정부', '김포', '광명', '광주경기', '군포',
            '하남', '오산', '양주', '이천', '구리', '안성', '포천', '의왕',
            '양평', '여주', '동두천', '과천', '가평', '연천',

            # 강원도
            '춘천', '원주', '강릉', '동해', '태백', '속초', '삼척',

            # 충청북도
            '청주', '충주', '제천',

            # 충청남도
            '천안', '공주', '보령', '아산', '서산', '논산', '계룡', '당진',

            # 전라북도
            '전주', '군산', '익산', '정읍', '남원', '김제',

            # 전라남도
            '목포', '여수', '순천', '나주', '광양',

            # 경상북도
            '포항', '경주', '김천', '안동', '구미', '영주', '영천', '상주', '문경', '경산',

            # 경상남도
            '창원', '김해', '진주', '양산', '거제', '통영', '사천', '밀양',

            # 제주
            '제주', '서귀포'
        }

    def is_available(self) -> bool:
        """API 키가 설정되어 있는지 확인"""
        return self.api_key is not None and self.api_key != ""

    def detect_location_in_text(self, text: str) -> Optional[str]:
        """
        텍스트에서 지역명 자동 감지 (한글 + 영문)

        Args:
            text: 사용자 입력 문장

        Returns:
            감지된 지역명 (한글 또는 영문) 또는 None
        """
        if not text:
            return None

        # 1. 한글 지역명 감지
        clean_text = text.replace(' ', '').replace(',', '')
        sorted_keys = sorted(self.korean_cities.keys(), key=len, reverse=True)

        # 2단계 매칭: 먼저 도시명만 추출 (도 이름 제외)
        # 예: "제주도서귀포시" → "서귀포시" 우선
        # 예: "경기도광명시" → "광명시" 우선

        # 1단계: 도 이름이 없는 순수 도시명 찾기 (우선순위 높음)
        for key in sorted_keys:
            if key in clean_text:
                # "도"가 앞에 붙지 않은 순수 도시명
                # 예: "서귀포시", "광명시", "부산", "서울" 등
                if not any(province in key for province in ['경기도', '강원도', '충청북도', '충청남도', '충북', '충남',
                                                              '전라북도', '전라남도', '전북', '전남', '경상북도', '경상남도',
                                                              '경북', '경남', '제주도', '제주특별자치도']):
                    # 단, 단순히 "도"로 끝나는 광역시/도는 제외 (강원도, 경기도 등)
                    if not (key.endswith('도') and len(key) <= 4):
                        return key

        # 2단계: 도 이름 포함된 경우도 매칭 (fallback)
        for key in sorted_keys:
            if key in clean_text:
                return key

        # 2. 영문 지역명 감지 (대소문자 구분 없음)
        # 'weather' 또는 '날씨' 키워드 앞의 단어 추출
        text_lower = text.lower()
        for keyword in ['weather', '날씨', '기온']:
            if keyword in text_lower:
                parts = text.split(keyword)[0].strip()
                if parts:
                    # 마지막 단어를 도시명으로 추출
                    words = parts.split()
                    if words:
                        # 여러 단어일 수 있음 (예: "New York")
                        # 마지막 1-3개 단어 확인
                        for i in range(min(3, len(words)), 0, -1):
                            potential_city = ' '.join(words[-i:])
                            # 영문자로만 구성되어 있고 2글자 이상이면 도시명으로 간주
                            if potential_city.replace(' ', '').isalpha() and len(potential_city) >= 2:
                                return potential_city.title()  # 첫 글자 대문자로
                return None

        # 3. 단순히 영문 도시명만 입력된 경우 (키워드 없이)
        # 예: "Paris", "Tokyo"
        words = text.strip().split()
        if len(words) <= 2:  # 1-2 단어
            potential_city = ' '.join(words)
            if potential_city.replace(' ', '').isalpha() and len(potential_city) >= 3:
                return potential_city.title()

        return None

    def parse_korean_location(self, location_text: str) -> tuple:
        """
        한국어 지역명에서 도시명 추출

        Args:
            location_text: 지역명 (예: "서울시 은평구", "경기도 광명시", "충북 청주시")

        Returns:
            (영문 도시명, 한글 지역명)
        """
        # 원본 저장
        original = location_text

        # 공백 제거 (파싱용)
        clean_text = location_text.replace(' ', '').replace(',', '')

        # 가장 긴 매칭부터 시도 (예: "은평구"가 "평구"보다 우선)
        # 매핑 테이블의 키를 길이 순으로 정렬
        sorted_keys = sorted(self.korean_cities.keys(), key=len, reverse=True)

        for key in sorted_keys:
            if key in clean_text:
                return self.korean_cities[key], key

        # 기본값
        return 'Seoul', '서울'

    def get_nationwide_weather(self) -> str:
        """
        전국 주요 도시 날씨 조회

        Returns:
            전국 주요 도시의 현재 날씨 정보
        """
        major_cities = [
            '서울', '부산', '인천', '대구', '대전', '광주', '울산', '세종',
            '수원', '청주', '전주', '포항', '제주'
        ]

        weather_list = []
        for city in major_cities:
            try:
                weather_data = self.get_weather(city, lang="kr")
                if weather_data:
                    # 간략한 정보만 추출
                    lines = weather_data.split('\n')
                    # 첫 줄과 온도 정보만
                    weather_list.append(f"{city}: {lines[0] if lines else 'N/A'}")
            except:
                continue

        if weather_list:
            return "🌍 전국 주요 도시 날씨\n\n" + "\n".join(weather_list)
        else:
            return "⚠️ 전국 날씨 정보를 가져올 수 없습니다."

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
            # 원본 입력 저장 (상세 주소 표시용)
            original_input = location_input

            # 한국어 지역명 처리
            if any(ord(char) > 127 for char in location_input):  # 한글 포함 여부
                city_en, city_kr = self.parse_korean_location(location_input)

                # Fallback: API가 인식하지 못하는 작은 도시는 가까운 큰 도시로 매핑
                if city_kr in self.city_fallback:
                    fallback_city = self.city_fallback[city_kr]
                    print(f"[날씨 API] '{city_kr}' → '{fallback_city}' (인근 도시로 조회)")
                    # 재귀 호출로 fallback 도시의 날씨 조회
                    result = self.get_weather(fallback_city, lang)
                    # 응답 메시지에 원래 도시명 포함
                    if result and not result.startswith('⚠️'):
                        # "부산 맑음, 15°C..." 형식에서 도시명을 거제로 변경
                        # 첫 번째 공백 이전이 도시명
                        parts = result.split(' ', 1)
                        if len(parts) == 2:
                            weather_part = parts[1]  # "맑음, 15°C..." 부분
                            return f"{original_input} (인근 {fallback_city} 기준) {weather_part}"
                        else:
                            # 파싱 실패 시 원본 그대로 반환
                            return result
                    return result

                # 한국 도시인지 확인하여 국가 코드 결정
                if city_kr in self.korean_city_names:
                    query = f"{city_en},KR"  # 한국 도시만 KR 국가 코드 추가
                else:
                    query = city_en  # 해외 도시는 영문명만 사용
            else:
                city_en = location_input
                city_kr = location_input
                query = city_en  # 영문 도시명은 그대로 사용 (전세계 검색)

            # 현재 날씨 조회
            weather_params = {
                'q': query,
                'appid': self.api_key,
                'units': 'metric',
                'lang': lang
            }

            weather_response = requests.get(self.base_url, params=weather_params, timeout=5)
            weather_response.raise_for_status()
            weather_data = weather_response.json()

            # 5일 예보 조회 (3시간 단위) - 강수확률 정보 포함
            forecast_params = {
                'q': query,
                'appid': self.api_key,
                'units': 'metric',
                'lang': lang,
                'cnt': 1  # 가장 최근 예보만
            }

            forecast_response = requests.get(self.forecast_url, params=forecast_params, timeout=5)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # 현재 날씨 정보 추출
            weather_main = weather_data['weather'][0]['main']  # 영문 날씨 코드
            weather_id = weather_data['weather'][0]['id']  # 날씨 ID

            # 영문 날씨 코드를 한글로 매핑
            weather_kr_map = {
                'Clear': '맑음',
                'Clouds': '흐림',
                'Rain': '비',
                'Drizzle': '이슬비',
                'Thunderstorm': '천둥번개',
                'Snow': '눈',
                'Mist': '안개',
                'Smoke': '연기',
                'Haze': '실안개',
                'Dust': '먼지',
                'Fog': '안개',
                'Sand': '황사',
                'Ash': '화산재',
                'Squall': '돌풍',
                'Tornado': '토네이도'
            }

            # 구름 양에 따라 세부 날씨 결정
            if weather_main == 'Clouds':
                cloudiness = weather_data.get('clouds', {}).get('all', 0)
                if cloudiness < 25:
                    weather_desc = '구름 조금'
                elif cloudiness < 50:
                    weather_desc = '구름 많음'
                else:
                    weather_desc = '흐림'
            else:
                weather_desc = weather_kr_map.get(weather_main, weather_data['weather'][0].get('description', '알 수 없음'))

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

            # 자연스러운 대화형 포맷으로 변경
            # 온도를 반올림하여 정수로 표시
            temp_rounded = round(temp)
            feels_like_rounded = round(feels_like)

            # 조사 없이 간결하게 표시
            weather_text = f"{original_input} {weather_desc}, {temp_rounded}°C (체감 {feels_like_rounded}°C)\n습도 {humidity}%, 강수확률 {rain_prob:.0f}%"

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

    def get_top_news(self, country: str = "kr", category: Optional[str] = None, count: int = 5) -> Optional[str]:
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

            # count 개수만큼 뉴스 가져오기 (중복 필터링 위해 더 많이 가져옴)
            articles = data['articles'][:count * 2]

            from datetime import datetime
            news_items = []
            seen_titles = set()  # 중복 제목 체크
            item_count = 0

            import re

            for article in articles:
                # 이미 count 개수만큼 수집했으면 중단
                if item_count >= count:
                    break

                title = article.get('title', '제목 없음')
                source = article.get('source', {}).get('name', '출처 불명')
                url = article.get('url', '')

                # 제목 정리 (불필요한 특수문자, 기자명 제거)
                title = title.replace('[', '').replace(']', '').replace('|', ' ').strip()
                title = re.sub(r'\s*-\s*[\w\s]+기자\s*$', '', title)
                title = re.sub(r'\s*-\s*[\w\s]+리포터\s*$', '', title)

                # 제목이 너무 길면 80자로 제한
                if len(title) > 80:
                    title = title[:77] + '...'

                # 중복 제목 체크
                if title in seen_titles:
                    continue

                seen_titles.add(title)
                item_count += 1

                # 출처 정리
                source = source.replace('(', '').replace(')', '').replace('[', '').replace(']', '').strip()

                # 표 형식 HTML로 포맷팅 (CSS 클래스 사용)
                news_item = f"""
                <tr>
                    <td>{item_count}</td>
                    <td><a href="{url}" target="_blank" class="news-link">{title}</a></td>
                    <td class="news-source">{source}</td>
                </tr>"""

                news_items.append(news_item)

            # 최종 뉴스 텍스트 (HTML 표 형식 - CSS 클래스 사용)
            news_text = f"""
            <div class="news-table-wrapper">
                <h3 class="news-title">📰 최신 뉴스</h3>
                <table class="news-table">
                    <thead>
                        <tr>
                            <th style="width: 30px;">#</th>
                            <th>제목</th>
                            <th style="width: 120px;">출처</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(news_items)}
                    </tbody>
                </table>
            </div>
            """

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
        if any(keyword in message_lower for keyword in ['날씨', '기온', '날씨알려줘', '날씨어때', 'weather']):
            # 자동 지역명 감지 사용
            detected_location = self.weather_api.detect_location_in_text(message)

            if detected_location:
                # 감지된 지역명 사용
                location = detected_location
            else:
                # 감지 실패 시 '날씨' 키워드 앞의 텍스트를 지역명으로 추출
                location = None
                for keyword in ['날씨', '기온', 'weather']:
                    if keyword in message_lower:
                        parts = message.split(keyword)[0].strip()
                        if parts:
                            # 불필요한 단어 제거
                            parts = parts.replace('의', '').replace('은', '').replace('는', '').replace('어때', '').strip()
                            if parts:
                                location = parts
                                break

                # 여전히 지역명이 없으면 기본값 사용
                if not location:
                    location = "서울"

            return self.weather_api.get_weather(location)

        # 뉴스 명령 감지
        if any(keyword in message_lower for keyword in ['뉴스', '최신뉴스', '뉴스알려줘', '헤드라인']):
            return self.news_api.get_top_news(count=10)

        return None


def search_google(query: str, num_results: int = 3) -> list:
    """
    Google 검색 수행 (Custom Search API)
    최근 1년 이내 결과 + 한국어 우선

    Args:
        query: 검색 쿼리
        num_results: 반환할 결과 개수 (최대 10개)

    Returns:
        검색 결과 리스트 (title, link, snippet)
    """
    try:
        import requests
        from dotenv import load_dotenv
        import os
        from datetime import datetime, timedelta

        load_dotenv()

        # Google Custom Search API 키와 검색 엔진 ID
        api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')

        if not api_key or not search_engine_id:
            print("[웹 검색] Google Search API 키가 설정되지 않았습니다.")
            return []

        # API 제한: 최대 10개
        num_results = min(num_results, 10)

        # 최근 1년 날짜 범위 계산
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        date_restrict = f"d365"  # 최근 365일

        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': search_engine_id,
            'q': query,
            'num': num_results,
            'dateRestrict': date_restrict,  # 최근 1년 이내
            'lr': 'lang_ko',  # 한국어 우선
            'hl': 'ko',  # 인터페이스 언어 한국어
            'gl': 'kr'  # 한국 지역 우선
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for idx, item in enumerate(data.get('items', []), 1):
            link = item.get('link', '')
            title = item.get('title', '')
            results.append({
                'title': title,
                'link': link,
                'snippet': item.get('snippet', '')
            })
            # 디버깅: 각 링크 출력
            print(f"  [{idx}] {title[:50]}... -> {link}")

        print(f"[웹 검색] '{query}' 검색 완료: {len(results)}개 결과 (최근 1년)")
        return results

    except Exception as e:
        print(f"[웹 검색 오류] {e}")
        return []
