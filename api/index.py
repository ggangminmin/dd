"""
Vercel 서버리스 함수 래퍼
Flask 앱을 Vercel의 서버리스 함수로 배포하기 위한 진입점
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 작업 디렉토리를 프로젝트 루트로 설정
os.chdir(project_root)

from app import app

# Vercel은 Flask 앱을 직접 사용할 수 있습니다
# handler 함수를 제공하거나 app을 직접 노출
application = app

# Vercel 서버리스 함수용 handler
def handler(request):
    """
    Vercel 서버리스 함수 핸들러
    Flask 앱을 WSGI 어플리케이션으로 실행
    """
    return app(request.environ, lambda status, headers: None)

