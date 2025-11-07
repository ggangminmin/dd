"""
전문가 시스템 - 역할 기반 AI 에이전트
메세징 전문가와 문서작성 전문가가 협업하는 시스템
"""
from typing import Dict, List, Optional
import json
from datetime import datetime


class MessagingExpert:
    """
    메세징 전문가 - 고객 질문에 자연스럽고 친절하게 답변
    감정 분석 결과에 따라 말투를 조절하여 응대
    """

    def __init__(self, sentiment_analyzer, use_gpt=False, openai_client=None):
        self.sentiment_analyzer = sentiment_analyzer
        self.use_gpt = use_gpt
        self.openai_client = openai_client

    def generate_response(self, message: str, sentiment: str, context: List[Dict] = None) -> str:
        """
        고객 메시지에 대한 응답 생성

        Args:
            message: 고객 메시지
            sentiment: 감정 분석 결과 (angry, sad, happy, polite, neutral)
            context: 이전 대화 컨텍스트

        Returns:
            생성된 응답 메시지
        """
        if self.use_gpt and self.openai_client:
            return self._generate_gpt_response(message, sentiment, context)
        else:
            return self._generate_rule_based_response(message, sentiment)

    def _generate_gpt_response(self, message: str, sentiment: str, context: List[Dict] = None) -> str:
        """GPT를 사용한 응답 생성"""
        # 감정별 시스템 프롬프트
        sentiment_prompts = {
            'angry': '고객이 화가 난 상태입니다. 매우 정중하고 사과하는 태도로, 문제 해결에 집중하여 답변해주세요.',
            'sad': '고객이 슬픈 상태입니다. 공감하고 위로하는 따뜻한 말투로, 긍정적인 해결책을 제시해주세요.',
            'happy': '고객이 기쁜 상태입니다. 밝고 친절한 말투로 응답하며, 고객의 긍정적인 기분을 유지시켜주세요.',
            'polite': '고객이 공손한 태도입니다. 전문적이면서도 친절한 말투로 정확한 정보를 제공해주세요.',
            'neutral': '고객이 중립적인 태도입니다. 친절하고 명확하게 답변해주세요.'
        }

        # 파일 첨부 확인
        has_file = '[첨부된 파일 내용]' in message
        file_instruction = ""
        if has_file:
            file_instruction = "\n\n⚠️ 중요: 고객이 파일을 첨부했습니다. 첨부된 파일 내용을 반드시 분석하고, 그 내용에 대해 구체적으로 답변해주세요. 파일을 확인할 수 없다고 말하지 마세요."

        system_prompt = f"""당신은 고객지원 메세징 전문가입니다.
다음 역할을 수행해주세요:

1. 고객의 질문에 자연스럽고 친절하게 답변
2. 감정 상태에 맞는 적절한 말투 사용
3. 구체적이고 도움이 되는 정보 제공
4. 한국어로 응답 (존댓말 사용)
5. 첨부된 파일이 있다면 반드시 내용을 분석하고 관련 답변 제공

현재 고객 감정 상태: {sentiment}
{sentiment_prompts.get(sentiment, sentiment_prompts['neutral'])}{file_instruction}
"""

        # 대화 컨텍스트 구성
        messages = [{"role": "system", "content": system_prompt}]

        if context:
            for msg in context[-5:]:  # 최근 5개 대화만 포함
                role = "user" if msg.get('is_user') else "assistant"
                messages.append({"role": role, "content": msg.get('message', '')})

        messages.append({"role": "user", "content": message})

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=1500  # 응답 길이 제한 증가
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GPT 응답 생성 오류: {e}")
            return self._generate_rule_based_response(message, sentiment)

    def _generate_rule_based_response(self, message: str, sentiment: str) -> str:
        """규칙 기반 응답 생성 (GPT 미사용 시)"""
        # 파일 첨부 확인
        has_file = '[첨부된 파일 내용]' in message

        if has_file:
            # 파일 내용 추출
            file_response = "첨부하신 파일을 확인했습니다. 📎\n\n"

            # 파일 타입별 응답
            if 'excel' in message.lower() or '.xlsx' in message.lower() or 'csv' in message.lower():
                file_response += "엑셀 파일의 데이터를 확인했습니다. 필요하신 분석이나 추가 정보가 있으시면 말씀해주세요."
            elif 'image' in message.lower() or '.jpg' in message.lower() or '.png' in message.lower():
                file_response += "이미지를 확인했습니다. 관련하여 도움이 필요하신 부분을 구체적으로 말씀해주시면 더 정확한 안내가 가능합니다."
            elif 'pdf' in message.lower() or 'docx' in message.lower():
                file_response += "문서 내용을 확인했습니다. 해당 내용과 관련하여 궁금하신 점이나 도움이 필요하신 부분이 있으시면 말씀해주세요."
            else:
                file_response += "파일 내용을 확인했습니다. 어떤 부분에 대해 도움이 필요하신가요?"

            return file_response

        # 감정별 응답 템플릿
        templates = {
            'angry': [
                "불편을 드려 정말 죄송합니다. 😔 ",
                "말씀하신 문제를 빠르게 해결해드리겠습니다. ",
                "고객님의 소중한 의견 감사드립니다."
            ],
            'sad': [
                "힘든 상황이시군요. 😢 ",
                "최선을 다해 도와드리겠습니다. ",
                "긍정적인 결과가 있을 거예요!"
            ],
            'happy': [
                "좋은 말씀 감사합니다! 😊 ",
                "더 나은 서비스로 보답하겠습니다. ",
                "항상 응원해주셔서 감사합니다!"
            ],
            'polite': [
                "정중한 문의 감사드립니다. 🙏 ",
                "자세히 안내해드리겠습니다. ",
                "추가로 궁금하신 점이 있으시면 언제든 말씀해주세요."
            ],
            'neutral': [
                "문의 주셔서 감사합니다. ",
                "도움이 되는 정보를 제공해드리겠습니다. ",
                "더 궁금하신 점이 있으시면 말씀해주세요."
            ]
        }

        response_parts = templates.get(sentiment, templates['neutral'])
        return ''.join(response_parts)


class MarketingExpert:
    """
    마케팅 전문가 - 긍정적인 반응 감지 시 자연스러운 CTA(Call-To-Action) 제안
    """

    def __init__(self, use_gpt=False, openai_client=None):
        self.use_gpt = use_gpt
        self.openai_client = openai_client
        # 긍정 신호 키워드
        self.positive_signals = [
            '좋아요', '괜찮네요', '관심 있어요', '좋은데요', '마음에 들어요',
            '구매', '사고 싶어요', '알아보고 싶어요', '더 알려주세요',
            '상담', '문의', '신청', '체험', '이용', '해보고 싶어요'
        ]

    def detect_positive_signal(self, message: str) -> bool:
        """긍정 신호 감지"""
        message_lower = message.lower()
        return any(signal in message_lower for signal in self.positive_signals)

    def generate_cta(self, message: str, sentiment: str, context: List[Dict] = None) -> Optional[str]:
        """
        긍정 신호 감지 시 자연스러운 CTA 생성

        Args:
            message: 고객 메시지
            sentiment: 감정 분석 결과
            context: 대화 컨텍스트

        Returns:
            CTA 문구 (긍정 신호가 없으면 None)
        """
        if not self.detect_positive_signal(message):
            return None

        if self.use_gpt and self.openai_client:
            return self._generate_gpt_cta(message, sentiment, context)
        else:
            return self._generate_rule_based_cta(message)

    def _generate_gpt_cta(self, message: str, sentiment: str, context: List[Dict] = None) -> str:
        """GPT를 사용한 CTA 생성"""
        system_prompt = """당신은 마케팅 전문가입니다.
고객이 긍정적인 반응을 보일 때, 자연스럽고 부드러운 다음 행동 제안(CTA)을 생성해주세요.

CTA 유형:
1. 상담 예약
2. 무료 체험 신청
3. 제품 페이지 방문
4. 추가 정보 요청
5. 특별 혜택 안내

중요 원칙:
- 강압적이지 않고 진심 어린 제안
- 고객 입장에서 도움이 되는 톤
- 한국어 존댓말 사용
- 1-2문장으로 간결하게

CTA만 응답해주세요."""

        messages = [{"role": "system", "content": system_prompt}]

        if context:
            for msg in context[-3:]:  # 최근 3개 대화만
                role = "user" if msg.get('is_user') else "assistant"
                messages.append({"role": role, "content": msg.get('message', '')})

        messages.append({"role": "user", "content": f"고객 메시지: {message}\n\n적절한 CTA를 생성해주세요."})

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"GPT CTA 생성 오류: {e}")
            return self._generate_rule_based_cta(message)

    def _generate_rule_based_cta(self, message: str) -> str:
        """규칙 기반 CTA 생성"""
        message_lower = message.lower()

        # 구매 관련 신호
        if any(word in message_lower for word in ['구매', '사고 싶', '주문']):
            return "지금 바로 구매 상담을 도와드릴까요? 전문 상담사가 친절하게 안내해드리겠습니다. 😊"

        # 체험 관련 신호
        if any(word in message_lower for word in ['체험', '써보', '이용']):
            return "무료 체험을 신청하시겠어요? 부담 없이 먼저 경험해보실 수 있습니다! ✨"

        # 상담 관련 신호
        if any(word in message_lower for word in ['상담', '문의', '알아보']):
            return "상담 예약을 도와드릴까요? 고객님께 딱 맞는 솔루션을 제안해드리겠습니다. 📞"

        # 일반적인 긍정 신호
        if any(word in message_lower for word in ['좋아', '괜찮', '관심']):
            return "더 자세한 정보를 확인하시겠어요? 추가로 궁금하신 점이 있으시면 언제든 말씀해주세요! 💡"

        # 기본 CTA
        return "도움이 되셨다니 기쁩니다! 추가로 궁금하신 점이나 도움이 필요하시면 언제든 말씀해주세요. 😊"


class DocumentationExpert:
    """
    문서작성 전문가 - 대화 내용을 구조화하여 FAQ나 내부 문서로 작성
    """

    def __init__(self, use_gpt=False, openai_client=None):
        self.use_gpt = use_gpt
        self.openai_client = openai_client
        self.conversation_buffer = []

    def add_conversation(self, user_message: str, bot_response: str, sentiment: str):
        """대화 내용을 버퍼에 추가"""
        self.conversation_buffer.append({
            'user_message': user_message,
            'bot_response': bot_response,
            'sentiment': sentiment,
            'timestamp': datetime.now().isoformat()
        })

    def generate_summary(self) -> Optional[Dict]:
        """
        대화 내용을 요약하고 구조화

        Returns:
            요약된 문서 정보 (주제, 키워드, FAQ 후보 등)
        """
        if not self.conversation_buffer:
            return None

        if self.use_gpt and self.openai_client:
            return self._generate_gpt_summary()
        else:
            return self._generate_simple_summary()

    def _generate_gpt_summary(self) -> Dict:
        """GPT를 사용한 대화 요약"""
        conversation_text = "\n".join([
            f"고객: {conv['user_message']}\n챗봇: {conv['bot_response']}"
            for conv in self.conversation_buffer
        ])

        system_prompt = """당신은 문서작성 전문가입니다.
고객과의 대화 내용을 분석하여 다음 정보를 JSON 형식으로 제공해주세요:

1. main_topic: 대화의 주요 주제 (한 문장)
2. keywords: 핵심 키워드 (리스트, 5-10개)
3. complaint_types: 고객 불만 유형 (리스트, 있다면. 예: "배송지연", "제품불량", "서비스불만")
4. faq_candidate: FAQ로 만들 수 있는 질문-답변 쌍 (최소 1개, 최대 3개)
5. sentiment_summary: 전체 대화의 감정 흐름 요약
6. positive_signals: 긍정적 반응이나 구매 의사 표현 (있다면)
7. customer_needs: 고객이 원하는 것 또는 해결하고자 하는 문제
8. action_items: 필요한 후속 조치 (리스트)

JSON 형식으로만 응답해주세요."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"다음 대화를 분석해주세요:\n\n{conversation_text}"}
                ],
                temperature=0.3,
                max_tokens=1000  # 요약 길이 제한 증가
            )

            summary_text = response.choices[0].message.content
            # JSON 파싱 시도
            try:
                summary = json.loads(summary_text)
            except:
                # JSON 파싱 실패 시 기본 구조 생성
                summary = {
                    'main_topic': summary_text[:100],
                    'keywords': [],
                    'faq_candidate': None,
                    'sentiment_summary': '분석 실패',
                    'action_items': []
                }

            summary['conversation_count'] = len(self.conversation_buffer)
            summary['generated_at'] = datetime.now().isoformat()
            return summary

        except Exception as e:
            print(f"GPT 요약 생성 오류: {e}")
            return self._generate_simple_summary()

    def _generate_simple_summary(self) -> Dict:
        """간단한 규칙 기반 요약"""
        # 감정 분포 계산
        sentiments = [conv['sentiment'] for conv in self.conversation_buffer]
        sentiment_counts = {}
        for s in sentiments:
            sentiment_counts[s] = sentiment_counts.get(s, 0) + 1

        # 가장 많이 나타난 감정
        dominant_sentiment = max(sentiment_counts.items(), key=lambda x: x[1])[0] if sentiment_counts else 'neutral'

        return {
            'main_topic': '고객 문의 대화',
            'keywords': ['고객지원', '문의'],
            'conversation_count': len(self.conversation_buffer),
            'sentiment_summary': f'주요 감정: {dominant_sentiment} ({sentiment_counts.get(dominant_sentiment, 0)}회)',
            'sentiment_distribution': sentiment_counts,
            'faq_candidate': None,
            'action_items': [],
            'generated_at': datetime.now().isoformat()
        }

    def clear_buffer(self):
        """대화 버퍼 초기화"""
        self.conversation_buffer = []

    def save_to_faq(self, summary: Dict, filename: str = 'faq_candidates.json'):
        """FAQ 후보를 파일에 저장"""
        try:
            # 기존 FAQ 파일 읽기
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    faq_data = json.load(f)
            except FileNotFoundError:
                faq_data = {'candidates': []}

            # 새로운 FAQ 후보 추가
            faq_data['candidates'].append(summary)

            # 파일에 저장
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(faq_data, f, ensure_ascii=False, indent=2)

            return True
        except Exception as e:
            print(f"FAQ 저장 오류: {e}")
            return False


class ExpertSystem:
    """
    전문가 협업 시스템 - 메세징, 마케팅, 문서작성 전문가 3인 체제
    """

    def __init__(self, sentiment_analyzer, use_gpt=False, openai_client=None):
        self.messaging_expert = MessagingExpert(sentiment_analyzer, use_gpt, openai_client)
        self.marketing_expert = MarketingExpert(use_gpt, openai_client)
        self.documentation_expert = DocumentationExpert(use_gpt, openai_client)
        self.conversation_counter = 0
        self.auto_summarize_interval = 10  # 10개 대화마다 자동 요약

    def process_message(self, message: str, sentiment: str, context: List[Dict] = None) -> Dict:
        """
        메시지 처리 - 3명의 전문가가 협업하여 응답 생성

        워크플로우:
        1. 메세징 전문가가 1차 응답 생성
        2. 마케팅 전문가가 긍정 신호 감지 시 CTA 추가
        3. 문서작성 전문가가 대화 내용 기록

        Args:
            message: 고객 메시지
            sentiment: 감정 분석 결과
            context: 대화 컨텍스트

        Returns:
            응답 딕셔너리 (response, cta, marketing_triggered)
        """
        # 1단계: 메세징 전문가가 응답 생성
        response = self.messaging_expert.generate_response(message, sentiment, context)

        # 2단계: 마케팅 전문가가 긍정 신호 감지 및 CTA 생성
        cta = self.marketing_expert.generate_cta(message, sentiment, context)
        marketing_triggered = cta is not None

        # CTA가 있으면 응답에 자연스럽게 추가
        if cta:
            response = f"{response}\n\n{cta}"
            print(f"[마케팅 전문가] CTA 생성: {cta[:50]}...")

        # 3단계: 문서작성 전문가가 대화 내용 기록
        self.documentation_expert.add_conversation(message, response, sentiment)
        self.conversation_counter += 1

        # 일정 대화 수마다 자동 요약
        if self.conversation_counter >= self.auto_summarize_interval:
            self.auto_summarize()

        return {
            'response': response,
            'cta': cta,
            'marketing_triggered': marketing_triggered
        }

    def auto_summarize(self):
        """자동 요약 및 FAQ 저장"""
        summary = self.documentation_expert.generate_summary()
        if summary:
            self.documentation_expert.save_to_faq(summary)
            self.documentation_expert.clear_buffer()
            self.conversation_counter = 0
            print(f"[문서작성 전문가] 대화 요약 완료: {summary.get('main_topic', 'N/A')}")

    def manual_summarize(self) -> Optional[Dict]:
        """수동 요약 트리거"""
        summary = self.documentation_expert.generate_summary()
        if summary:
            self.documentation_expert.save_to_faq(summary)
            self.documentation_expert.clear_buffer()
            self.conversation_counter = 0
        return summary

    def get_conversation_count(self) -> int:
        """현재 버퍼의 대화 수 반환"""
        return len(self.documentation_expert.conversation_buffer)
