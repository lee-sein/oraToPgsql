"""
실시간 동기화 관리 모듈
Oracle과 PostgreSQL 간의 지속적인 데이터 동기화를 관리합니다.
"""

import logging
import time
from datetime import datetime
from typing import Optional, Callable, List, Dict
from enum import Enum
import threading

logger = logging.getLogger(__name__)


class SyncMode(Enum):
    """동기화 모드"""
    FULL = "full"  # 전체 동기화
    INCREMENTAL = "incremental"  # 증분 동기화 (변경된 데이터만)
    DELETE_INSERT = "delete_insert"  # 삭제 후 재삽입


class SyncStrategy(Enum):
    """동기화 전략"""
    TIMESTAMP = "timestamp"  # 타임스탬프 기반
    PRIMARY_KEY = "primary_key"  # Primary Key 비교
    HASH = "hash"  # 해시 비교


class SyncStatus:
    """동기화 상태"""
    def __init__(self):
        self.is_running = False
        self.last_sync_time = None
        self.next_sync_time = None
        self.total_syncs = 0
        self.successful_syncs = 0
        self.failed_syncs = 0
        self.last_error = None
        self.current_table = None

    def to_dict(self) -> Dict:
        return {
            'is_running': self.is_running,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'next_sync_time': self.next_sync_time.isoformat() if self.next_sync_time else None,
            'total_syncs': self.total_syncs,
            'successful_syncs': self.successful_syncs,
            'failed_syncs': self.failed_syncs,
            'success_rate': (self.successful_syncs / self.total_syncs * 100) if self.total_syncs > 0 else 0,
            'last_error': self.last_error,
            'current_table': self.current_table
        }


class SyncManager:
    """실시간 동기화 관리자"""

    def __init__(self, oracle_conn, postgres_conn):
        """
        Args:
            oracle_conn: OracleConnection 인스턴스
            postgres_conn: PostgresConnection 인스턴스
        """
        self.oracle_conn = oracle_conn
        self.postgres_conn = postgres_conn
        self.status = SyncStatus()
        self._stop_event = threading.Event()
        self._sync_thread = None

    def start_sync(self, owner: str, table_name: str,
                   interval_minutes: int = 10,
                   sync_mode: SyncMode = SyncMode.INCREMENTAL,
                   timestamp_column: Optional[str] = None,
                   callback: Optional[Callable] = None):
        """
        동기화 시작

        Args:
            owner: Oracle 스키마 소유자
            table_name: 테이블 이름
            interval_minutes: 동기화 간격 (분)
            sync_mode: 동기화 모드
            timestamp_column: 증분 동기화용 타임스탬프 컬럼명
            callback: 동기화 완료 시 호출될 콜백 함수
        """
        if self.status.is_running:
            logger.warning("동기화가 이미 실행 중입니다")
            return

        self._stop_event.clear()
        self.status.is_running = True
        self.status.current_table = table_name

        # 동기화 스레드 시작
        self._sync_thread = threading.Thread(
            target=self._sync_loop,
            args=(owner, table_name, interval_minutes, sync_mode, timestamp_column, callback),
            daemon=True
        )
        self._sync_thread.start()

        logger.info(f"동기화 시작: {table_name}, 간격: {interval_minutes}분")

    def stop_sync(self):
        """동기화 중지"""
        if not self.status.is_running:
            logger.warning("동기화가 실행 중이 아닙니다")
            return

        self._stop_event.set()
        if self._sync_thread:
            self._sync_thread.join(timeout=5)

        self.status.is_running = False
        self.status.current_table = None
        logger.info("동기화 중지됨")

    def _sync_loop(self, owner: str, table_name: str, interval_minutes: int,
                   sync_mode: SyncMode, timestamp_column: Optional[str],
                   callback: Optional[Callable]):
        """동기화 루프"""
        interval_seconds = interval_minutes * 60

        while not self._stop_event.is_set():
            try:
                # 다음 동기화 시간 설정
                self.status.next_sync_time = datetime.now()

                # 동기화 실행
                logger.info(f"동기화 시작: {table_name}")
                sync_result = self._perform_sync(
                    owner, table_name, sync_mode, timestamp_column
                )

                # 상태 업데이트
                self.status.last_sync_time = datetime.now()
                self.status.total_syncs += 1

                if sync_result['success']:
                    self.status.successful_syncs += 1
                    logger.info(f"동기화 성공: {sync_result['rows_affected']}행 처리")
                else:
                    self.status.failed_syncs += 1
                    self.status.last_error = sync_result.get('error')
                    logger.error(f"동기화 실패: {self.status.last_error}")

                # 콜백 호출
                if callback:
                    callback(self.status, sync_result)

                # 대기
                if not self._stop_event.wait(timeout=interval_seconds):
                    continue  # 정상 대기 후 계속
                else:
                    break  # 중지 요청

            except Exception as e:
                logger.error(f"동기화 루프 오류: {str(e)}", exc_info=True)
                self.status.failed_syncs += 1
                self.status.last_error = str(e)

                # 오류 발생 시 짧은 대기 후 재시도
                if not self._stop_event.wait(timeout=60):
                    continue
                else:
                    break

        logger.info("동기화 루프 종료")

    def _perform_sync(self, owner: str, table_name: str,
                      sync_mode: SyncMode, timestamp_column: Optional[str]) -> Dict:
        """동기화 수행"""
        try:
            if sync_mode == SyncMode.FULL:
                return self._full_sync(owner, table_name)
            elif sync_mode == SyncMode.INCREMENTAL:
                return self._incremental_sync(owner, table_name, timestamp_column)
            elif sync_mode == SyncMode.DELETE_INSERT:
                return self._delete_insert_sync(owner, table_name)
            else:
                raise ValueError(f"지원하지 않는 동기화 모드: {sync_mode}")

        except Exception as e:
            logger.error(f"동기화 수행 오류: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _full_sync(self, owner: str, table_name: str) -> Dict:
        """전체 동기화"""
        logger.info("전체 동기화 시작")

        # Oracle에서 전체 데이터 조회
        oracle_cursor = self.oracle_conn.connection.cursor()
        columns = self.oracle_conn.get_table_columns(owner, table_name)
        column_names = [col['name'] for col in columns]
        columns_str = ', '.join(column_names)

        query = f"SELECT {columns_str} FROM {owner}.{table_name}"
        oracle_cursor.execute(query)

        # PostgreSQL 테이블 비우기
        pg_table = table_name.lower()
        pg_cursor = self.postgres_conn.connection.cursor()
        pg_cursor.execute(f"TRUNCATE TABLE {pg_table}")
        self.postgres_conn.connection.commit()

        # 데이터 삽입
        rows_affected = 0
        batch_size = 1000

        while True:
            rows = oracle_cursor.fetchmany(batch_size)
            if not rows:
                break

            # PostgreSQL에 삽입
            pg_columns = ', '.join([col.lower() for col in column_names])
            placeholders = ', '.join(['%s'] * len(column_names))
            insert_sql = f"INSERT INTO {pg_table} ({pg_columns}) VALUES ({placeholders})"

            pg_cursor.executemany(insert_sql, rows)
            self.postgres_conn.connection.commit()

            rows_affected += len(rows)

        oracle_cursor.close()
        pg_cursor.close()

        logger.info(f"전체 동기화 완료: {rows_affected}행")
        return {'success': True, 'rows_affected': rows_affected, 'mode': 'full'}

    def _incremental_sync(self, owner: str, table_name: str,
                          timestamp_column: Optional[str]) -> Dict:
        """증분 동기화 (타임스탬프 기반)"""
        if not timestamp_column:
            logger.warning("타임스탬프 컬럼이 지정되지 않아 전체 동기화로 전환")
            return self._full_sync(owner, table_name)

        logger.info(f"증분 동기화 시작 (컬럼: {timestamp_column})")

        # PostgreSQL에서 마지막 동기화 시간 조회
        pg_table = table_name.lower()
        pg_cursor = self.postgres_conn.connection.cursor()

        try:
            pg_cursor.execute(f"SELECT MAX({timestamp_column.lower()}) FROM {pg_table}")
            last_sync = pg_cursor.fetchone()[0]
        except:
            last_sync = None

        if not last_sync:
            logger.info("마지막 동기화 시간이 없어 전체 동기화 수행")
            return self._full_sync(owner, table_name)

        # Oracle에서 변경된 데이터 조회
        oracle_cursor = self.oracle_conn.connection.cursor()
        columns = self.oracle_conn.get_table_columns(owner, table_name)
        column_names = [col['name'] for col in columns]
        columns_str = ', '.join(column_names)

        # 타임스탬프 컬럼 타입 확인 (VARCHAR2 vs DATE/TIMESTAMP)
        timestamp_col_info = next((col for col in columns if col['name'].upper() == timestamp_column.upper()), None)
        is_varchar_timestamp = timestamp_col_info and 'VARCHAR' in timestamp_col_info['data_type'].upper()

        # 쿼리 생성 - VARCHAR2는 문자열 비교, DATE/TIMESTAMP는 날짜 비교
        if is_varchar_timestamp:
            # VARCHAR2 컬럼: 문자열 비교
            # 형식: 'YYYY-MM-DD HH:MI:SS', 'YYYY-MM-DD HH:MI:SS 밀리초', 'YYYY-MM-DD' 등
            # 그대로 문자열 비교하면 됨 (사전순 = 날짜순)
            query = f"""
                SELECT {columns_str}
                FROM {owner}.{table_name}
                WHERE {timestamp_column} > '{last_sync}'
                ORDER BY {timestamp_column}
            """
            oracle_cursor.execute(query)
        else:
            # DATE/TIMESTAMP 컬럼: 바인드 변수 사용
            query = f"""
                SELECT {columns_str}
                FROM {owner}.{table_name}
                WHERE {timestamp_column} > :last_sync
                ORDER BY {timestamp_column}
            """
            oracle_cursor.execute(query, {'last_sync': last_sync})

        # PostgreSQL에 UPSERT (INSERT ... ON CONFLICT UPDATE)
        pk = self.oracle_conn.get_primary_key(owner, table_name)
        if not pk:
            logger.warning("Primary Key가 없어 INSERT만 수행")
            rows_affected = self._insert_new_rows(oracle_cursor, pg_table, column_names)
            oracle_cursor.close()
            pg_cursor.close()
            logger.info(f"증분 동기화 완료: {rows_affected}행")
            return {'success': True, 'rows_affected': rows_affected, 'mode': 'incremental'}

        rows_affected = self._upsert_rows(oracle_cursor, pg_table, column_names, pk['columns'])

        oracle_cursor.close()
        pg_cursor.close()

        logger.info(f"증분 동기화 완료: {rows_affected}행")
        return {'success': True, 'rows_affected': rows_affected, 'mode': 'incremental'}

    def _delete_insert_sync(self, owner: str, table_name: str) -> Dict:
        """삭제 후 재삽입 동기화"""
        logger.info("DELETE-INSERT 동기화 시작")

        # PostgreSQL 테이블 삭제
        pg_table = table_name.lower()
        self.postgres_conn.drop_table(pg_table)

        # DDL 재생성
        from src.core.ddl_converter import DDLConverter

        columns = self.oracle_conn.get_table_columns(owner, table_name)
        pk = self.oracle_conn.get_primary_key(owner, table_name)
        indexes = self.oracle_conn.get_indexes(owner, table_name)

        converter = DDLConverter()
        ddl = converter.generate_full_ddl(table_name, columns, pk, indexes)

        self.postgres_conn.execute_ddl(ddl)

        # 전체 데이터 재삽입
        return self._full_sync(owner, table_name)

    def _upsert_rows(self, oracle_cursor, pg_table: str,
                     column_names: List[str], pk_columns: List[str]) -> int:
        """UPSERT 수행"""
        pg_cursor = self.postgres_conn.connection.cursor()
        rows_affected = 0
        batch_size = 1000

        pg_columns = ', '.join([col.lower() for col in column_names])
        pk_columns_lower = [col.lower() for col in pk_columns]
        pk_constraint = ', '.join(pk_columns_lower)

        # UPDATE 절 생성
        update_cols = [col.lower() for col in column_names if col.lower() not in pk_columns_lower]
        update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_cols])

        while True:
            rows = oracle_cursor.fetchmany(batch_size)
            if not rows:
                break

            for row in rows:
                placeholders = ', '.join(['%s'] * len(column_names))
                upsert_sql = f"""
                    INSERT INTO {pg_table} ({pg_columns})
                    VALUES ({placeholders})
                    ON CONFLICT ({pk_constraint})
                    DO UPDATE SET {update_clause}
                """

                try:
                    pg_cursor.execute(upsert_sql, row)
                    rows_affected += 1
                except Exception as e:
                    logger.warning(f"UPSERT 실패: {str(e)[:100]}")

            self.postgres_conn.connection.commit()

        pg_cursor.close()
        return rows_affected

    def _insert_new_rows(self, oracle_cursor, pg_table: str,
                         column_names: List[str]) -> int:
        """새 행 삽입"""
        pg_cursor = self.postgres_conn.connection.cursor()
        rows_affected = 0
        batch_size = 1000

        pg_columns = ', '.join([col.lower() for col in column_names])
        placeholders = ', '.join(['%s'] * len(column_names))
        insert_sql = f"INSERT INTO {pg_table} ({pg_columns}) VALUES ({placeholders})"

        while True:
            rows = oracle_cursor.fetchmany(batch_size)
            if not rows:
                break

            pg_cursor.executemany(insert_sql, rows)
            self.postgres_conn.connection.commit()
            rows_affected += len(rows)

        pg_cursor.close()
        return rows_affected

    def check_sync_gap(self, owner: str, table_name: str, timestamp_column: str) -> Dict:
        """
        동기화 간격 확인

        Returns:
            {
                'has_gap': bool,
                'pg_last_time': datetime or str,
                'missing_count': int,
                'is_varchar': bool
            }
        """
        try:
            # PostgreSQL에서 마지막 타임스탬프 조회
            pg_table = table_name.lower()
            pg_cursor = self.postgres_conn.connection.cursor()

            try:
                pg_cursor.execute(f"SELECT MAX({timestamp_column.lower()}) FROM {pg_table}")
                pg_last_time = pg_cursor.fetchone()[0]
            except:
                pg_last_time = None
            finally:
                pg_cursor.close()

            if not pg_last_time:
                return {'has_gap': False, 'pg_last_time': None, 'missing_count': 0, 'is_varchar': False}

            # Oracle에서 컬럼 타입 확인
            columns = self.oracle_conn.get_table_columns(owner, table_name)
            timestamp_col_info = next((col for col in columns if col['name'].upper() == timestamp_column.upper()), None)
            is_varchar = timestamp_col_info and 'VARCHAR' in timestamp_col_info['data_type'].upper()

            # Oracle에서 누락 데이터 수 확인
            oracle_cursor = self.oracle_conn.connection.cursor()

            if is_varchar:
                # VARCHAR2: 문자열 비교 (그대로 사용)
                count_query = f"""
                    SELECT COUNT(*)
                    FROM {owner}.{table_name}
                    WHERE {timestamp_column} > '{pg_last_time}'
                """
                oracle_cursor.execute(count_query)
            else:
                # DATE/TIMESTAMP: 바인드 변수 사용
                count_query = f"""
                    SELECT COUNT(*)
                    FROM {owner}.{table_name}
                    WHERE {timestamp_column} > :pg_last_time
                """
                oracle_cursor.execute(count_query, {'pg_last_time': pg_last_time})

            missing_count = oracle_cursor.fetchone()[0]
            oracle_cursor.close()

            return {
                'has_gap': missing_count > 0,
                'pg_last_time': pg_last_time,
                'missing_count': missing_count,
                'is_varchar': is_varchar
            }

        except Exception as e:
            logger.error(f"간격 확인 오류: {str(e)}")
            return {'has_gap': False, 'pg_last_time': None, 'missing_count': 0, 'error': str(e), 'is_varchar': False}

    def get_status(self) -> Dict:
        """현재 상태 조회"""
        return self.status.to_dict()


class MultiTableSyncManager:
    """다중 테이블 동기화 관리자"""

    def __init__(self, oracle_conn, postgres_conn):
        self.oracle_conn = oracle_conn
        self.postgres_conn = postgres_conn
        self.sync_managers: Dict[str, SyncManager] = {}

    def add_table(self, owner: str, table_name: str, interval_minutes: int,
                  sync_mode: SyncMode = SyncMode.INCREMENTAL,
                  timestamp_column: Optional[str] = None,
                  callback: Optional[Callable] = None):
        """동기화할 테이블 추가"""
        key = f"{owner}.{table_name}"

        if key in self.sync_managers:
            logger.warning(f"이미 등록된 테이블: {key}")
            return

        sync_manager = SyncManager(self.oracle_conn, self.postgres_conn)
        sync_manager.start_sync(
            owner, table_name, interval_minutes, sync_mode, timestamp_column, callback
        )

        self.sync_managers[key] = sync_manager
        logger.info(f"테이블 동기화 추가: {key}")

    def remove_table(self, owner: str, table_name: str):
        """동기화 테이블 제거"""
        key = f"{owner}.{table_name}"

        if key not in self.sync_managers:
            logger.warning(f"등록되지 않은 테이블: {key}")
            return

        self.sync_managers[key].stop_sync()
        del self.sync_managers[key]
        logger.info(f"테이블 동기화 제거: {key}")

    def stop_all(self):
        """모든 동기화 중지"""
        for key, manager in self.sync_managers.items():
            manager.stop_sync()
            logger.info(f"동기화 중지: {key}")

        self.sync_managers.clear()

    def get_all_status(self) -> Dict[str, Dict]:
        """모든 테이블의 상태 조회"""
        return {key: manager.get_status() for key, manager in self.sync_managers.items()}
