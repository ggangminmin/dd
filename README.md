# 업무 자동화 AI 챗봇

Flask 기반의 업무 자동화 AI 챗봇입니다. 사용자의 대화 이력을 저장하고, 감정을 분석하며, **Excel 파일 자동 분석 및 차트 시각화** 기능을 제공합니다.

**최신 업데이트**:

- 📊 **차트 시각화 기능**: Excel 파일의 모든 시트를 자동으로 막대/선/원 그래프로 시각화
- 🔄 **스크롤 가능 차트**: 대용량 데이터셋(100+ 행)도 가로 스크롤로 모든 데이터 포인트 표시
- ⚡ **자동 차트 생성**: Excel/CSV 업로드 시 명령 없이도 자동으로 차트 생성
- 📈 **전체 데이터 분석**: 모든 행 표시 (20행 제한 제거), 데이터 포인트당 40px 동적 너비 할당
- 🤖 **자연어 명령 처리**: "차트 그려줘", "요약해줘" 같은 자연어 명령 자동 인식
- 🎯 **데이터 시각화 전문 GPT**: Excel 구조 자동 파악, 최적 차트 유형 추천, 조건부 필터링 지원
- 🎨 **간결한 분석 리포트**: 표 형식의 일목요연한 데이터 분석 결과

## 주요 기능

### 🔐 사용자 인증

- ✅ **회원가입/로그인**: 비밀번호 해싱을 통한 보안 인증
- ✅ **비밀번호 재설정**: 이메일 인증을 통한 비밀번호 복구 (Gmail SMTP)
- ✅ **세션 관리**: Flask Session 기반 사용자 상태 유지
- ✅ **하이브리드 DB**: 로컬(SQLite) / Vercel(MongoDB Atlas) 자동 전환

### 🤖 업무 자동화 기능 (NEW!)

- ✅ **자연어 명령 인식**: NLU를 통해 "요약해줘", "차트 그려줘" 같은 명령 자동 감지
- ✅ **Excel 자동 분석**: 업로드된 Excel 파일의 모든 시트 자동 통계 생성
  - 합계, 평균, 최대값, 최소값 자동 계산
  - 시트별 독립적인 분석 제공
- ✅ **차트 시각화**: Chart.js 기반 인터랙티브 차트 생성
  - 막대 그래프, 선 그래프, 원 그래프 지원
  - 모든 시트를 개별 차트로 시각화
  - 차트별 제목 및 범례 표시
  - **대용량 데이터 지원**: 100+ 행도 가로 스크롤로 표시
  - **동적 너비 계산**: 데이터 포인트당 40px 자동 할당
  - **자동 차트 생성**: Excel/CSV 업로드 시 즉시 차트 생성 (명령 불필요)
- ✅ **간결한 분석 리포트**: 표 형식의 일목요연한 통계 출력
  - 코드 블록 형식으로 깔끔하게 정렬
  - 추세 분석 (상승/하락/보합)
  - 최대 3개 데이터셋까지 요약

### 💬 대화 기능

- ✅ **대화 이력 저장**: 환경에 따라 SQLite 또는 MongoDB에 저장
- ✅ **사용자별 이력 관리**: 로그인한 사용자의 대화 내용 자동 불러오기
- ✅ **감정 분석**: 사용자의 말투와 감정을 분석 (화남, 슬픔, 기쁨, 공손, 중립)
- ✅ **응답 어조 조절**: 감정에 맞춰 적절한 어조로 응답
- ✅ **GPT API 연동**: OpenAI GPT-4o 및 GPT-4 Vision 지원
- ✅ **현재 날짜 인식**: GPT가 현재 날짜를 자동으로 인식하여 응답
- ✅ **파일 첨부 기능**: 이미지, 문서, 엑셀 등 다양한 파일 형식 지원
- ✅ **대화 통계**: 총 대화 수, 첫/마지막 대화 시간 등 통계 제공
- ✅ **대화 검색**: MongoDB 지원으로 키워드 기반 대화 내용 검색
- ✅ **대화 삭제**: MongoDB 지원으로 전체 대화 이력 삭제 기능

### 🌐 외부 API 통합

- ✅ **날씨 정보**: OpenWeatherMap API를 통한 실시간 날씨 조회
- ✅ **뉴스 정보**: NewsAPI를 통한 최신 뉴스 제공
- ✅ **웹 검색**: Google Custom Search API를 통한 실시간 링크 제공
- ✅ **자동 감지**: 사용자 질문에서 날씨/뉴스/링크 요청 자동 인식

### 🎨 UI/UX

- ✅ **모던한 UI**: 반응형 웹 디자인
- ✅ **다크모드**: 통합 색상 테마로 눈의 피로 감소 (통계, 뉴스 테이블 포함 완전 지원)
- ✅ **테마 전환**: 라이트/다크 모드 자유 전환 (localStorage 저장)
- ✅ **대화 검색**: 키워드로 과거 대화 검색 및 해당 메시지로 이동
- ✅ **검색 하이라이트**: 검색 결과 클릭 시 해당 메시지로 스크롤 + 2초간 강조
- ✅ **이미지 뷰어**: 이미지 클릭 시 원본 크기 팝업 보기 (줌 애니메이션)
- ✅ **파일 콘텐츠 카드**: 첨부 파일 내용을 깔끔한 카드 형식으로 표시
- ✅ **차트 컨테이너**: 인터랙티브 차트를 전용 컨테이너에 표시
- ✅ **이메일 템플릿**: HTML 기반 비밀번호 재설정 이메일
- ✅ **회원탈퇴**: 계정 삭제 기능 제공
- ✅ **뉴스 테이블 다크모드**: 최신 뉴스 표시 시 다크 테마 자동 적용

### 📎 지원하는 파일 형식

- **이미지**: jpg, jpeg, png, gif, webp (GPT-4 Vision으로 분석)
- **문서**: pdf, docx, txt (텍스트 추출 및 분석)
- **스프레드시트**: xlsx, csv (로컬 환경에서만 지원 - pandas 필요)
  - **다중 시트 지원**: Excel 파일의 모든 시트를 자동으로 처리
  - **자동 차트 생성**: 각 시트별로 독립적인 차트 생성
- **데이터**: json, xml (구조화된 데이터 분석)

> **참고**: Vercel 배포 환경에서는 서버리스 함수 크기 제한(50MB)으로 인해 pandas가 제외되어 CSV/XLSX 파일 처리가 제한됩니다. 이미지, PDF, DOCX, TXT, JSON, XML은 정상 작동합니다.

### 💾 하이브리드 데이터베이스

- **로컬 개발**: SQLite 사용 (빠른 개발 및 테스트)
- **Vercel 배포**: MongoDB Atlas 사용 (영구 데이터 저장)
- **자동 전환**: 환경 변수(`MONGODB_URI`)에 따라 자동으로 DB 선택
- **완전한 MongoDB 지원**:
  - ✅ 회원가입/로그인 (사용자 조회 및 생성)
  - ✅ 대화 이력 저장 및 조회
  - ✅ 파일 첨부 정보 저장
  - ✅ 비밀번호 재설정 토큰 관리
  - ✅ 마지막 로그인 시간 업데이트
- **Vercel 호환**: ephemeral 파일시스템 문제 완전 해결

## 프로젝트 구조

```text
dd/
├── app.py                    # Flask 메인 애플리케이션
├── config.py                 # 설정 파일
├── database.py               # 데이터베이스 관리
├── email_service.py          # 이메일 발송 서비스 (Gmail SMTP)
├── external_apis.py          # 외부 API 통합 (날씨, 뉴스, 웹 검색)
├── sentiment_analyzer.py     # 감정 분석 모듈
├── automation_assistant.py   # 업무 자동화 모듈 (NEW!)
├── file_processor.py         # 파일 처리 모듈 (이미지, 문서, Excel)
├── requirements.txt          # 필요한 패키지
├── .env.example              # 환경 변수 예시
├── .gitignore                # Git 무시 파일
├── static/
│   ├── css/
│   │   └── style.css        # 스타일시트 (차트 컨테이너, 파일 카드)
│   └── js/
│       └── chat.js          # 프론트엔드 로직 (차트 렌더링)
└── templates/
    ├── index.html           # 메인 페이지 (로그인/회원가입/채팅)
    └── reset_password.html  # 비밀번호 재설정 페이지
```

## 설치 및 실행 방법

### 1. 필요한 패키지 설치

```bash
# 가상환경 생성 (선택사항이지만 권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env.example`을 `.env`로 복사하고 필요한 API 키를 설정하세요:

```bash
# .env.example을 .env로 복사
cp .env.example .env
```

`.env` 파일 설정:

```env
# Flask 설정
SECRET_KEY=your-secret-key-here

# OpenAI API (GPT 사용 시)
OPENAI_API_KEY=your-openai-api-key
USE_GPT_API=True

# 날씨 API (OpenWeatherMap)
OPENWEATHER_API_KEY=your-weather-api-key

# 뉴스 API (NewsAPI)
NEWS_API_KEY=your-news-api-key

# Google Custom Search API (웹 검색 기능용)
GOOGLE_SEARCH_API_KEY=your-google-search-api-key
GOOGLE_SEARCH_ENGINE_ID=your-search-engine-id

# Gmail SMTP 설정 (비밀번호 재설정용)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
BASE_URL=http://localhost:5000

# MongoDB 설정 (선택사항 - Vercel 배포 시 필요)
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority
```

**Gmail SMTP 설정 방법:**
1. [Google 앱 비밀번호](https://myaccount.google.com/apppasswords) 생성
2. 2단계 인증 활성화 필요
3. 생성된 16자리 비밀번호를 `SMTP_PASSWORD`에 입력

**Google Custom Search API 설정 방법:**
1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials)에서 API 키 생성
2. [Programmable Search Engine](https://programmablesearchengine.google.com/controlpanel/all)에서 검색 엔진 생성
   - "Search the entire web" 선택
   - Search Engine ID (cx) 복사
3. API 키와 Search Engine ID를 환경 변수에 입력
4. 하루 100회 무료 검색 제한

**MongoDB Atlas 설정 방법 (Vercel 배포 시):**
1. [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) 무료 계정 생성
2. 새 클러스터 생성 (무료 M0 티어 선택)
3. Database Access에서 사용자 생성
4. Network Access에서 `0.0.0.0/0` 추가 (모든 IP 허용)
5. 클러스터 연결 → "Connect your application" 선택
6. Connection String 복사하여 `MONGODB_URI`에 입력

### 3. 애플리케이션 실행

```bash
python app.py
```

### 4. 브라우저에서 접속

<http://localhost:5000>

## 사용 방법

### 1. 로그인

- 이름과 이메일, 비밀번호를 입력하고 "회원가입" 클릭
- 이미 계정이 있다면 "로그인" 탭에서 로그인

### 2. 기본 채팅

- 메시지를 입력하고 Enter 또는 "전송" 버튼 클릭
- 챗봇이 자동으로 감정을 분석하고 적절한 어조로 응답합니다
- 감정 종류: 😠 화남, 😢 슬픔, 😊 기쁨, 🙏 공손, 😐 중립

### 3. Excel 파일 분석 및 차트 생성

1. **파일 업로드**: 📎 버튼을 클릭하여 Excel 파일 선택
2. **자동 차트 생성**: 파일 업로드 시 자동으로 막대 그래프 생성 (명령 불필요)
   - Excel/CSV 파일 감지 시 즉시 차트 시각화
   - 모든 행 데이터 포함 (20행 제한 없음)
   - 대용량 데이터(100+ 행)는 가로 스크롤로 표시
3. **차트 유형 변경** (선택사항): "선 그래프로 보여줘", "파이 차트 만들어줘" 등의 명령
4. **결과 확인**:
   - 각 시트별로 개별 차트가 생성됩니다
   - 차트 너비는 데이터 개수에 따라 자동 조정 (포인트당 40px)
   - 차트 아래에 간결한 통계 분석 표가 표시됩니다
   - 합계, 평균, 최대/최소값, 추세 등을 확인할 수 있습니다
   - 121개 행 예시: 약 4,840px 너비 차트 + 스크롤바

### 4. 지원하는 차트 유형

- **막대 그래프**: "막대 그래프", "bar chart"
- **선 그래프**: "선 그래프", "꺾은선 그래프", "line chart"
- **원 그래프**: "원 그래프", "파이 차트", "pie chart"

### 5. 기타 기능

- **통계 확인**: 우측 상단의 📊 버튼으로 대화 통계 확인
- **대화 검색**: 🔍 버튼으로 과거 대화 검색
- **다크모드**: 🌙 버튼으로 테마 전환

## 감정별 응답 예시

### 화난 말투 감지 시
```
사용자: 이거 정말 화나네요! 최악이에요!!
챗봇: 불편을 드려 정말 죄송합니다. [해결 방안 제시]
```

### 슬픈 말투 감지 시
```
사용자: 너무 힘들어요...
챗봇: 힘든 상황이시군요. [공감 및 긍정적 해결책]
```

### 기쁜 말투 감지 시
```
사용자: 완벽해요! 정말 좋아요 ㅎㅎ
챗봇: 좋은 말씀 감사합니다! [밝은 응답]
```

## GPT API 연동하기

### 1. OpenAI API 키 발급
1. https://platform.openai.com/api-keys 접속
2. "Create new secret key" 클릭
3. API 키 복사

### 2. 환경 변수 설정
```bash
# .env 파일 생성 및 편집
OPENAI_API_KEY=sk-your-actual-api-key-here
USE_GPT_API=True
```

### 3. 애플리케이션 재시작
```bash
python app.py
```

GPT API가 활성화되면 시작 메시지에 "GPT API 사용: True"로 표시됩니다.

## 기술 스택

### Backend

- **Flask** 3.0.0 - 웹 프레임워크
- **SQLite** - 로컬 데이터베이스
- **MongoDB Atlas** - 클라우드 데이터베이스 (Vercel 배포용)
- **OpenAI API** - GPT-4o 및 GPT-4 Vision 연동
- **Pandas** - Excel 데이터 처리 및 분석
- **openpyxl** - Excel 파일 읽기/쓰기
- **Chart.js** 4.4.0 - 데이터 시각화

### Frontend

- **HTML5/CSS3** - 마크업 및 스타일
- **Vanilla JavaScript** - 인터랙티브 기능
- **Fetch API** - 비동기 통신
- **Chart.js** - 인터랙티브 차트 렌더링

## 데이터베이스 구조

### SQLite (로컬 개발)

**users 테이블**
```sql
- id: INTEGER PRIMARY KEY
- username: TEXT UNIQUE
- email: TEXT UNIQUE
- password_hash: TEXT
- reset_token: TEXT
- reset_token_expiry: TIMESTAMP
- created_at: TIMESTAMP
- last_login: TIMESTAMP
```

**chat_history 테이블**
```sql
- id: INTEGER PRIMARY KEY
- user_id: INTEGER (FK)
- message: TEXT
- is_user: BOOLEAN
- sentiment: TEXT
- timestamp: TIMESTAMP
```

### MongoDB (Vercel 배포)

**users 컬렉션**
```javascript
{
  _id: ObjectId,
  username: String (unique),
  email: String (unique),
  password_hash: String,
  reset_token: String,
  reset_token_expiry: Date,
  created_at: Date,
  last_login: Date
}
```

**chat_history 컬렉션**
```javascript
{
  _id: ObjectId,
  user_id: String,
  message: String,
  is_user: Boolean,
  sentiment: String,
  timestamp: Date,
  file_path: String (optional),
  file_type: String (optional)
}
```

## 구현된 기능 및 향후 계획

### 현재 구현 ✅

- ✅ 회원가입/로그인 시스템 (비밀번호 해싱)
- ✅ 비밀번호 재설정 (이메일 인증)
- ✅ 키워드 기반 감정 분석
- ✅ GPT API 통합 (GPT-4o, 현재 날짜 인식 포함)
- ✅ 외부 API 통합 (날씨, 뉴스, 웹 검색)
- ✅ 파일 첨부 기능 (이미지, 문서, Excel, 데이터)
- ✅ **업무 자동화 기능** (자연어 명령 인식, Excel 자동 분석)
- ✅ **차트 시각화** (막대/선/원 그래프, 다중 시트 지원)
- ✅ **간결한 데이터 분석** (표 형식 통계, 추세 분석)
- ✅ 대화 검색 및 하이라이트 기능
- ✅ 이미지 뷰어 (팝업)
- ✅ 완전한 다크모드 지원
- ✅ 하이브리드 데이터베이스 (SQLite/MongoDB 자동 전환)
- ✅ MongoDB Atlas 완전 지원 (회원가입, 대화, 파일, 토큰 관리)
- ✅ Vercel 서버리스 배포 최적화

### 향후 개선 방향 🔄

- 🔄 더 정교한 감정 분석 (NLP 모델)
- 🔄 다중 언어 지원
- 🔄 음성 인식/합성
- 🔄 대화 요약 기능
- 🔄 더 다양한 차트 유형 (산점도, 영역 차트 등)
- 🔄 Excel 파일 생성 및 다운로드 기능
- 🔄 실시간 협업 기능

## 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# app.py에서 포트 변경
app.run(debug=True, host='0.0.0.0', port=5001)  # 5001로 변경
```

### 데이터베이스 초기화
```bash
# chat_history.db 파일 삭제 후 재실행
rm chat_history.db
python app.py
```

### 패키지 설치 오류
```bash
# pip 업그레이드
pip install --upgrade pip

# 개별 설치
pip install Flask
pip install openai
pip install python-dotenv
```

## 라이선스

이 프로젝트는 학습 및 개발 목적으로 자유롭게 사용 가능합니다.

## 개발자

AI 대화형 개발 프로젝트

---

**참고**: 이 프로젝트는 "AI에게 개발 의도를 설명하고 결과를 함께 만들어가는 대화형 개발 경험"을 실현하기 위해 만들어졌습니다.
