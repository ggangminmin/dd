"""
Vercel 서버리스 함수 진입점
Flask 앱을 Vercel의 서버리스 함수로 배포하기 위한 핸들러
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 환경 변수 설정 (서버리스 환경 대응)
os.environ.setdefault('IS_VERCEL', 'true')

try:
    # 작업 디렉토리를 프로젝트 루트로 설정
    os.chdir(project_root)
except:
    pass

# Flask 앱 임포트
from app import app

# Vercel은 WSGI 앱을 직접 처리할 수 있습니다
# 'app' 변수를 노출하면 자동으로 인식됩니다

