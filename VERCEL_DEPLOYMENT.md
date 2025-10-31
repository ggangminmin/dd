# Vercel 배포 가이드

이 문서는 Flask 챗봇 애플리케이션을 Vercel에 배포하는 방법을 설명합니다.

## 🔧 필수 설정

### 1. Vercel 환경 변수 설정

Vercel 대시보드에서 다음 환경 변수를 설정해야 합니다:

1. **Vercel 프로젝트 페이지 접속**
   - https://vercel.com/dashboard
   - 프로젝트 선택

2. **Settings > Environment Variables 메뉴로 이동**

3. **다음 환경 변수들을 추가:**

| 변수명 | 값 | 설명 |
|--------|-----|------|
| `SECRET_KEY` | `chatbot-secret-key-2024` | Flask 세션 암호화 키 |
| `OPENAI_API_KEY` | `sk-proj-...` | OpenAI API 키 (GPT 사용 시) |
| `USE_GPT_API` | `True` | GPT API 사용 여부 |
| `IS_VERCEL` | `true` | Vercel 환경 감지용 |

**중요**: Production, Preview, Development 모든 환경에 추가하세요!

### 2. 환경 변수 추가 방법

#### 방법 1: Vercel 대시보드
```
1. 프로젝트 > Settings > Environment Variables
2. "Add New" 버튼 클릭
3. Name, Value 입력
4. Environment 선택 (Production, Preview, Development 모두 체크)
5. "Save" 클릭
```

#### 방법 2: Vercel CLI
```bash
vercel env add SECRET_KEY
# 값을 입력하라는 프롬프트에 입력

vercel env add OPENAI_API_KEY
# API 키 입력

vercel env add USE_GPT_API
# True 입력

vercel env add IS_VERCEL
# true 입력
```

## 🚀 배포 방법

### 자동 배포 (권장)
```bash
# Git에 커밋 후 푸시
git add .
git commit -m "Vercel 배포 설정 수정"
git push origin main
```

GitHub와 연동된 경우 자동으로 배포됩니다.

### 수동 배포
```bash
# Vercel CLI로 배포
vercel --prod
```

## 📋 배포 후 체크리스트

### 1. 홈페이지 접속 확인
- [ ] `https://your-project.vercel.app/` 접속
- [ ] 로그인 화면이 정상적으로 표시되는지 확인

### 2. API 엔드포인트 테스트
- [ ] `/api/register` - 사용자 등록
- [ ] `/api/chat` - 챗봇 대화
- [ ] `/api/history` - 대화 이력 조회

### 3. 정적 파일 확인
- [ ] CSS 파일 로드 확인
- [ ] JavaScript 파일 로드 확인
- [ ] 이미지 파일 표시 확인

### 4. 기능 테스트
- [ ] 사용자 등록/로그인
- [ ] 메시지 전송
- [ ] 감정 분석 작동
- [ ] GPT API 응답 (USE_GPT_API=True인 경우)

## ⚠️ 중요 제한사항 및 해결 방법

### 1. 데이터베이스 (SQLite) 문제

**문제**: SQLite는 서버리스 환경에서 `/tmp`에 저장되며 **휘발성**입니다.
- 배포할 때마다 초기화됨
- 서버리스 함수가 재시작되면 데이터 손실

**해결 방법**:
1. **Vercel Postgres** (권장)
   ```bash
   # Vercel 대시보드에서 Storage > Postgres 추가
   ```

2. **Supabase**
   - 무료 PostgreSQL 데이터베이스
   - https://supabase.com/

3. **PlanetScale**
   - 무료 MySQL 데이터베이스
   - https://planetscale.com/

### 2. 파일 업로드 문제

**문제**: 업로드된 파일이 `/tmp`에 저장되어 휘발성입니다.

**해결 방법**:
1. **Vercel Blob Storage**
   ```bash
   npm i @vercel/blob
   ```

2. **Cloudinary** (이미지 전용)
   ```bash
   pip install cloudinary
   ```

3. **AWS S3**
   ```bash
   pip install boto3
   ```

### 3. 세션 관리 문제

**문제**: 서버리스 환경에서 세션이 유지되지 않을 수 있습니다.

**해결 방법**:
- JWT 토큰 기반 인증으로 변경
- Redis 세션 스토어 사용 (Upstash Redis)

## 🐛 트러블슈팅

### 404 에러 발생 시

1. **Build 로그 확인**
   ```
   Vercel Dashboard > Deployments > 최신 배포 > Build Logs
   ```

2. **Function 로그 확인**
   ```
   Vercel Dashboard > Deployments > 최신 배포 > Functions
   ```

3. **일반적인 원인**
   - `api/index.py`가 제대로 임포트되지 않음
   - Python 의존성 설치 실패
   - 환경 변수 누락

### 500 Internal Server Error

1. **Function 로그 확인**
   - 상세한 에러 메시지 확인

2. **로컬에서 테스트**
   ```bash
   export IS_VERCEL=true
   python app.py
   ```

3. **흔한 원인**
   - OpenAI API 키 오류
   - 데이터베이스 연결 실패
   - 모듈 임포트 오류

### CSS/JS 파일 404 에러

1. **vercel.json 확인**
   - `static/**` 빌드 설정 확인

2. **템플릿 경로 확인**
   ```html
   <!-- 상대 경로 사용 -->
   <link rel="stylesheet" href="/static/css/style.css">
   ```

## 📚 참고 자료

- [Vercel Python 문서](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Flask on Vercel 가이드](https://vercel.com/guides/using-flask-with-vercel)
- [Vercel 환경 변수](https://vercel.com/docs/projects/environment-variables)

## 💡 추가 최적화

### 1. Cold Start 최소화
```python
# 전역 변수로 클라이언트 초기화
openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
```

### 2. 응답 시간 개선
- GPT API timeout 설정
- 데이터베이스 쿼리 최적화

### 3. 로깅 설정
```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🔄 업데이트 및 재배포

코드 변경 후:
```bash
git add .
git commit -m "업데이트 내용"
git push origin main
```

또는 즉시 배포:
```bash
vercel --prod
```

---

**마지막 업데이트**: 2025-10-31
**버전**: 1.0.0
