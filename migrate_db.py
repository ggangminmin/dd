"""
데이터베이스 마이그레이션 스크립트
file_attachments 테이블에 file_url 컬럼 추가
"""
import sqlite3

db_path = 'chat_history.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # file_url 컬럼 추가
    cursor.execute('ALTER TABLE file_attachments ADD COLUMN file_url TEXT')
    conn.commit()

    print("✅ 마이그레이션 완료: file_url 컬럼이 추가되었습니다.")

except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print("ℹ️  file_url 컬럼이 이미 존재합니다.")
    else:
        print(f"❌ 오류 발생: {e}")
except Exception as e:
    print(f"❌ 예상치 못한 오류: {e}")
finally:
    if conn:
        conn.close()
