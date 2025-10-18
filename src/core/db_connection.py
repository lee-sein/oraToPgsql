"""
데이터베이스 연결 관리 모듈
Oracle과 PostgreSQL 연결을 관리합니다.
"""

import os
import sys

try:
    import oracledb
except ImportError:
    import oracledb as oracledb  # fallback
import psycopg2
from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class OracleConfig:
    """Oracle 연결 설정"""
    host: str
    port: int = 1521
    service_name: Optional[str] = None
    sid: Optional[str] = None
    user: str = ""
    password: str = ""
    thick_mode: bool = False  # Oracle 11g는 True 필요
    instant_client_dir: Optional[str] = None


@dataclass
class PostgresConfig:
    """PostgreSQL 연결 설정"""
    host: str
    database: str
    user: str
    password: str
    port: int = 5432
    schema: str = "public"


class OracleConnection:
    """Oracle 데이터베이스 연결 클래스"""

    def __init__(self, config: OracleConfig):
        self.config = config
        self.connection = None

    def connect(self) -> oracledb.Connection:
        """Oracle 데이터베이스에 연결"""
        try:
            logger.info("=" * 80)
            logger.info("🔌 Oracle 연결 시도 시작")
            logger.info("=" * 80)

            # Thick 모드 초기화 (Oracle 11g용)
            if self.config.thick_mode:
                logger.info("🔧 Thick 모드 활성화 (Oracle 11g 폐쇄망 지원)")

                if not self.config.instant_client_dir:
                    raise ValueError("❌ Thick 모드에는 Instant Client 디렉토리가 필요합니다")

                client_dir = self.config.instant_client_dir

                # 실행 파일(frozen) 환경인지 확인하고, 상대 경로인 경우 절대 경로로 변환
                if not os.path.isabs(client_dir):
                    if getattr(sys, 'frozen', False):
                        # PyInstaller와 같은 번들러로 실행된 경우
                        base_path = os.path.dirname(sys.executable)
                    else:
                        # 일반 Python 스크립트로 실행된 경우
                        base_path = os.path.abspath(".")
                    
                    client_dir = os.path.join(base_path, client_dir)
                    logger.info(f"🌍 상대 경로를 절대 경로로 변환: {client_dir}")

                logger.info(f"📁 Instant Client 최종 경로: {client_dir}")

                try:
                    oracledb.init_oracle_client(lib_dir=client_dir)
                    logger.info("✅ Thick 모드 초기화 성공!")

                    try:
                        client_version = oracledb.clientversion()
                        logger.info(f"   → Oracle Client 버전: {client_version[0]}.{client_version[1]}.{client_version[2]}.{client_version[3]}.{client_version[4]}")
                    except Exception as ve:
                        logger.warning(f"   ⚠ Client 버전 확인 실패: {str(ve)}")

                except Exception as e:
                    error_msg = str(e).lower()
                    if "already been initialized" in error_msg or "already initialized" in error_msg:
                        logger.info("✅ Thick 모드 이미 초기화됨 (정상)")
                        try:
                            client_version = oracledb.clientversion()
                            logger.info(f"   → Oracle Client 버전: {client_version[0]}.{client_version[1]}.{client_version[2]}.{client_version[3]}.{client_version[4]}")
                        except:
                            pass
                    else:
                        logger.error(f"❌ Thick 모드 초기화 실패: {str(e)}")
                        logger.error("💡 해결 방법:")
                        logger.error("   1. Instant Client가 올바르게 설치되었는지 확인")
                        logger.error("   2. 경로에 공백이나 특수문자가 없는지 확인")
                        logger.error("   3. Oracle 11g와 호환되는 Instant Client 버전 사용")
                        raise
            else:
                logger.info("⚡ Thin 모드 (Oracle 12.1+ 지원)")
                logger.info("   → Instant Client 불필요")
                logger.info("   ⚠ Oracle 11g는 Thick 모드를 사용하세요!")

            # DSN 생성
            logger.info("\n📋 연결 정보:")
            logger.info(f"   - Host: {self.config.host}")
            logger.info(f"   - Port: {self.config.port}")

            if self.config.service_name:
                logger.info(f"   - Service Name: {self.config.service_name}")
                dsn = oracledb.makedsn(
                    self.config.host,
                    self.config.port,
                    service_name=self.config.service_name
                )
            else:
                logger.info(f"   - SID: {self.config.sid}")
                dsn = oracledb.makedsn(
                    self.config.host,
                    self.config.port,
                    sid=self.config.sid
                )

            logger.info(f"   - User: {self.config.user}")
            logger.info(f"   - DSN: {dsn}")
            logger.info(f"   - 모드: {'Thick (Oracle 11g 호환)' if self.config.thick_mode else 'Thin (Oracle 12.1+)'}")

            logger.info("\n🔌 데이터베이스 연결 시도 중...")

            # 연결
            self.connection = oracledb.connect(
                user=self.config.user,
                password=self.config.password,
                dsn=dsn
            )

            # 연결 성공 - 데이터베이스 정보 조회
            logger.info("\n" + "=" * 80)
            logger.info("✅ Oracle 연결 성공!")
            logger.info("=" * 80)

            try:
                cursor = self.connection.cursor()

                # Oracle 버전 확인
                cursor.execute("SELECT BANNER FROM v$version WHERE ROWNUM = 1")
                version = cursor.fetchone()[0]
                logger.info(f"📊 Oracle 버전: {version}")

                # DB 이름 확인
                cursor.execute("SELECT SYS_CONTEXT('USERENV', 'DB_NAME') FROM DUAL")
                db_name = cursor.fetchone()[0]
                logger.info(f"📊 DB 이름: {db_name}")

                # 인스턴스 이름
                cursor.execute("SELECT SYS_CONTEXT('USERENV', 'INSTANCE_NAME') FROM DUAL")
                instance_name = cursor.fetchone()[0]
                logger.info(f"📊 인스턴스: {instance_name}")

                # 현재 스키마
                cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
                current_schema = cursor.fetchone()[0]
                logger.info(f"📊 현재 스키마: {current_schema}")

                cursor.close()

            except Exception as info_err:
                logger.warning(f"⚠ DB 정보 조회 중 경고: {str(info_err)}")

            logger.info(f"\n✅ 연결 주소: {self.config.host}:{self.config.port}")
            logger.info(f"✅ 사용자: {self.config.user}")
            logger.info(f"✅ 모드: {'Thick (Oracle 11g 폐쇄망 지원 ✓)' if self.config.thick_mode else 'Thin'}")
            logger.info("=" * 80 + "\n")

            return self.connection

        except Exception as e:
            logger.error("\n" + "=" * 80)
            logger.error("❌ Oracle 연결 실패!")
            logger.error("=" * 80)
            logger.error(f"❌ 오류 메시지: {str(e)}")
            logger.error(f"❌ 오류 타입: {type(e).__name__}")

            if self.config.thick_mode:
                logger.error("\n🔍 Thick 모드 (Oracle 11g 폐쇄망) 체크리스트:")
                logger.error("   1. ✓ Instant Client가 올바르게 설치되었나요?")
                logger.error(f"      경로: {self.config.instant_client_dir}")
                logger.error("   2. ✓ Instant Client 버전이 Oracle 11g와 호환되나요?")
                logger.error("      권장: Oracle Instant Client 11.2 또는 12.1")
                logger.error("   3. ✓ 환경변수가 설정되었나요?")
                logger.error("      Linux: LD_LIBRARY_PATH")
                logger.error("      macOS: DYLD_LIBRARY_PATH")
                logger.error("      Windows: PATH")

            logger.error("\n🔍 네트워크 및 연결 정보 체크리스트:")
            logger.error(f"   1. ✓ 호스트 접근 가능: {self.config.host}:{self.config.port}")
            logger.error(f"      (ping {self.config.host} 테스트)")
            logger.error(f"   2. ✓ Oracle Listener 실행 중")
            logger.error(f"      (lsnrctl status 확인)")
            logger.error(f"   3. ✓ Service Name/SID 정확: {self.config.service_name or self.config.sid}")
            logger.error(f"   4. ✓ 사용자 권한 확인: {self.config.user}")
            logger.error("   5. ✓ 방화벽 설정 확인 (폐쇄망)")
            logger.error("=" * 80 + "\n")
            raise

    def test_connection(self) -> bool:
        """연결 테스트"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM DUAL")
            cursor.close()
            self.close()
            return True
        except Exception as e:
            logger.error(f"Oracle 연결 테스트 실패: {str(e)}")
            return False

    def get_tables(self, owner: str) -> list:
        """스키마의 테이블 목록 조회"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        query = """
            SELECT table_name, num_rows,
                   (SELECT comments FROM all_tab_comments
                    WHERE table_name = t.table_name AND owner = t.owner) as comments
            FROM all_tables t
            WHERE owner = :owner
            ORDER BY table_name
        """
        cursor.execute(query, {"owner": owner.upper()})
        tables = cursor.fetchall()
        cursor.close()

        return [{"name": t[0], "rows": t[1], "comment": t[2]} for t in tables]

    def get_table_columns(self, owner: str, table_name: str) -> list:
        """테이블 컬럼 정보 조회"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        query = """
            SELECT column_name, data_type, data_length, data_precision,
                   data_scale, nullable, data_default
            FROM all_tab_columns
            WHERE owner = :owner AND table_name = :table_name
            ORDER BY column_id
        """
        cursor.execute(query, {"owner": owner.upper(), "table_name": table_name.upper()})
        columns = cursor.fetchall()
        cursor.close()

        return [{
            "name": c[0],
            "data_type": c[1],
            "length": c[2],
            "precision": c[3],
            "scale": c[4],
            "nullable": c[5] == 'Y',
            "default": c[6]
        } for c in columns]

    def get_primary_key(self, owner: str, table_name: str) -> Optional[Dict]:
        """Primary Key 정보 조회"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        query = """
            SELECT c.constraint_name,
                   LISTAGG(cc.column_name, ', ') WITHIN GROUP (ORDER BY cc.position) as columns
            FROM all_constraints c
            JOIN all_cons_columns cc ON c.constraint_name = cc.constraint_name
                                      AND c.owner = cc.owner
            WHERE c.owner = :owner
              AND c.table_name = :table_name
              AND c.constraint_type = 'P'
            GROUP BY c.constraint_name
        """
        cursor.execute(query, {"owner": owner.upper(), "table_name": table_name.upper()})
        result = cursor.fetchone()
        cursor.close()

        if result:
            return {"name": result[0], "columns": result[1].split(', ')}
        return None

    def get_indexes(self, owner: str, table_name: str) -> list:
        """인덱스 정보 조회"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        query = """
            SELECT i.index_name, i.uniqueness,
                   LISTAGG(ic.column_name, ', ') WITHIN GROUP (ORDER BY ic.column_position) as columns
            FROM all_indexes i
            JOIN all_ind_columns ic ON i.index_name = ic.index_name AND i.owner = ic.index_owner
            WHERE i.owner = :owner AND i.table_name = :table_name
            GROUP BY i.index_name, i.uniqueness
            ORDER BY i.index_name
        """
        cursor.execute(query, {"owner": owner.upper(), "table_name": table_name.upper()})
        indexes = cursor.fetchall()
        cursor.close()

        return [{
            "name": idx[0],
            "unique": idx[1] == 'UNIQUE',
            "columns": idx[2].split(', ')
        } for idx in indexes]

    def close(self):
        """연결 종료"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Oracle 연결 종료")


class PostgresConnection:
    """PostgreSQL 데이터베이스 연결 클래스"""

    def __init__(self, config: PostgresConfig):
        self.config = config
        self.connection = None

    def connect(self) -> psycopg2.extensions.connection:
        """PostgreSQL 데이터베이스에 연결"""
        try:
            self.connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password
            )

            # 스키마 설정
            cursor = self.connection.cursor()
            cursor.execute(f"SET search_path TO {self.config.schema}")
            cursor.close()

            logger.info(f"PostgreSQL 연결 성공: {self.config.host}:{self.config.port}/{self.config.database}")
            return self.connection

        except Exception as e:
            logger.error(f"PostgreSQL 연결 실패: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """연결 테스트"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            self.close()
            return True
        except Exception as e:
            logger.error(f"PostgreSQL 연결 테스트 실패: {str(e)}")
            return False

    def table_exists(self, table_name: str) -> bool:
        """테이블 존재 여부 확인"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
            )
        """, (self.config.schema, table_name.lower()))

        exists = cursor.fetchone()[0]
        cursor.close()
        return exists

    def drop_table(self, table_name: str):
        """테이블 삭제"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
        self.connection.commit()
        cursor.close()
        logger.info(f"테이블 삭제: {table_name}")

    def execute_ddl(self, ddl: str):
        """DDL 실행"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute(ddl)
        self.connection.commit()
        cursor.close()
        logger.info("DDL 실행 완료")

    def get_table_count(self, table_name: str) -> int:
        """테이블 행 수 조회"""
        if not self.connection:
            self.connect()

        cursor = self.connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def close(self):
        """연결 종료"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("PostgreSQL 연결 종료")
