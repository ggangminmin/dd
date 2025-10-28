"""
Flask 기반 고객지원 챗봇 애플리케이션
상담 이력을 기억하고 감정에 맞춰 응답하는 챗봇
"""
from flask import Flask, render_template, request, jsonify, session
from config import Config
from database import Database
from sentiment_analyzer import SentimentAnalyzer
from file_processor import FileProcessor
import os
import json
import uuid
from werkzeug.utils import secure_filename

# GPT API 연동 (선택적)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

app = Flask(__name__)
app.config.from_object(Config)

# 업로드 폴더 설정
UPLOAD_FOLDER = os.path.join(app.static_folder, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# 데이터베이스 및 감정 분석기 초기화
db = Database()
sentiment_analyzer = SentimentAnalyzer()

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


@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html', chatbot_name=Config.CHATBOT_NAME)


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

    # 이전 대화 이력 조회
    history = db.get_user_history(user_id)
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

    for file in files:
        if file and file.filename:
            # 파일 읽기
            file_data = file.read()

            # 이미지 파일인 경우 저장
            if allowed_image_file(file.filename):
                # 고유한 파일명 생성
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = f"{uuid.uuid4()}.{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

                # 파일 저장
                with open(filepath, 'wb') as f:
                    f.write(file_data)

                # URL 생성
                image_url = f"/static/uploads/{unique_filename}"
                image_urls.append(image_url)

            # 파일 처리
            result = FileProcessor.process_file(file_data, file.filename)

            if result['success']:
                file_contents.append(result['text'])
                file_infos.append(result['info'])
                if result.get('has_image'):
                    has_image = True
            else:
                return jsonify({'error': result['error']}), 400

    # 파일 내용을 메시지에 추가
    full_message = user_message
    if file_contents:
        full_message += "\n\n[첨부된 파일 내용]\n" + "\n\n".join(file_contents)

    # 사용자 메시지 저장
    message_id = db.save_message(user_id, user_message if user_message else "[파일 첨부]", is_user=True, sentiment=sentiment)

    # 파일 정보 저장
    for file_info in file_infos:
        db.save_file_attachment(
            message_id,
            file_info['filename'],
            file_info['type'],
            file_info.get('size', 0),
            json.dumps(file_info)
        )

    # 봇 응답 생성
    if USE_GPT:
        bot_response = generate_gpt_response(user_id, full_message, sentiment, has_image, file_infos if has_image else None)
    else:
        bot_response = generate_rule_based_response(full_message, sentiment)

    # 감정에 맞춰 응답 조절
    bot_response = sentiment_analyzer.adjust_response(bot_response, sentiment)

    # 봇 응답 저장
    db.save_message(user_id, bot_response, is_user=False, sentiment='neutral')

    return jsonify({
        'response': bot_response,
        'sentiment': sentiment,
        'sentiment_info': sentiment_result,
        'files_processed': len(file_infos),
        'image_urls': image_urls
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
    system_prompt = f"""당신은 친절한 고객지원 챗봇입니다.
사용자의 현재 감정: {sentiment}
응답 스타일: {tone_info['style']}

다음 지침을 따라주세요:
1. 항상 공손하고 도움이 되는 답변을 제공하세요.
2. 사용자의 감정을 고려하여 적절한 어조로 응답하세요.
3. 구체적이고 실용적인 해결책을 제시하세요.
4. 이전 대화 내용을 참고하여 맥락을 유지하세요.
5. 첨부된 파일이 있다면 그 내용을 분석하여 답변하세요.
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
    """사용자의 대화 이력 조회"""
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    history = db.get_user_history(user_id)
    stats = db.get_user_stats(user_id)

    return jsonify({
        'history': history,
        'stats': stats
    })


if __name__ == '__main__':
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
