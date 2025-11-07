"""
파일 처리 모듈
다양한 파일 형식을 처리하고 텍스트로 추출
"""
import os
import io
import json
import base64
from PIL import Image
from PyPDF2 import PdfReader
from docx import Document
import openpyxl
import pandas as pd


class FileProcessor:
    """파일 처리 클래스"""

    # 지원하는 파일 확장자
    SUPPORTED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
        'document': ['.pdf', '.docx', '.txt'],
        'spreadsheet': ['.xlsx', '.csv'],
        'data': ['.json', '.xml']
    }

    # 최대 파일 크기 (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    @staticmethod
    def is_supported(filename):
        """파일이 지원되는 형식인지 확인"""
        ext = os.path.splitext(filename)[1].lower()
        for extensions in FileProcessor.SUPPORTED_EXTENSIONS.values():
            if ext in extensions:
                return True
        return False

    @staticmethod
    def get_file_type(filename):
        """파일 타입 반환"""
        ext = os.path.splitext(filename)[1].lower()
        for file_type, extensions in FileProcessor.SUPPORTED_EXTENSIONS.items():
            if ext in extensions:
                return file_type
        return 'unknown'

    @staticmethod
    def process_image(file_data, filename):
        """이미지 파일 처리"""
        try:
            image = Image.open(io.BytesIO(file_data))

            # 이미지 정보
            info = {
                'type': 'image',
                'filename': filename,
                'size': f"{image.size[0]}x{image.size[1]}",
                'format': image.format,
                'mode': image.mode
            }

            # base64 인코딩 (GPT-4 Vision용)
            base64_image = base64.b64encode(file_data).decode('utf-8')
            info['base64'] = base64_image

            return {
                'success': True,
                'info': info,
                'text': f"[이미지: {filename}, 크기: {info['size']}, 형식: {image.format}]",
                'has_image': True
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"이미지 처리 오류: {str(e)}"
            }

    @staticmethod
    def process_pdf(file_data, filename):
        """PDF 파일 처리"""
        try:
            pdf_file = io.BytesIO(file_data)
            reader = PdfReader(pdf_file)

            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"

            return {
                'success': True,
                'info': {
                    'type': 'pdf',
                    'filename': filename,
                    'pages': len(reader.pages)
                },
                'text': text.strip() if text.strip() else "[PDF에서 텍스트를 추출할 수 없습니다]",
                'has_image': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"PDF 처리 오류: {str(e)}"
            }

    @staticmethod
    def process_docx(file_data, filename):
        """DOCX 파일 처리"""
        try:
            docx_file = io.BytesIO(file_data)
            doc = Document(docx_file)

            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])

            return {
                'success': True,
                'info': {
                    'type': 'docx',
                    'filename': filename,
                    'paragraphs': len(doc.paragraphs)
                },
                'text': text.strip() if text.strip() else "[DOCX에서 텍스트를 추출할 수 없습니다]",
                'has_image': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"DOCX 처리 오류: {str(e)}"
            }

    @staticmethod
    def process_txt(file_data, filename):
        """TXT 파일 처리"""
        try:
            text = file_data.decode('utf-8')

            return {
                'success': True,
                'info': {
                    'type': 'txt',
                    'filename': filename,
                    'lines': len(text.split('\n'))
                },
                'text': text,
                'has_image': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"TXT 처리 오류: {str(e)}"
            }

    @staticmethod
    def process_xlsx(file_data, filename):
        """XLSX 파일 처리"""
        try:
            print(f"[FileProcessor] XLSX 처리 시작: {filename}, 크기: {len(file_data)} bytes")
            xlsx_file = io.BytesIO(file_data)

            # pandas로 Excel 읽기 (openpyxl 엔진 명시)
            df = pd.read_excel(xlsx_file, engine='openpyxl')
            print(f"[FileProcessor] Excel 읽기 성공: {len(df)} 행, {len(df.columns)} 열")

            # 데이터프레임을 텍스트로 변환
            text = df.to_string()
            summary = f"행: {len(df)}, 열: {len(df.columns)}\n열 이름: {', '.join(df.columns.tolist())}\n\n"

            # 표 데이터 추출 (최대 20행)
            preview_df = df.head(20)

            # NaN 값을 None으로 변환 (JSON 직렬화를 위해)
            table_data = {
                'headers': preview_df.columns.tolist(),
                'rows': preview_df.fillna('').values.tolist(),  # NaN을 빈 문자열로 변환
                'total_rows': len(df),
                'total_columns': len(df.columns)
            }

            print(f"[FileProcessor] XLSX 처리 완료: {filename}")
            return {
                'success': True,
                'info': {
                    'type': 'xlsx',
                    'filename': filename,
                    'rows': len(df),
                    'columns': len(df.columns)
                },
                'text': summary + text,
                'has_image': False,
                'table_data': table_data
            }
        except Exception as e:
            print(f"[FileProcessor] XLSX 처리 오류: {filename} - {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f"XLSX 처리 오류: {str(e)}"
            }

    @staticmethod
    def process_csv(file_data, filename):
        """CSV 파일 처리"""
        try:
            csv_file = io.BytesIO(file_data)
            df = pd.read_csv(csv_file)

            text = df.to_string()
            summary = f"행: {len(df)}, 열: {len(df.columns)}\n열 이름: {', '.join(df.columns.tolist())}\n\n"

            # 표 데이터 추출 (최대 20행)
            preview_df = df.head(20)
            table_data = {
                'headers': preview_df.columns.tolist(),
                'rows': preview_df.values.tolist(),
                'total_rows': len(df),
                'total_columns': len(df.columns)
            }

            return {
                'success': True,
                'info': {
                    'type': 'csv',
                    'filename': filename,
                    'rows': len(df),
                    'columns': len(df.columns)
                },
                'text': summary + text,
                'has_image': False,
                'table_data': table_data
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"CSV 처리 오류: {str(e)}"
            }

    @staticmethod
    def process_json(file_data, filename):
        """JSON 파일 처리"""
        try:
            text = file_data.decode('utf-8')
            data = json.loads(text)

            # JSON을 보기 좋게 포맷팅
            formatted = json.dumps(data, indent=2, ensure_ascii=False)

            return {
                'success': True,
                'info': {
                    'type': 'json',
                    'filename': filename
                },
                'text': formatted,
                'has_image': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"JSON 처리 오류: {str(e)}"
            }

    @staticmethod
    def process_xml(file_data, filename):
        """XML 파일 처리"""
        try:
            text = file_data.decode('utf-8')

            return {
                'success': True,
                'info': {
                    'type': 'xml',
                    'filename': filename
                },
                'text': text,
                'has_image': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"XML 처리 오류: {str(e)}"
            }

    @staticmethod
    def process_file(file_data, filename):
        """파일 타입에 따라 적절한 처리 함수 호출"""
        ext = os.path.splitext(filename)[1].lower()

        # 파일 크기 체크
        if len(file_data) > FileProcessor.MAX_FILE_SIZE:
            return {
                'success': False,
                'error': '파일 크기가 너무 큽니다 (최대 10MB)'
            }

        # 확장자별 처리
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            return FileProcessor.process_image(file_data, filename)
        elif ext == '.pdf':
            return FileProcessor.process_pdf(file_data, filename)
        elif ext == '.docx':
            return FileProcessor.process_docx(file_data, filename)
        elif ext == '.txt':
            return FileProcessor.process_txt(file_data, filename)
        elif ext == '.xlsx':
            return FileProcessor.process_xlsx(file_data, filename)
        elif ext == '.csv':
            return FileProcessor.process_csv(file_data, filename)
        elif ext == '.json':
            return FileProcessor.process_json(file_data, filename)
        elif ext == '.xml':
            return FileProcessor.process_xml(file_data, filename)
        else:
            return {
                'success': False,
                'error': f'지원하지 않는 파일 형식입니다: {ext}'
            }
