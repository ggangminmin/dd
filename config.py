"""
설정 파일 - API 키 및 애플리케이션 설정
"""
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Config:
    # Flask 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # 데이터베이스 설정 (서버리스 환경 대응)
    IS_VERCEL = os.getenv('IS_VERCEL', 'false') == 'true'
    if IS_VERCEL:
        # Vercel 환경에서는 /tmp 디렉토리 사용 (휘발성)
        DATABASE_PATH = '/tmp/chat_history.db'
    else:
        DATABASE_PATH = 'chat_history.db'

    # OpenAI API 설정 (향후 사용)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    USE_GPT_API = os.getenv('USE_GPT_API', 'False').lower() == 'true'

    # 챗봇 설정
    CHATBOT_NAME = "고객지원 봇"
    MAX_HISTORY_LENGTH = 10  # 불러올 최대 이전 대화 개수
