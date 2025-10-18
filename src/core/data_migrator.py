"""
데이터 마이그레이션 모듈
Oracle에서 PostgreSQL로 데이터를 이관합니다.
"""

import logging
from typing import List, Dict, Optional, Callable
from datetime import datetime
import io

logger = logging.getLogger(__name__)


class MigrationProgress:
    """마이그레이션 진행 상황 추적"""
    def __init__(self, total_rows: int):
        self.total_rows = total_rows
        self.migrated_rows = 0
        self.failed_rows = 0
        self.start_time = None
        self.end_time = None
        self.errors = []

    def start(self):
        self.start_time = datetime.now()

    def finish(self):
        self.end_time = datetime.now()

    def update(self, migrated: int, failed: int = 0):
        self.migrated_rows += migrated
        self.failed_rows += failed

    def add_error(self, error: str):
        self.errors.append(error)

    def get_progress_percentage(self) -> float:
        if self.total_rows == 0:
            return 100.0
        return (self.migrated_rows / self.total_rows) * 100

    def get_elapsed_time(self) -> float:
        if not self.start_time:
            return 0
        end = self.end_time if self.end_time else datetime.now()
        return (end - self.start_time).total_seconds()

    def get_summary(self) -> Dict:
        return {
            'total_rows': self.total_rows,
            'migrated_rows': self.migrated_rows,
            'failed_rows': self.failed_rows,
            'success_rate': (self.migrated_rows / self.total_rows * 100) if self.total_rows > 0 else 0,
            'elapsed_time': self.get_elapsed_time(),
            'errors': self.errors
        }


class DataMigrator:
    """데이터 마이그레이션 클래스"""

    def __init__(self, oracle_conn, postgres_conn, batch_size: int = 1000,
                 enable_checkpoint: bool = True):
        """
        Args:
            oracle_conn: OracleConnection 인스턴스
            postgres_conn: PostgresConnection 인스턴스
            batch_size: 배치 크기 (기본 1000건)
            enable_checkpoint: 체크포인트 활성화 (기본 True)
        """
        self.oracle_conn = oracle_conn
        self.postgres_conn = postgres_conn
        self.batch_size = batch_size
        self.progress = None
        self._cancelled = False
        self.enable_checkpoint = enable_checkpoint
        self._checkpoint_table = "_migration_checkpoint"

    def cancel(self):
        """마이그레이션 취소"""
        self._cancelled = True
        logger.info("마이그레이션 취소 요청")

    def migrate_table(self, owner: str, table_name: str,
                      progress_callback: Optional[Callable] = None,
                      where_clause: Optional[str] = None,
                      resume: bool = False) -> MigrationProgress:
        """
        테이블 데이터 마이그레이션

        Args:
            owner: Oracle 스키마 소유자
            table_name: 테이블 이름
            progress_callback: 진행 상황 콜백 함수
            where_clause: 필터 조건 (예: "created_date >= TO_DATE('2024-01-01', 'YYYY-MM-DD')")

        Returns:
            MigrationProgress: 마이그레이션 결과
        """
        self._cancelled = False

        # Oracle 연결 확인
        if not self.oracle_conn.connection:
            self.oracle_conn.connect()

        # PostgreSQL 연결 확인
        if not self.postgres_conn.connection:
            self.postgres_conn.connect()

        # 총 행 수 조회
        total_rows = self._count_rows(owner, table_name, where_clause)
        self.progress = MigrationProgress(total_rows)
        self.progress.start()

        logger.info(f"마이그레이션 시작: {table_name} (총 {total_rows:,}건)")

        try:
            # 컬럼 목록 조회
            columns = self.oracle_conn.get_table_columns(owner, table_name)
            column_names = [col['name'] for col in columns]

            # 데이터 추출 및 적재
            self._migrate_data_batch(
                owner, table_name, column_names, where_clause, progress_callback
            )

            self.progress.finish()
            logger.info(f"마이그레이션 완료: {self.progress.migrated_rows:,}/{total_rows:,}건")

            return self.progress

        except Exception as e:
            logger.error(f"마이그레이션 오류: {str(e)}")
            self.progress.add_error(str(e))
            self.progress.finish()
            raise

    def _count_rows(self, owner: str, table_name: str, where_clause: Optional[str] = None) -> int:
        """총 행 수 조회"""
        cursor = self.oracle_conn.connection.cursor()
        query = f"SELECT COUNT(*) FROM {owner}.{table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def _migrate_data_batch(self, owner: str, table_name: str,
                            column_names: List[str], where_clause: Optional[str],
                            progress_callback: Optional[Callable]):
        """배치 단위로 데이터 마이그레이션"""
        oracle_cursor = self.oracle_conn.connection.cursor()
        oracle_cursor.arraysize = self.batch_size

        # SELECT 쿼리 생성
        columns_str = ', '.join(column_names)
        query = f"SELECT {columns_str} FROM {owner}.{table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"

        logger.debug(f"실행 쿼리: {query}")
        oracle_cursor.execute(query)

        # PostgreSQL COPY 준비
        pg_cursor = self.postgres_conn.connection.cursor()
        pg_table_name = table_name.lower()
        pg_columns_str = ', '.join([col.lower() for col in column_names])

        batch_count = 0
        while not self._cancelled:
            rows = oracle_cursor.fetchmany(self.batch_size)
            if not rows:
                break

            try:
                # COPY를 사용한 빠른 삽입
                self._copy_data(pg_cursor, pg_table_name, pg_columns_str, rows)

                self.progress.update(len(rows))
                batch_count += 1

                # 진행 상황 콜백
                if progress_callback:
                    progress_callback(self.progress)

                logger.debug(f"배치 {batch_count}: {len(rows):,}건 이관 완료")

            except Exception as e:
                logger.error(f"배치 {batch_count} 이관 실패: {str(e)}")
                self.progress.update(0, len(rows))
                self.progress.add_error(f"배치 {batch_count}: {str(e)}")

                # 실패한 경우 개별 행 단위로 재시도
                self._insert_rows_individually(pg_cursor, pg_table_name, column_names, rows)

        oracle_cursor.close()
        pg_cursor.close()

        if self._cancelled:
            logger.info("마이그레이션이 취소되었습니다")

    def _copy_data(self, cursor, table_name: str, columns: str, rows: List):
        """PostgreSQL COPY를 사용한 빠른 데이터 삽입"""
        # CSV 형식으로 데이터 준비
        output = io.StringIO()
        for row in rows:
            # NULL 처리 및 특수 문자 이스케이프
            formatted_row = []
            for value in row:
                if value is None:
                    formatted_row.append('\\N')
                elif isinstance(value, str):
                    # 탭, 줄바꿈, 백슬래시 이스케이프
                    value = value.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n').replace('\r', '\\r')
                    formatted_row.append(value)
                elif isinstance(value, datetime):
                    formatted_row.append(value.strftime('%Y-%m-%d %H:%M:%S'))
                else:
                    formatted_row.append(str(value))

            output.write('\t'.join(formatted_row) + '\n')

        output.seek(0)

        # COPY 실행
        copy_sql = f"COPY {table_name} ({columns}) FROM STDIN"
        cursor.copy_expert(copy_sql, output)
        cursor.connection.commit()

    def _insert_rows_individually(self, cursor, table_name: str,
                                  column_names: List[str], rows: List):
        """개별 행 단위로 삽입 (오류 발생 시 재시도용)"""
        columns_str = ', '.join([col.lower() for col in column_names])
        placeholders = ', '.join(['%s'] * len(column_names))
        insert_sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

        for row in rows:
            try:
                cursor.execute(insert_sql, row)
                cursor.connection.commit()
                self.progress.update(1)
            except Exception as e:
                logger.warning(f"행 삽입 실패: {str(e)[:100]}")
                self.progress.update(0, 1)
                self.progress.add_error(f"행 데이터: {str(row)[:100]}")
                cursor.connection.rollback()

    def migrate_with_date_range(self, owner: str, table_name: str,
                                date_column: str, start_date: str, end_date: str,
                                date_format: str = 'YYYY-MM-DD',
                                progress_callback: Optional[Callable] = None) -> MigrationProgress:
        """
        날짜 범위를 지정하여 데이터 마이그레이션

        Args:
            owner: Oracle 스키마 소유자
            table_name: 테이블 이름
            date_column: 날짜 컬럼명
            start_date: 시작 날짜
            end_date: 종료 날짜
            date_format: 날짜 형식
            progress_callback: 진행 상황 콜백

        Returns:
            MigrationProgress: 마이그레이션 결과
        """
        where_clause = f"{date_column} >= TO_DATE('{start_date}', '{date_format}') " \
                       f"AND {date_column} < TO_DATE('{end_date}', '{date_format}')"

        return self.migrate_table(owner, table_name, progress_callback, where_clause)

    def verify_migration(self, owner: str, table_name: str) -> Dict:
        """마이그레이션 결과 검증"""
        pg_table_name = table_name.lower()

        # 행 수 비교
        oracle_count = self._count_rows(owner, table_name)
        pg_count = self.postgres_conn.get_table_count(pg_table_name)

        verification = {
            'oracle_count': oracle_count,
            'postgres_count': pg_count,
            'match': oracle_count == pg_count,
            'difference': abs(oracle_count - pg_count)
        }

        logger.info(f"검증 결과: Oracle={oracle_count:,}, PostgreSQL={pg_count:,}, "
                    f"일치={'예' if verification['match'] else '아니오'}")

        return verification
