"""
Flask 기반 고객지원 챗봇 애플리케이션
상담 이력을 기억하고 감정에 맞춰 응답하는 챗봇
"""
from flask import Flask, render_template, request, jsonify, session
from config import Config
from database import Database
from sentiment_analyzer import SentimentAnalyzer
from file_processor import FileProcessor
from external_apis import ExternalAPIManager, search_google
from email_service import EmailService
from automation_assistant import AutomationAssistant
import os
import json
import uuid
import re
import secrets
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

# GPT API 연동 (선택적)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = Flask(__name__)
app.config.from_object(Config)

# 파일 업로드 크기 제한 (100MB)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# 업로드 폴더 설정 (서버리스 환경 대응)
IS_VERCEL = os.environ.get('IS_VERCEL', 'false') == 'true'
if IS_VERCEL:
    # Vercel 서버리스 환경에서는 /tmp 디렉토리 사용
    UPLOAD_FOLDER = '/tmp/uploads'
else:
    UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 데이터베이스 및 감정 분석기 초기화
db = Database()
sentiment_analyzer = SentimentAnalyzer()
email_service = EmailService()

def allowed_image_file(filename):
    """이미지 파일인지 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

# OpenAI 클라이언트 초기화 (API 키가 있을 경우)
if OPENAI_AVAILABLE and Config.OPENAI_API_KEY and Config.USE_GPT_API:
    openai_client = OpenAI(api_key=Config.OPENAI_API_KEY)
    USE_GPT = True
    print(f"[OpenAI] 클라이언트 초기화 성공: {openai_client is not None}")
else:
    openai_client = None
    USE_GPT = False
    print(f"[OpenAI] 클라이언트 초기화 실패 - OPENAI_AVAILABLE:{OPENAI_AVAILABLE}, API_KEY:{bool(Config.OPENAI_API_KEY)}, USE_GPT:{Config.USE_GPT_API}")

# 외부 API 관리자 초기화
api_manager = ExternalAPIManager()
api_status = api_manager.check_availability()
print(f"[외부 API] 날씨 API: {api_status['weather']}, 뉴스 API: {api_status['news']}")


# ==================== 라우트 ====================

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html', chatbot_name=Config.CHATBOT_NAME)


@app.route('/reset-password')
def reset_password_page():
    """비밀번호 재설정 페이지"""
    return render_template('reset_password.html')


@app.route('/api/register', methods=['POST'])
def register_user():
    """사용자 등록 또는 로그인"""
    data = request.json
    username = data.get('username', '').strip()

    if not username:
        return jsonify({'error': '사용자 이름을 입력해주세요.'}), 400

    # 사용자 생성 또는 조회
    user_id = db.get_or_create_user(username)
    session['user_id'] = user_id
    session['username'] = username

    # 이전 대화 이력 조회 (첨부 파일 정보 포함)
    history = db.get_user_history(user_id)

    # 첨부 파일 정보 처리 (URL 및 미리보기 데이터 추가)
    for msg in history:
        if 'attachments' in msg and msg['attachments']:
            msg['attached_files'] = []
            for att in msg['attachments']:
                parsed_info = att.get('parsed_info', {})

                # file_info는 저장된 전체 정보 (file_processor에서 반환한 것)
                file_ext = parsed_info.get('extension', parsed_info.get('type', 'unknown'))
                filename = att['filename']

                # 파일 정보 구성
                file_info_dict = {
                    'filename': filename,
                    'size': parsed_info.get('size', att.get('file_size', 0)),
                    'extension': file_ext,
                    'is_image': parsed_info.get('is_image', False)
                }

                # 저장된 URL 사용
                if parsed_info.get('url'):
                    file_info_dict['url'] = parsed_info['url']
                elif att.get('file_url'):
                    file_info_dict['url'] = att['file_url']

                # 표 데이터가 있으면 추가 (Excel, CSV)
                if 'table_data' in parsed_info:
                    file_info_dict['table_data'] = parsed_info['table_data']
                    print(f"[파일 이력] 표 데이터 로드: {filename}, 행: {parsed_info['table_data'].get('total_rows', 0)}")

                # 텍스트 미리보기 추가 (Word, TXT, PDF)
                if 'text_preview' in parsed_info:
                    file_info_dict['text_preview'] = parsed_info['text_preview']
                    print(f"[파일 이력] 텍스트 미리보기 로드: {filename}, 길이: {len(parsed_info['text_preview'])}")

                msg['attached_files'].append(file_info_dict)
                print(f"[파일 이력] 파일 추가: {filename}, is_image={file_info_dict.get('is_image')}, url={file_info_dict.get('url')[:50] if file_info_dict.get('url') else 'None'}...")

    stats = db.get_user_stats(user_id)

    # 환영 메시지
    if stats and stats['total_messages'] > 0:
        welcome_message = f"다시 오신 것을 환영합니다, {username}님! 이전 대화 이력을 불러왔습니다."
    else:
        welcome_message = f"안녕하세요, {username}님! 무엇을 도와드릴까요?"

    return jsonify({
        'user_id': user_id,
        'username': username,
        'history': history,
        'stats': stats,
        'welcome_message': welcome_message
    })


@app.route('/api/delete-account', methods=['POST'])
def delete_account():
    """회원탈퇴 API"""
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '')

    # 입력 검증
    if not username or not password:
        return jsonify({'success': False, 'error': '아이디와 비밀번호를 입력해주세요.'}), 400

    # 사용자 확인
    user = db.get_user_by_username(username)
    if not user:
        user = db.get_user_by_email(username)

    if not user:
        return jsonify({'success': False, 'error': '존재하지 않는 계정입니다.'}), 404

    # 비밀번호 확인
    if not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'error': '비밀번호가 일치하지 않습니다.'}), 401

    # 계정 삭제
    try:
        user_id = user['id']
        # 사용자의 모든 데이터 삭제
        db.delete_all_messages(user_id)
        db.delete_user(user_id)

        return jsonify({'success': True, 'message': '계정이 성공적으로 삭제되었습니다.'})
    except Exception as e:
        print(f"계정 삭제 오류: {str(e)}")
        return jsonify({'success': False, 'error': '계정 삭제 중 오류가 발생했습니다.'}), 500


@app.route('/api/signup', methods=['POST'])
def signup():
    """회원가입 API"""
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # 입력 검증
    if not username or not email or not password:
        return jsonify({'success': False, 'error': '모든 필드를 입력해주세요.'}), 400

    # 이메일 형식 검증
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({'success': False, 'error': '올바른 이메일 형식이 아닙니다.'}), 400

    # 비밀번호 강도 검증 (최소 6자)
    if len(password) < 6:
        return jsonify({'success': False, 'error': '비밀번호는 최소 6자 이상이어야 합니다.'}), 400

    # 사용자명 중복 확인
    existing_user = db.get_user_by_username(username)
    if existing_user:
        return jsonify({'success': False, 'error': '이미 사용 중인 사용자명입니다.'}), 400

    # 이메일 중복 확인
    existing_email = db.get_user_by_email(email)
    if existing_email:
        return jsonify({'success': False, 'error': '이미 가입된 이메일입니다.'}), 400

    # 비밀번호 해싱
    password_hash = generate_password_hash(password)

    # 사용자 생성
    user_id = db.create_user(username, email, password_hash)

    if user_id:
        # 자동 로그인 (세션 설정)
        session.permanent = True  # 영구 세션 활성화
        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email
        db.update_last_login(user_id)

        return jsonify({
            'success': True,
            'message': '회원가입이 완료되었습니다.',
            'user': {
                'id': user_id,
                'username': username,
                'email': email
            }
        })
    else:
        return jsonify({'success': False, 'error': '회원가입 중 오류가 발생했습니다.'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """로그인 API"""
    data = request.json
    username_or_email = data.get('username', '').strip()
    password = data.get('password', '')

    # 입력 검증
    if not username_or_email or not password:
        return jsonify({'success': False, 'error': '아이디와 비밀번호를 입력해주세요.'}), 400

    # 이메일 또는 사용자명으로 조회
    if '@' in username_or_email:
        user = db.get_user_by_email(username_or_email)
    else:
        user = db.get_user_by_username(username_or_email)

    # 사용자 확인 및 비밀번호 검증
    if not user or not user.get('password_hash'):
        return jsonify({'success': False, 'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}), 401

    if not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'error': '아이디 또는 비밀번호가 올바르지 않습니다.'}), 401

    # 로그인 성공 - 세션 설정
    session.permanent = True  # 영구 세션 활성화
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['email'] = user['email']
    db.update_last_login(user['id'])

    # 이전 대화 이력 조회
    history = db.get_user_history(user['id'])

    # 첨부 파일 정보 처리
    for msg in history:
        if 'attachments' in msg and msg['attachments']:
            msg['attached_files'] = []
            for att in msg['attachments']:
                parsed_info = att.get('parsed_info', {})
                file_ext = parsed_info.get('extension', parsed_info.get('type', 'unknown'))
                filename = att['filename']

                file_info_dict = {
                    'filename': filename,
                    'size': parsed_info.get('size', att.get('file_size', 0)),
                    'extension': file_ext,
                    'is_image': parsed_info.get('is_image', False)
                }

                if parsed_info.get('url'):
                    file_info_dict['url'] = parsed_info['url']
                elif att.get('file_url'):
                    file_info_dict['url'] = att['file_url']

                if 'table_data' in parsed_info:
                    file_info_dict['table_data'] = parsed_info['table_data']

                msg['attached_files'].append(file_info_dict)

    return jsonify({
        'success': True,
        'message': '로그인 되었습니다.',
        'user': {
            'id': user['id'],
            'username': user['username'],
            'email': user['email']
        },
        'history': history
    })


@app.route('/api/logout', methods=['POST'])
def logout():
    """로그아웃 API"""
    session.clear()
    return jsonify({'success': True, 'message': '로그아웃 되었습니다.'})


@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """로그인 상태 확인 API"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'email': session.get('email', '')
            }
        })
    else:
        return jsonify({'authenticated': False})


@app.route('/api/request-password-reset', methods=['POST'])
def request_password_reset():
    """비밀번호 재설정 요청 API"""
    data = request.json
    email = data.get('email', '').strip()

    # 입력 검증
    if not email:
        return jsonify({'success': False, 'error': '이메일을 입력해주세요.'}), 400

    # 이메일 형식 검증
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({'success': False, 'error': '올바른 이메일 형식이 아닙니다.'}), 400

    # 사용자 조회
    user = db.get_user_by_email(email)

    # 보안을 위해 이메일이 없어도 성공 메시지 반환 (이메일 노출 방지)
    if not user:
        return jsonify({
            'success': True,
            'message': '가입된 이메일이라면 비밀번호 재설정 링크가 발송되었습니다.'
        })

    # 재설정 토큰 생성 (32바이트 = 64자 hex)
    reset_token = secrets.token_urlsafe(32)

    # 토큰 만료 시간 (1시간)
    expiry = datetime.now() + timedelta(hours=1)

    # 토큰 저장
    db.save_reset_token(email, reset_token, expiry.isoformat())

    # 재설정 링크 생성
    # 로컬 개발: http://localhost:5000
    # 프로덕션: 환경변수에서 BASE_URL 가져오기
    base_url = os.getenv('BASE_URL', 'http://localhost:5000')
    reset_link = f"{base_url}/reset-password?token={reset_token}"

    # 이메일 발송
    email_sent = email_service.send_password_reset_email(email, reset_link, user['username'])

    if email_sent:
        return jsonify({
            'success': True,
            'message': '비밀번호 재설정 링크가 이메일로 발송되었습니다.'
        })
    else:
        return jsonify({
            'success': False,
            'error': '이메일 발송 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
        }), 500


@app.route('/api/verify-reset-token', methods=['POST'])
def verify_reset_token():
    """비밀번호 재설정 토큰 검증 API"""
    data = request.json
    token = data.get('token', '')

    if not token:
        return jsonify({'success': False, 'error': '유효하지 않은 토큰입니다.'}), 400

    # 토큰 검증
    user = db.verify_reset_token(token)

    if not user:
        return jsonify({
            'success': False,
            'error': '토큰이 만료되었거나 유효하지 않습니다.'
        }), 400

    return jsonify({
        'success': True,
        'username': user['username']
    })


@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    """비밀번호 재설정 API"""
    data = request.json
    token = data.get('token', '')
    new_password = data.get('password', '')

    # 입력 검증
    if not token or not new_password:
        return jsonify({'success': False, 'error': '필수 정보가 누락되었습니다.'}), 400

    # 비밀번호 강도 검증
    if len(new_password) < 6:
        return jsonify({'success': False, 'error': '비밀번호는 최소 6자 이상이어야 합니다.'}), 400

    # 토큰 검증
    user = db.verify_reset_token(token)

    if not user:
        return jsonify({
            'success': False,
            'error': '토큰이 만료되었거나 유효하지 않습니다.'
        }), 400

    # 새 비밀번호 해싱
    password_hash = generate_password_hash(new_password)

    # 비밀번호 업데이트
    success = db.update_password(user['id'], password_hash)

    if success:
        return jsonify({
            'success': True,
            'message': '비밀번호가 성공적으로 변경되었습니다.'
        })
    else:
        return jsonify({
            'success': False,
            'error': '비밀번호 변경 중 오류가 발생했습니다.'
        }), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """챗봇 대화 처리"""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    # JSON 또는 multipart/form-data 처리
    if request.content_type and 'multipart/form-data' in request.content_type:
        user_message = request.form.get('message', '').strip()
        files = request.files.getlist('files')
    else:
        data = request.json
        user_message = data.get('message', '').strip()
        files = []

    if not user_message and not files:
        return jsonify({'error': '메시지 또는 파일을 입력해주세요.'}), 400

    # 감정 분석
    sentiment_result = sentiment_analyzer.analyze(user_message) if user_message else {'sentiment': 'neutral'}
    sentiment = sentiment_result['sentiment']

    # 파일 처리
    file_contents = []
    file_infos = []
    has_image = False
    image_urls = []
    attached_files = []  # 모든 첨부 파일 정보

    for file in files:
        if file and file.filename:
            try:
                # 파일 읽기
                file_data = file.read()
                print(f"[파일 처리] 파일명: {file.filename}, 크기: {len(file_data)} bytes")

                # 모든 파일 저장
                ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'bin'
                unique_filename = f"{uuid.uuid4()}.{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

                # 파일 저장
                with open(filepath, 'wb') as f:
                    f.write(file_data)

                # URL 생성 (서버리스 환경 대응)
                if IS_VERCEL:
                    # Vercel 환경에서는 base64 데이터 URL 사용
                    if allowed_image_file(file.filename):
                        import base64
                        file_url = f"data:image/{ext};base64,{base64.b64encode(file_data).decode()}"
                    else:
                        file_url = None
                else:
                    file_url = f"/static/uploads/{unique_filename}"

                # 파일 처리 (텍스트 추출)
                result = FileProcessor.process_file(file_data, file.filename)

                if result['success']:
                    file_contents.append(result['text'])
                    file_infos.append(result['info'])
                    if result.get('has_image'):
                        has_image = True

                    # 파일 정보 저장 (table_data, text_preview, base64 포함)
                    file_info_dict = {
                        'filename': file.filename,
                        'url': file_url,
                        'size': len(file_data),
                        'is_image': allowed_image_file(file.filename),
                        'extension': ext
                    }

                    # 이미지 base64 데이터 추가 (미리보기용)
                    if 'base64' in result['info']:
                        file_info_dict['base64'] = result['info']['base64']
                        file_info_dict['format'] = result['info'].get('format')
                        file_info_dict['image_size'] = result['info'].get('size')

                    # 표 데이터가 있으면 추가 (Excel, CSV)
                    if 'table_data' in result:
                        file_info_dict['table_data'] = result['table_data']

                    # 텍스트 미리보기 추가 (Word, TXT, PDF 등)
                    if 'text' in result and result['info']['type'] in ['docx', 'txt', 'pdf']:
                        # 최대 500자로 제한
                        preview_text = result['text'][:500] if len(result['text']) > 500 else result['text']
                        file_info_dict['text_preview'] = preview_text

                    # 이미지인 경우 image_urls에도 추가
                    if file_info_dict['is_image']:
                        image_urls.append(file_url)

                    attached_files.append(file_info_dict)
                    print(f"[파일 처리] 성공: {file.filename}")
                else:
                    print(f"[파일 처리] 실패: {file.filename} - {result['error']}")
                    return jsonify({'error': result['error']}), 400
            except Exception as e:
                error_msg = f"파일 처리 중 오류 발생: {str(e)}"
                print(f"[파일 처리 오류] {file.filename}: {error_msg}")
                import traceback
                traceback.print_exc()
                return jsonify({'error': error_msg}), 500

    # 파일 내용을 메시지에 추가
    full_message = user_message
    automation_analysis = None

    if file_contents:
        full_message += "\n\n[첨부된 파일 내용]\n" + "\n\n".join(file_contents)

        # 업무 자동화: 엑셀 파일이 있으면 자동 분석 수행
        for attached_file in attached_files:
            if 'table_data' in attached_file and attached_file.get('extension') in ['xlsx', 'csv']:
                print(f"[자동화] 엑셀 파일 자동 분석 시작: {attached_file['filename']}")

                # AutomationAssistant를 사용한 데이터 분석
                analysis_result = AutomationAssistant.analyze_excel_data(
                    {'table_data': attached_file['table_data']},
                    user_message
                )

                if analysis_result.get('success'):
                    # 분석 결과를 메시지에 추가
                    analysis_summary = "\n\n[📊 자동 데이터 분석 결과]\n"

                    if 'basic_info' in analysis_result:
                        info = analysis_result['basic_info']
                        analysis_summary += f"- 총 행 수: {info.get('total_rows', 0)}\n"
                        analysis_summary += f"- 총 열 수: {info.get('total_columns', 0)}\n"
                        analysis_summary += f"- 컬럼: {', '.join(info.get('columns', []))}\n"

                    if 'statistics' in analysis_result and analysis_result['statistics']:
                        analysis_summary += "\n[통계 정보]\n"
                        for col_name, stats in analysis_result['statistics'].items():
                            analysis_summary += f"\n{col_name}:\n"
                            analysis_summary += f"  - 평균: {stats.get('average', 0):.2f}\n"
                            analysis_summary += f"  - 합계: {stats.get('sum', 0):.2f}\n"
                            analysis_summary += f"  - 최소: {stats.get('min', 0)}\n"
                            analysis_summary += f"  - 최대: {stats.get('max', 0)}\n"

                    full_message += analysis_summary
                    automation_analysis = analysis_result
                    print(f"[자동화] 분석 완료 - 통계 컬럼 수: {len(analysis_result.get('statistics', {}))}")

    # 사용자 메시지 저장
    message_id = db.save_message(user_id, user_message if user_message else "", is_user=True, sentiment=sentiment)

    # 파일 정보 저장 (table_data, text_preview, URL 포함)
    for attached_file in attached_files:
        # file_info에서 type 정보 가져오기 (file_infos에서)
        file_type = 'unknown'
        for info in file_infos:
            if info['filename'] == attached_file['filename']:
                file_type = info['type']
                break

        db.save_file_attachment(
            message_id,
            attached_file['filename'],
            file_type,
            attached_file.get('size', 0),
            json.dumps(attached_file),  # attached_file에는 table_data, text_preview 포함
            attached_file.get('url')
        )

    # 1단계: 외부 API 명령 확인 (날씨, 뉴스)
    api_response = api_manager.process_command(user_message)

    if api_response:
        # 외부 API 응답이 있으면 바로 반환
        bot_response = api_response
        cta = None
        marketing_triggered = False

        # API 응답도 대화 기록에 저장
        db.save_message(user_id, bot_response, is_user=False, sentiment='neutral')

        print(f"[외부 API] 명령 처리 완료")

        return jsonify({
            'response': bot_response,
            'sentiment': sentiment,
            'sentiment_info': sentiment_result,
            'files_processed': len(file_infos),
            'image_urls': image_urls,
            'attached_files': attached_files,
            'marketing_triggered': False,
            'cta': None,
            'api_triggered': True  # API 응답임을 표시
        })

    # 2단계: 차트 요청 감지 및 생성 (모든 시트)
    chart_data_list = []
    chart_analysis_combined = ""
    chart_type = AutomationAssistant.detect_chart_type(user_message)

    # 엑셀/CSV 파일이 있으면 차트 타입이 없어도 기본 막대 차트 생성
    has_spreadsheet = any(f.get('extension') in ['xlsx', 'csv'] for f in attached_files)
    if not chart_type and has_spreadsheet:
        chart_type = 'bar'  # 기본값: 막대 그래프
        print(f"[차트] 엑셀/CSV 파일 감지 - 자동으로 {chart_type} 차트 생성")

    if chart_type and attached_files:
        # 엑셀/CSV 파일에서 차트 데이터 생성
        for attached_file in attached_files:
            if attached_file.get('extension') in ['xlsx', 'csv']:
                # 엑셀 파일: 모든 시트 처리
                if 'all_sheets' in attached_file and attached_file['all_sheets']:
                    print(f"[차트] {len(attached_file['all_sheets'])}개 시트에 대해 {chart_type} 차트 생성")

                    for sheet_data in attached_file['all_sheets']:
                        sheet_name = sheet_data.get('sheet_name', '시트')
                        print(f"[차트] 시트 '{sheet_name}' 차트 생성 시작")

                        chart_data = AutomationAssistant.prepare_chart_data(
                            {'table_data': sheet_data},
                            chart_type
                        )

                        if chart_data:
                            # 시트 이름을 차트 제목에 추가
                            chart_data['options']['plugins']['title']['text'] = f'{sheet_name} - 데이터 시각화'
                            chart_data['sheet_name'] = sheet_name
                            chart_data_list.append(chart_data)
                            print(f"[차트] 시트 '{sheet_name}' 차트 데이터 생성 완료")

                            # 차트 분석 생성
                            chart_analysis = AutomationAssistant.generate_chart_analysis(
                                chart_data,
                                sheet_data
                            )

                            if chart_analysis:
                                chart_analysis_combined += f"\n\n## 시트: {sheet_name}\n" + chart_analysis

                # CSV 또는 단일 시트: 기존 방식
                elif 'table_data' in attached_file:
                    print(f"[차트] {chart_type} 차트 생성 시작")
                    chart_data = AutomationAssistant.prepare_chart_data(
                        {'table_data': attached_file['table_data']},
                        chart_type
                    )
                    if chart_data:
                        chart_data_list.append(chart_data)
                        print(f"[차트] 차트 데이터 생성 완료")

                        # 차트 분석 생성
                        chart_analysis = AutomationAssistant.generate_chart_analysis(
                            chart_data,
                            attached_file['table_data']
                        )
                        if chart_analysis:
                            chart_analysis_combined += chart_analysis

                # 분석 텍스트를 GPT 메시지에 추가
                if chart_analysis_combined:
                    full_message += chart_analysis_combined
                    print(f"[차트] 차트 분석 추가 완료 - 총 {len(chart_data_list)}개 차트")

                break

    # 3단계: GPT를 통한 응답 생성
    if USE_GPT and openai_client:
        bot_response = generate_gpt_response(user_id, full_message, sentiment,
                                            has_image=len(image_urls) > 0,
                                            image_infos=[{'base64': img['base64']} for img in file_infos if img.get('base64')])
    else:
        bot_response = generate_rule_based_response(full_message, sentiment)

    # 봇 응답 저장
    db.save_message(user_id, bot_response, is_user=False, sentiment='neutral')

    response_data = {
        'response': bot_response,
        'sentiment': sentiment,
        'sentiment_info': sentiment_result,
        'files_processed': len(file_infos),
        'image_urls': image_urls,
        'attached_files': attached_files
    }

    # 차트 데이터가 있으면 추가 (여러 차트 지원)
    if chart_data_list:
        response_data['chart_data_list'] = chart_data_list
        print(f"[응답] {len(chart_data_list)}개 차트 데이터 전달")

    return jsonify(response_data)


def generate_rule_based_response(message, sentiment):
    """
    규칙 기반 응답 생성 (GPT 미사용 시)
    """
    message_lower = message.lower()

    # 인사말 응답
    if any(keyword in message_lower for keyword in ['안녕', '반가워', '처음']):
        return "안녕하세요! 무엇을 도와드릴까요?"

    # 감사 인사 응답
    if any(keyword in message_lower for keyword in ['감사', '고마워']):
        return "천만에요! 더 도와드릴 것이 있으신가요?"

    # 제품 문의
    if any(keyword in message_lower for keyword in ['제품', '상품', '가격', '구매']):
        return "제품에 대해 문의하셨군요. 구체적으로 어떤 제품에 대해 알고 싶으신가요?"

    # 배송 문의
    if any(keyword in message_lower for keyword in ['배송', '배달', '언제', '도착']):
        return "배송 관련 문의시군요. 주문번호를 알려주시면 더 정확한 안내가 가능합니다."

    # 환불/교환
    if any(keyword in message_lower for keyword in ['환불', '교환', '반품', '취소']):
        return "환불/교환 문의시군요. 제품 수령 후 7일 이내 가능하며, 상세한 절차를 안내해드리겠습니다."

    # 기본 응답
    return "문의 내용을 잘 이해했습니다. 더 구체적으로 설명해주시면 더 정확한 도움을 드릴 수 있습니다."


def generate_gpt_response(user_id, message, sentiment, has_image=False, image_infos=None):
    """
    GPT API를 사용한 응답 생성 (이미지 지원 + 웹 검색)
    """
    print(f"[generate_gpt_response] 호출됨 - openai_client: {openai_client is not None}")
    if not openai_client:
        print("[generate_gpt_response] openai_client가 None이므로 rule-based로 전환")
        return generate_rule_based_response(message, sentiment)

    # 이전 대화 이력 가져오기
    history = db.get_user_history(user_id, limit=5)

    # 웹 검색 기능 임시 비활성화 (Google API 403 오류로 인해)
    # 링크 요청 감지 (키워드 기반)
    # search_keywords = ['링크', 'url', '사이트', '웹사이트', '홈페이지', '주소',
    #                    '최신', '뉴스', '정보', '검색', '찾아', '추천', '맛집', '리스트']
    # needs_search = any(keyword in message.lower() for keyword in search_keywords)

    # # 디버깅: 키워드 감지 로그
    # if needs_search:
    #     matched_keywords = [kw for kw in search_keywords if kw in message.lower()]
    #     print(f"[키워드 감지] '{message}' - 매칭된 키워드: {matched_keywords}")

    # # TOP N 요청 감지 (TOP10, TOP 10, 상위 10개, 10가지 등)
    # import re
    # top_n_match = re.search(r'(?:top|상위|추천)\s*(\d+)|(\d+)\s*(?:개|가지|곳)', message.lower())
    # num_results = 10 if top_n_match else 3  # TOP N 요청이면 해당 개수, 아니면 기본 3개

    # if top_n_match:
    #     try:
    #         requested_num = int(top_n_match.group(1) or top_n_match.group(2))
    #         num_results = min(requested_num, 10)  # 최대 10개
    #         needs_search = True  # TOP N 요청은 자동으로 검색 활성화
    #         print(f"[TOP N 감지] {num_results}개 검색 요청")
    #     except:
    #         num_results = 10

    # # 웹 검색 결과 추가
    # search_results = ""
    # if needs_search:
    #     print(f"[웹 검색 시작] 쿼리: '{message}', 개수: {num_results}")
    #     try:
    #         # Google 검색 수행
    #         results = search_google(message, num_results=num_results)
    #         if results:
    #             search_results = "\n\n[웹 검색 결과]\n"
    #             for idx, result in enumerate(results, 1):
    #                 search_results += f"{idx}. {result['title']}\n   {result['link']}\n   {result['snippet']}\n\n"
    #             print(f"[웹 검색 완료] {len(results)}개 결과 GPT에 전달")
    #         else:
    #             print("[웹 검색] 결과 없음")
    #     except Exception as e:
    #         print(f"[웹 검색 오류] {e}")

    search_results = ""  # 웹 검색 비활성화

    # 시스템 프롬프트 (감정에 따라 조절)
    tone_info = sentiment_analyzer.get_response_tone(sentiment)
    current_date = datetime.now().strftime('%Y년 %m월 %d일 %A')
    system_prompt = f"""당신은 친절한 고객지원 챗봇이자 지능형 업무 자동화 비서입니다.
현재 날짜: {current_date}
사용자의 현재 감정: {sentiment}
응답 스타일: {tone_info['style']}

⚠️ 중요: 당신의 학습 데이터는 2024년 10월까지입니다.

다음 지침을 따라주세요:
1. 항상 공손하고 도움이 되는 답변을 제공하세요.
2. 사용자의 감정을 고려하여 적절한 어조로 응답하세요.
3. 구체적이고 실용적인 해결책을 제시하세요.
4. 이전 대화 내용을 참고하여 맥락을 유지하세요.
5. 첨부된 파일이 있다면 그 내용을 분석하여 답변하세요.
6. 날짜를 물어보면 위에 명시된 현재 날짜를 사용하세요.

📋 **맛집, 카페, 장소 추천 시 표 형식 사용 (필수!):**

7. 맛집, 카페, 관광지 등 추천 요청 시 **반드시 아래 HTML 표 형식**을 사용하세요:

<div class="search-table-wrapper">
    <h3 class="search-title">✨ 추천 장소</h3>
    <table class="search-table">
        <thead>
            <tr>
                <th>#</th>
                <th>이름</th>
                <th>설명</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>1</td>
                <td><strong>장소 이름</strong></td>
                <td class="search-snippet">위치, 특징, 대표 메뉴 등 간단한 설명</td>
            </tr>
            <tr>
                <td>2</td>
                <td><strong>장소 이름</strong></td>
                <td class="search-snippet">위치, 특징, 대표 메뉴 등 간단한 설명</td>
            </tr>
        </tbody>
    </table>
</div>

8. **표 작성 규칙:**
   - 이름: 간결하고 정확한 장소명만 (예: "테라로사 커피"), 링크는 절대 포함하지 마세요
   - 설명: 위치(동/구), 특징, 대표 메뉴, 분위기 등을 간단하게 요약
   - 2024년 10월까지의 지식을 바탕으로 유명하고 검증된 장소를 추천
   - 표 위에 간단한 인사말 추가 가능 (예: "서울의 인기 카페 5곳을 추천드립니다!")

9. 추천이 아닌 일반 질문은 표 형식을 사용하지 마세요.

🤖 **데이터 시각화 전문 비서 역할:**

당신은 엑셀(XLSX/CSV) 데이터를 자동으로 분석하고 시각화하는 전문가입니다.

10. **데이터 구조 자동 파악:**
    - 업로드된 엑셀/CSV의 컬럼 구조를 자동으로 분석합니다
    - 컬럼 타입 자동 인식: 날짜형(Date), 숫자형(Numeric), 카테고리형(Category), 텍스트형(Text)
    - 각 컬럼의 특성을 파악하여 최적의 시각화 방법을 제안합니다

11. **자연어 명령 해석 규칙:**
    사용자 요청을 다음 요소로 분해하여 처리합니다:
    - **행동(Action)**: 분석해줘, 그려줘, 시각화해줘, 비교해줘, 보여줘 등
    - **대상(Data)**: 매출, 고객, 카테고리, 상품, 날짜, 특정 컬럼명 등
    - **조건(Filter)**: 특정 기간, 카테고리, 매출 기준, 상위 N개 등
    - **출력형식(Chart Type)**: 라인 차트, 막대그래프, 파이차트, 히트맵 등

    예시:
    - "카테고리별 매출 그래프 그려줘" → 카테고리 집계 → Bar Chart 추천
    - "일자별 매출 추이 보여줘" → 날짜 그룹화 → Line Chart 추천
    - "상위 5개 제품을 차트로 보여줘" → TOP 5 정렬 → Bar Chart 추천
    - "전부다 시각화해" → 모든 숫자형 컬럼에 대해 적절한 차트 제안

12. **차트 자동 생성 규칙:**
    - **날짜 컬럼**이 있으면 → 시간 기반 추이 분석 (Line Chart 우선)
    - **숫자형 컬럼**이 있으면 → 자동으로 합계, 평균, 최대/최소값 계산
    - **카테고리형 컬럼**이 있으면 → 그룹별 집계 수행 (Bar Chart 또는 Pie Chart)
    - **복수의 차트**를 한 번에 제안 가능 (예: 월별 추이 + 카테고리별 점유율)
    - 사용자가 이해하기 쉬운 형태로 자동 최적화

13. **차트 타입 선택 가이드:**
    - **Line Chart**: 시간에 따른 추이, 트렌드 분석
    - **Bar Chart**: 카테고리별 비교, 순위, TOP N
    - **Pie Chart**: 전체 대비 비율, 구성비, 점유율
    - **Scatter Plot**: 두 변수 간 상관관계 (향후 지원 예정)

14. **모호한 요청 처리:**
    - 요청이 명확하지 않으면 **1회만** 질문하여 구체화를 요청합니다
    - 예: "이거 그래프로 보여줘" → "어떤 컬럼을 기준으로 차트를 만들까요? (예: 날짜별, 카테고리별, 제품별)"
    - 가능하면 사용자의 의도를 추론하여 자동으로 처리합니다

15. **출력 규칙:**
    - **분석 요약**: 데이터의 핵심 특징을 3-5줄로 요약
    - **차트 생성**: 시스템이 자동으로 생성한 차트가 표시됩니다
    - **인사이트 제공**: 차트에서 발견한 패턴, 트렌드, 이상치를 설명
    - **실행 가능한 제안**: 비즈니스 의사결정에 도움이 되는 구체적 제안

    예시:
    "매출이 3월부터 지속적으로 상승하고 있습니다. 특히 A 카테고리가 전체 매출의 40%를 차지하고 있어
    집중 관리가 필요합니다. 6월에 소폭 하락이 있었으므로 원인 분석을 권장합니다."

16. **차트 분석 및 설명:**
    - 차트가 자동 생성되면 "[📊 차트 분석]" 섹션의 데이터를 바탕으로 설명합니다
    - 주요 트렌드, 패턴, 이상치를 명확히 언급합니다
    - 숫자는 구체적으로 제시합니다 (예: "평균 50만원", "최대 120만원")
    - 사용자가 다음 액션을 취할 수 있도록 구체적 제안을 제공합니다

📊 **데이터 분석 결과 표시 형식 (필수!):**

17. **Excel/CSV 데이터 분석 결과는 반드시 HTML 표 형식으로 출력하세요:**

<div class='data-analysis-table'>
<h4>분석 제목</h4>
<table>
  <thead>
    <tr><th>항목</th><th>값</th><th>세부사항</th></tr>
  </thead>
  <tbody>
    <tr><td>합계</td><td>123,456</td><td>-</td></tr>
    <tr><td>평균</td><td>1,234.5</td><td>-</td></tr>
    <tr><td>최대</td><td>5,000</td><td>2024-01-15</td></tr>
    <tr><td>최소</td><td>100</td><td>2024-01-01</td></tr>
  </tbody>
</table>
</div>

18. **응답 형식 규칙 (매우 중요!):**

   ⚠️ **절대 금지사항:**
   - 마크다운 문법 사용 금지: ###, ##, -, *, **, 1., 2. 등
   - 긴 텍스트 나열 금지
   - 불필요한 설명 금지

   ✅ **필수 사용 형식:**
   - 모든 내용은 HTML 표 형식으로만 작성
   - 제목: <h3>, <h4> 태그
   - 짧은 설명: <p> 태그 (1-2문장만)
   - 리스트: <ul>, <ol> 태그

19. **데이터 분석 응답 템플릿 (반드시 따르세요):**

<h3>📊 데이터 분석 결과</h3>

<div class='data-analysis-table'>
<h4>주요 통계</h4>
<table>
  <thead>
    <tr><th>항목</th><th>값</th><th>비고</th></tr>
  </thead>
  <tbody>
    <tr><td>총 주문 수</td><td>500건</td><td>-</td></tr>
    <tr><td>평균 매출</td><td>9,903원</td><td>편차 큼</td></tr>
  </tbody>
</table>
</div>

<div class='data-analysis-table'>
<h4>주요 발견사항</h4>
<table>
  <thead>
    <tr><th>문제점</th><th>영향도</th><th>권장 조치</th></tr>
  </thead>
  <tbody>
    <tr><td>가격 편차 큼</td><td>⚠️ 높음</td><td>가격 정책 표준화</td></tr>
    <tr><td>매출 불균형</td><td>⚠️ 중간</td><td>지역별 전략 수립</td></tr>
  </tbody>
</table>
</div>

<p><strong>💡 핵심 요약:</strong> 가격 정책 재검토와 지역별 맞춤 마케팅이 필요합니다.</p>

20. **응답 길이 제한:**
   - 각 표는 3-5행 이내로 제한
   - 전체 응답은 2-3개 표로 요약
   - 불필요한 배경 설명 제거
   - 핵심만 간결하게 전달

**당신의 목표**: 사용자가 자연어로 간단히 요청해도 엑셀 데이터 분석과 차트 시각화를 자동으로 정확하게 수행하는 것입니다. 응답은 반드시 HTML 표 형식으로만 작성하세요.
"""

    # 대화 이력을 메시지 형식으로 변환
    messages = [{"role": "system", "content": system_prompt}]

    for msg in history:
        role = "user" if msg['is_user'] else "assistant"
        messages.append({"role": role, "content": msg['message']})

    # 현재 메시지 추가 (이미지가 있으면 GPT-4 Vision 사용)
    if has_image and image_infos:
        # GPT-4 Vision을 사용하여 이미지 분석
        message_with_search = message + search_results if search_results else message
        content = [{"type": "text", "text": message_with_search}]

        for img_info in image_infos:
            if 'base64' in img_info:
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_info['base64']}"
                    }
                })

        messages.append({"role": "user", "content": content})

        try:
            # GPT-4o Vision API 호출
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GPT-4o Vision API 오류: {e}")
            # Vision 실패 시 일반 GPT-4o로 폴백
            message_with_search = message + search_results if search_results else message
            messages[-1] = {"role": "user", "content": message_with_search}
    else:
        message_with_search = message + search_results if search_results else message
        messages.append({"role": "user", "content": message_with_search})

    try:
        # GPT API 호출 (GPT-4o)
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            max_tokens=1000,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"GPT API 오류: {e}")
        # 오류 시 규칙 기반 응답 사용
        return generate_rule_based_response(message, sentiment)


@app.route('/api/history', methods=['GET'])
def get_history():
    """사용자의 대화 이력 조회 (첨부 파일 미리보기 포함)"""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    history = db.get_user_history(user_id)

    # 첨부 파일 정보 처리 (URL 및 미리보기 데이터 추가)
    for msg in history:
        if 'attachments' in msg and msg['attachments']:
            msg['attached_files'] = []
            for att in msg['attachments']:
                parsed_info = att.get('parsed_info', {})

                # file_info는 저장된 전체 정보 (file_processor에서 반환한 것)
                file_ext = parsed_info.get('extension', parsed_info.get('type', 'unknown'))
                filename = att['filename']

                # 파일 정보 구성
                file_info_dict = {
                    'filename': filename,
                    'size': parsed_info.get('size', att.get('file_size', 0)),
                    'extension': file_ext,
                    'is_image': parsed_info.get('is_image', False)
                }

                # 저장된 URL 사용
                if parsed_info.get('url'):
                    file_info_dict['url'] = parsed_info['url']
                elif att.get('file_url'):
                    file_info_dict['url'] = att['file_url']

                # 이미지 base64 데이터 추가
                if 'base64' in parsed_info:
                    file_info_dict['base64'] = parsed_info['base64']
                    file_info_dict['format'] = parsed_info.get('format')
                    file_info_dict['image_size'] = parsed_info.get('size')

                # 표 데이터가 있으면 추가 (Excel, CSV)
                if 'table_data' in parsed_info:
                    file_info_dict['table_data'] = parsed_info['table_data']

                # 텍스트 미리보기 추가 (Word, TXT, PDF)
                if 'text_preview' in parsed_info:
                    file_info_dict['text_preview'] = parsed_info['text_preview']

                msg['attached_files'].append(file_info_dict)

    stats = db.get_user_stats(user_id)

    return jsonify({
        'history': history,
        'stats': stats
    })


@app.route('/api/search', methods=['GET'])
def search_messages():
    """대화 내용 검색 API"""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    keyword = request.args.get('keyword', '').strip()

    if not keyword:
        return jsonify({'error': '검색어를 입력해주세요.'}), 400

    try:
        print(f"[검색 API] user_id: {user_id}, keyword: {keyword}")

        # 데이터베이스에서 검색
        result = db.search_messages(user_id, keyword=keyword, limit=100)

        print(f"[검색 API] 결과: total={result['total']}, messages={len(result['messages'])}")

        return jsonify({
            'success': True,
            'keyword': keyword,
            'results': result['messages'],
            'total': result['total']
        })
    except Exception as e:
        print(f"[검색 API 오류] {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '검색 중 오류가 발생했습니다.'}), 500


@app.route('/api/delete-history', methods=['POST'])
def delete_history():
    """대화 기록 삭제 API"""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    try:
        deleted_count = db.delete_all_messages(user_id)
        return jsonify({
            'success': True,
            'message': f'{deleted_count}개의 메시지가 삭제되었습니다.',
            'deleted_count': deleted_count
        })
    except Exception as e:
        print(f"[대화 삭제 오류] {str(e)}")
        return jsonify({'error': '대화 삭제 중 오류가 발생했습니다.'}), 500


if __name__ == '__main__':
    # 로컬 개발 환경에서만 실행
    if not IS_VERCEL:
        db_info = "MongoDB (영구 저장)" if Config.USE_MONGODB else f"SQLite ({Config.DATABASE_PATH})"
        print(f"""
        ========================================
        고객지원 챗봇 서버 시작
        ========================================
        - GPT API 사용: {USE_GPT}
        - 데이터베이스: {db_info}
        - 서버 주소: http://localhost:5000
        ========================================
        """)
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        print("Vercel 서버리스 환경 - WSGI 모드로 실행됩니다.")


# ==================== 사용자 설정 API ====================

@app.route('/api/preferences', methods=['GET'])
def get_preferences():
    """사용자 설정 조회"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    try:
        prefs = db.get_user_preferences(user_id)
        if not prefs:
            return jsonify({'error': '설정을 찾을 수 없습니다.'}), 404
        return jsonify(prefs)
    except Exception as e:
        print(f"설정 조회 오류: {str(e)}")
        return jsonify({'error': f'설정 조회 중 오류: {str(e)}'}), 500


@app.route('/api/preferences', methods=['POST'])
def update_preferences():
    """사용자 설정 업데이트"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    data = request.json
    db.update_user_preferences(user_id, data)

    return jsonify({
        'success': True,
        'message': '설정이 저장되었습니다.'
    })


# New endpoint names (frontend uses these)
@app.route('/api/settings', methods=['GET'])
def get_settings():
    """사용자 설정 조회 (새 엔드포인트)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    try:
        prefs = db.get_user_preferences(user_id)
        if not prefs:
            return jsonify({'error': '설정을 찾을 수 없습니다.'}), 404
        return jsonify(prefs)
    except Exception as e:
        print(f"설정 조회 오류: {str(e)}")
        return jsonify({'error': f'설정 조회 중 오류: {str(e)}'}), 500


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """사용자 설정 업데이트 (새 엔드포인트)"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    try:
        data = request.json
        db.update_user_preferences(user_id, data)

        return jsonify({
            'success': True,
            'message': '설정이 저장되었습니다.'
        })
    except Exception as e:
        print(f"설정 저장 오류: {str(e)}")
        return jsonify({'error': f'설정 저장 중 오류: {str(e)}'}), 500


# ==================== 대화 기록 검색 API ====================
# 간단한 검색은 위의 /api/search 사용


@app.route('/api/messages/by-date', methods=['GET'])
def get_messages_by_date():
    """날짜별 메시지 조회"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({'error': '시작일과 종료일이 필요합니다.'}), 400
    
    result = db.get_messages_by_date_range(user_id, start_date, end_date)
    return jsonify(result)


@app.route('/api/messages/by-sentiment', methods=['GET'])
def get_messages_by_sentiment():
    """감정별 메시지 조회"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    sentiment = request.args.get('sentiment')
    limit = int(request.args.get('limit', 50))
    
    if not sentiment:
        return jsonify({'error': '감정 타입이 필요합니다.'}), 400
    
    result = db.get_messages_by_sentiment(user_id, sentiment, limit)
    return jsonify(result)

