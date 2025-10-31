"""
기존 첨부 파일의 URL 복구 스크립트
file_info JSON에서 파일명을 추출하고 업로드 폴더의 파일과 매칭하여 URL 업데이트
"""
import sqlite3
import json
import os
from datetime import datetime

db_path = 'chat_history.db'
upload_folder = 'static/uploads'

def restore_file_urls():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 업로드 폴더의 모든 파일 리스트 (확장자별로 그룹화, 시간 정보 포함)
    uploaded_files = {}
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            if os.path.isfile(file_path):
                ext = filename.split('.')[-1].lower() if '.' in filename else 'unknown'
                if ext not in uploaded_files:
                    uploaded_files[ext] = []
                file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                uploaded_files[ext].append({
                    'filename': filename,
                    'mtime': file_mtime
                })

    # file_url이 NULL인 첨부 파일 조회
    cursor.execute('''
        SELECT id, filename, file_type, file_info, timestamp
        FROM file_attachments
        WHERE file_url IS NULL
        ORDER BY timestamp ASC
    ''')

    attachments = cursor.fetchall()
    updated_count = 0

    print(f"📁 복구할 파일: {len(attachments)}개")
    print("-" * 60)

    for att in attachments:
        att_id = att['id']
        original_filename = att['filename']
        file_type = att['file_type']
        file_info_json = att['file_info']
        timestamp = att['timestamp']

        # file_info에서 실제 확장자 추출
        ext = None
        if file_info_json:
            try:
                file_info = json.loads(file_info_json)
                ext = file_info.get('type', '').lower()
            except:
                pass

        # ext가 없으면 원본 파일명에서 추출
        if not ext or ext == 'image':
            if '.' in original_filename:
                ext = original_filename.split('.')[-1].lower()
            else:
                ext = file_type.lower() if file_type else 'unknown'

        # 해당 확장자의 업로드된 파일 중에서 타임스탬프가 가장 가까운 파일 찾기
        if ext in uploaded_files:
            # 타임스탬프 파싱
            try:
                att_time = datetime.fromisoformat(timestamp.replace(' ', 'T'))
            except:
                att_time = None

            best_match = None
            min_time_diff = float('inf')

            for file_info in uploaded_files[ext]:
                uploaded_filename = file_info['filename']
                file_mtime = file_info['mtime']

                if att_time:
                    time_diff = abs((file_mtime - att_time).total_seconds())
                    if time_diff < min_time_diff:
                        min_time_diff = time_diff
                        best_match = uploaded_filename
                else:
                    # 타임스탬프가 없으면 첫 번째 파일 사용
                    best_match = uploaded_filename
                    break

            if best_match:
                file_url = f"/static/uploads/{best_match}"

                # URL 업데이트
                cursor.execute('''
                    UPDATE file_attachments
                    SET file_url = ?
                    WHERE id = ?
                ''', (file_url, att_id))

                updated_count += 1
                print(f"✅ [{att_id}] {original_filename} -> {best_match}")

    conn.commit()
    conn.close()

    print("-" * 60)
    print(f"✅ 총 {updated_count}개 파일의 URL이 복구되었습니다.")

if __name__ == '__main__':
    restore_file_urls()
