"""
Flask 기반 고객지원 챗봇 애플리케이션
상담 이력을 기억하고 감정에 맞춰 응답하는 챗봇
"""
from flask import Flask, render_template, request, jsonify, session
from config import Config
from database import Database
from sentiment_analyzer import SentimentAnalyzer
from file_processor import FileProcessor
from external_apis import ExternalAPIManager
from email_service import EmailService
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
else:
    openai_client = None
    USE_GPT = False

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
    if file_contents:
        full_message += "\n\n[첨부된 파일 내용]\n" + "\n\n".join(file_contents)

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

    # 2단계: GPT를 통한 응답 생성
    if USE_GPT and openai_client:
        bot_response = generate_gpt_response(user_id, full_message, sentiment,
                                            has_image=len(image_urls) > 0,
                                            image_infos=[{'base64': img['base64']} for img in file_infos if img.get('base64')])
    else:
        bot_response = generate_rule_based_response(full_message, sentiment)

    # 봇 응답 저장
    db.save_message(user_id, bot_response, is_user=False, sentiment='neutral')

    return jsonify({
        'response': bot_response,
        'sentiment': sentiment,
        'sentiment_info': sentiment_result,
        'files_processed': len(file_infos),
        'image_urls': image_urls,
        'attached_files': attached_files
    })


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
    GPT API를 사용한 응답 생성 (이미지 지원)
    """
    if not openai_client:
        return generate_rule_based_response(message, sentiment)

    # 이전 대화 이력 가져오기
    history = db.get_user_history(user_id, limit=5)

    # 시스템 프롬프트 (감정에 따라 조절)
    tone_info = sentiment_analyzer.get_response_tone(sentiment)
    current_date = datetime.now().strftime('%Y년 %m월 %d일 %A')
    system_prompt = f"""당신은 친절한 고객지원 챗봇입니다.
현재 날짜: {current_date}
사용자의 현재 감정: {sentiment}
응답 스타일: {tone_info['style']}

다음 지침을 따라주세요:
1. 항상 공손하고 도움이 되는 답변을 제공하세요.
2. 사용자의 감정을 고려하여 적절한 어조로 응답하세요.
3. 구체적이고 실용적인 해결책을 제시하세요.
4. 이전 대화 내용을 참고하여 맥락을 유지하세요.
5. 첨부된 파일이 있다면 그 내용을 분석하여 답변하세요.
6. 날짜를 물어보면 위에 명시된 현재 날짜를 사용하세요.
"""

    # 대화 이력을 메시지 형식으로 변환
    messages = [{"role": "system", "content": system_prompt}]

    for msg in history:
        role = "user" if msg['is_user'] else "assistant"
        messages.append({"role": role, "content": msg['message']})

    # 현재 메시지 추가 (이미지가 있으면 GPT-4 Vision 사용)
    if has_image and image_infos:
        # GPT-4 Vision을 사용하여 이미지 분석
        content = [{"type": "text", "text": message}]

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
            # GPT-4 Vision API 호출
            response = openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=300
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GPT-4 Vision API 오류: {e}")
            # Vision 실패 시 일반 GPT-3.5로 폴백
            messages[-1] = {"role": "user", "content": message}
    else:
        messages.append({"role": "user", "content": message})

    try:
        # GPT API 호출
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=200,
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

    # 검색 파라미터
    keyword = request.args.get('keyword', '').strip()

    if not keyword:
        return jsonify({'error': '검색어를 입력해주세요.'}), 400

    try:
        # 데이터베이스에서 검색
        result = db.search_messages(user_id, keyword=keyword, limit=100)

        return jsonify({
            'success': True,
            'keyword': keyword,
            'results': result['messages'],
            'total': result['total']
        })
    except Exception as e:
        print(f"[검색 오류] {str(e)}")
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
        print(f"""
        ========================================
        고객지원 챗봇 서버 시작
        ========================================
        - GPT API 사용: {USE_GPT}
        - 데이터베이스: {Config.DATABASE_PATH}
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

