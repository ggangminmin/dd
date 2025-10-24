"""
데이터베이스 관리 모듈 - SQLite를 사용한 대화 이력 저장
"""
import sqlite3
from datetime import datetime
from config import Config

class Database:
    def __init__(self):
        self.db_path = Config.DATABASE_PATH
        self.init_db()

    def get_connection(self):
        """데이터베이스 연결 생성"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        return conn

    def init_db(self):
        """데이터베이스 테이블 초기화"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 사용자 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 대화 이력 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                is_user BOOLEAN NOT NULL,
                sentiment TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.commit()
        conn.close()

    def get_or_create_user(self, username):
        """사용자 조회 또는 생성"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 사용자 조회
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()

        if user:
            user_id = user['id']
        else:
            # 사용자 생성
            cursor.execute('INSERT INTO users (username) VALUES (?)', (username,))
            conn.commit()
            user_id = cursor.lastrowid

        conn.close()
        return user_id

    def save_message(self, user_id, message, is_user, sentiment=None):
        """메시지 저장"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO chat_history (user_id, message, is_user, sentiment)
            VALUES (?, ?, ?, ?)
        ''', (user_id, message, is_user, sentiment))

        conn.commit()
        conn.close()

    def get_user_history(self, user_id, limit=None):
        """사용자의 대화 이력 조회"""
        if limit is None:
            limit = Config.MAX_HISTORY_LENGTH

        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT message, is_user, sentiment, timestamp
            FROM chat_history
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (user_id, limit))

        history = cursor.fetchall()
        conn.close()

        # 최신 순서를 오래된 순서로 변경
        return list(reversed([dict(row) for row in history]))

    def get_user_stats(self, user_id):
        """사용자 통계 정보"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT COUNT(*) as total_messages,
                   MIN(timestamp) as first_interaction,
                   MAX(timestamp) as last_interaction
            FROM chat_history
            WHERE user_id = ?
        ''', (user_id,))

        stats = cursor.fetchone()
        conn.close()

        return dict(stats) if stats else None
