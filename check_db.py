"""
데이터베이스 상태 확인 스크립트
"""
import sqlite3
import json

db_path = 'chat_history.db'

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# file_url이 NULL인 첨부 파일 조회
cursor.execute('''
    SELECT id, filename, file_type, file_info, file_url, timestamp
    FROM file_attachments
    WHERE file_url IS NULL
    ORDER BY timestamp ASC
    LIMIT 15
''')

attachments = cursor.fetchall()

print(f"📊 file_url이 NULL인 파일: {len(attachments)}개\n")
print("=" * 80)

for att in attachments:
    print(f"ID: {att['id']}")
    print(f"파일명: {att['filename']}")
    print(f"타입: {att['file_type']}")
    print(f"URL: {att['file_url']}")
    print(f"시간: {att['timestamp']}")

    if att['file_info']:
        try:
            info = json.loads(att['file_info'])
            print(f"정보: {info}")
        except:
            print(f"정보: (파싱 실패)")
    print("-" * 80)

conn.close()
