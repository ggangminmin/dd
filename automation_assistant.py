"""
업무 자동화 비서 모듈
자연어 명령을 해석하고 파일 분석, 데이터 처리, 보고서 생성 등을 수행
"""
import re
import json
from typing import Dict, List, Any, Optional, Tuple


class AutomationAssistant:
    """지능형 업무 자동화 비서"""

    # 명령 패턴 정의
    COMMAND_PATTERNS = {
        # 요약 관련
        'summarize': [
            r'요약',
            r'정리',
            r'간단하게',
            r'핵심만',
            r'summary',
            r'summarize'
        ],
        # 분석 관련
        'analyze': [
            r'분석',
            r'파악',
            r'알려줘',
            r'확인',
            r'analyze',
            r'analysis'
        ],
        # 필터링 관련
        'filter': [
            r'필터',
            r'추출',
            r'뽑아',
            r'찾아',
            r'filter',
            r'extract'
        ],
        # 정렬 관련
        'sort': [
            r'정렬',
            r'순서',
            r'sort',
            r'order'
        ],
        # 비교 관련
        'compare': [
            r'비교',
            r'차이',
            r'다른점',
            r'compare',
            r'difference'
        ],
        # 생성 관련
        'generate': [
            r'생성',
            r'만들',
            r'작성',
            r'create',
            r'generate',
            r'make'
        ],
        # 계산 관련
        'calculate': [
            r'계산',
            r'합계',
            r'평균',
            r'통계',
            r'calculate',
            r'sum',
            r'average'
        ],
        # 보고서 관련
        'report': [
            r'보고서',
            r'리포트',
            r'report'
        ],
        # 차트/그래프 관련
        'chart': [
            r'차트',
            r'그래프',
            r'시각화',
            r'chart',
            r'graph',
            r'visualize'
        ]
    }

    # 차트 타입 패턴
    CHART_TYPE_PATTERNS = {
        'bar': [r'막대', r'막대그래프', r'막대차트', r'bar', r'바차트'],
        'line': [r'선\s*차트', r'선\s*그래프', r'꺾은선', r'line', r'라인'],
        'pie': [r'원\s*차트', r'원\s*그래프', r'파이', r'pie', r'도넛']
    }

    # 출력 형식 패턴
    OUTPUT_FORMATS = {
        'table': [r'표', r'테이블', r'table'],
        'list': [r'리스트', r'목록', r'list'],
        'pdf': [r'pdf', r'피디에프'],
        'docx': [r'워드', r'docx', r'문서'],
        'excel': [r'엑셀', r'xlsx', r'excel'],
        'chart': [r'차트', r'그래프', r'chart', r'graph']
    }

    # 조건 패턴 (필터링용)
    CONDITION_PATTERNS = {
        'greater': [r'이상', r'넘', r'초과', r'높은', r'큰', r'>', r'greater', r'more than'],
        'less': [r'이하', r'미만', r'낮은', r'작은', r'<', r'less', r'lower'],
        'equal': [r'같은', r'동일', r'=', r'equal', r'same'],
        'contains': [r'포함', r'있는', r'contains', r'include'],
        'top': [r'상위', r'top', r'최고'],
        'bottom': [r'하위', r'bottom', r'최저']
    }

    @staticmethod
    def detect_intent(message: str) -> Dict[str, Any]:
        """
        사용자 메시지에서 의도 파악
        Returns: {
            'action': str,  # 수행할 작업
            'target': str,  # 대상 (파일, 데이터 등)
            'conditions': List[str],  # 조건들
            'output_format': str,  # 출력 형식
            'confidence': float  # 신뢰도
        }
        """
        message_lower = message.lower()
        result = {
            'action': None,
            'target': None,
            'conditions': [],
            'output_format': None,
            'confidence': 0.0
        }

        # 1. 액션 감지
        for action, patterns in AutomationAssistant.COMMAND_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    result['action'] = action
                    result['confidence'] += 0.3
                    break
            if result['action']:
                break

        # 2. 출력 형식 감지
        for fmt, patterns in AutomationAssistant.OUTPUT_FORMATS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    result['output_format'] = fmt
                    result['confidence'] += 0.2
                    break

        # 3. 조건 감지
        for condition, patterns in AutomationAssistant.CONDITION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    result['conditions'].append(condition)
                    result['confidence'] += 0.1

        # 4. 대상 감지 (파일명, 데이터 타입 등)
        # 엑셀, CSV 등의 키워드
        if re.search(r'엑셀|xlsx|csv|스프레드시트', message_lower):
            result['target'] = 'spreadsheet'
            result['confidence'] += 0.2
        elif re.search(r'문서|pdf|docx|워드', message_lower):
            result['target'] = 'document'
            result['confidence'] += 0.2
        elif re.search(r'이미지|사진|그림', message_lower):
            result['target'] = 'image'
            result['confidence'] += 0.2

        return result

    @staticmethod
    def analyze_excel_data(data: Dict[str, Any], message: str) -> Dict[str, Any]:
        """
        엑셀 데이터 분석
        Args:
            data: 엑셀 파일에서 추출한 데이터 (table_data)
            message: 사용자 메시지
        Returns:
            분석 결과
        """
        if not data or 'table_data' not in data:
            return {
                'success': False,
                'error': '엑셀 데이터가 없습니다.'
            }

        table_data = data['table_data']
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])

        analysis = {
            'success': True,
            'basic_info': {
                'total_rows': table_data.get('total_rows', len(rows)),
                'total_columns': table_data.get('total_columns', len(headers)),
                'columns': headers
            },
            'statistics': {},
            'insights': []
        }

        # 숫자 컬럼에 대한 통계 계산
        for col_idx, col_name in enumerate(headers):
            numeric_values = []
            for row in rows:
                try:
                    if col_idx < len(row):
                        val = row[col_idx]
                        if isinstance(val, (int, float)):
                            numeric_values.append(val)
                        elif isinstance(val, str) and val.replace('.', '').replace('-', '').isdigit():
                            numeric_values.append(float(val))
                except:
                    continue

            if numeric_values:
                analysis['statistics'][col_name] = {
                    'count': len(numeric_values),
                    'sum': sum(numeric_values),
                    'average': sum(numeric_values) / len(numeric_values),
                    'min': min(numeric_values),
                    'max': max(numeric_values)
                }

        # 인사이트 생성
        intent = AutomationAssistant.detect_intent(message)

        if intent['action'] == 'summarize':
            analysis['insights'].append(f"총 {analysis['basic_info']['total_rows']}개의 데이터가 있습니다.")
            analysis['insights'].append(f"{analysis['basic_info']['total_columns']}개의 컬럼: {', '.join(headers)}")

            for col_name, stats in analysis['statistics'].items():
                analysis['insights'].append(
                    f"{col_name}: 평균 {stats['average']:.2f}, 최소 {stats['min']}, 최대 {stats['max']}"
                )

        return analysis

    @staticmethod
    def filter_data(data: Dict[str, Any], condition: str) -> Dict[str, Any]:
        """
        데이터 필터링
        Args:
            data: 테이블 데이터
            condition: 필터링 조건 (예: "이익률 > 10")
        Returns:
            필터링된 데이터
        """
        # TODO: 실제 필터링 로직 구현
        return {
            'success': True,
            'message': '필터링 기능이 구현 중입니다.'
        }

    @staticmethod
    def sort_data(data: Dict[str, Any], column: str, ascending: bool = True) -> Dict[str, Any]:
        """
        데이터 정렬
        Args:
            data: 테이블 데이터
            column: 정렬 기준 컬럼
            ascending: 오름차순 여부
        Returns:
            정렬된 데이터
        """
        # TODO: 실제 정렬 로직 구현
        return {
            'success': True,
            'message': '정렬 기능이 구현 중입니다.'
        }

    @staticmethod
    def generate_report_content(data: Dict[str, Any], report_type: str = 'summary') -> str:
        """
        보고서 내용 생성
        Args:
            data: 분석 데이터
            report_type: 보고서 타입 (summary, executive, detailed)
        Returns:
            보고서 텍스트
        """
        if report_type == 'summary':
            content = "# 데이터 분석 요약 보고서\n\n"

            if 'basic_info' in data:
                content += "## 기본 정보\n"
                content += f"- 총 행 수: {data['basic_info'].get('total_rows', 0)}\n"
                content += f"- 총 열 수: {data['basic_info'].get('total_columns', 0)}\n"
                content += f"- 컬럼: {', '.join(data['basic_info'].get('columns', []))}\n\n"

            if 'statistics' in data and data['statistics']:
                content += "## 주요 통계\n"
                for col_name, stats in data['statistics'].items():
                    content += f"\n### {col_name}\n"
                    content += f"- 평균: {stats.get('average', 0):.2f}\n"
                    content += f"- 최소값: {stats.get('min', 0)}\n"
                    content += f"- 최대값: {stats.get('max', 0)}\n"
                    content += f"- 합계: {stats.get('sum', 0):.2f}\n"

            if 'insights' in data and data['insights']:
                content += "\n## 인사이트\n"
                for insight in data['insights']:
                    content += f"- {insight}\n"

            return content

        return "보고서 생성 중..."

    @staticmethod
    def should_trigger_automation(message: str) -> bool:
        """
        자동화 기능이 트리거되어야 하는지 판단
        """
        intent = AutomationAssistant.detect_intent(message)

        # confidence가 0.3 이상이면 자동화 기능 트리거
        return intent['confidence'] >= 0.3

    @staticmethod
    def create_clarifying_question(message: str, context: Dict[str, Any]) -> Optional[str]:
        """
        모호한 요청에 대한 명확화 질문 생성
        """
        intent = AutomationAssistant.detect_intent(message)

        # 액션은 감지되었지만 대상이 불명확한 경우
        if intent['action'] and not intent['target'] and intent['confidence'] < 0.5:
            if intent['action'] == 'summarize':
                return "어떤 파일이나 데이터를 요약해 드릴까요? 파일을 업로드하거나 구체적으로 말씀해주세요."
            elif intent['action'] == 'analyze':
                return "어떤 데이터를 분석해 드릴까요? 엑셀 파일이나 CSV 파일을 업로드해주세요."
            elif intent['action'] == 'generate':
                return "어떤 형식의 문서를 생성하시겠습니까? (예: PDF 보고서, 엑셀 표, 워드 문서)"

        # 조건이 불명확한 경우
        if intent['action'] == 'filter' and not intent['conditions']:
            return "어떤 조건으로 필터링하시겠습니까? (예: 값이 10 이상, 특정 단어 포함 등)"

        return None

    @staticmethod
    def detect_chart_type(message: str) -> Optional[str]:
        """
        차트 타입 감지 (막대, 선, 원 그래프)
        Returns: 'bar', 'line', 'pie', None
        """
        message_lower = message.lower()

        for chart_type, patterns in AutomationAssistant.CHART_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return chart_type

        # 기본값: 막대 그래프
        if any(p in message_lower for p in ['차트', '그래프', 'chart', 'graph']):
            return 'bar'

        return None

    @staticmethod
    def detect_chart_types(message: str) -> List[str]:
        """
        여러 차트 타입 감지 (복수 차트 생성용)
        Returns: ['bar', 'line', 'pie'] 리스트
        """
        message_lower = message.lower()
        detected_types = []

        for chart_type, patterns in AutomationAssistant.CHART_TYPE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    if chart_type not in detected_types:
                        detected_types.append(chart_type)
                    break

        # 아무것도 감지되지 않았으면 빈 리스트 반환 (파일 업로드 시 기본값 사용)
        # "차트", "그래프" 같은 일반적인 단어만으로는 차트 타입을 결정하지 않음
        return detected_types

    @staticmethod
    def extract_column_names(message: str, available_columns: List[str]) -> Tuple[Optional[str], List[str]]:
        """
        메시지에서 X축(라벨)과 Y축(데이터) 칼럼명 추출

        예시:
        - "Category별 SalesAmount 선 차트" → ('Category', ['SalesAmount'])
        - "월별 매출과 이익 막대 그래프" → ('월', ['매출', '이익'])

        Args:
            message: 사용자 메시지
            available_columns: 사용 가능한 칼럼명 리스트

        Returns:
            (x_column, y_columns) 튜플
            - x_column: X축 칼럼명 (라벨)
            - y_columns: Y축 칼럼명 리스트 (데이터)
        """
        if not available_columns:
            return (None, [])

        message_lower = message.lower()

        # 칼럼명을 소문자로 매핑 (대소문자 무시 검색용)
        column_map = {col.lower(): col for col in available_columns}

        x_column = None
        y_columns = []

        # "A별 B" 패턴 감지 (예: "Category별 SalesAmount")
        pattern_x_y = r'(\w+)별\s+(\w+(?:\s*,\s*\w+)*)'
        match = re.search(pattern_x_y, message)
        if match:
            x_candidate = match.group(1).lower()
            y_candidates = [y.strip().lower() for y in match.group(2).split(',')]

            # X축 칼럼 찾기
            if x_candidate in column_map:
                x_column = column_map[x_candidate]

            # Y축 칼럼들 찾기
            for y_cand in y_candidates:
                if y_cand in column_map:
                    y_columns.append(column_map[y_cand])

        # "A와 B를 C로" 패턴 감지 (예: "매출과 이익을 월별로")
        if not x_column or not y_columns:
            pattern_y_x = r'(\w+(?:\s*(?:와|과|,)\s*\w+)*)\s*(?:를|을)\s*(\w+)(?:별|로)'
            match = re.search(pattern_y_x, message)
            if match:
                y_candidates = re.split(r'\s*(?:와|과|,)\s*', match.group(1))
                x_candidate = match.group(2).lower()

                # X축 칼럼 찾기
                if x_candidate in column_map:
                    x_column = column_map[x_candidate]

                # Y축 칼럼들 찾기
                for y_cand in y_candidates:
                    y_cand_lower = y_cand.strip().lower()
                    if y_cand_lower in column_map:
                        y_columns.append(column_map[y_cand_lower])

        # 칼럼명이 직접 언급된 경우 (부분 매칭)
        if not y_columns:
            for col_lower, col_original in column_map.items():
                if col_lower in message_lower and col_original not in y_columns:
                    y_columns.append(col_original)

        return (x_column, y_columns)

    @staticmethod
    def aggregate_large_data(rows: List[List], headers: List[str], x_col_idx: int, y_col_indices: List[int], threshold: int = 100) -> Tuple[List[List], str]:
        """
        대용량 데이터를 스마트하게 집계
        Args:
            rows: 원본 데이터 행
            headers: 컬럼 헤더
            x_col_idx: X축 칼럼 인덱스
            y_col_indices: Y축 칼럼 인덱스들
            threshold: 집계 시작 임계값 (기본 100개)
        Returns:
            (집계된 행, 집계 방법 설명)
        """
        from datetime import datetime
        import re

        if len(rows) <= threshold:
            return rows, "원본 데이터"

        print(f"[집계] {len(rows)}개 행 → 자동 집계 시작")

        # X축 데이터 타입 분석
        x_values = [row[x_col_idx] for row in rows if len(row) > x_col_idx]

        # 1. 날짜/시간 데이터 감지
        date_pattern = r'\d{4}[-/.]\d{1,2}[-/.]\d{1,2}'
        is_date = any(isinstance(v, str) and re.search(date_pattern, v) for v in x_values[:10])

        if is_date:
            # 날짜별 → 월별 집계
            print(f"[집계] 날짜 데이터 감지 → 월별 집계")
            aggregated = {}

            for row in rows:
                if len(row) <= x_col_idx:
                    continue

                date_str = str(row[x_col_idx])
                # 날짜에서 연-월 추출
                match = re.search(r'(\d{4})[-/.](\d{1,2})', date_str)
                if match:
                    month_key = f"{match.group(1)}-{match.group(2).zfill(2)}"

                    if month_key not in aggregated:
                        aggregated[month_key] = {idx: [] for idx in y_col_indices}

                    # 숫자 데이터 수집
                    for idx in y_col_indices:
                        if len(row) > idx:
                            try:
                                val = float(row[idx]) if isinstance(row[idx], (int, float, str)) else 0
                                aggregated[month_key][idx].append(val)
                            except:
                                pass

            # 월별 평균 계산
            result_rows = []
            for month_key in sorted(aggregated.keys()):
                new_row = [None] * len(headers)
                new_row[x_col_idx] = month_key

                for idx in y_col_indices:
                    values = aggregated[month_key][idx]
                    new_row[idx] = sum(values) / len(values) if values else 0

                result_rows.append(new_row)

            return result_rows, f"월별 평균 ({len(rows)}개 → {len(result_rows)}개)"

        # 2. 카테고리 데이터 감지 (중복이 많은 경우)
        unique_x = list(set(x_values))
        if len(unique_x) < len(rows) * 0.5:  # 50% 이상 중복
            print(f"[집계] 카테고리 데이터 감지 → 카테고리별 합계")
            aggregated = {}

            for row in rows:
                if len(row) <= x_col_idx:
                    continue

                category = str(row[x_col_idx])

                if category not in aggregated:
                    aggregated[category] = {idx: [] for idx in y_col_indices}

                for idx in y_col_indices:
                    if len(row) > idx:
                        try:
                            val = float(row[idx]) if isinstance(row[idx], (int, float, str)) else 0
                            aggregated[category][idx].append(val)
                        except:
                            pass

            # 카테고리별 합계 계산
            result_rows = []
            for category in sorted(aggregated.keys()):
                new_row = [None] * len(headers)
                new_row[x_col_idx] = category

                for idx in y_col_indices:
                    values = aggregated[category][idx]
                    new_row[idx] = sum(values)  # 합계

                result_rows.append(new_row)

            return result_rows, f"카테고리별 합계 ({len(rows)}개 → {len(result_rows)}개)"

        # 3. 기타: 균등 샘플링 (100개로 축소)
        print(f"[집계] 일반 데이터 → 균등 샘플링")
        sample_size = 100
        step = len(rows) // sample_size
        sampled_rows = [rows[i] for i in range(0, len(rows), step)][:sample_size]

        return sampled_rows, f"균등 샘플링 ({len(rows)}개 → {len(sampled_rows)}개)"

    @staticmethod
    def detect_column_types(headers: List[str], rows: List[List]) -> Tuple[List[str], List[str]]:
        """
        컬럼 타입을 자동으로 감지 (범주형 vs 수치형)
        Args:
            headers: 컬럼 헤더 리스트
            rows: 데이터 행 리스트
        Returns:
            (categorical_columns, numeric_columns) 튜플
        """
        categorical_cols = []
        numeric_cols = []

        # ID 관련 컬럼명 패턴 (집계에서 제외)
        id_patterns = [r'^id$', r'_id$', r'^.*id$', r'index', r'번호']

        for col_idx, col_name in enumerate(headers):
            col_name_lower = col_name.lower()

            # ID 컬럼은 건너뛰기
            is_id_column = any(re.search(pattern, col_name_lower) for pattern in id_patterns)
            if is_id_column:
                print(f"[컬럼 분석] '{col_name}': ID 컬럼으로 감지, 집계에서 제외")
                continue

            # 샘플 데이터 수집 (최대 100개)
            sample_values = []
            for row in rows[:100]:
                if col_idx < len(row) and row[col_idx] is not None:
                    sample_values.append(row[col_idx])

            if not sample_values:
                continue

            # 수치형 판단: 90% 이상이 숫자면 수치형
            numeric_count = 0
            for val in sample_values:
                if isinstance(val, (int, float)):
                    numeric_count += 1
                elif isinstance(val, str):
                    try:
                        float(val.replace(',', ''))
                        numeric_count += 1
                    except:
                        pass

            numeric_ratio = numeric_count / len(sample_values)

            if numeric_ratio >= 0.9:
                numeric_cols.append(col_name)
                print(f"[컬럼 분석] '{col_name}': 수치형 ({numeric_ratio*100:.0f}% 숫자)")
            else:
                # 범주형: 고유값이 전체의 50% 미만이면 범주형으로 간주
                unique_values = len(set(str(v) for v in sample_values))
                if unique_values < len(sample_values) * 0.5:
                    categorical_cols.append(col_name)
                    print(f"[컬럼 분석] '{col_name}': 범주형 ({unique_values}개 고유값)")

        return categorical_cols, numeric_cols

    @staticmethod
    def extract_groupby_from_message(message: str, headers: List[str]) -> Optional[List[str]]:
        """
        사용자 메시지에서 집계 기준 컬럼 추출
        예:
        - "Year별로 Category와 UnitsSold" → ['Year']
        - "Year로 Category 보고싶어" → ['Year', 'Category']
        - "Year, Category를 기준으로" → ['Year', 'Category']

        Args:
            message: 사용자 메시지
            headers: 사용 가능한 컬럼 리스트
        Returns:
            집계 기준 컬럼 리스트
        """
        if not message or not headers:
            return None

        message_lower = message.lower()
        header_map = {h.lower(): h for h in headers}
        group_columns = []

        # 패턴 1: "~별" (가장 명확한 패턴)
        # 예: "Year별로", "Category별"
        pattern_byeol = r'(\w+)별'
        matches = re.findall(pattern_byeol, message)
        for match in matches:
            match_lower = match.lower()
            if match_lower in header_map:
                original_col = header_map[match_lower]
                if original_col not in group_columns:
                    group_columns.append(original_col)
                    print(f"[집계 기준 추출] '{original_col}' 감지 (패턴: ~별)")

        # 패턴 2: "~로 ~" (예: "Year로 Category로")
        # 단, "보여줘", "그려줘", "해줘" 같은 동사는 제외
        if not group_columns:
            # 먼저 메시지에서 컬럼명과 "로"가 함께 나오는 패턴 찾기
            for header in headers:
                header_lower = header.lower()
                # "컬럼명로" 또는 "컬럼명으로" 패턴
                if re.search(rf'\b{re.escape(header_lower)}(?:으)?로(?!\s*(보|그리|시각화|분석|해))', message_lower):
                    if header not in group_columns:
                        group_columns.append(header)
                        print(f"[집계 기준 추출] '{header}' 감지 (패턴: ~로)")

        # 패턴 3: 기본 - 메시지에 등장한 컬럼 중 범주형만 추출
        # 단, 수치형 컬럼은 Y축 데이터로 간주하여 제외
        # 예: "Customer별 Revenue" → Customer만 추출 (Revenue는 수치형이므로 제외)
        if not group_columns:
            mentioned_cols = []
            for header in headers:
                header_lower = header.lower()
                # 컬럼명이 메시지에 등장하는지 확인
                if re.search(rf'\b{re.escape(header_lower)}\b', message_lower):
                    mentioned_cols.append(header)

            # 언급된 컬럼이 있으면 일단 추가
            if mentioned_cols:
                group_columns = mentioned_cols
                print(f"[집계 기준 추출] 언급된 컬럼: {', '.join(group_columns)} (패턴: 기본)")

        return group_columns if group_columns else None

    @staticmethod
    def auto_aggregate_data(headers: List[str], rows: List[List], group_columns: Optional[List[str]] = None) -> Tuple[List[str], List[List], str, List[str]]:
        """
        범주형 컬럼 기준으로 데이터를 자동 집계
        Args:
            headers: 컬럼 헤더
            rows: 원본 데이터 행
            group_columns: 집계 기준 컬럼 리스트 (선택사항, 없으면 자동 감지)
        Returns:
            (new_headers, aggregated_rows, group_column, numeric_columns) 튜플
        """
        # 컬럼 타입 감지
        categorical_cols, numeric_cols = AutomationAssistant.detect_column_types(headers, rows)

        if not numeric_cols:
            print(f"[자동 집계] 수치형 컬럼 없음 → 원본 데이터 사용")
            return headers, rows, headers[0] if headers else '', []

        # 집계 기준 컬럼 결정
        if group_columns:
            # 사용자가 지정한 컬럼 사용
            # 수치형 컬럼은 제외하고 범주형만 그룹 기준으로 사용
            valid_group_cols = [col for col in group_columns if col in headers and col not in numeric_cols]
            if not valid_group_cols:
                print(f"[자동 집계] 유효한 집계 기준 없음 → 첫 번째 범주형 컬럼 사용")
                valid_group_cols = [categorical_cols[0]] if categorical_cols else [headers[0]]
            group_column_list = valid_group_cols
        else:
            # 자동 감지: 첫 번째 범주형 컬럼 사용
            if not categorical_cols:
                print(f"[자동 집계] 범주형 컬럼 없음 → 원본 데이터 사용")
                return headers, rows, headers[0] if headers else '', []
            group_column_list = [categorical_cols[0]]

        # 그룹 컬럼 인덱스 찾기
        group_indices = [headers.index(col) for col in group_column_list]
        group_column = ', '.join(group_column_list)  # 표시용

        print(f"[자동 집계] '{group_column}' 기준으로 집계 시작")
        print(f"[자동 집계] 수치형 컬럼: {', '.join(numeric_cols)}")

        # 집계 수행 (다중 컬럼 그룹화 지원)
        aggregated = {}

        for row in rows:
            # 모든 그룹 컬럼의 값이 있는지 확인
            if any(idx >= len(row) for idx in group_indices):
                continue

            # 그룹 키 생성 (튜플로)
            group_key = tuple(str(row[idx]) for idx in group_indices)

            if group_key not in aggregated:
                aggregated[group_key] = {col: [] for col in numeric_cols}

            # 수치형 컬럼 값 수집
            for num_col in numeric_cols:
                try:
                    num_idx = headers.index(num_col)
                    if num_idx < len(row):
                        val = row[num_idx]
                        if isinstance(val, (int, float)):
                            aggregated[group_key][num_col].append(val)
                        elif isinstance(val, str):
                            try:
                                aggregated[group_key][num_col].append(float(val.replace(',', '')))
                            except:
                                pass
                except ValueError:
                    pass

        # 집계 결과를 행으로 변환 (합계 사용)
        new_headers = group_column_list + numeric_cols
        aggregated_rows = []

        for group_key in sorted(aggregated.keys()):
            # 그룹 키를 개별 값으로 변환
            new_row = list(group_key)
            for num_col in numeric_cols:
                values = aggregated[group_key][num_col]
                total = sum(values) if values else 0
                new_row.append(total)
            aggregated_rows.append(new_row)

        print(f"[자동 집계] 완료: {len(rows)}개 → {len(aggregated_rows)}개 ({group_column}별 합계)")

        return new_headers, aggregated_rows, group_column, numeric_cols

    @staticmethod
    def prepare_chart_data(data: Dict[str, Any], chart_type: str = 'bar', x_column: Optional[str] = None, y_columns: Optional[List[str]] = None, message: str = '') -> Optional[Dict[str, Any]]:
        """
        엑셀 데이터를 Chart.js 형식으로 변환
        Args:
            data: 테이블 데이터 (table_data)
            chart_type: 차트 타입 ('bar', 'line', 'pie')
            x_column: X축 칼럼명 (라벨, 선택사항)
            y_columns: Y축 칼럼명 리스트 (데이터, 선택사항)
            message: 사용자 메시지 (집계 기준 추출용)
        Returns:
            Chart.js 데이터 구조
        """
        if not data or 'table_data' not in data:
            return None

        table_data = data['table_data']
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])

        if len(headers) < 2 or len(rows) == 0:
            return None

        # 자동 집계: x_column과 y_columns가 명시되지 않은 경우에만 수행
        aggregation_note = ""
        if not x_column and not y_columns:
            print(f"[차트] 자동 집계 모드: 범주형 컬럼 기준 집계 시작")

            # 사용자 메시지에서 집계 기준 추출
            group_columns = None
            if message:
                group_columns = AutomationAssistant.extract_groupby_from_message(message, headers)

            original_headers = headers  # 원본 헤더 저장
            headers, rows, group_col, numeric_cols = AutomationAssistant.auto_aggregate_data(headers, rows, group_columns)

            # 집계 결과가 있으면 x_column과 y_columns 자동 설정
            if numeric_cols:
                # group_col이 "Year, Category" 형태이므로 그대로 전달
                x_column = group_col
                y_columns = numeric_cols
                aggregation_note = f"{group_col}별 합계"
                print(f"[차트] 자동 집계 완료: X={x_column}, Y={y_columns}")
                print(f"[차트] 집계 후 헤더: {headers}")

        # 칼럼 인덱스 찾기
        x_col_idx = 0  # 기본값: 첫 번째 칼럼
        x_col_indices = [0]  # 다중 그룹 컬럼 지원
        y_col_indices = list(range(1, len(headers)))  # 기본값: 모든 나머지 칼럼

        if x_column:
            # 복합 그룹 컬럼인 경우 (예: "Year, Category")
            if ', ' in x_column:
                x_col_names = [col.strip() for col in x_column.split(',')]
                x_col_indices = []
                for col_name in x_col_names:
                    try:
                        idx = headers.index(col_name)
                        x_col_indices.append(idx)
                        print(f"[차트] X축 칼럼: {col_name} (인덱스: {idx})")
                    except ValueError:
                        print(f"[차트] 경고: X축 칼럼 '{col_name}'을 찾을 수 없음")
                x_col_idx = x_col_indices[0] if x_col_indices else 0
            else:
                try:
                    x_col_idx = headers.index(x_column)
                    x_col_indices = [x_col_idx]
                    print(f"[차트] X축 칼럼: {x_column} (인덱스: {x_col_idx})")
                except ValueError:
                    print(f"[차트] 경고: X축 칼럼 '{x_column}'을 찾을 수 없음, 기본값 사용")

        if y_columns:
            y_col_indices = []
            for y_col in y_columns:
                try:
                    idx = headers.index(y_col)
                    y_col_indices.append(idx)
                    print(f"[차트] Y축 칼럼: {y_col} (인덱스: {idx})")
                except ValueError:
                    print(f"[차트] 경고: Y축 칼럼 '{y_col}'을 찾을 수 없음")

            if not y_col_indices:
                print(f"[차트] Y축 칼럼을 찾을 수 없어 기본값 사용")
                y_col_indices = list(range(1, len(headers)))

        # 첫 번째 컬럼: 라벨 (카테고리)
        # 나머지 컬럼: 데이터셋
        labels = []
        datasets = []

        total_rows = len(rows)

        # 대용량 데이터 자동 집계 (막대/선 차트만, 100개 이상일 때, 자동집계가 이미 수행되지 않은 경우)
        if chart_type in ['bar', 'line'] and total_rows > 100 and not aggregation_note:
            rows, aggregation_note = AutomationAssistant.aggregate_large_data(
                rows, headers, x_col_idx, y_col_indices, threshold=100
            )
            total_rows = len(rows)  # 집계 후 행 수로 업데이트
            print(f"[차트] 대용량 집계 완료: {aggregation_note}")

        # 파이 차트: 상위 10개만 표시 + 기타 (직관성 향상)
        if chart_type == 'pie' and total_rows > 10:
            print(f"[차트] 파이 차트: {total_rows}개 행 → 상위 10개 + 기타로 축약")
            # 첫 번째 숫자 컬럼의 값으로 정렬 (내림차순)
            sorted_rows = sorted(rows, key=lambda r: float(r[y_col_indices[0]]) if len(r) > y_col_indices[0] and isinstance(r[y_col_indices[0]], (int, float)) else 0, reverse=True)
            selected_rows = sorted_rows[:10]
            has_others = True
        else:
            selected_rows = rows
            has_others = False

        # 라벨 추출 (X축 칼럼 사용)
        # 다중 그룹 컬럼인 경우 결합하여 표시 (예: "2023-A", "2024-B")
        print(f"[차트] 레이블 추출 시작: x_col_idx={x_col_idx}, x_col_indices={x_col_indices}")
        print(f"[차트] 선택된 행 수: {len(selected_rows)}, 헤더: {headers}")
        for i, row in enumerate(selected_rows):
            if i < 3:  # 처음 3개 행만 디버그 출력
                print(f"[차트] 행 {i}: {row}")

            if len(x_col_indices) > 1:
                # 여러 그룹 컬럼이 있는 경우 "-"로 결합
                label_parts = []
                for idx in x_col_indices:
                    if idx < len(row):
                        label_parts.append(str(row[idx]))
                label = '-'.join(label_parts)
                labels.append(label)
                if i < 3:
                    print(f"[차트] 다중 그룹 레이블 {i}: {label}")
            else:
                # 단일 그룹 컬럼
                if len(row) > x_col_idx:
                    label = str(row[x_col_idx])
                    labels.append(label)
                    if i < 3:
                        print(f"[차트] 단일 그룹 레이블 {i}: {label} (인덱스 {x_col_idx})")
                else:
                    print(f"[차트] 경고: 행 {i}의 길이({len(row)})가 x_col_idx({x_col_idx})보다 작음")

        print(f"[차트] 최종 레이블 수: {len(labels)}, 처음 10개: {labels[:10]}")

        # 데이터셋 생성 (숫자 컬럼만)
        colors = [
            'rgba(102, 126, 234, 0.8)',  # 보라
            'rgba(14, 165, 233, 0.8)',   # 파랑
            'rgba(16, 185, 129, 0.8)',   # 초록
            'rgba(245, 158, 11, 0.8)',   # 주황
            'rgba(239, 68, 68, 0.8)',    # 빨강
            'rgba(236, 72, 153, 0.8)',   # 핑크
            'rgba(168, 85, 247, 0.8)',   # 자주
            'rgba(34, 197, 94, 0.8)',    # 라임
            'rgba(251, 191, 36, 0.8)',   # 노랑
            'rgba(59, 130, 246, 0.8)',   # 스카이블루
            'rgba(236, 253, 245, 0.8)',  # 민트
            'rgba(134, 239, 172, 0.8)',  # 연두
        ]

        for col_idx in y_col_indices:  # 선택된 Y축 칼럼만
            col_name = headers[col_idx]
            values = []

            for row in selected_rows:  # 선택된 행만
                if col_idx < len(row):
                    try:
                        val = row[col_idx]
                        if isinstance(val, (int, float)):
                            values.append(val)
                        elif isinstance(val, str) and val.replace('.', '').replace('-', '').isdigit():
                            values.append(float(val))
                        else:
                            values.append(0)
                    except:
                        values.append(0)
                else:
                    values.append(0)

            # 파이 차트에서 "기타" 항목 추가
            if has_others and chart_type == 'pie':
                # 나머지 행들의 합계 계산
                others_sum = 0
                for row in rows[10:]:  # 상위 10개 제외
                    if col_idx < len(row):
                        try:
                            val = row[col_idx]
                            if isinstance(val, (int, float)):
                                others_sum += val
                            elif isinstance(val, str) and val.replace('.', '').replace('-', '').isdigit():
                                others_sum += float(val)
                        except:
                            pass

                if others_sum > 0:
                    values.append(others_sum)
                    # "기타" 라벨 추가 (마지막에 한 번만)
                    if col_idx == 1 and '기타' not in labels:
                        labels.append('기타')

            # 숫자 데이터가 있으면 데이터셋 추가
            if any(v != 0 for v in values):
                # 색상 인덱스 계산 (y_col_indices에서의 순서 사용)
                color_idx = y_col_indices.index(col_idx) % len(colors)

                # 파이 차트는 각 조각마다 다른 색상 배열 사용
                if chart_type == 'pie':
                    background_colors = [colors[i % len(colors)] for i in range(len(values))]
                    border_colors = [colors[i % len(colors)].replace('0.8', '1') for i in range(len(values))]
                else:
                    background_colors = colors[color_idx]
                    border_colors = colors[color_idx].replace('0.8', '1')

                datasets.append({
                    'label': col_name,
                    'data': values,
                    'backgroundColor': background_colors,
                    'borderColor': border_colors,
                    'borderWidth': 2
                })

        if not datasets:
            return None

        # 차트 제목 생성 (의미있는 제목)
        # X축과 Y축 정보를 기반으로 자동 생성
        if chart_type == 'pie':
            chart_min_width = 600
            # Y축 첫 번째 칼럼을 제목으로
            y_label = headers[y_col_indices[0]] if y_col_indices and y_col_indices[0] < len(headers) else '데이터'
            chart_title = f'{y_label} 분포'
            if has_others:
                chart_title += f' (상위 10개)'
        else:
            min_width_per_point = 40
            chart_min_width = len(labels) * min_width_per_point

            # X축 칼럼명
            x_label = headers[x_col_idx] if x_col_idx < len(headers) else 'X축'

            # Y축 칼럼명들 (최대 2개만 제목에 표시)
            y_labels = [headers[idx] for idx in y_col_indices if idx < len(headers)]
            if len(y_labels) > 2:
                y_label = f'{y_labels[0]}, {y_labels[1]} 외 {len(y_labels) - 2}개'
            elif len(y_labels) == 2:
                y_label = f'{y_labels[0]}, {y_labels[1]}'
            elif len(y_labels) == 1:
                y_label = y_labels[0]
            else:
                y_label = 'Y축'

            # 의미있는 제목 생성
            chart_title = f'{x_label}별 {y_label}'

            # 집계 정보 추가
            if aggregation_note and aggregation_note != "원본 데이터":
                chart_title += f' ({aggregation_note})'

        # 줌/팬 기능은 집계 후에도 데이터가 많으면 활성화 (비활성화로 변경)
        enable_zoom = False  # 집계 방식으로 변경했으므로 줌/팬 비활성화
        # if enable_zoom:
        #     print(f"[차트] {total_rows}개 데이터 → 줌/팬 기능 활성화")

        # plugins 설정 구성
        plugins_config = {
            'legend': {
                'display': False,  # 범례 숨김
            },
            'title': {
                'display': False,  # 차트 제목 숨김
            }
        }

        # X축, Y축 스케일 설정
        scales_config = {}
        if chart_type in ['bar', 'line']:
            # X축 라벨: 다중 그룹 컬럼인 경우 모두 표시
            if len(x_col_indices) > 1:
                x_axis_labels = [headers[idx] for idx in x_col_indices if idx < len(headers)]
                x_axis_label = ', '.join(x_axis_labels)
            else:
                x_axis_label = headers[x_col_idx] if x_col_idx < len(headers) else ''

            # Y축 라벨: Y축 칼럼명들 (최대 2개까지 표시)
            y_labels = [headers[idx] for idx in y_col_indices if idx < len(headers)]
            if len(y_labels) > 2:
                y_axis_label = f'{y_labels[0]}, {y_labels[1]} 외 {len(y_labels) - 2}개'
            elif len(y_labels) == 2:
                y_axis_label = f'{y_labels[0]}, {y_labels[1]}'
            elif len(y_labels) == 1:
                y_axis_label = y_labels[0]
            else:
                y_axis_label = ''

            scales_config = {
                'x': {
                    'title': {
                        'display': True,
                        'text': x_axis_label,
                        'font': {
                            'size': 13,
                            'weight': '600'
                        },
                        'padding': {
                            'top': 10
                        }
                    },
                    'ticks': {
                        'autoSkip': True,
                        'maxRotation': 45,
                        'minRotation': 0,
                        'font': {
                            'size': 11
                        }
                    },
                    'grid': {
                        'display': False
                    }
                },
                'y': {
                    'title': {
                        'display': True,
                        'text': y_axis_label,
                        'font': {
                            'size': 13,
                            'weight': '600'
                        },
                        'padding': {
                            'bottom': 10
                        }
                    },
                    'beginAtZero': True,
                    'ticks': {
                        'font': {
                            'size': 11
                        },
                        'callback': 'function(value) { if (value >= 1000000) { return (value/1000000).toFixed(1) + "M"; } else if (value >= 1000) { return (value/1000).toFixed(0) + "K"; } else { return value.toLocaleString(); } }'
                    },
                    'grid': {
                        'color': 'rgba(0, 0, 0, 0.05)'
                    }
                }
            }

        return {
            'type': chart_type,
            'data': {
                'labels': labels,
                'datasets': datasets
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False if chart_type != 'pie' else True,
                'layout': {
                    'padding': {
                        'left': 15,
                        'right': 15,
                        'top': 15,
                        'bottom': 15
                    }
                },
                'plugins': plugins_config,
                'scales': scales_config
            },
            'minWidth': chart_min_width
        }

    @staticmethod
    def generate_chart_analysis(chart_data: Dict[str, Any], table_data: Dict[str, Any]) -> str:
        """
        차트 데이터를 분석하여 간결한 설명 생성 (HTML 표 형식)
        Args:
            chart_data: Chart.js 차트 데이터
            table_data: 원본 테이블 데이터
        Returns:
            분석 설명 텍스트 (HTML 표 형식)
        """
        if not chart_data or not table_data:
            return ""

        chart_type = chart_data.get('type', 'bar')
        data = chart_data.get('data', {})
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])

        if not datasets:
            return ""

        # HTML 표 형식으로 분석 결과 생성
        analysis = "\n\n<div class='data-analysis-table'>\n"

        # 각 데이터셋을 표 형식으로 분석 (최대 3개만)
        for idx, dataset in enumerate(datasets[:3]):
            label = dataset.get('label', '데이터')
            values = dataset.get('data', [])

            if not values:
                continue

            total = sum(values)
            avg = total / len(values) if values else 0
            max_val = max(values) if values else 0
            min_val = min(values) if values else 0
            max_idx = values.index(max_val) if max_val in values else 0
            min_idx = values.index(min_val) if min_val in values else 0

            # HTML 표로 간결하게 표시
            analysis += f"<h4>{label}</h4>\n"
            analysis += "<table>\n"
            analysis += "  <thead>\n"
            analysis += "    <tr><th>항목</th><th>값</th><th>세부사항</th></tr>\n"
            analysis += "  </thead>\n"
            analysis += "  <tbody>\n"
            analysis += f"    <tr><td>합계</td><td>{total:,.0f}</td><td>-</td></tr>\n"
            analysis += f"    <tr><td>평균</td><td>{avg:,.1f}</td><td>-</td></tr>\n"
            analysis += f"    <tr><td>최대</td><td>{max_val:,.0f}</td><td>{labels[max_idx] if max_idx < len(labels) else ''}</td></tr>\n"
            analysis += f"    <tr><td>최소</td><td>{min_val:,.0f}</td><td>{labels[min_idx] if min_idx < len(labels) else ''}</td></tr>\n"

            # 추세 분석 (선 그래프만)
            if chart_type == 'line' and len(values) > 1:
                increases = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
                decreases = sum(1 for i in range(1, len(values)) if values[i] < values[i-1])

                if increases > decreases:
                    trend = f"↗ 상승"
                    trend_detail = f"{increases}회 증가"
                elif decreases > increases:
                    trend = f"↘ 하락"
                    trend_detail = f"{decreases}회 감소"
                else:
                    trend = "→ 보합"
                    trend_detail = "변동 없음"
                analysis += f"    <tr><td>추세</td><td>{trend}</td><td>{trend_detail}</td></tr>\n"

            analysis += "  </tbody>\n"
            analysis += "</table>\n\n"

        analysis += "</div>\n"

        return analysis

    @staticmethod
    def perform_eda(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        전체 데이터셋에 대한 탐색적 데이터 분석(EDA) 수행
        Args:
            data: 테이블 데이터 (table_data)
        Returns:
            EDA 결과 (통계, 차트 리스트, 인사이트)
        """
        if not data or 'table_data' not in data:
            return {
                'success': False,
                'error': 'EDA를 수행할 데이터가 없습니다.'
            }

        table_data = data['table_data']
        headers = table_data.get('headers', [])
        rows = table_data.get('rows', [])

        if len(headers) == 0 or len(rows) == 0:
            return {
                'success': False,
                'error': '데이터가 비어있습니다.'
            }

        print(f"[EDA] 시작: {len(rows)}행 x {len(headers)}열")

        # 1. 데이터 타입 분류
        numeric_cols = []
        categorical_cols = []
        date_cols = []

        for col_idx, col_name in enumerate(headers):
            # ID 컬럼 제외
            if col_name.lower() in ['id', '_id', 'index', '번호', 'no']:
                continue

            numeric_count = 0
            total_count = 0

            for row in rows:
                if col_idx < len(row):
                    val = row[col_idx]
                    if val is not None and val != '':
                        total_count += 1
                        if isinstance(val, (int, float)):
                            numeric_count += 1
                        elif isinstance(val, str):
                            # 날짜 패턴 체크
                            if re.match(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}', str(val)):
                                date_cols.append(col_idx)
                                break
                            # 숫자 문자열 체크
                            elif val.replace('.', '').replace('-', '').replace(',', '').isdigit():
                                numeric_count += 1

            if col_idx in date_cols:
                continue

            # 70% 이상이 숫자면 수치형으로 분류
            if total_count > 0 and numeric_count / total_count >= 0.7:
                numeric_cols.append(col_idx)
            else:
                categorical_cols.append(col_idx)

        print(f"[EDA] 수치형: {[headers[i] for i in numeric_cols]}")
        print(f"[EDA] 범주형: {[headers[i] for i in categorical_cols]}")
        print(f"[EDA] 날짜형: {[headers[i] for i in date_cols]}")

        # 2. 기본 통계 생성
        stats_html = AutomationAssistant.generate_basic_statistics(headers, rows, numeric_cols, categorical_cols)

        # 3. 자동 차트 생성 리스트
        chart_list = []

        # 3-1. 수치형 변수: 히스토그램 (분포도)
        for col_idx in numeric_cols[:3]:  # 최대 3개
            chart_data = AutomationAssistant.create_histogram(headers, rows, col_idx)
            if chart_data:
                chart_list.append(chart_data)

        # 3-2. 범주형 변수: 파이 차트 (상위 10개)
        for col_idx in categorical_cols[:2]:  # 최대 2개
            chart_data = AutomationAssistant.create_category_pie_chart(headers, rows, col_idx)
            if chart_data:
                chart_list.append(chart_data)

        # 3-3. 상관관계 히트맵 (수치형 변수 2개 이상)
        if len(numeric_cols) >= 2:
            correlation_chart = AutomationAssistant.create_correlation_heatmap(headers, rows, numeric_cols)
            if correlation_chart:
                chart_list.append(correlation_chart)

        # 4. 인사이트 생성
        insights = AutomationAssistant.generate_insights(headers, rows, numeric_cols, categorical_cols)

        return {
            'success': True,
            'stats_html': stats_html,
            'charts': chart_list,
            'insights': insights,
            'summary': f"총 {len(rows)}개 행, {len(headers)}개 칼럼 분석 완료"
        }

    @staticmethod
    def generate_basic_statistics(headers: List[str], rows: List[List], numeric_cols: List[int], categorical_cols: List[int]) -> str:
        """기본 통계 HTML 생성"""
        html = '<div class="eda-stats">\n'
        html += '<h3>📊 데이터 개요</h3>\n'
        html += '<table class="data-analysis-table">\n'
        html += '  <thead><tr><th>항목</th><th>값</th></tr></thead>\n'
        html += '  <tbody>\n'
        html += f'    <tr><td>총 행 수</td><td>{len(rows):,}개</td></tr>\n'
        html += f'    <tr><td>총 열 수</td><td>{len(headers)}개</td></tr>\n'
        html += f'    <tr><td>수치형 변수</td><td>{len(numeric_cols)}개</td></tr>\n'
        html += f'    <tr><td>범주형 변수</td><td>{len(categorical_cols)}개</td></tr>\n'

        # 결측치 계산
        total_cells = len(rows) * len(headers)
        missing_count = 0
        for row in rows:
            for val in row:
                if val is None or val == '':
                    missing_count += 1

        missing_pct = (missing_count / total_cells * 100) if total_cells > 0 else 0
        html += f'    <tr><td>결측치</td><td>{missing_count}개 ({missing_pct:.1f}%)</td></tr>\n'
        html += '  </tbody>\n'
        html += '</table>\n'

        # 수치형 변수 통계
        if numeric_cols:
            html += '<h3>📈 수치형 변수 통계</h3>\n'
            html += '<table class="data-analysis-table">\n'
            html += '  <thead><tr><th>변수명</th><th>평균</th><th>중앙값</th><th>표준편차</th><th>최소</th><th>최대</th></tr></thead>\n'
            html += '  <tbody>\n'

            for col_idx in numeric_cols[:5]:  # 최대 5개
                col_name = headers[col_idx]
                values = []
                for row in rows:
                    if col_idx < len(row):
                        val = row[col_idx]
                        try:
                            if isinstance(val, (int, float)):
                                values.append(float(val))
                            elif isinstance(val, str) and val.replace('.', '').replace('-', '').replace(',', '').isdigit():
                                values.append(float(val.replace(',', '')))
                        except:
                            pass

                if values:
                    avg = sum(values) / len(values)
                    sorted_vals = sorted(values)
                    median = sorted_vals[len(sorted_vals) // 2]
                    variance = sum((x - avg) ** 2 for x in values) / len(values)
                    std_dev = variance ** 0.5
                    min_val = min(values)
                    max_val = max(values)

                    html += f'    <tr><td>{col_name}</td><td>{avg:,.1f}</td><td>{median:,.1f}</td><td>{std_dev:,.1f}</td><td>{min_val:,.1f}</td><td>{max_val:,.1f}</td></tr>\n'

            html += '  </tbody>\n'
            html += '</table>\n'

        html += '</div>\n'
        return html

    @staticmethod
    def create_histogram(headers: List[str], rows: List[List], col_idx: int) -> Optional[Dict[str, Any]]:
        """히스토그램 생성 (수치형 변수 분포)"""
        col_name = headers[col_idx]
        values = []

        for row in rows:
            if col_idx < len(row):
                val = row[col_idx]
                try:
                    if isinstance(val, (int, float)):
                        values.append(float(val))
                    elif isinstance(val, str) and val.replace('.', '').replace('-', '').replace(',', '').isdigit():
                        values.append(float(val.replace(',', '')))
                except:
                    pass

        if not values or len(values) < 2:
            return None

        # 구간 나누기 (최대 12개 구간으로 줄여서 가독성 향상)
        min_val = min(values)
        max_val = max(values)
        num_bins = min(12, max(5, len(values) // 15))
        bin_width = (max_val - min_val) / num_bins

        # 히스토그램 데이터 생성
        bins = {}
        for val in values:
            bin_idx = min(int((val - min_val) / bin_width), num_bins - 1)
            bins[bin_idx] = bins.get(bin_idx, 0) + 1

        labels = []
        counts = []
        for i in range(num_bins):
            bin_start = min_val + i * bin_width
            bin_end = bin_start + bin_width
            # 숫자 포맷팅: 큰 숫자는 K/M 단위로 표시
            if bin_end >= 1000000:
                label = f'{bin_start/1000000:.1f}M~{bin_end/1000000:.1f}M'
            elif bin_end >= 1000:
                label = f'{bin_start/1000:.0f}K~{bin_end/1000:.0f}K'
            else:
                label = f'{bin_start:.0f}~{bin_end:.0f}'
            labels.append(label)
            counts.append(bins.get(i, 0))

        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': '빈도',
                    'data': counts,
                    'backgroundColor': 'rgba(102, 126, 234, 0.7)',
                    'borderColor': 'rgba(102, 126, 234, 1)',
                    'borderWidth': 1,
                    'borderRadius': 4
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'layout': {
                    'padding': {
                        'left': 10,
                        'right': 10,
                        'top': 10,
                        'bottom': 10
                    }
                },
                'plugins': {
                    'legend': {'display': False},
                    'title': {
                        'display': True,
                        'text': f'{col_name} 분포',
                        'font': {'size': 16, 'weight': 'bold'},
                        'padding': {'bottom': 20}
                    },
                    'tooltip': {
                        'callbacks': {
                            'label': 'function(context) { return "빈도: " + context.parsed.y.toLocaleString() + "개"; }'
                        }
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': col_name,
                            'font': {'size': 13, 'weight': '600'}
                        },
                        'ticks': {
                            'autoSkip': False,
                            'maxRotation': 45,
                            'minRotation': 45,
                            'font': {'size': 11}
                        },
                        'grid': {'display': False}
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': '빈도 (개수)',
                            'font': {'size': 13, 'weight': '600'}
                        },
                        'beginAtZero': True,
                        'ticks': {
                            'font': {'size': 11},
                            'callback': 'function(value) { return value.toLocaleString(); }'
                        },
                        'grid': {'color': 'rgba(0, 0, 0, 0.05)'}
                    }
                }
            },
            'minWidth': 700
        }

    @staticmethod
    def create_category_pie_chart(headers: List[str], rows: List[List], col_idx: int) -> Optional[Dict[str, Any]]:
        """범주형 변수 파이 차트 생성"""
        col_name = headers[col_idx]
        category_counts = {}

        for row in rows:
            if col_idx < len(row):
                val = str(row[col_idx]) if row[col_idx] is not None else 'N/A'
                category_counts[val] = category_counts.get(val, 0) + 1

        if len(category_counts) < 2:
            return None

        # 상위 10개만
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        labels = [item[0] for item in sorted_categories]
        counts = [item[1] for item in sorted_categories]

        colors = [
            'rgba(102, 126, 234, 0.8)', 'rgba(14, 165, 233, 0.8)', 'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)', 'rgba(239, 68, 68, 0.8)', 'rgba(236, 72, 153, 0.8)',
            'rgba(168, 85, 247, 0.8)', 'rgba(34, 197, 94, 0.8)', 'rgba(251, 191, 36, 0.8)',
            'rgba(59, 130, 246, 0.8)'
        ]

        return {
            'type': 'pie',
            'data': {
                'labels': labels,
                'datasets': [{
                    'data': counts,
                    'backgroundColor': colors[:len(labels)],
                    'borderColor': [c.replace('0.8', '1') for c in colors[:len(labels)]],
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': True,
                'plugins': {
                    'legend': {'display': True, 'position': 'right'},
                    'title': {'display': True, 'text': f'{col_name} 분포'}
                }
            },
            'minWidth': 600
        }

    @staticmethod
    def create_correlation_heatmap(headers: List[str], rows: List[List], numeric_cols: List[int]) -> Optional[Dict[str, Any]]:
        """상관관계 히트맵 (간단한 막대 차트로 표현)"""
        # 상관계수 계산은 복잡하므로, 대신 각 변수의 평균값을 비교하는 막대 차트로 대체
        labels = [headers[idx] for idx in numeric_cols[:5]]
        averages = []

        for col_idx in numeric_cols[:5]:
            values = []
            for row in rows:
                if col_idx < len(row):
                    val = row[col_idx]
                    try:
                        if isinstance(val, (int, float)):
                            values.append(float(val))
                        elif isinstance(val, str) and val.replace('.', '').replace('-', '').replace(',', '').isdigit():
                            values.append(float(val.replace(',', '')))
                    except:
                        pass

            if values:
                averages.append(sum(values) / len(values))
            else:
                averages.append(0)

        if not averages:
            return None

        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': '평균값',
                    'data': averages,
                    'backgroundColor': 'rgba(16, 185, 129, 0.8)',
                    'borderColor': 'rgba(16, 185, 129, 1)',
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': False},
                    'title': {'display': True, 'text': '수치형 변수 평균 비교'}
                },
                'scales': {
                    'x': {'title': {'display': True, 'text': '변수명'}},
                    'y': {'title': {'display': True, 'text': '평균값'}, 'beginAtZero': True}
                }
            },
            'minWidth': 600
        }

    @staticmethod
    def generate_insights(headers: List[str], rows: List[List], numeric_cols: List[int], categorical_cols: List[int]) -> str:
        """데이터 인사이트 생성"""
        insights = []

        # 1. 데이터 크기 인사이트
        if len(rows) > 1000:
            insights.append(f"✅ 대용량 데이터셋: {len(rows):,}개 행으로 통계적으로 유의미한 분석이 가능합니다.")
        elif len(rows) < 30:
            insights.append(f"⚠️ 소규모 데이터셋: {len(rows)}개 행으로 통계적 신뢰도가 제한적일 수 있습니다.")

        # 2. 수치형 변수 인사이트
        if numeric_cols:
            insights.append(f"📊 {len(numeric_cols)}개의 수치형 변수를 통해 정량적 분석이 가능합니다.")

        # 3. 범주형 변수 인사이트
        if categorical_cols:
            insights.append(f"🏷️ {len(categorical_cols)}개의 범주형 변수를 통해 그룹별 비교 분석이 가능합니다.")

        # 4. 결측치 인사이트
        total_cells = len(rows) * len(headers)
        missing_count = sum(1 for row in rows for val in row if val is None or val == '')
        missing_pct = (missing_count / total_cells * 100) if total_cells > 0 else 0

        if missing_pct > 10:
            insights.append(f"⚠️ 결측치가 {missing_pct:.1f}%로 높습니다. 데이터 품질 확인이 필요합니다.")
        elif missing_pct == 0:
            insights.append(f"✅ 결측치가 없는 완전한 데이터셋입니다.")

        return '\n'.join(insights) if insights else '데이터 분석 완료'
