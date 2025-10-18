#!/usr/bin/env python3
"""
빠른 마이그레이션 테스트 스크립트
GUI 없이 명령줄에서 전체 마이그레이션 프로세스를 테스트합니다.
"""

import sys
from src.core.db_connection import OracleConfig, PostgresConfig, OracleConnection, PostgresConnection
from src.core.ddl_converter import DDLConverter
from src.core.data_migrator import DataMigrator
from src.utils.logger import setup_logger

logger = setup_logger()


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("Oracle to PostgreSQL Migration - Quick Test")
    print("="*60)

    try:
        # 1. Oracle 연결
        print("\n[1/7] Oracle 연결 중...")
        oracle_config = OracleConfig(
            host="localhost",
            port=1521,
            service_name="XEPDB1",
            user="system",
            password="oracle",
            thick_mode=False  # Oracle 21c는 Thin 모드
        )
        oracle_conn = OracleConnection(oracle_config)
        oracle_conn.connect()
        print("✓ Oracle 연결 성공")

        # 2. PostgreSQL 연결
        print("\n[2/7] PostgreSQL 연결 중...")
        postgres_config = PostgresConfig(
            host="localhost",
            port=5432,
            database="postgres",
            schema="public",
            user="postgres",
            password="postgres"
        )
        postgres_conn = PostgresConnection(postgres_config)
        postgres_conn.connect()
        print("✓ PostgreSQL 연결 성공")

        # 3. 테이블 정보 조회
        print("\n[3/7] 테이블 메타데이터 조회 중...")
        owner = "SYSTEM"
        table_name = "EMPLOYEES"

        columns = oracle_conn.get_table_columns(owner, table_name)
        pk = oracle_conn.get_primary_key(owner, table_name)
        indexes = oracle_conn.get_indexes(owner, table_name)

        print(f"✓ 테이블 정보 조회 완료")
        print(f"  - 컬럼 수: {len(columns)}")
        print(f"  - Primary Key: {pk['columns'] if pk else 'None'}")
        print(f"  - 인덱스 수: {len(indexes)}")

        # 4. DDL 생성
        print("\n[4/7] PostgreSQL DDL 생성 중...")
        converter = DDLConverter()
        ddl = converter.generate_full_ddl(table_name, columns, pk, indexes)

        print("✓ DDL 생성 완료:")
        print("-" * 60)
        print(ddl)
        print("-" * 60)

        # 경고 확인
        warnings = converter.validate_conversion(columns)
        if warnings:
            print("\n⚠ 변환 경고:")
            for warning in warnings:
                print(f"  - {warning}")

        # 5. PostgreSQL에 테이블 생성
        print("\n[5/7] PostgreSQL에 테이블 생성 중...")
        pg_table_name = table_name.lower()

        if postgres_conn.table_exists(pg_table_name):
            print(f"  기존 테이블 삭제: {pg_table_name}")
            postgres_conn.drop_table(pg_table_name)

        postgres_conn.execute_ddl(ddl)
        print(f"✓ 테이블 생성 완료: {pg_table_name}")

        # 6. 데이터 마이그레이션
        print("\n[6/7] 데이터 마이그레이션 중...")
        migrator = DataMigrator(oracle_conn, postgres_conn, batch_size=1000)

        def progress_callback(progress):
            percentage = progress.get_progress_percentage()
            print(f"  진행률: {progress.migrated_rows:,}/{progress.total_rows:,} ({percentage:.1f}%)")

        result = migrator.migrate_table(owner, table_name, progress_callback=progress_callback)

        print(f"\n✓ 마이그레이션 완료!")
        print(f"  - 총 행 수: {result.total_rows:,}")
        print(f"  - 이관 완료: {result.migrated_rows:,}")
        print(f"  - 실패: {result.failed_rows:,}")
        print(f"  - 소요 시간: {result.get_elapsed_time():.2f}초")

        # 7. 검증
        print("\n[7/7] 마이그레이션 검증 중...")
        verification = migrator.verify_migration(owner, table_name)

        print(f"✓ 검증 완료:")
        print(f"  - Oracle 행 수: {verification['oracle_count']:,}")
        print(f"  - PostgreSQL 행 수: {verification['postgres_count']:,}")
        print(f"  - 일치 여부: {'✓ 일치' if verification['match'] else '✗ 불일치'}")

        if not verification['match']:
            print(f"  - 차이: {verification['difference']:,}행")

        # 연결 종료
        oracle_conn.close()
        postgres_conn.close()

        print("\n" + "="*60)
        print("테스트 완료!")
        print("="*60)

        return True

    except Exception as e:
        print(f"\n✗ 오류 발생: {str(e)}")
        logger.error(f"테스트 오류: {str(e)}", exc_info=True)
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
