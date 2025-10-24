"""
감정 분석 및 응답 어조 조절 모듈
사용자의 말투와 감정을 분석하여 적절한 응답 어조를 결정합니다.
"""
import re

class SentimentAnalyzer:
    def __init__(self):
        # 감정별 키워드 정의
        self.angry_keywords = [
            '화나', '짜증', '불만', '최악', '엉망', '말도 안', '어이없',
            '답답', '화남', '기분 나쁘', '실망', '!', '!!!'
        ]

        self.sad_keywords = [
            '슬프', '우울', '힘들', '속상', '안타깝', '아쉽',
            '걱정', '불안', '외로', '서러'
        ]

        self.happy_keywords = [
            '좋아', '감사', '고마', '훌륭', '최고', '멋지', '완벽',
            '기쁘', '행복', '만족', '굿', 'ㅎㅎ', 'ㅋㅋ'
        ]

        self.polite_keywords = [
            '부탁', '도와주', '문의', '질문', '여쭤', '궁금',
            '알려주', '확인', '요청'
        ]

    def analyze(self, message):
        """
        메시지의 감정을 분석

        Returns:
            dict: {
                'sentiment': 'angry'|'sad'|'happy'|'polite'|'neutral',
                'confidence': float (0-1),
                'detected_keywords': list
            }
        """
        message_lower = message.lower()

        # 각 감정별 점수 계산
        scores = {
            'angry': self._calculate_score(message_lower, self.angry_keywords),
            'sad': self._calculate_score(message_lower, self.sad_keywords),
            'happy': self._calculate_score(message_lower, self.happy_keywords),
            'polite': self._calculate_score(message_lower, self.polite_keywords)
        }

        # 느낌표가 많으면 화남 가능성 증가
        exclamation_count = message.count('!')
        if exclamation_count >= 2:
            scores['angry'] += exclamation_count * 0.2

        # 가장 높은 점수의 감정 선택
        max_sentiment = max(scores, key=scores.get)
        max_score = scores[max_sentiment]

        # 점수가 너무 낮으면 중립으로 분류
        if max_score < 0.3:
            sentiment = 'neutral'
            confidence = 0.5
        else:
            sentiment = max_sentiment
            confidence = min(max_score, 1.0)

        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': scores
        }

    def _calculate_score(self, message, keywords):
        """키워드 매칭을 통한 점수 계산"""
        score = 0
        for keyword in keywords:
            if keyword in message:
                score += 1

        # 정규화 (0-1 범위)
        return min(score / 3, 1.0)

    def get_response_tone(self, sentiment):
        """
        감정에 따른 응답 어조 결정

        Returns:
            dict: {
                'tone': str (응답 어조 설명),
                'prefix': str (응답 시작 문구),
                'style': str (응답 스타일 가이드)
            }
        """
        tone_map = {
            'angry': {
                'tone': 'apologetic',
                'prefix': '불편을 드려 정말 죄송합니다. ',
                'style': '공손하고 진정시키는 어조, 해결 방안 제시'
            },
            'sad': {
                'tone': 'empathetic',
                'prefix': '힘든 상황이시군요. ',
                'style': '공감하고 위로하는 어조, 긍정적인 해결책 제시'
            },
            'happy': {
                'tone': 'cheerful',
                'prefix': '좋은 말씀 감사합니다! ',
                'style': '밝고 긍정적인 어조'
            },
            'polite': {
                'tone': 'professional',
                'prefix': '문의 주셔서 감사합니다. ',
                'style': '전문적이고 친절한 어조'
            },
            'neutral': {
                'tone': 'friendly',
                'prefix': '',
                'style': '친근하고 자연스러운 어조'
            }
        }

        return tone_map.get(sentiment, tone_map['neutral'])

    def adjust_response(self, response, sentiment):
        """
        감정에 맞춰 응답 조절
        """
        tone_info = self.get_response_tone(sentiment)

        # 응답 앞에 감정에 맞는 접두사 추가
        if tone_info['prefix'] and not response.startswith(tone_info['prefix']):
            response = tone_info['prefix'] + response

        return response
