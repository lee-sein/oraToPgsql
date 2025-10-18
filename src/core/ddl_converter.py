"""
DDL 변환 모듈
Oracle DDL을 PostgreSQL DDL로 변환합니다.
"""

from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DDLConverter:
    """Oracle DDL을 PostgreSQL DDL로 변환하는 클래스"""

    # Oracle → PostgreSQL 데이터 타입 매핑
    TYPE_MAPPING = {
        'VARCHAR2': 'VARCHAR',
        'NVARCHAR2': 'VARCHAR',
        'CHAR': 'CHAR',
        'NCHAR': 'CHAR',
        'NUMBER': 'NUMERIC',
        'FLOAT': 'DOUBLE PRECISION',
        'BINARY_FLOAT': 'REAL',
        'BINARY_DOUBLE': 'DOUBLE PRECISION',
        'DATE': 'TIMESTAMP',
        'TIMESTAMP': 'TIMESTAMP',
        'TIMESTAMP(6)': 'TIMESTAMP',
        'CLOB': 'TEXT',
        'NCLOB': 'TEXT',
        'BLOB': 'BYTEA',
        'RAW': 'BYTEA',
        'LONG': 'TEXT',
        'LONG RAW': 'BYTEA',
        'XMLTYPE': 'XML',
    }

    def __init__(self):
        pass

    def convert_data_type(self, oracle_type: str, length: Optional[int] = None,
                          precision: Optional[int] = None, scale: Optional[int] = None) -> str:
        """Oracle 데이터 타입을 PostgreSQL 타입으로 변환"""
        oracle_type = oracle_type.upper()

        # NUMBER 타입 특별 처리
        if oracle_type == 'NUMBER':
            if precision is None:
                return 'NUMERIC'
            elif scale is None or scale == 0:
                # 정수형
                if precision <= 4:
                    return 'SMALLINT'
                elif precision <= 9:
                    return 'INTEGER'
                elif precision <= 18:
                    return 'BIGINT'
                else:
                    return f'NUMERIC({precision})'
            else:
                # 실수형
                return f'NUMERIC({precision},{scale})'

        # VARCHAR2, CHAR 등 길이가 있는 타입
        if oracle_type in ['VARCHAR2', 'NVARCHAR2', 'CHAR', 'NCHAR']:
            pg_type = self.TYPE_MAPPING.get(oracle_type, 'VARCHAR')
            if length:
                return f'{pg_type}({length})'
            return pg_type

        # 일반 매핑
        return self.TYPE_MAPPING.get(oracle_type, 'TEXT')

    def generate_create_table(self, table_name: str, columns: List[Dict],
                              primary_key: Optional[Dict] = None) -> str:
        """CREATE TABLE DDL 생성"""
        ddl_parts = [f'CREATE TABLE {table_name.lower()} (']

        # 컬럼 정의
        column_definitions = []
        for col in columns:
            col_def = f"  {col['name'].lower()} "

            # 데이터 타입 변환
            col_def += self.convert_data_type(
                col['data_type'],
                col.get('length'),
                col.get('precision'),
                col.get('scale')
            )

            # NULL 제약
            if not col.get('nullable', True):
                col_def += ' NOT NULL'

            # DEFAULT 값
            if col.get('default'):
                default_value = self._convert_default_value(col['default'])
                if default_value:
                    col_def += f' DEFAULT {default_value}'

            column_definitions.append(col_def)

        ddl_parts.append(',\n'.join(column_definitions))

        # Primary Key 제약
        if primary_key:
            pk_columns = ', '.join([col.lower() for col in primary_key['columns']])
            ddl_parts.append(f',\n  CONSTRAINT {primary_key["name"].lower()}_pk PRIMARY KEY ({pk_columns})')

        ddl_parts.append('\n);')

        return ''.join(ddl_parts)

    def generate_indexes(self, table_name: str, indexes: List[Dict],
                         primary_key: Optional[Dict] = None) -> List[str]:
        """인덱스 생성 DDL 생성"""
        index_ddls = []
        pk_columns = set(primary_key['columns']) if primary_key else set()

        for idx in indexes:
            # PK 인덱스는 자동 생성되므로 제외
            idx_columns = set(idx['columns'])
            if idx_columns == pk_columns:
                continue

            unique_clause = 'UNIQUE ' if idx.get('unique') else ''
            columns_str = ', '.join([col.lower() for col in idx['columns']])
            index_name = idx['name'].lower()

            ddl = f"CREATE {unique_clause}INDEX {index_name} ON {table_name.lower()} ({columns_str});"
            index_ddls.append(ddl)

        return index_ddls

    def _convert_default_value(self, oracle_default: str) -> Optional[str]:
        """Oracle DEFAULT 값을 PostgreSQL 형식으로 변환"""
        if not oracle_default:
            return None

        oracle_default = oracle_default.strip()

        # SYSDATE → CURRENT_TIMESTAMP
        if 'SYSDATE' in oracle_default.upper():
            return 'CURRENT_TIMESTAMP'

        # NULL
        if oracle_default.upper() == 'NULL':
            return 'NULL'

        # 문자열 리터럴
        if oracle_default.startswith("'") and oracle_default.endswith("'"):
            return oracle_default

        # 숫자
        try:
            float(oracle_default)
            return oracle_default
        except ValueError:
            pass

        # 기타 표현식은 그대로 반환
        return oracle_default

    def generate_full_ddl(self, table_name: str, columns: List[Dict],
                          primary_key: Optional[Dict] = None,
                          indexes: Optional[List[Dict]] = None) -> str:
        """전체 DDL 생성 (테이블 + 인덱스)"""
        ddl_statements = []

        # CREATE TABLE
        create_table_ddl = self.generate_create_table(table_name, columns, primary_key)
        ddl_statements.append(create_table_ddl)

        # CREATE INDEX
        if indexes:
            index_ddls = self.generate_indexes(table_name, indexes, primary_key)
            ddl_statements.extend(index_ddls)

        return '\n\n'.join(ddl_statements)

    def validate_conversion(self, columns: List[Dict]) -> List[str]:
        """변환 검증 및 경고 메시지 생성"""
        warnings = []

        for col in columns:
            oracle_type = col['data_type'].upper()

            # 매핑되지 않은 타입 확인
            if oracle_type not in self.TYPE_MAPPING and not oracle_type.startswith('NUMBER'):
                warnings.append(
                    f"컬럼 '{col['name']}': 알 수 없는 타입 '{oracle_type}'이 TEXT로 변환됩니다."
                )

            # NUMBER 타입에서 precision이 너무 큰 경우
            if oracle_type == 'NUMBER' and col.get('precision'):
                if col['precision'] > 38:
                    warnings.append(
                        f"컬럼 '{col['name']}': PRECISION {col['precision']}이(가) PostgreSQL의 최대값 38을 초과합니다."
                    )

        return warnings


# 테스트용 함수
def test_converter():
    """DDL 변환기 테스트"""
    converter = DDLConverter()

    # 샘플 테이블 정의
    columns = [
        {'name': 'ID', 'data_type': 'NUMBER', 'precision': 10, 'scale': 0, 'nullable': False},
        {'name': 'NAME', 'data_type': 'VARCHAR2', 'length': 100, 'nullable': False},
        {'name': 'EMAIL', 'data_type': 'VARCHAR2', 'length': 255, 'nullable': True},
        {'name': 'CREATED_DATE', 'data_type': 'DATE', 'nullable': False, 'default': 'SYSDATE'},
        {'name': 'AMOUNT', 'data_type': 'NUMBER', 'precision': 15, 'scale': 2, 'nullable': True},
    ]

    primary_key = {
        'name': 'PK_USERS',
        'columns': ['ID']
    }

    indexes = [
        {'name': 'IDX_EMAIL', 'unique': True, 'columns': ['EMAIL']},
        {'name': 'IDX_NAME', 'unique': False, 'columns': ['NAME']},
    ]

    # DDL 생성
    ddl = converter.generate_full_ddl('USERS', columns, primary_key, indexes)
    print(ddl)

    # 검증
    warnings = converter.validate_conversion(columns)
    if warnings:
        print("\n경고:")
        for warning in warnings:
            print(f"  - {warning}")


if __name__ == '__main__':
    test_converter()
