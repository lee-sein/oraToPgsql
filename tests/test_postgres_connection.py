#!/usr/bin/env python3
"""
PostgreSQL 연결 테스트 스크립트
"""

import sys
import os
import pytest

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.db_connection import PostgresConfig, PostgresConnection
from src.utils.config import ConfigManager
from src.utils.logger import setup_logger

logger = setup_logger()

# 설정 관리자 초기화
config_manager = ConfigManager()

# 프로파일 로드
test_profile = config_manager.load_profile('css_test')

@pytest.mark.skipif(not test_profile, reason="'test' 프로파일이 config/profiles.json에 없습니다.")
def test_postgres():
    """PostgreSQL 연결 테스트"""
    print("\n" + "=" * 60)
    print("PostgreSQL 연결 테스트")
    print("=" * 60)

    assert 'postgres' in test_profile, "설정에 'postgres' 섹션이 없습니다."
    pg_creds = test_profile['postgres']

    # 필수 설정 확인
    required_keys = ['host', 'port', 'user', 'password', 'database', 'schema']
    for key in required_keys:
        assert key in pg_creds and pg_creds[key] is not None, f"PostgreSQL 설정에 '{key}'가 필요합니다."

    config = PostgresConfig(
        host=pg_creds['host'],
        port=int(pg_creds['port']),
        database=pg_creds['database'],
        schema=pg_creds['schema'],
        user=pg_creds['user'],
        password=pg_creds['password']
    )

    try:
        print(f"연결 정보:")
        print(f"  Host: {config.host}:{config.port}")
        print(f"  Database: {config.database}")
        print(f"  Schema: {config.schema}")
        print(f"  User: {config.user}")

        conn = PostgresConnection(config)

        assert conn.test_connection(), "PostgreSQL 연결 실패"
        print("\n✓ PostgreSQL 연결 성공!")

        # 추가 정보 조회
        conn.connect()
        cursor = conn.connection.cursor()

        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"\nPostgreSQL 버전: {version[0]}")

        cursor.execute("SELECT current_database()")
        db_name = cursor.fetchone()
        print(f"현재 데이터베이스: {db_name[0]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")
        logger.error(f"PostgreSQL 연결 오류: {str(e)}")
        assert False, f"PostgreSQL 연결 오류: {e}"


if __name__ == '__main__':
    success = test_postgres()
    sys.exit(0 if success else 1)