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
    def prepare_chart_data(data: Dict[str, Any], chart_type: str = 'bar', x_column: Optional[str] = None, y_columns: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        엑셀 데이터를 Chart.js 형식으로 변환
        Args:
            data: 테이블 데이터 (table_data)
            chart_type: 차트 타입 ('bar', 'line', 'pie')
            x_column: X축 칼럼명 (라벨, 선택사항)
            y_columns: Y축 칼럼명 리스트 (데이터, 선택사항)
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

        # 칼럼 인덱스 찾기
        x_col_idx = 0  # 기본값: 첫 번째 칼럼
        y_col_indices = list(range(1, len(headers)))  # 기본값: 모든 나머지 칼럼

        if x_column:
            try:
                x_col_idx = headers.index(x_column)
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

        # 파이 차트: 상위 10개만 표시 + 기타 (직관성 향상)
        # 막대/선 차트: 모든 행 표시 (스크롤 가능)
        if chart_type == 'pie' and total_rows > 10:
            print(f"[차트] 파이 차트: {total_rows}개 행 → 상위 10개 + 기타로 축약")
            # 첫 번째 숫자 컬럼의 값으로 정렬 (내림차순)
            sorted_rows = sorted(rows, key=lambda r: float(r[1]) if len(r) > 1 and isinstance(r[1], (int, float)) else 0, reverse=True)
            selected_rows = sorted_rows[:10]
            has_others = True
        else:
            print(f"[차트] 총 {total_rows}개 행 데이터 - 전체 표시 (스크롤 가능)")
            selected_rows = rows
            has_others = False

        # 라벨 추출 (X축 칼럼 사용)
        for i, row in enumerate(selected_rows):
            if len(row) > x_col_idx:
                labels.append(str(row[x_col_idx]))

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

        # 데이터 개수에 따라 차트 너비 계산 (각 데이터 포인트당 최소 너비 확보)
        # 원 차트는 고정 너비, 막대/선 차트는 데이터 개수에 비례
        if chart_type == 'pie':
            chart_min_width = 600  # 원 차트는 정사각형에 가까운 고정 너비
            # 파이 차트 제목 (기타 포함 여부 표시)
            chart_title = f'데이터 시각화 - 원 차트'
            if has_others:
                chart_title += f' (상위 10개 + 기타 {total_rows - 10}개)'
        else:
            min_width_per_point = 40  # 각 데이터 포인트당 최소 40px
            chart_min_width = len(labels) * min_width_per_point
            chart_title = '데이터 시각화'

        # 줌/팬 플러그인 설정 (100개 이상 데이터일 때만)
        enable_zoom = chart_type in ['bar', 'line'] and total_rows >= 100
        if enable_zoom:
            print(f"[차트] {total_rows}개 데이터 → 줌/팬 기능 활성화")

        # plugins 설정 구성
        plugins_config = {
            'legend': {
                'position': 'top',
                'align': 'start',  # 왼쪽 정렬
                'labels': {
                    'boxWidth': 12,
                    'padding': 10,
                    'font': {
                        'size': 11
                    }
                }
            },
            'title': {
                'display': True,
                'text': chart_title + (' (마우스 휠로 줌, 드래그로 이동)' if enable_zoom else ''),
                'align': 'center',  # 제목은 중앙
                'padding': {
                    'bottom': 10
                }
            }
        }

        # zoom 플러그인 설정 추가 (100개 이상일 때만)
        if enable_zoom:
            plugins_config['zoom'] = {
                'zoom': {
                    'wheel': {
                        'enabled': True,  # 마우스 휠 줌
                        'speed': 0.1
                    },
                    'pinch': {
                        'enabled': True  # 모바일 핀치 줌
                    },
                    'mode': 'x',  # X축만 줌 (가로)
                },
                'pan': {
                    'enabled': True,  # 팬(드래그) 활성화
                    'mode': 'x',  # X축만 팬
                    'modifierKey': None  # 수정키 없이 드래그만으로 팬
                },
                'limits': {
                    'x': {
                        'minRange': 10  # 최소 10개 항목은 표시
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
                'plugins': plugins_config,
                'scales': {
                    'x': {
                        'ticks': {
                            'autoSkip': False,  # 모든 라벨 표시
                            'maxRotation': 45,  # 45도 회전으로 통일
                            'minRotation': 45,
                            'font': {
                                'size': 10
                            }
                        }
                    },
                    'y': {
                        'beginAtZero': True
                    }
                } if chart_type in ['bar', 'line'] else {}
            },
            'minWidth': chart_min_width  # 최소 너비 설정 (스크롤용)
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
