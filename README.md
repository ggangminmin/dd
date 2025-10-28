# 상담 이력을 기억하는 고객지원 챗봇

Flask 기반의 AI 고객지원 챗봇입니다. 사용자의 대화 이력을 저장하고, 감정을 분석하여 적절한 어조로 응답합니다.

## 주요 기능

- ✅ **대화 이력 저장**: SQLite를 사용하여 모든 대화 내용 저장
- ✅ **사용자 인식**: 동일 사용자의 이전 대화 내용 자동 불러오기
- ✅ **감정 분석**: 사용자의 말투와 감정을 분석 (화남, 슬픔, 기쁨, 공손, 중립)
- ✅ **응답 어조 조절**: 감정에 맞춰 적절한 어조로 응답
- ✅ **GPT API 연동**: OpenAI GPT-3.5 및 GPT-4 Vision 지원
- ✅ **파일 첨부 기능**: 이미지, 문서, 엑셀 등 다양한 파일 형식 지원
- ✅ **모던한 UI**: 반응형 웹 디자인

### 📎 지원하는 파일 형식
- **이미지**: jpg, jpeg, png, gif, webp (GPT-4 Vision으로 분석)
- **문서**: pdf, docx, txt (텍스트 추출 및 분석)
- **스프레드시트**: xlsx, csv (데이터 파싱 및 분석)
- **데이터**: json, xml (구조화된 데이터 분석)

## 프로젝트 구조

```
dd/
├── app.py                    # Flask 메인 애플리케이션
├── config.py                 # 설정 파일
├── database.py               # 데이터베이스 관리
├── sentiment_analyzer.py     # 감정 분석 모듈
├── requirements.txt          # 필요한 패키지
├── .env.example              # 환경 변수 예시
├── .gitignore                # Git 무시 파일
├── static/
│   ├── css/
│   │   └── style.css        # 스타일시트
│   └── js/
│       └── chat.js          # 프론트엔드 로직
└── templates/
    └── index.html           # 메인 페이지
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

### 2. 환경 변수 설정 (선택사항)

GPT API를 사용하려면:

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 편집하여 API 키 입력
# OPENAI_API_KEY=your-api-key-here
# USE_GPT_API=True
```

### 3. 애플리케이션 실행

```bash
python app.py
```

### 4. 브라우저에서 접속

```
http://localhost:5000
```

## 사용 방법

### 1. 로그인
- 이름을 입력하고 "시작하기" 클릭
- 이전에 사용한 이름이면 대화 이력이 자동으로 로드됩니다

### 2. 채팅
- 메시지를 입력하고 Enter 또는 "전송" 버튼 클릭
- 챗봇이 자동으로 감정을 분석하고 적절한 어조로 응답합니다

### 3. 감정 분석 확인
- 메시지 전송 후 입력창 아래에 감지된 감정이 표시됩니다
- 감정 종류: 😠 화남, 😢 슬픔, 😊 기쁨, 🙏 공손, 😐 중립

### 4. 통계 확인
- 우측 상단의 📊 버튼을 클릭하여 대화 통계 확인

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
- **SQLite** - 데이터베이스
- **OpenAI API** - GPT 연동 (선택사항)

### Frontend
- **HTML5/CSS3** - 마크업 및 스타일
- **Vanilla JavaScript** - 인터랙티브 기능
- **Fetch API** - 비동기 통신

## 데이터베이스 구조

### users 테이블
```sql
- id: INTEGER PRIMARY KEY
- username: TEXT UNIQUE
- created_at: TIMESTAMP
```

### chat_history 테이블
```sql
- id: INTEGER PRIMARY KEY
- user_id: INTEGER (FK)
- message: TEXT
- is_user: BOOLEAN
- sentiment: TEXT
- timestamp: TIMESTAMP
```

## 확장 가능성

### 현재 구현
- ✅ 키워드 기반 감정 분석
- ✅ 규칙 기반 응답 시스템
- ✅ SQLite 데이터베이스

### 향후 개선 방향
- 🔄 GPT API 완전 통합
- 🔄 더 정교한 감정 분석 (NLP 모델)
- 🔄 다중 언어 지원
- 🔄 음성 인식/합성
- 🔄 대화 요약 기능
- 🔄 관리자 대시보드
- 🔄 실시간 알림

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
