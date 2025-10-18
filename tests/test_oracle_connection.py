#!/usr/bin/env python3
"""
Oracle 연결 테스트 스크립트
"""

import sys
import os
import pytest

# 프로젝트 루트를 path에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.db_connection import OracleConfig, OracleConnection
from src.utils.config import ConfigManager
from src.utils.logger import setup_logger

logger = setup_logger()

# 설정 관리자 초기화
config_manager = ConfigManager()

# 프로파일 로드
test_profile = config_manager.load_profile('css_test')

@pytest.mark.skipif(not test_profile, reason="'test' 프로파일이 config/profiles.json에 없습니다.")
def test_oracle_11g():
    """Oracle 11g 연결 테스트 (Thick 모드)"""
    print("\n" + "=" * 60)
    print("Oracle 11g 연결 테스트 (Thick Mode)")
    print("=" * 60)

    assert 'oracle' in test_profile, "설정에 'oracle' 섹션이 없습니다."
    oracle_creds = test_profile['oracle']

    # 필수 설정 확인
    required_keys = ['host', 'port', 'user', 'password', 'sid', 'thick_mode', 'instant_client_dir']
    for key in required_keys:
        assert key in oracle_creds and oracle_creds[key] is not None, f"Oracle 설정에 '{key}'가 필요합니다."

    # instant_client_dir이 플레이스홀더인지 확인
    if oracle_creds['instant_client_dir'] == "C:\\path\\to\\your\\instantclient_11_2":
        pytest.skip("Oracle Instant Client 경로가 설정되지 않았습니다. config/profiles.json을 수정하세요.")

    config = OracleConfig(
        host=oracle_creds['host'],
        port=int(oracle_creds['port']),
        sid=oracle_creds['sid'],
        user=oracle_creds['user'],
        password=oracle_creds['password'],
        thick_mode=oracle_creds['thick_mode'],
        instant_client_dir=oracle_creds['instant_client_dir']
    )

    try:
        print(f"연결 정보:")
        print(f"  Host: {config.host}:{config.port}")
        print(f"  SID: {config.sid}")
        print(f"  User: {config.user}")
        print(f"  Thick Mode: {config.thick_mode}")
        print(f"  Instant Client: {config.instant_client_dir}")

        conn = OracleConnection(config)

        assert conn.test_connection(), "Oracle 11g 연결 실패"
        print("\n✓ Oracle 11g 연결 성공!")

        # 추가 정보 조회
        conn.connect()
        cursor = conn.connection.cursor()

        cursor.execute("SELECT * FROM v$version WHERE ROWNUM = 1")
        version = cursor.fetchone()
        print(f"\nOracle 버전: {version[0]}")

        cursor.execute("SELECT SYS_CONTEXT('USERENV', 'DB_NAME') FROM DUAL")
        db_name = cursor.fetchone()
        print(f"데이터베이스: {db_name[0]}")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")
        logger.error(f"Oracle 11g 연결 오류: {str(e)}")
        assert False, f"Oracle 11g 연결 오류: {e}"

@pytest.mark.skip(reason="사용자 요청에 따라 Oracle 11g에 집중하기 위해 21c 테스트는 건너뜁니다.")
def test_oracle_21c():
    """Oracle 21c 연결 테스트 (건너뜀)"""
    pass