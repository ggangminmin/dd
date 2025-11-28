"""
데이터베이스 관리 모듈 - SQLite/MongoDB를 사용한 대화 이력 저장
"""
import sqlite3
from datetime import datetime
from config import Config

# MongoDB 선택적 임포트
try:
    from pymongo import MongoClient
    from bson.objectid import ObjectId
    MONGODB_AVAILABLE = True
except ImportError:
    MongoClient = None
    ObjectId = None
    MONGODB_AVAILABLE = False

class Database:
    def __init__(self):
        self.use_mongodb = Config.USE_MONGODB and MONGODB_AVAILABLE

        if self.use_mongodb:
            # MongoDB 연결
            self.client = MongoClient(Config.MONGODB_URI)
            self.db = self.client.get_default_database()
            self.users = self.db.users
            self.chat_history = self.db.chat_history
            self.file_attachments = self.db.file_attachments
            self.user_preferences = self.db.user_preferences
            self.init_mongodb()
        else:
            # SQLite 연결
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
                email TEXT UNIQUE,
                password_hash TEXT,
                reset_token TEXT,
                reset_token_expiry TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
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

        # 파일 첨부 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS file_attachments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_id INTEGER,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                file_info TEXT,
                file_url TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (message_id) REFERENCES chat_history (id)
            )
        ''')

        # 사용자 설정 테이블 (개인화)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                theme TEXT DEFAULT 'light',
                language TEXT DEFAULT 'ko',
                bot_personality TEXT DEFAULT 'friendly',
                notifications_enabled BOOLEAN DEFAULT 1,
                font_size TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.commit()
        conn.close()

    def init_mongodb(self):
        """MongoDB 인덱스 초기화"""
        # 사용자 테이블 인덱스
        self.users.create_index('username', unique=True)
        self.users.create_index('email', unique=True, sparse=True)

        # 대화 이력 인덱스
        self.chat_history.create_index('user_id')
        self.chat_history.create_index('timestamp')

        # 파일 첨부 인덱스
        self.file_attachments.create_index('message_id')

    def get_or_create_user(self, username):
        """사용자 조회 또는 생성 (기존 호환성 유지)"""
        if self.use_mongodb:
            from datetime import datetime
            # MongoDB에서 사용자 조회 또는 생성
            user = self.users.find_one({'username': username})

            if user:
                return str(user['_id'])
            else:
                # 새 사용자 생성
                result = self.users.insert_one({
                    'username': username,
                    'created_at': datetime.now()
                })
                return str(result.inserted_id)
        else:
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

    def create_user(self, username, email, password_hash):
        """신규 사용자 생성 (회원가입)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash)
                VALUES (?, ?, ?)
            ''', (username, email, password_hash))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None  # 중복된 username 또는 email

    def get_user_by_username(self, username):
        """username으로 사용자 정보 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, email, password_hash, created_at, last_login
            FROM users WHERE username = ?
        ''', (username,))
        user = cursor.fetchone()
        conn.close()

        return dict(user) if user else None

    def get_user_by_email(self, email):
        """email로 사용자 정보 조회"""
        if self.use_mongodb:
            user = self.users.find_one({'email': email})
            if user:
                return {
                    'id': str(user['_id']),
                    'username': user.get('username'),
                    'email': user.get('email'),
                    'password_hash': user.get('password_hash'),
                    'created_at': user.get('created_at'),
                    'last_login': user.get('last_login')
                }
            return None
        else:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, username, email, password_hash, created_at, last_login
                FROM users WHERE email = ?
            ''', (email,))
            user = cursor.fetchone()
            conn.close()

            return dict(user) if user else None

    def update_last_login(self, user_id):
        """마지막 로그인 시간 업데이트"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            from datetime import datetime
            self.users.update_one(
                {'_id': ObjectId(user_id) if isinstance(user_id, str) else user_id},
                {'$set': {'last_login': datetime.now()}}
            )
        else:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE users SET last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_id,))
            conn.commit()
            conn.close()

    def save_message(self, user_id, message, is_user, sentiment=None):
        """메시지 저장"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            from datetime import datetime

            # user_id가 문자열이면 ObjectId로 변환
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)

            result = self.chat_history.insert_one({
                'user_id': user_id,
                'message': message,
                'is_user': is_user,
                'sentiment': sentiment,
                'timestamp': datetime.now()
            })
            return str(result.inserted_id)
        else:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO chat_history (user_id, message, is_user, sentiment)
                VALUES (?, ?, ?, ?)
            ''', (user_id, message, is_user, sentiment))

            message_id = cursor.lastrowid
            conn.commit()
            conn.close()

            return message_id

    def save_file_attachment(self, message_id, filename, file_type, file_size, file_info, file_url=None):
        """파일 첨부 정보 저장"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            from datetime import datetime

            # message_id가 문자열이면 ObjectId로 변환
            if isinstance(message_id, str):
                message_id = ObjectId(message_id)

            self.file_attachments.insert_one({
                'message_id': message_id,
                'filename': filename,
                'file_type': file_type,
                'file_size': file_size,
                'file_info': file_info,
                'file_url': file_url,
                'timestamp': datetime.now()
            })
        else:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO file_attachments (message_id, filename, file_type, file_size, file_info, file_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (message_id, filename, file_type, file_size, file_info, file_url))

            conn.commit()
            conn.close()

    def get_user_history(self, user_id, limit=None):
        """사용자의 대화 이력 조회 (첨부 파일 정보 포함)"""
        if limit is None:
            limit = Config.MAX_HISTORY_LENGTH

        if self.use_mongodb:
            from bson.objectid import ObjectId
            import json

            # user_id가 문자열이면 ObjectId로 변환
            if isinstance(user_id, str):
                user_id_obj = ObjectId(user_id)
            else:
                user_id_obj = user_id

            # MongoDB에서 대화 이력 조회
            messages = list(self.chat_history.find(
                {'user_id': user_id_obj}
            ).sort('timestamp', -1).limit(limit))

            result = []
            for msg in messages:
                message_dict = {
                    'id': str(msg['_id']),
                    'message': msg.get('message'),
                    'is_user': msg.get('is_user'),
                    'sentiment': msg.get('sentiment'),
                    'timestamp': msg.get('timestamp').isoformat() if msg.get('timestamp') else None
                }

                # 첨부 파일 조회
                attachments = list(self.file_attachments.find({'message_id': msg['_id']}))
                if attachments:
                    message_dict['attachments'] = []
                    for att in attachments:
                        att_dict = {
                            'filename': att.get('filename'),
                            'file_type': att.get('file_type'),
                            'file_size': att.get('file_size'),
                            'file_info': att.get('file_info'),
                            'file_url': att.get('file_url')
                        }
                        # file_info JSON 파싱
                        if att_dict.get('file_info'):
                            try:
                                if isinstance(att_dict['file_info'], str):
                                    file_info = json.loads(att_dict['file_info'])
                                else:
                                    file_info = att_dict['file_info']
                                att_dict['parsed_info'] = file_info
                            except:
                                pass
                        message_dict['attachments'].append(att_dict)

                result.append(message_dict)

            # 최신 순서를 오래된 순서로 변경
            return list(reversed(result))
        else:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, message, is_user, sentiment, timestamp
                FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (user_id, limit))

            history = cursor.fetchall()

            # 각 메시지에 첨부 파일 정보 추가
            result = []
            for row in history:
                message_dict = dict(row)
                message_id = message_dict['id']

                # 첨부 파일 조회
                cursor.execute('''
                    SELECT filename, file_type, file_size, file_info, file_url
                    FROM file_attachments
                    WHERE message_id = ?
                ''', (message_id,))

                attachments = cursor.fetchall()
                if attachments:
                    import json
                    message_dict['attachments'] = []
                    for att in attachments:
                        att_dict = dict(att)
                        # file_info JSON 파싱
                        if att_dict.get('file_info'):
                            try:
                                file_info = json.loads(att_dict['file_info'])
                                att_dict['parsed_info'] = file_info
                            except:
                                pass
                        message_dict['attachments'].append(att_dict)

                result.append(message_dict)

            conn.close()

            # 최신 순서를 오래된 순서로 변경
            return list(reversed(result))

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

    def save_reset_token(self, email, token, expiry):
        """비밀번호 재설정 토큰 저장"""
        if self.use_mongodb:
            result = self.users.update_one(
                {'email': email},
                {'$set': {
                    'reset_token': token,
                    'reset_token_expiry': expiry
                }}
            )
            return result.modified_count > 0
        else:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE users
                SET reset_token = ?, reset_token_expiry = ?
                WHERE email = ?
            ''', (token, expiry, email))

            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0

    def verify_reset_token(self, token):
        """토큰 검증 및 사용자 정보 반환"""
        if self.use_mongodb:
            user = self.users.find_one({'reset_token': token})

            if not user:
                return None

            # 토큰 만료 확인
            expiry = user.get('reset_token_expiry')
            if datetime.now() > expiry:
                return None

            return {
                'id': str(user['_id']),
                'username': user.get('username'),
                'email': user.get('email'),
                'reset_token_expiry': expiry
            }
        else:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, username, email, reset_token_expiry
                FROM users
                WHERE reset_token = ?
            ''', (token,))

            user = cursor.fetchone()
            conn.close()

            if not user:
                return None

            user_dict = dict(user)

            # 토큰 만료 확인
            from datetime import datetime
            expiry = datetime.fromisoformat(user_dict['reset_token_expiry'])
            if datetime.now() > expiry:
                return None

            return user_dict

    def update_password(self, user_id, new_password_hash):
        """비밀번호 업데이트 및 토큰 삭제"""
        if self.use_mongodb:
            from bson.objectid import ObjectId
            result = self.users.update_one(
                {'_id': ObjectId(user_id) if isinstance(user_id, str) else user_id},
                {'$set': {
                    'password_hash': new_password_hash
                },
                '$unset': {
                    'reset_token': '',
                    'reset_token_expiry': ''
                }}
            )
            return result.modified_count > 0
        else:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE users
                SET password_hash = ?, reset_token = NULL, reset_token_expiry = NULL
                WHERE id = ?
            ''', (new_password_hash, user_id))

            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0

    def delete_all_messages(self, user_id):
        """사용자의 모든 대화 기록 삭제"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 먼저 첨부 파일 정보 삭제
        cursor.execute('''
            DELETE FROM file_attachments
            WHERE message_id IN (
                SELECT id FROM chat_history WHERE user_id = ?
            )
        ''', (user_id,))

        # 대화 기록 삭제
        cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))

        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected

    def delete_user(self, user_id):
        """사용자 계정 삭제"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 사용자 preferences 삭제
        cursor.execute('DELETE FROM user_preferences WHERE user_id = ?', (user_id,))

        # 사용자 계정 삭제
        cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))

        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected

    def delete_message(self, message_id, user_id):
        """특정 메시지 삭제 (사용자 확인 포함)"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # 먼저 해당 메시지가 해당 사용자의 것인지 확인
        cursor.execute('SELECT user_id FROM chat_history WHERE id = ?', (message_id,))
        result = cursor.fetchone()

        if not result or result['user_id'] != user_id:
            conn.close()
            return False

        # 첨부 파일 정보 삭제
        cursor.execute('DELETE FROM file_attachments WHERE message_id = ?', (message_id,))

        # 메시지 삭제
        cursor.execute('DELETE FROM chat_history WHERE id = ?', (message_id,))

        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    # ==================== 사용자 설정 관리 ====================
    
    def get_user_preferences(self, user_id):
        """사용자 설정 조회"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
        prefs = cursor.fetchone()
        
        if not prefs:
            # 기본 설정 생성
            cursor.execute('''
                INSERT INTO user_preferences (user_id)
                VALUES (?)
            ''', (user_id,))
            conn.commit()
            
            cursor.execute('SELECT * FROM user_preferences WHERE user_id = ?', (user_id,))
            prefs = cursor.fetchone()
        
        conn.close()
        return dict(prefs) if prefs else None
    
    def update_user_preferences(self, user_id, preferences):
        """사용자 설정 업데이트"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 설정 필드 목록
        valid_fields = ['theme', 'language', 'bot_personality', 'notifications_enabled', 'font_size']
        
        # 업데이트할 필드와 값 준비
        update_fields = []
        update_values = []
        
        for field in valid_fields:
            if field in preferences:
                update_fields.append(f"{field} = ?")
                update_values.append(preferences[field])
        
        if update_fields:
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            update_values.append(user_id)
            
            query = f"UPDATE user_preferences SET {', '.join(update_fields)} WHERE user_id = ?"
            cursor.execute(query, update_values)
            conn.commit()
        
        conn.close()
        return True
    
    # ==================== 대화 기록 검색/필터링 ====================
    
    def search_messages(self, user_id, keyword=None, start_date=None, end_date=None, 
                       sentiment=None, limit=50, offset=0):
        """대화 기록 검색 및 필터링"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, message, is_user, sentiment, timestamp
            FROM chat_history
            WHERE user_id = ?
        '''
        params = [user_id]
        
        # 키워드 검색
        if keyword:
            query += ' AND message LIKE ?'
            params.append(f'%{keyword}%')
        
        # 날짜 범위 필터
        if start_date:
            query += ' AND timestamp >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND timestamp <= ?'
            params.append(end_date)
        
        # 감정 필터
        if sentiment:
            query += ' AND sentiment = ?'
            params.append(sentiment)
        
        # 정렬 및 페이지네이션
        query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        messages = cursor.fetchall()
        
        # 전체 개수 조회
        count_query = '''
            SELECT COUNT(*) as total
            FROM chat_history
            WHERE user_id = ?
        '''
        count_params = [user_id]
        
        if keyword:
            count_query += ' AND message LIKE ?'
            count_params.append(f'%{keyword}%')
        
        if start_date:
            count_query += ' AND timestamp >= ?'
            count_params.append(start_date)
        
        if end_date:
            count_query += ' AND timestamp <= ?'
            count_params.append(end_date)
        
        if sentiment:
            count_query += ' AND sentiment = ?'
            count_params.append(sentiment)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()['total']
        
        conn.close()
        
        return {
            'messages': [dict(msg) for msg in messages],
            'total': total,
            'limit': limit,
            'offset': offset
        }
    
    def get_messages_by_date_range(self, user_id, start_date, end_date):
        """특정 기간의 메시지 조회"""
        return self.search_messages(user_id, start_date=start_date, end_date=end_date, limit=1000)
    
    def get_messages_by_sentiment(self, user_id, sentiment, limit=50):
        """감정별 메시지 조회"""
        return self.search_messages(user_id, sentiment=sentiment, limit=limit)
