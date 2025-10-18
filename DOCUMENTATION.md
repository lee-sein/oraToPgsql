# Project Documentation

This file is a consolidation of all the markdown documentation files in the project.

---
---

# `PROJECT_SUMMARY.md`

# Oracle to PostgreSQL Migration & Sync Tool - 프로젝트 요약

## 개요

Oracle 데이터베이스에서 PostgreSQL로 테이블을 마이그레이션하고, **실시간 동기화**를 수행하는 Python GUI 애플리케이션입니다.

**핵심 기능:**
- ✅ 일회성 테이블 마이그레이션 (DDL + 데이터)
- ✅ **실시간 자동 동기화** (10분, 30분, 1시간 등 간격 선택)
- ✅ Oracle 11g (Thick 모드) 및 21c (Thin 모드) 지원
- ✅ 폐쇄망 환경 지원

---

## 주요 기능

### 1. 데이터베이스 연결 관리
- Oracle 11g/21c 연결 (Thin/Thick 모드 자동 지원)
- PostgreSQL 연결
- 연결 프로파일 저장/로드 (암호화)
- 연결 테스트 기능

### 2. 테이블 마이그레이션
- Oracle 스키마 테이블 목록 조회
- DDL 자동 변환 (Oracle → PostgreSQL)
- 데이터 타입 매핑 (NUMBER, VARCHAR2, DATE 등)
- Primary Key, Index 자동 변환
- 배치 처리 (대용량 데이터 지원)
- 실시간 진행률 표시

### 3. **실시간 동기화** (핵심 기능)
- **자동 주기 실행**: 10분/30분/1시간/2시간/6시간/12시간/24시간
- **3가지 동기화 모드**:
  - **증분 동기화 (Incremental)**: 타임스탬프 기반으로 변경된 데이터만 동기화
  - **전체 동기화 (Full)**: 테이블 전체를 매번 동기화
  - **DELETE & INSERT**: 기존 테이블 삭제 후 재생성 및 전체 데이터 삽입
- **동기화 상태 모니터링**:
  - 현재 상태, 다음 동기화 시간, 성공/실패 통계
  - 동기화 히스토리 테이블
- **백그라운드 실행**: GUI를 사용하면서 백그라운드에서 자동 동기화

### 4. 보안
- 비밀번호 암호화 저장 (cryptography.Fernet)
- 프로파일 파일 암호화
- 로그에 민감 정보 노출 금지

---

## 프로젝트 구조

```
oraToPgsql/
├── src/
│   ├── core/                      # 핵심 비즈니스 로직
│   │   ├── db_connection.py       # DB 연결 (Oracle, PostgreSQL)
│   │   ├── ddl_converter.py       # DDL 변환
│   │   ├── data_migrator.py       # 데이터 마이그레이션
│   │   └── sync_manager.py        # 실시간 동기화 관리 ⭐
│   ├── gui/                       # PyQt5 GUI
│   │   └── main_window.py         # 메인 윈도우
│   ├── utils/                     # 유틸리티
│   │   ├── logger.py              # 로깅
│   │   └── config.py              # 설정 관리
│   └── main.py                    # 메인 진입점
│
├── tests/                         # 테스트 스크립트
│   ├── test_oracle_connection.py
│   ├── test_postgres_connection.py
│   └── quick_test.py              # 전체 마이그레이션 테스트
│
├── config/                        # 설정 파일 저장소
├── logs/                          # 로그 파일
├── data/                          # 데이터 파일
│
├── requirements.txt               # Python 패키지
├── docker-compose.yml             # Docker 테스트 환경
├── setup_test_data.sql            # Oracle 테스트 데이터
│
└── 문서/
    ├── README.md                  # 프로젝트 소개
    ├── QUICKSTART.md              # 빠른 시작 가이드
    ├── CLOSED_NETWORK_SETUP.md    # 폐쇄망 설치 가이드
    └── PROJECT_SUMMARY.md         # 프로젝트 요약 (본 문서)
```

---

## 기술 스택

### 언어 및 프레임워크
- **Python 3.13** (3.9+ 지원)
- **PyQt5**: GUI 프레임워크
- **python-oracledb**: Oracle 데이터베이스 연결 (2.0+)
- **psycopg2-binary**: PostgreSQL 데이터베이스 연결
- **cryptography**: 암호화
- **colorlog**: 컬러 로깅

### 데이터베이스
- **Oracle** 11g / 21c
- **PostgreSQL** 10+

### 배포
- Docker (테스트 환경)
- 폐쇄망 오프라인 패키지 지원

---

## 설치 및 실행

### 1. 의존성 설치

```bash
# 가상환경 생성
python3.13 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. Docker 테스트 환경 (선택사항)

```bash
docker-compose up -d

# Oracle 21c: localhost:1521 (XEPDB1)
# PostgreSQL: localhost:5432
```

### 3. GUI 실행

```bash
python src/main.py
```

---

## 사용 방법

### Step 1: 데이터베이스 연결
1. **Tab 1: Connection**에서 Oracle과 PostgreSQL 연결 정보 입력
2. Oracle 11g 사용 시 "Thick Mode" 체크 필수
3. "Test Connection" 버튼으로 연결 확인
4. 프로파일 저장 (선택사항)

### Step 2: 테이블 선택
1. **Tab 2: Table Selection**에서 스키마 입력 (예: SYSTEM)
2. "Load Tables" 버튼 클릭
3. 마이그레이션할 테이블 선택

### Step 3: 초기 마이그레이션 (최초 1회)
1. **Tab 3: Migration**에서 "Generate DDL" 버튼 클릭
2. PostgreSQL DDL 확인
3. "Start Migration" 버튼으로 테이블 생성 및 데이터 이관

### Step 4: **실시간 동기화 설정** ⭐
1. **Tab 4: Sync**로 이동
2. 동기화 간격 선택 (예: 10 minutes)
3. 동기화 모드 선택:
   - **Incremental**: 빠름, 타임스탬프 컬럼 필요
   - **Full**: 안전, 전체 데이터 재동기화
   - **Delete & Insert**: 테이블 재생성
4. 타임스탬프 컬럼 입력 (증분 동기화 시)
5. "Start Sync" 버튼 클릭

### Step 5: 모니터링
- 실시간 동기화 상태 확인
- 동기화 히스토리 테이블에서 이력 확인
- **Tab 5: Logs**에서 상세 로그 확인

---

## 동기화 시나리오 예시

### 시나리오 1: 실시간 주문 데이터 동기화
```
Oracle에서 매 10분마다 신규 주문 데이터를 PostgreSQL로 동기화

설정:
- Sync Interval: 10 minutes
- Sync Mode: Incremental
- Timestamp Column: ORDER_DATE
```

### 시나리오 2: 매시간 전체 재동기화
```
매시간 전체 데이터를 재동기화하여 완전한 일치 보장

설정:
- Sync Interval: 1 hour
- Sync Mode: Full
```

### 시나리오 3: 일일 야간 배치
```
매일 자정에 테이블 재생성 후 전체 데이터 동기화

설정:
- Sync Interval: 24 hours
- Sync Mode: Delete & Insert
```

---

## Oracle 11g 폐쇄망 환경 지원

### 특징
- ✅ 인터넷 없는 환경에서도 설치 및 실행 가능
- ✅ Oracle 11g Thick 모드 지원
- ✅ 오프라인 패키지 다운로드 지원

### 준비 사항 (인터넷 환경)
1. Python 3.13 설치 파일
2. Oracle Instant Client (11.2+)
3. Python 패키지:
   ```bash
   pip download -r requirements.txt -d ./offline_packages
   ```

### 설치 (폐쇄망 환경)
자세한 내용은 **`CLOSED_NETWORK_SETUP.md`** 참조

---

## 성능 특성

### 마이그레이션 성능
- **소량 데이터** (< 10만 건): ~10초
- **중량 데이터** (10만~100만 건): ~1-5분
- **대량 데이터** (100만+ 건): ~5-30분

성능은 네트워크 속도, DB 서버 성능, 배치 크기에 따라 달라집니다.

### 동기화 성능
- **증분 동기화**: 매우 빠름 (초 단위)
- **전체 동기화**: 테이블 크기에 비례
- **백그라운드 실행**: GUI 성능에 영향 없음

---

## 로그 및 트러블슈팅

### 로그 위치
```
logs/migration_YYYYMMDD_HHMMSS.log
```

### 주요 오류 해결
1. **Oracle 연결 실패**
   - Thick 모드 확인 (Oracle 11g는 필수)
   - Instant Client 경로 확인
   - SID/Service Name 확인

2. **동기화 실패**
   - 타임스탬프 컬럼 존재 여부 확인
   - Primary Key 존재 여부 확인
   - 네트워크 연결 확인

3. **성능 저하**
   - 배치 크기 조정 (기본 1000)
   - 동기화 간격 늘리기
   - Full 모드 대신 Incremental 모드 사용

---

## 향후 계획

- [ ] 다중 테이블 동기화 (한번에 여러 테이블)
- [ ] CLI 모드 추가
- [ ] 변경 감지 (CDC - Change Data Capture)
- [ ] 충돌 해결 전략 (Conflict Resolution)
- [ ] 알림 기능 (이메일, Slack)
- [ ] 스케줄러 기능 (특정 시간 실행)

---

## 라이선스

MIT License

---<ctrl62>## 참고 문서

1. **README.md**: 프로젝트 소개 및 기본 사용법
2. **QUICKSTART.md**: 빠른 시작 가이드 (Docker 환경)
3. **CLOSED_NETWORK_SETUP.md**: 폐쇄망 설치 가이드 (Oracle 11g 지원)
4. **development_requirements.md**: 원본 개발 요구사항

---

## 핵심 차별점

✅ **Oracle 11g 폐쇄망 환경 완벽 지원**
✅ **실시간 자동 동기화 (주기적 실행)**
✅ **3가지 동기화 모드 (증분/전체/재생성)**
✅ **GUI 기반 사용 편의성**
✅ **암호화된 프로파일 관리**
✅ **Python 3.13 최신 버전 지원**

---

## 프로젝트 완성도

- [x] 데이터베이스 연결 관리
- [x] DDL 변환
- [x] 데이터 마이그레이션
- [x] **실시간 동기화** ⭐
- [x] PyQt5 GUI
- [x] Oracle 11g 지원
- [x] 폐쇄망 배포 가이드
- [x] Docker 테스트 환경
- [x] 테스트 스크립트
- [x] 완전한 문서화

**프로젝트 완성!** 🎉

---
---

# `CLOSED_NETWORK_SETUP.md`

# 폐쇄망 환경 설치 가이드 (Oracle 11g 지원)

이 문서는 인터넷이 연결되지 않은 폐쇄망 환경에서 Oracle 11g에 접속하여 PostgreSQL로 마이그레이션하는 프로그램을 설치하는 방법을 설명합니다.

## 목차
1. [사전 준비 (인터넷 환경)](#1-사전-준비-인터넷-환경)
2. [폐쇄망 설치 (오프라인 환경)](#2-폐쇄망-설치-오프라인-환경)
3. [Oracle 11g 연결 설정](#3-oracle-11g-연결-설정)
4. [실행 및 테스트](#4-실행-및-테스트)
5. [트러블슈팅](#5-트러블슈팅)

---

## 1. 사전 준비 (인터넷 환경)

폐쇄망에 반입하기 전에 인터넷이 연결된 환경에서 다음 파일들을 준비합니다.

### 1.1 Python 3.13 설치 파일 다운로드

**Windows:**
```
https://www.python.org/ftp/python/3.13.7/python-3.13.7-amd64.exe
```

**Linux (CentOS/RHEL):**
```bash
# Python 소스 또는 RPM 패키지
wget https://www.python.org/ftp/python/3.13.7/Python-3.13.7.tgz
```

**macOS:**
```
https://www.python.org/ftp/python/3.13.7/python-3.13.7-macos11.pkg
```

### 1.2 Oracle Instant Client 다운로드

**중요: Oracle 11g 연결을 위해서는 Instant Client 11.2 이상이 필요합니다.**

Oracle 공식 사이트에서 다운로드:
https://www.oracle.com/database/technologies/instant-client/downloads.html

**Windows (64-bit):**
```
instantclient-basic-windows.x64-21.15.0.0.0dbru.zip
instantclient-sdk-windows.x64-21.15.0.0.0dbru.zip  (선택사항)
```

**Linux (64-bit):**
```
instantclient-basic-linux.x64-21.15.0.0.0dbru.zip
```

**macOS (Intel/M1):**
```
instantclient-basic-macos.x64-19.8.0.0.0dbru.dmg
```

### 1.3 Python 패키지 다운로드

프로젝트 디렉토리에서 실행:

```bash
# 프로젝트 클론 또는 복사
cd oraToPgsql

# 오프라인 패키지 디렉토리 생성
mkdir offline_packages

# 필요한 모든 패키지 다운로드
pip download -r requirements.txt -d ./offline_packages --platform manylinux1_x86_64 --python-version 313 --only-binary=:all:

# Windows용 (Windows 환경인 경우)
pip download -r requirements.txt -d ./offline_packages --platform win_amd64 --python-version 313 --only-binary=:all:

# macOS용 (macOS 환경인 경우)
pip download -r requirements.txt -d ./offline_packages --platform macosx_10_9_x86_64 --python-version 313 --only-binary=:all:
```

### 1.4 프로젝트 소스 패키징

```bash
# 전체 프로젝트를 압축
cd ..
tar -czf oraToPgsql.tar.gz oraToPgsql/
# 또는 zip
zip -r oraToPgsql.zip oraToPgsql/
```

### 1.5 준비된 파일 목록 확인

```
준비할 파일들:
├── python-3.13.7-amd64.exe (또는 해당 OS용 설치 파일)
├── instantclient-basic-*.zip
├── oraToPgsql.tar.gz (또는 .zip)
└── 문서 (선택사항)
    ├── README.md
    └── CLOSED_NETWORK_SETUP.md
```

---

## 2. 폐쇄망 설치 (오프라인 환경)

### 2.1 Python 3.13 설치

**Windows:**
```cmd
# 관리자 권한으로 실행
python-3.13.7-amd64.exe /quiet InstallAllUsers=1 PrependPath=1

# 설치 확인
python --version
```

**Linux:**
```bash
# 소스에서 빌드
tar -xzf Python-3.13.7.tgz
cd Python-3.13.7
./configure --enable-optimizations
make -j$(nproc)
sudo make altinstall

# 설치 확인
python3.13 --version
```

**macOS:**
```bash
# PKG 파일 설치
sudo installer -pkg python-3.13.7-macos11.pkg -target /

# 설치 확인
python3.13 --version
```

### 2.2 Oracle Instant Client 설치

**Windows:**
```cmd
# 1. ZIP 파일 압축 해제
# C:\oracle\instantclient_21_15\ 에 압축 해제

# 2. 환경 변수 설정
setx PATH "%PATH%;C:\oracle\instantclient_21_15"

# 또는 시스템 환경 변수에 추가:
# 내 컴퓨터 → 속성 → 고급 시스템 설정 → 환경 변수 → PATH에 추가
```

**Linux:**
```bash
# 1. ZIP 파일 압축 해제
sudo mkdir -p /opt/oracle
sudo unzip instantclient-basic-linux.x64-*.zip -d /opt/oracle

# 2. 심볼릭 링크 생성 (필요시)
cd /opt/oracle/instantclient_21_15
sudo ln -s libclntsh.so.21.1 libclntsh.so
sudo ln -s libocci.so.21.1 libocci.so

# 3. 라이브러리 경로 설정
echo /opt/oracle/instantclient_21_15 | sudo tee /etc/ld.so.conf.d/oracle-instantclient.conf
sudo ldconfig

# 또는 환경 변수 설정
echo 'export LD_LIBRARY_PATH=/opt/oracle/instantclient_21_15:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc
```

**macOS:**
```bash
# 1. DMG 마운트 및 설치 또는 ZIP 압축 해제
mkdir -p ~/oracle
unzip instantclient-basic-macos.x64-*.zip -d ~/oracle

# 2. 환경 변수 설정
echo 'export DYLD_LIBRARY_PATH=~/oracle/instantclient_19_8:$DYLD_LIBRARY_PATH' >> ~/.zshrc
source ~/.zshrc
```

### 2.3 프로젝트 설치

```bash
# 1. 프로젝트 압축 해제
tar -xzf oraToPgsql.tar.gz
cd oraToPgsql

# 2. 가상환경 생성
python3.13 -m venv venv

# 3. 가상환경 활성화
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 오프라인 패키지 설치
pip install --no-index --find-links=./offline_packages -r requirements.txt

# 5. 설치 확인
pip list
```

---

## 3. Oracle 11g 연결 설정

### 3.1 Thick 모드 활성화 확인

Oracle 11g는 **반드시 Thick 모드**로 연결해야 합니다.

프로그램 내에서 다음과 같이 설정:

```python
from src.core.db_connection import OracleConfig, OracleConnection

# Oracle 11g 연결 설정
config = OracleConfig(
    host="192.168.1.100",
    port=1521,
    sid="ORCL11G",  # 또는 service_name 사용
    user="your_user",
    password="your_password",
    thick_mode=True,  # 필수!
    instant_client_dir="/opt/oracle/instantclient_21_15"  # Windows: "C:\\oracle\\instantclient_21_15"
)

oracle_conn = OracleConnection(config)
```

### 3.2 연결 테스트

```python
# 테스트 스크립트 (test_connection.py)
if __name__ == '__main__':
    from src.core.db_connection import OracleConfig, OracleConnection

    config = OracleConfig(
        host="your_oracle_host",
        port=1521,
        sid="your_sid",
        user="your_user",
        password="your_password",
        thick_mode=True,
        instant_client_dir="/opt/oracle/instantclient_21_15"
    )

    conn = OracleConnection(config)

    if conn.test_connection():
        print("✓ Oracle 11g 연결 성공!")
    else:
        print("✗ 연결 실패")
```

실행:
```bash
python test_connection.py
```

### 3.3 tnsnames.ora 사용 (선택사항)

복잡한 연결 문자열이 필요한 경우:

```bash
# tnsnames.ora 파일 생성
# Linux/macOS: /opt/oracle/instantclient_21_15/network/admin/tnsnames.ora
# Windows: C:\oracle\instantclient_21_15\network\admin\tnsnames.ora

ORCL11G =
  (DESCRIPTION =
    (ADDRESS = (PROTOCOL = TCP)(HOST = 192.168.1.100)(PORT = 1521))
    (CONNECT_DATA =
      (SID = ORCL11G)
    )
  )
```

환경 변수 설정:
```bash
export TNS_ADMIN=/opt/oracle/instantclient_21_15/network/admin
```

---

## 4. 실행 및 테스트

### 4.1 GUI 실행

```bash
cd oraToPgsql
source venv/bin/activate  # Windows: venv\Scripts\activate
python src/main.py
```

### 4.2 명령줄 테스트 (개발 중)

```bash
# DDL 변환 테스트
python -m src.core.ddl_converter

# 연결 테스트
python test_connection.py
```

---

## 5. 트러블슈팅

### 5.1 "DPI-1047: Cannot locate a 64-bit Oracle Client library"

**원인:** Oracle Instant Client를 찾을 수 없음

**해결:**
```bash
# Linux
export LD_LIBRARY_PATH=/opt/oracle/instantclient_21_15:$LD_LIBRARY_PATH

# macOS
export DYLD_LIBRARY_PATH=~/oracle/instantclient_19_8:$DYLD_LIBRARY_PATH

# Windows
set PATH=%PATH%;C:\oracle\instantclient_21_15
```

### 5.2 "ORA-12154: TNS:could not resolve the connect identifier specified"

**원인:** SID 또는 Service Name이 잘못됨

**해결:**
1. SID 확인:
   ```sql
   -- Oracle에서 확인
   SELECT instance_name FROM v$instance;
   ```

2. 연결 문자열 확인:
   ```python
   # SID 사용
   config = OracleConfig(host="...", port=1521, sid="ORCL11G", ...)

   # 또는 Service Name 사용
   config = OracleConfig(host="...", port=1521, service_name="ORCL11G.domain", ...)
   ```

### 5.3 "ORA-12170: TNS:Connect timeout occurred"

**원인:** 네트워크 연결 문제 또는 방화벽

**해결:**
1. 방화벽 확인:
   ```bash
   # Linux
   sudo firewall-cmd --add-port=1521/tcp --permanent
   sudo firewall-cmd --reload
   ```

2. 연결 가능 여부 테스트:
   ```bash
telnet oracle_host 1521
# 또는
nc -zv oracle_host 1521
```

### 5.4 Python 패키지 설치 오류

**원인:** 플랫폼 불일치 또는 의존성 문제

**해결:**
```bash
# 현재 환경에 맞는 패키지 다시 다운로드 (인터넷 환경에서)
pip download -r requirements.txt -d ./offline_packages

# 개별 패키지 설치
pip install --no-index --find-links=./offline_packages python-oracledb
pip install --no-index --find-links=./offline_packages psycopg2-binary
pip install --no-index --find-links=./offline_packages PyQt5
```

### 5.5 "python-oracledb: Thick mode not supported"

**원인:** Instant Client 경로 문제

**해결:**
```python
import oracledb

# 명시적으로 초기화
oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_21_15")

# 확인
print(oracledb.is_thin_mode())  # False여야 함
```

---

## 6. 성능 최적화

### 6.1 배치 크기 조정

```python
from src.core.data_migrator import DataMigrator

migrator = DataMigrator(
    oracle_conn,
    postgres_conn,
    batch_size=5000  # 기본 1000에서 증가
)
```

### 6.2 네트워크 버퍼 크기

```python
# Oracle 연결 시
cursor.arraysize = 10000  # 기본값보다 증가
```

---

## 7. 보안 권장사항

### 7.1 연결 정보 암호화

프로그램에서 제공하는 암호화 기능 사용:
- Keyring을 통한 안전한 비밀번호 저장
- 설정 파일 암호화

### 7.2 로그 파일 관리

```bash
# 로그 파일에서 민감 정보 제거
grep -v "PASSWORD" logs/migration.log > logs/migration_safe.log
```

---

## 8. 지원 및 문의

프로젝트 이슈: https://github.com/your-org/oraToPgsql/issues

---

## 부록: 빠른 체크리스트

폐쇄망 설치 전 확인사항:

- [ ] Python 3.13 설치 파일 준비
- [ ] Oracle Instant Client (11.2+) 준비
- [ ] 프로젝트 소스 코드 (.tar.gz 또는 .zip)
- [ ] Python 패키지 (`offline_packages/` 디렉토리)
- [ ] Oracle 11g 접속 정보 (호스트, 포트, SID, 계정)
- [ ] PostgreSQL 접속 정보
- [ ] 네트워크 연결 확인 (Oracle, PostgreSQL)
- [ ] 방화벽 규칙 확인

설치 후 확인:

- [ ] `python --version` → 3.13.x
- [ ] `pip list` → python-oracledb, psycopg2-binary, PyQt5 확인
- [ ] Oracle Instant Client 환경 변수 설정 완료
- [ ] Oracle 11g 연결 테스트 성공
- [ ] PostgreSQL 연결 테스트 성공

---
---

# `QUICKSTART.md`

# Quick Start Guide

Oracle to PostgreSQL Migration Tool 빠른 시작 가이드

## 1. 환경 준비 (현재 인터넷 환경)

### 1.1 Docker 컨테이너 확인

```bash
# 컨테이너 상태 확인
docker ps

# Oracle 21c와 PostgreSQL이 실행 중이어야 함
# - oracle21c (포트 1521)
# - postgres-docker (포트 5432)
```

### 1.2 가상환경 생성 및 패키지 설치

```bash
cd /Users/sein/Desktop/oraToPgsql

# 가상환경 생성
python3.13 -m venv venv

# 가상환경 활성화
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt
```

## 2. 데이터베이스 연결 테스트

### 2.1 PostgreSQL 연결 테스트

```bash
python tests/test_postgres_connection.py
```

**예상 출력:**
```
PostgreSQL 연결 테스트
✓ PostgreSQL 연결 성공!
PostgreSQL 버전: PostgreSQL 16.x ...
```

### 2.2 Oracle 21c 연결 테스트

```bash
python tests/test_oracle_connection.py
```

**예상 출력:**
```
Oracle 21c 연결 테스트 (Thin Mode)
✓ Oracle 21c 연결 성공!
Oracle 버전: Oracle Database 21c Express Edition ...
```

## 3. 테스트 데이터 생성

### 3.1 Oracle에 테스트 테이블 생성

```bash
# Docker를 통해 Oracle SQL*Plus 접속
docker exec -it oracle21c sqlplus system/oracle@XEPDB1

# 또는 로컬 SQL 클라이언트로 접속:
# Host: localhost
# Port: 1521
# Service Name: XEPDB1
# User: system
# Password: oracle
```

SQL*Plus에서 실행:
```sql
-- setup_test_data.sql 파일의 내용을 복사하여 실행
@setup_test_data.sql

-- 또는 수동으로 실행
CREATE TABLE EMPLOYEES (
    EMPLOYEE_ID NUMBER(10) NOT NULL,
    FIRST_NAME VARCHAR2(50) NOT NULL,
    LAST_NAME VARCHAR2(50) NOT NULL,
    EMAIL VARCHAR2(100),
    PHONE_NUMBER VARCHAR2(20),
    HIRE_DATE DATE DEFAULT SYSDATE NOT NULL,
    SALARY NUMBER(10,2),
    DEPARTMENT_ID NUMBER(10),
    CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT PK_EMPLOYEES PRIMARY KEY (EMPLOYEE_ID)
);

-- 테스트 데이터 삽입
INSERT INTO EMPLOYEES VALUES (1, 'John', 'Doe', 'john.doe@example.com', '010-1234-5678', TO_DATE('2020-01-15', 'YYYY-MM-DD'), 75000.00, 10, SYSTIMESTAMP);
INSERT INTO EMPLOYEES VALUES (2, 'Jane', 'Smith', 'jane.smith@example.com', '010-2345-6789', TO_DATE('2021-03-20', 'YYYY-MM-DD'), 82000.00, 20, SYSTIMESTAMP);
COMMIT;

-- 확인
SELECT * FROM EMPLOYEES;
```

### 3.2 데이터 확인

```bash
# Oracle 데이터 확인
docker exec oracle21c sqlplus -s system/oracle@XEPDB1 <<EOF
SET PAGESIZE 50
SELECT COUNT(*) FROM SYSTEM.EMPLOYEES;
SELECT * FROM SYSTEM.EMPLOYEES ORDER BY EMPLOYEE_ID;
EXIT;
EOF
```

## 4. GUI 프로그램 실행

### 4.1 프로그램 시작

```bash
python src/main.py
```

### 4.2 GUI 사용 방법

#### Step 1: 데이터베이스 연결 설정

**Oracle 설정 (Tab 1: Connection):**
- Host: `localhost`
- Port: `1521`
- Service Name: `XEPDB1`
- User: `system`
- Password: `oracle`
- Thick Mode: 체크 해제 (Oracle 21c는 Thin 모드 지원)

**PostgreSQL 설정:**
- Host: `localhost`
- Port: `5432`
- Database: `postgres`
- Schema: `public`
- User: `postgres`
- Password: `postgres`

**연결 테스트:**
- "Test Oracle Connection" 버튼 클릭 → 성공 확인
- "Test PostgreSQL Connection" 버튼 클릭 → 성공 확인

**프로파일 저장 (선택사항):**
- "Save" 버튼 클릭
- 프로파일 이름 입력 (예: "Docker Test")

#### Step 2: 테이블 선택

**Tab 2: Table Selection**
1. Schema (Owner) 입력: `SYSTEM` (대문자)
2. "Load Tables" 버튼 클릭
3. 테이블 목록에서 `EMPLOYEES` 선택
4. 하단에 테이블 상세 정보 (컬럼, PK, 인덱스) 표시 확인

#### Step 3: DDL 생성 및 마이그레이션

**Tab 3: Migration**
1. "Generate DDL" 버튼 클릭
2. 생성된 PostgreSQL DDL 확인:
   ```sql
   CREATE TABLE employees (
     employee_id INTEGER NOT NULL,
     first_name VARCHAR(50) NOT NULL,
     ...
   );
   ```
3. Migration Settings:
   - ☑ Overwrite existing table (체크)
   - Batch Size: 1000 (기본값)
4. "Start Migration" 버튼 클릭
5. 진행률 바에서 진행 상황 확인
6. 완료 메시지 확인

#### Step 4: 결과 확인

**Tab 4: Logs**
- 마이그레이션 로그 확인

**PostgreSQL에서 데이터 확인:**
```bash
docker exec -it postgres-docker psql -U postgres -d postgres -c "SELECT * FROM employees ORDER BY employee_id;"
```

## 5. 명령줄에서 빠른 테스트

전체 마이그레이션 프로세스를 Python 스크립트로 테스트:

```python
# quick_test.py
from src.core.db_connection import OracleConfig, PostgresConfig, OracleConnection, PostgresConnection
from src.core.ddl_converter import DDLConverter
from src.core.data_migrator import DataMigrator

# Oracle 연결
oracle_config = OracleConfig(
    host="localhost", port=1521, service_name="XEPDB1",
    user="system", password="oracle", thick_mode=False
)
oracle_conn = OracleConnection(oracle_config)
oracle_conn.connect()

# PostgreSQL 연결
postgres_config = PostgresConfig(
    host="localhost", port=5432, database="postgres",
    schema="public", user="postgres", password="postgres"
)
postgres_conn = PostgresConnection(postgres_config)
postgres_conn.connect()

# 테이블 정보 조회
columns = oracle_conn.get_table_columns("SYSTEM", "EMPLOYEES")
pk = oracle_conn.get_primary_key("SYSTEM", "EMPLOYEES")
indexes = oracle_conn.get_indexes("SYSTEM", "EMPLOYEES")

# DDL 생성
converter = DDLConverter()
ddl = converter.generate_full_ddl("EMPLOYEES", columns, pk, indexes)
print("Generated DDL:")
print(ddl)

# PostgreSQL에 테이블 생성
if postgres_conn.table_exists("employees"):
    postgres_conn.drop_table("employees")
postgres_conn.execute_ddl(ddl)
print("\nTable created in PostgreSQL")

# 데이터 마이그레이션
migrator = DataMigrator(oracle_conn, postgres_conn, batch_size=1000)
result = migrator.migrate_table("SYSTEM", "EMPLOYEES")

print(f"\nMigration completed!")
print(f"Total rows: {result.total_rows}")
print(f"Migrated: {result.migrated_rows}")
print(f"Failed: {result.failed_rows}")

# 검증
verification = migrator.verify_migration("SYSTEM", "EMPLOYEES")
print(f"\nVerification:")
print(f"Oracle count: {verification['oracle_count']}")
print(f"PostgreSQL count: {verification['postgres_count']}")
print(f"Match: {verification['match']}")

# 연결 종료
oracle_conn.close()
postgres_conn.close()
```

실행:
```bash
python quick_test.py
```

## 6. 폐쇄망 배포 준비

### 6.1 오프라인 패키지 다운로드

```bash
# 현재 인터넷 환경에서 실행
mkdir offline_packages

# 모든 의존성 패키지 다운로드
pip download -r requirements.txt -d ./offline_packages
```

### 6.2 Oracle 11g 지원 준비

Oracle 11g 연결을 위해 추가로 필요한 파일:

1. **Oracle Instant Client 다운로드:**
   - https://www.oracle.com/database/technologies/instant-client/downloads.html
   - instantclient-basic-*.zip (플랫폼에 맞게)

2. **폐쇄망 설치 가이드 참조:**
   - `CLOSED_NETWORK_SETUP.md` 문서 확인

### 6.3 배포 파일 목록

```
배포할 파일:
├── oraToPgsql.tar.gz (전체 프로젝트)
├── offline_packages/ (Python 패키지)
├── instantclient-basic-*.zip (Oracle Instant Client)
├── python-3.13.7-*.exe/pkg (Python 설치 파일)
└── 문서
    ├── README.md
    ├── QUICKSTART.md
    └── CLOSED_NETWORK_SETUP.md
```

## 7. Oracle 11g 테스트 (폐쇄망 환경)

Oracle 11g 환경에서는 Thick 모드 필수:

```python
# GUI에서 설정
Oracle 설정:
- Host: [Oracle 11g 서버 IP]
- Port: 1521
- SID: ORCL11G (또는 해당 SID)
- User: [사용자명]
- Password: [비밀번호]
- ☑ Thick Mode (Oracle 11g 필수)
- Instant Client Dir: /opt/oracle/instantclient_21_15
```

## 8. 트러블슈팅

### Oracle 연결 실패

```bash
# Docker 컨테이너 상태 확인
docker ps

# Oracle 로그 확인
docker logs oracle21c

# Oracle 재시작
docker restart oracle21c

# 연결 테스트
telnet localhost 1521
```

### PostgreSQL 연결 실패

```bash
# PostgreSQL 로그 확인
docker logs postgres-docker

# PostgreSQL 재시작
docker restart postgres-docker
```

### Python 패키지 오류

```bash
# 패키지 재설치
pip install --upgrade --force-reinstall -r requirements.txt

# 특정 패키지 확인
pip show python-oracledb
pip show psycopg2-binary
pip show PyQt5
```

## 9. 다음 단계

- [ ] 다중 테이블 마이그레이션 기능 추가
- [ ] 스케줄러 기능 구현
- [ ] CLI 모드 추가
- [ ] 마이그레이션 리포트 자동 생성
- [ ] 성능 최적화 (병렬 처리)

## 지원

문제 발생 시 로그 파일 확인:
```bash
ls -lh logs/
tail -f logs/migration_*.log
```

프로젝트 이슈: [GitHub Issues](https://github.com/your-org/oraToPgsql/issues)

---
---

# `development_requirements.md`

# 오라클 11g → PostgreSQL 테이블 마이그레이션 폼 프로그램 개발 요구서

## 1. 프로젝트 개요
- **목표**: 오라클 11g 데이터베이스의 특정 테이블을 선택하여 PostgreSQL 데이터베이스로 구조와 데이터를 안전하게 마이그레이션하는 Python 기반 GUI 애플리케이션 개발
- **사용자**: DBA, 데이터 마이그레이션 담당자, 개발자
- **운영 환경**
  - Python 3.9 이상
  - GUI 프레임워크: PyQt5 또는 PySide6 (최종 선정 시 라이선스와 유지보수 편의성 고려)
  - Oracle Instant Client 및 `cx_Oracle` 라이브러리
  - PostgreSQL 접속을 위한 `psycopg2` 또는 `asyncpg`
  - 운영 체제: Windows 10 이상, macOS, Linux (Cross-platform 지원)

## 2. 시스템 구성 및 흐름
1. **DB 연결 설정**
   - 오라클, PostgreSQL 각각의 접속 정보 입력 및 저장
   - 저장된 프로파일 관리 (등록, 수정, 삭제)
2. **테이블 선택**
   - 오라클 스키마 내 테이블 목록 조회 및 검색 필터
   - 다중 선택을 지원하지만 이번 범위는 단일 테이블 중심으로 개발
3. **구조 마이그레이션**
   - 선택된 테이블의 DDL 스크립트를 Oracle → PostgreSQL 규칙에 맞게 변환
   - PostgreSQL에서 대상 스키마 및 테이블 존재 여부 확인 후 생성 또는 덮어쓰기 선택 옵션 제공
4. **데이터 마이그레이션**
   - 소량 데이터 판단 기준(예: 100만 건 미만, 사용자 설정 가능)
   - 소량: 전체 데이터 일괄 복사
   - 대량: 날짜 컬럼 또는 사용자 정의 조건을 기준으로 분할 이관
   - 실행 상태 모니터링 및 로그 출력
5. **결과 검증**
   - 이관 후 건수 비교, 해시/체크섬 검증 옵션
   - 로그와 요약 리포트 저장

## 3. 기능 요구사항
### 3.1 연결 관리
- Oracle, PostgreSQL 접속 정보 입력 폼 제공 (호스트, 포트, SID/서비스명, 스키마, 계정, 패스워드)
- 접속 정보 암호화 저장 (예: OS Keyring, 암호화 파일, 선택 옵션)
- 연결 테스트 버튼으로 즉각적인 검증

### 3.2 테이블 메타데이터 조회
- 선택한 Oracle 스키마의 테이블 목록 로딩, 이름/코멘트/행 개수 표시
- 특정 테이블을 클릭 시 컬럼 정의, 인덱스, 제약조건 미리보기

### 3.3 DDL 변환 및 생성
- Oracle 데이터 타입 → PostgreSQL 매핑 테이블 정의 (예: NUMBER → NUMERIC, VARCHAR2 → VARCHAR)
- PRIMARY KEY, UNIQUE, FOREIGN KEY, CHECK 제약조건 변환
- 시퀀스/트리거 기반 PK 자동 증가 로직을 PostgreSQL 시퀀스로 변환
- 변환된 DDL을 사용자에게 미리 보여주고 편집 저장 가능
- PostgreSQL에 테이블 생성 시 기존 테이블 존재하면 덮어쓰기 여부 선택

### 3.4 데이터 마이그레이션 로직
- **소량 데이터**: `SELECT *` 기반 일괄 추출 후 `COPY` 또는 batched insert로 PostgreSQL 적재
- **대량 데이터**
  - 사용자 정의 기준 컬럼 지정 (DATE, NUMBER, VARCHAR)
  - 범위 지정 (날짜 범위, 조건식) 후 배치 처리
  - 배치 단위 설정 (건수/일자/조건)
- 마이그레이션 도중 일시 중지/재개, 취소 기능
- 각 단계별 진행률, 예상 남은 시간 표시

### 3.5 로그 및 리포트
- 연결, DDL 변환, 데이터 전송 단계별 로그 파일 저장
- 오류 발생 시 상세 메시지와 원인 추적 정보 제공
- 이관 완료 후 요약 리포트 (총 건수, 성공/실패 건수, 소요 시간, 경고) 저장

### 3.6 UI/UX 요구사항
- 주요 화면
  1. 시작/설정 화면: DB 프로파일 관리
  2. 테이블 선택 화면: 테이블 목록/검색/미리보기
  3. 마이그레이션 설정 화면: DDL 미리보기, 데이터 이관 설정
  4. 진행 모니터 화면: 로그, 진행률, 오류 알림
- 상태 메시지 및 오류 알림은 트레이 알림/팝업으로 표시
- 작업 로그 패널에서 필터링(정보/경고/오류) 지원

## 4. 비기능 요구사항
- **성능**: 100만 건 기준 30분 내 이관 완료 목표 (네트워크 및 DB 성능에 따라 달라질 수 있음을 명시)
- **안정성**: 예외 처리 강화, 재시도 로직, 부분 실패 시 롤백 또는 재처리 지원
- **보안**: 로그인 정보 암호화 저장, 로그에 민감 정보 노출 금지
- **확장성**: 향후 다중 테이블, 스키마 전체 이관 기능 추가를 고려한 아키텍처
- **유지보수성**: 설정 파일 및 로그 경로 사용자 지정, 구조화된 모듈 설계

## 5. 예외 및 오류 처리
- DB 연결 실패: 사용자 재입력 유도, 상세 오류 메시지 표시
- DDL 변환 오류: 매핑 불가능한 데이터 타입 목록화 후 사용자 승인 요청
- 데이터 이관 중 오류: 실패 건 로그 저장, 재시도 옵션 제공
- PostgreSQL 트랜잭션 실패 시 롤백 처리 및 사용자에게 경고

## 6. 테스트 및 검증 계획
- 단위 테스트: DDL 변환 모듈, 데이터 매핑 함수, 조건 분할 로직
- 통합 테스트: 실제 Oracle 테스트 DB와 PostgreSQL 테스트 DB를 활용한 엔드투엔드 검증
- 성능 테스트: 대량 데이터 이관 시 처리 시간과 안정성 확인
- 사용자 수용 테스트(UAT): 마이그레이션 담당자 대상 시나리오 기반 테스트

## 7. 향후 확장 아이디어
- 다중 테이블 및 스키마 전체 이관 자동화
- 스케줄러 기능(예약 실행)
- CLI 모드 제공 및 CI/CD 파이프라인과 연동
- 마이그레이션 전후 데이터 검증 리포트 자동 생성 (PDF/HTML)

---
---

# `README.md`

# Oracle to PostgreSQL Migration Tool

Oracle 11g+ 데이터베이스의 테이블을 PostgreSQL로 마이그레이션하는 Python GUI 애플리케이션

## 주요 기능

- Oracle 및 PostgreSQL 데이터베이스 연결 관리
- 테이블 구조 자동 변환 (DDL)
- 대용량 데이터 배치 마이그레이션
- 실시간 진행 상황 모니터링
- 마이그레이션 결과 검증

## 시스템 요구사항

- Python 3.13+
- Oracle Instant Client (Thick 모드 사용 시)
- 지원 데이터베이스:
  - Oracle 11g 이상 (11g는 Thick 모드 필요)
  - PostgreSQL 10 이상

## 설치 방법

### 1. 가상환경 생성 및 활성화
```bash
python3.13 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. Oracle Instant Client 설치 (Thick 모드용)
Oracle 11g 연결을 위해서는 Thick 모드가 필요합니다.

**macOS:**
```bash
# Oracle Instant Client 다운로드
# https://www.oracle.com/database/technologies/instant-client/downloads.html
# instantclient-basic-macos.x64-21.x.x.x.zip 다운로드

# 압축 해제 및 환경변수 설정
export DYLD_LIBRARY_PATH=/path/to/instantclient_21_x:$DYLD_LIBRARY_PATH
```

**Linux:**
```bash
sudo dnf install oracle-instantclient-basic
# 또는
export LD_LIBRARY_PATH=/path/to/instantclient_21_x:$LD_LIBRARY_PATH
```

**Windows:**
```
instantclient-basic-windows.x64-21.x.x.x.zip 다운로드 후 압축 해제
PATH 환경변수에 추가
```

## 사용 방법

### GUI 모드
```bash
python src/main.py
```

### Docker 테스트 환경
```bash
# Oracle 21c 컨테이너
docker run -d --name oracle21 -p 1521:1521 -e ORACLE_PASSWORD=oracle gvenzl/oracle-xe:21-slim

# PostgreSQL 컨테이너
docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:16
```

## 폐쇄망 배포

### 패키지 다운로드 (인터넷 환경)
```bash
pip download -r requirements.txt -d ./offline_packages
```

### 설치 (폐쇄망 환경)
```bash
pip install --no-index --find-links=./offline_packages -r requirements.txt
```

## 프로젝트 구조

```
oraToPgsql/
├── src/
│   ├── core/           # 핵심 비즈니스 로직
│   │   ├── db_connection.py
│   │   ├── ddl_converter.py
│   │   └── data_migrator.py
│   ├── gui/            # PyQt5 GUI
│   │   ├── main_window.py
│   │   └── widgets/
│   ├── utils/          # 유틸리티
│   │   ├── logger.py
│   │   └── config.py
│   └── main.py
├── tests/              # 테스트 코드
├── config/             # 설정 파일
├── logs/               # 로그 파일
└── data/               # 데이터 파일
```

## 라이선스

MIT License

---
---

# `ORACLE_11G_CONNECTION_GUIDE.md`

# Oracle 11g 폐쇄망 접속 가이드

## ⚠️ 중요: Python 버전과 Oracle 드라이버

### 현재 프로그램 구성

| 항목 | 설정 |
|------|------|
| **Python 버전** | 3.13 |
| **Oracle 드라이버** | `oracledb 3.4.0` (구 python-oracledb) |
| **모드** | Thick 모드 (Oracle 11g 지원) |
| **Instant Client** | 필수 |

### cx_Oracle vs python-oracledb

#### cx_Oracle (구버전)
```python
# Python 3.9에서 사용
import cx_Oracle

# Thick 모드 (자동)
connection = cx_Oracle.connect(user, password, dsn)
```

**특징:**
- ✅ Oracle 11g 완벽 지원
- ✅ Python 3.9까지 안정적
- ❌ Python 3.13 미지원
- ❌ 개발 중단 (레거시)

#### python-oracledb (신버전)
```python
# Python 3.13에서 사용
import oracledb

# Thick 모드 (수동 초기화 필요)
oracledb.init_oracle_client(lib_dir="/path/to/instantclient")
connection = oracledb.connect(user, password, dsn)
```

**특징:**
- ✅ Python 3.13 지원
- ✅ Oracle 11g 지원 (Thick 모드)
- ✅ Oracle의 공식 후속 드라이버
- ⚠️ Thick 모드 수동 초기화 필요

---

## Oracle 11g 폐쇄망 접속 절차

### 1. Instant Client 설치

**Oracle 11g 호환 버전:**
- Oracle Instant Client 11.2
- Oracle Instant Client 12.1
- Oracle Instant Client 12.2

**다운로드:**
```
https://www.oracle.com/database/technologies/instant-client/downloads.html
```

**설치 경로 예시:**
```
Linux: /opt/oracle/instantclient_11_2
macOS: /usr/local/oracle/instantclient_11_2
Windows: C:\oracle\instantclient_11_2
```

### 2. 환경 변수 설정

#### Linux
```bash
export LD_LIBRARY_PATH=/opt/oracle/instantclient_11_2:$LD_LIBRARY_PATH
export ORACLE_HOME=/opt/oracle/instantclient_11_2
```

#### macOS
```bash
export DYLD_LIBRARY_PATH=/usr/local/oracle/instantclient_11_2:$DYLD_LIBRARY_PATH
export ORACLE_HOME=/usr/local/oracle/instantclient_11_2
```

#### Windows
```cmd
set PATH=C:\oracle\instantclient_11_2;%PATH%
set ORACLE_HOME=C:\oracle\instantclient_11_2
```

### 3. GUI 설정

**Tab 1: Connection**

```
Oracle Database Connection:
  Host: 192.168.1.100
  Port: 1521
  SID: ORCL
  Service Name: (비워두기)
  User: your_user
  Password: your_password

☑ Thick Mode (Oracle 11g 필수)
Instant Client Dir: /opt/oracle/instantclient_11_2

[Test Oracle Connection]
```

### 4. 연결 테스트 로그 확인

**성공 시 로그:**
```
================================================================================
🔌 Oracle 연결 시도 시작
================================================================================
🔧 Thick 모드 활성화 (Oracle 11g 폐쇄망 지원)
📁 Instant Client 경로: /opt/oracle/instantclient_21_15
✅ Thick 모드 초기화 성공!
   → Oracle Client 버전: 11.2.0.4.0

📋 연결 정보:
   - Host: 192.168.1.100
   - Port: 1521
   - SID: ORCL
   - User: your_user
   - DSN: (DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=192.168.1.100)(PORT=1521))(CONNECT_DATA=(SID=ORCL)))
   - 모드: Thick (Oracle 11g 호환)

🔌 데이터베이스 연결 시도 중...

================================================================================
✅ Oracle 연결 성공!
================================================================================
📊 Oracle 버전: Oracle Database 11g Enterprise Edition Release 11.2.0.4.0 - 64bit Production
📊 DB 이름: ORCL
📊 인스턴스: ORCL
📊 현재 스키마: YOUR_USER

✅ 연결 주소: 192.168.1.100:1521
✅ 사용자: your_user
✅ 모드: Thick (Oracle 11g 폐쇄망 지원 ✓)
================================================================================
```

**실패 시 로그:**
```
================================================================================
❌ Oracle 연결 실패!
================================================================================
❌ 오류 메시지: DPY-6005: cannot connect to database...
❌ 오류 타입: DatabaseError

🔍 Thick 모드 (Oracle 11g 폐쇄망) 체크리스트:
   1. ✓ Instant Client가 올바르게 설치되었나요?
      경로: /opt/oracle/instantclient_21_15
   2. ✓ Instant Client 버전이 Oracle 11g와 호환되나요?
      권장: Oracle Instant Client 11.2 또는 12.1
   3. ✓ 환경변수가 설정되었나요?
      Linux: LD_LIBRARY_PATH
      macOS: DYLD_LIBRARY_PATH
      Windows: PATH

🔍 네트워크 및 연결 정보 체크리스트:
   1. ✓ 호스트 접근 가능: 192.168.1.100:1521
      (ping 192.168.1.100 테스트)
   2. ✓ Oracle Listener 실행 중
      (lsnrctl status 확인)
   3. ✓ Service Name/SID 정확: ORCL
   4. ✓ 사용자 권한 확인: your_user
   5. ✓ 방화벽 설정 확인 (폐쇄망)
================================================================================
```

---

## 트러블슈팅

### 문제 1: "Thick mode requires Oracle Client libraries"

**원인:**
- Instant Client가 설치되지 않음
- Instant Client 경로가 잘못됨

**해결:**
```bash
# 1. Instant Client 설치 확인
ls /opt/oracle/instantclient_11_2/

# 2. 필수 파일 확인
- libclntsh.so (Linux)
- libclntsh.dylib (macOS)
- oci.dll (Windows)

# 3. GUI에서 정확한 경로 입력
Instant Client Dir: /opt/oracle/instantclient_11_2
```

### 문제 2: "DPY-6001: cannot connect to database"

**원인:**
- 네트워크 문제
- Oracle Listener 중지
- SID/Service Name 오류

**해결:**
```bash
# 1. 네트워크 테스트
ping 192.168.1.100
telnet 192.168.1.100 1521

# 2. Oracle Listener 상태 확인 (DB 서버에서)
lsnrctl status

# 3. SID 확인 (DB 서버에서)
echo $ORACLE_SID
```

### 문제 3: Python 3.13에서 접속 안 됨 (Python 3.9에서는 됨)

**원인:**
- cx_Oracle은 Python 3.13 미지원
- python-oracledb 사용 필요

**현재 프로그램:**
✅ python-oracledb 사용 중 (Python 3.13 호환)
✅ Thick 모드 지원
✅ Oracle 11g 지원

**확인 방법:**
```python
# 터미널에서 확인
python3 --version  # Python 3.13 확인

# 드라이버 확인
import oracledb
print(oracledb.__version__)  # 3.4.0 이상
```

### 문제 4: "init_oracle_client() already been initialized"

**원인:**
- 정상 동작 (경고만 표시)
- 이미 Thick 모드 초기화됨

**로그:**
```
✅ Thick 모드 이미 초기화됨 (정상)
   → Oracle Client 버전: 11.2.0.4.0
```

**해결:**
- 무시해도 됨 (정상)

---

## 폐쇄망 환경 오프라인 설치

### 1. 인터넷 환경에서 패키지 다운로드

```bash
# 의존성 다운로드
pip download -r requirements.txt -d ./packages

# 패키지 목록
- oracledb-3.4.0-*.whl
- psycopg2_binary-2.9.9-*.whl
- PyQt5-5.15.10-*.whl
- ...
```

### 2. 폐쇄망으로 전송

```bash
# 전송할 파일
./packages/          # Python 패키지
./instantclient_11_2/ # Oracle Instant Client
./oraToPgsql/        # 프로그램 소스
```

### 3. 폐쇄망에서 설치

```bash
# Python 가상환경 생성
python3.13 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 오프라인 패키지 설치
pip install --no-index --find-links=./packages -r requirements.txt

# Instant Client 설치
cp -r instantclient_11_2 /opt/oracle/

# 환경변수 설정
export LD_LIBRARY_PATH=/opt/oracle/instantclient_11_2:$LD_LIBRARY_PATH

# 프로그램 실행
python src/main.py
```

---

## 연결 테스트 스크립트

폐쇄망에서 간단히 테스트:

```python
#!/usr/bin/env python3
"""Oracle 11g Thick 모드 연결 테스트"""

import oracledb

# Thick 모드 초기화
oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_11_2")

# 연결 정보
host = "192.168.1.100"
port = 1521
sid = "ORCL"
user = "your_user"
password = "your_password"

# DSN 생성
dsn = oracledb.makedsn(host, port, sid=sid)

# 연결
try:
    connection = oracledb.connect(user=user, password=password, dsn=dsn)
    print("✅ 연결 성공!")

    # 버전 확인
    cursor = connection.cursor()
    cursor.execute("SELECT BANNER FROM v$version WHERE ROWNUM = 1")
    print(f"📊 {cursor.fetchone()[0]}")
    cursor.close()
    connection.close()

except Exception as e:
    print(f"❌ 연결 실패: {e}")
```

**실행:**
```bash
python test_oracle_connection.py
```

---

## 요약

### ✅ 현재 프로그램 장점

1. **Python 3.13 지원**
   - 최신 Python 버전 사용 가능

2. **Oracle 11g 폐쇄망 지원**
   - Thick 모드 완벽 지원
   - Instant Client 11.2/12.1 호환

3. **상세한 로그**
   - 연결 과정 모든 단계 출력
   - 오류 발생 시 체크리스트 제공

4. **GUI 통합**
   - Thick 모드 체크박스
   - Instant Client 경로 선택
   - 연결 테스트 버튼

### 🔍 폐쇄망 접속 체크리스트

- [ ] Oracle Instant Client 11.2/12.1 설치
- [ ] 환경변수 설정 (LD_LIBRARY_PATH 등)
- [ ] GUI에서 Thick Mode 체크
- [ ] Instant Client Dir 경로 입력
- [ ] Host, Port, SID 정확히 입력
- [ ] Test Oracle Connection 클릭
- [ ] 로그 확인 (성공/실패 상세 정보)

### 📞 문제 해결

**연결 실패 시:**
1. 로그의 체크리스트 확인
2. Instant Client 경로 재확인
3. 네트워크 ping 테스트
4. Oracle Listener 상태 확인
5. 방화벽 설정 확인

**성공 시:**
- Oracle 버전 확인 (로그)
- DB 이름 확인 (로그)
- 스키마 확인 (로그)
- 마이그레이션 진행 가능 ✅

---
---

# `SYNC_MODE_COMPARISON.md`

# 동기화 모드 비교 가이드

## 3가지 동기화 모드 상세 비교

---

## 1. 증분 동기화 (Incremental) ⭐ 추천

### 작동 방식

```
시간: 10:00 - 초기 마이그레이션
┌─────────────────────────────────────┐
│ Oracle: 1000건                      │
│ ↓                                   │
│ PostgreSQL: 1000건 INSERT           │
└─────────────────────────────────────┘

시간: 10:10 - 1차 동기화 (10분 후)
┌─────────────────────────────────────┐
│ Oracle: 1050건 (50건 추가됨)        │
│ ↓ WHERE created_date > '10:00'     │
│ PostgreSQL: +50건 UPSERT            │
│ (50건만 확인, 나머지 999건 무시)     │
└─────────────────────────────────────┘

시간: 10:20 - 2차 동기화
┌─────────────────────────────────────┐
│ Oracle: 1100건 (50건 추가)          │
│ ↓ WHERE created_date > '10:10'     │
│ PostgreSQL: +50건 UPSERT            │
│ (50건만 확인)                       │
└─────────────────────────────────────┘
```

### 상세 로직

```python
# 1. PostgreSQL에서 마지막 동기화 시간 조회
last_sync_time = "SELECT MAX(created_date) FROM postgres_table"
# 결과: 2024-10-17 10:10:00

# 2. Oracle에서 변경된 데이터만 조회
query = """
    SELECT * FROM oracle_table
    WHERE created_date > :last_sync
    ORDER BY created_date
"""
# 10:10 이후 데이터만 가져옴 (50건)

# 3. PostgreSQL에 UPSERT
for row in new_rows:
    """
    INSERT INTO postgres_table VALUES (...) 
    ON CONFLICT (primary_key)
    DO UPDATE SET ...
    """
```

### 장점
- ✅ **매우 빠름**: 변경된 데이터만 처리
- ✅ **효율적**: 네트워크 부하 최소화
- ✅ **확장 가능**: 데이터가 많아도 속도 유지

### 단점
- ⚠️ **타임스탬프 컬럼 필수**: CREATED_DATE, UPDATED_AT 등
- ⚠️ **삭제 감지 불가**: Oracle에서 삭제된 데이터는 동기화 안 됨
- ⚠️ **시간 동기화 필요**: Oracle과 PostgreSQL 시간 일치 필요

### 사용 시나리오
```
✅ 추천:
- 대용량 데이터 (100만+ 건)
- INSERT/UPDATE만 발생
- 실시간 동기화 필요

❌ 비추천:
- 타임스탬프 컬럼 없음
- DELETE가 빈번함
- 데이터 무결성 완벽 보장 필요
```

---

## 2. 전체 동기화 (Full)

### 작동 방식

```
시간: 10:00 - 초기 마이그레이션
┌─────────────────────────────────────┐
│ Oracle: 1000건                      │
│ ↓                                   │
│ PostgreSQL: 1000건 INSERT           │
└─────────────────────────────────────┘

시간: 10:10 - 1차 동기화 (10분 후)
┌─────────────────────────────────────┐
│ Oracle: 1050건                      │
│ ↓ SELECT * (전체 조회)              │
│ PostgreSQL:                         │
│   1. TRUNCATE TABLE (기존 삭제)     │
│   2. INSERT 1050건 (전체 재삽입)    │
└─────────────────────────────────────┘

시간: 10:20 - 2차 동기화
┌─────────────────────────────────────┐
│ Oracle: 1100건                      │
│ ↓ SELECT * (전체 조회)              │
│ PostgreSQL:                         │
│   1. TRUNCATE TABLE                 │
│   2. INSERT 1100건                  │
└─────────────────────────────────────┘
```

### 상세 로직

```python
# 1. Oracle에서 전체 데이터 조회
query = "SELECT * FROM oracle_table"
all_rows = oracle_cursor.fetchall()  # 1100건 전체

# 2. PostgreSQL 테이블 비우기
postgres_cursor.execute("TRUNCATE TABLE postgres_table")

# 3. 전체 데이터 재삽입
for batch in batches(all_rows, 1000):
    postgres_cursor.executemany("INSERT ...", batch)
```

### 장점
- ✅ **단순함**: 조건 없이 전체 복사
- ✅ **완전 동기화**: 삭제도 반영됨
- ✅ **타임스탬프 불필요**: 어떤 테이블이든 가능

### 단점
- ❌ **느림**: 매번 전체 데이터 처리
- ❌ **네트워크 부하**: 모든 데이터 전송
- ❌ **순간 다운타임**: TRUNCATE 시 데이터 없음

### 사용 시나리오
```
✅ 추천:
- 소규모 데이터 (10만 건 미만)
- DELETE가 빈번함
- 완전한 일치 보장 필요
- 타임스탬프 컬럼 없음

❌ 비추천:
- 대용량 데이터
- 실시간 서비스 중인 테이블
- 빈번한 동기화 (1분마다 등)
```

---

## 3. 삭제 후 재삽입 (Delete & Insert)

### 작동 방식

```
시간: 10:00 - 초기 마이그레이션
┌─────────────────────────────────────┐
│ Oracle: 1000건                      │
│ ↓                                   │
│ PostgreSQL: 1000건 INSERT           │
└─────────────────────────────────────┘

시간: 10:10 - 1차 동기화 (10분 후)
┌─────────────────────────────────────┐
│ Oracle: 1050건                      │
│ ↓                                   │
│ PostgreSQL:                         │
│   1. DROP TABLE (테이블 삭제)       │
│   2. CREATE TABLE (DDL 재생성)      │
│   3. CREATE INDEX (인덱스 재생성)   │
│   4. INSERT 1050건 (전체 삽입)      │
└─────────────────────────────────────┘
```

### 상세 로직

```python
# 1. PostgreSQL 테이블 삭제
postgres_conn.execute("DROP TABLE IF EXISTS postgres_table CASCADE")

# 2. DDL 재생성
columns = oracle_conn.get_table_columns(owner, table_name)
pk = oracle_conn.get_primary_key(owner, table_name)
indexes = oracle_conn.get_indexes(owner, table_name)

converter = DDLConverter()
ddl = converter.generate_full_ddl(table_name, columns, pk, indexes)

# 3. 테이블 재생성
postgres_conn.execute(ddl)

# 4. 전체 데이터 삽입
query = "SELECT * FROM oracle_table"
# ... INSERT 1050건
```

### 장점
- ✅ **완전 초기화**: 스키마 변경도 반영
- ✅ **깨끗한 상태**: 인덱스 최적화
- ✅ **간단함**: 복잡한 로직 없음

### 단점
- ❌ **가장 느림**: DDL + 전체 INSERT
- ❌ **다운타임 김**: DROP~CREATE 동안 테이블 없음
- ❌ **권한 필요**: DROP/CREATE 권한 필요

### 사용 시나리오
```
✅ 추천:
- 스키마 변경 있음 (컬럼 추가/삭제)
- 일일/주간 배치 (자정 실행)
- 테스트/개발 환경
- 데이터 무결성 문제 발생

❌ 비추천:
- 운영 중인 테이블
- 빈번한 동기화
- 대용량 데이터
```

---

## 성능 비교 (100만 건 기준)

| 모드 | 초기 | 10분 후<br>(+1000건) | 20분 후<br>(+1000건) | 총 시간 |
|------|------|---------------------|---------------------|---------|
| **증분** | 5분 | **5초** | **5초** | 5분 10초 |
| **전체** | 5분 | **5분** | **5분** | 15분 |
| **삭제+삽입** | 6분 | **6분** | **6분** | 18분 |

--- 

## 실제 예시

### 시나리오 1: 실시간 주문 데이터

**요구사항:**
- 주문 테이블: 1000만 건
- 10분마다 약 1000건 신규 주문
- 기존 주문은 UPDATE 안 됨

**권장:**
```
모드: 증분 (Incremental)
간격: 10분
타임스탬프: ORDER_DATE
```

**이유:**
- 신규 데이터만 1000건씩 동기화
- 매 동기화 5초 소요
- 네트워크 부하 최소

### 시나리오 2: 마스터 데이터 (상품 정보)

**요구사항:**
- 상품 테이블: 10만 건
- 1시간마다 약 100건 변경
- 삭제도 빈번함

**권장:**
```
모드: 전체 (Full)
간격: 1시간
```

**이유:**
- 데이터 적음 (10만 건)
- 삭제 반영 필요
- 1시간마다 3분 소요 (허용 가능)

### 시나리오 3: 일일 배치 (분석용)

**요구사항:**
- 거래 테이블: 5000만 건
- 매일 자정 동기화
- 스키마 변경 가능성

**권장:**
```
모드: 삭제+삽입 (Delete & Insert)
간격: 24시간
실행 시간: 02:00 (새벽)
```

**이유:**
- 하루 한 번이라 시간 여유
- 스키마 변경 자동 반영
- 깨끗한 상태 보장

---

## 모드 선택 플로우차트

```
테이블에 타임스탬프 컬럼이 있나?
├─ Yes → 데이터가 대용량인가? (100만+ 건)
│         ├─ Yes → 증분 동기화 ⭐
│         └─ No → 전체 동기화도 OK
│
└─ No → 삭제가 빈번한가?
          ├─ Yes → 전체 동기화
          └─ No → 스키마 변경이 있나?
                    ├─ Yes → 삭제+삽입
                    └─ No → 전체 동기화
```

---

## 실전 팁

### 1. 증분 동기화 최적화

```sql
-- 타임스탬프 컬럼에 인덱스 생성 (필수!)
CREATE INDEX idx_created_date ON table_name(created_date);
```

### 2. 전체 동기화 최적화

```python
# 동기화 간격 조정
- 10만 건: 10~30분
- 100만 건: 1~2시간
- 1000만+ 건: 증분 모드로 변경 권장
```

### 3. 삭제+삽입 최적화

```python
# 새벽 시간대 실행
간격: 24시간
실행 시간: 02:00
```

---

## GUI 설정 예시

### Tab 4: Sync

**설정 1 (증분):**
```
Sync Interval: 10 minutes
Sync Mode: Incremental (증분)
Timestamp Column: CREATED_DATE
```

**설정 2 (전체):**
```
Sync Interval: 1 hour
Sync Mode: Full (전체)
Timestamp Column: (비워두기)
```

**설정 3 (삭제+삽입):**
```
Sync Interval: 24 hours
Sync Mode: Delete & Insert
Timestamp Column: (비워두기)
```

---

## 요약 테이블

| 특성 | 증분 | 전체 | 삭제+삽입 |
|------|------|------|-----------|
| **속도** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **완전성** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **타임스탬프** | 필수 | 불필요 | 불필요 |
| **삭제 반영** | ❌ | ✅ | ✅ |
| **스키마 변경** | ❌ | ❌ | ✅ |
| **다운타임** | 없음 | 짧음 | 김 |
| **추천 데이터량** | 대용량 | 중소규모 | 중소규모 |
| **추천 간격** | 짧음 | 중간 | 김 |

--- 

## 결론

**일반적인 선택:**
1. 🥇 **증분 동기화**: 대부분의 경우 (빠르고 효율적)
2. 🥈 **전체 동기화**: 삭제 반영 필요할 때
3. 🥉 **삭제+삽입**: 스키마 변경 있을 때

**핵심:**
- 타임스탬프 컬럼 있으면 → **증분**
- 완전한 동기화 필요하면 → **전체**
- 스키마도 동기화하려면 → **삭제+삽입**

---
---

# `VARCHAR2_TIMESTAMP_SUPPORT.md`

# VARCHAR2 타임스탬프 컬럼 지원 가이드

## 개요

Oracle 데이터베이스에서 타임스탬프 컬럼이 `DATE`, `TIMESTAMP` 타입이 아닌 `VARCHAR2` 타입으로 저장되어 있는 경우를 지원합니다.

---

## 지원 타입

### 1. DATE/TIMESTAMP 컬럼 (기존)

```sql
-- Oracle
CREATE TABLE orders (
    order_id NUMBER PRIMARY KEY,
    created_date DATE,
    updated_at TIMESTAMP
);

-- 데이터 예시
INSERT INTO orders VALUES (1, SYSDATE, SYSTIMESTAMP);
```

**처리 방식:**
- 바인드 변수 사용
- 자동 날짜 비교

---

### 2. VARCHAR2 컬럼 (신규 지원)

```sql
-- Oracle
CREATE TABLE orders (
    order_id NUMBER PRIMARY KEY,
    created_date VARCHAR2(14)  # YYYYMMDDHHMMSS
);

-- 데이터 예시
INSERT INTO orders VALUES (1, '20241018143000');  # 2024-10-18 14:30:00
```

**처리 방식:**
- 문자열 비교 사용
- `YYYYMMDDHHMMSS` 형식 가정

---

## 자동 감지 및 처리

프로그램이 자동으로 컬럼 타입을 감지하여 적절한 쿼리를 생성합니다:

### DATE/TIMESTAMP 컬럼

```sql
-- 증분 동기화 쿼리
SELECT * FROM orders
WHERE created_date > :last_sync
ORDER BY created_date;
```

### VARCHAR2 컬럼

```sql
-- 증분 동기화 쿼리
SELECT * FROM orders
WHERE created_date > '20241015143000'
ORDER BY created_date;
```

---

## 사용 방법

### 1. GUI에서 타임스탬프 컬럼 입력

**Tab 4: Sync**

```
Timestamp Column: CREATED_DATE
```

- DATE, TIMESTAMP, VARCHAR2 타입 모두 입력 가능
- 프로그램이 자동으로 타입 감지

### 2. 증분 동기화 시작

프로그램이 자동으로:
1. 컬럼 타입 확인
2. VARCHAR2인 경우 문자열 비교 쿼리 생성
3. DATE/TIMESTAMP인 경우 바인드 변수 쿼리 생성

### 3. 누락 데이터 동기화 (Catchup Sync)

**입력 형식:** `YYYY-MM-DD HH:MI:SS`

예시:
```
2024-10-15 14:30:00
```

**자동 변환:**
- VARCHAR2 컬럼: `20241015143000`으로 자동 변환
- DATE/TIMESTAMP 컬럼: 그대로 사용

---

## 실전 예시

### 시나리오: VARCHAR2 타임스탬프 컬럼 동기화

**Oracle 테이블:**
```sql
CREATE TABLE transactions (
    tx_id NUMBER PRIMARY KEY,
    tx_date VARCHAR2(14),  # YYYYMMDDHHMMSS
    amount NUMBER(10,2)
);

-- 데이터
INSERT INTO transactions VALUES (1, '20241001120000', 1000);
INSERT INTO transactions VALUES (2, '20241015143000', 2000);
INSERT INTO transactions VALUES (3, '20241018153000', 3000);
```

**PostgreSQL 테이블:**
```sql
CREATE TABLE transactions (
    tx_id NUMERIC PRIMARY KEY,
    tx_date VARCHAR(14),  # 동일하게 VARCHAR
    amount NUMERIC(10,2)
);

-- 마이그레이션 후
-- tx_id 1, 2만 있음 (2024-10-15까지 마이그레이션)
```

**동기화 절차:**

1. **Tab 4: Sync 설정**
   ```
   Sync Mode: Incremental (증분)
   Sync Interval: 10 minutes
   Timestamp Column: TX_DATE
   ```

2. **Start Sync 클릭**

3. **자동 갭 감지 팝업**
   ```
   📊 PostgreSQL 마지막 데이터: 20241015143000
   📈 누락된 데이터: 1건

   ❓ 정기 동기화를 시작하기 전에
      누락된 데이터를 먼저 동기화하시겠습니까?

   • 예: 누락 데이터 동기화 → 정기 동기화 시작
   • 아니오: 바로 정기 동기화 시작 (누락 데이터 무시)
   ```

4. **"예" 선택**
   - tx_id 3 (20241018153000) 자동 동기화
   - 완료 후 정기 동기화 시작

---

## 수동 누락 데이터 동기화

**Tab 4: Sync**

```
📅 누락 데이터 동기화 (마이그레이션 후 간격이 있을 때)

마지막 동기화 시간: 2024-10-15 14:30:00

[누락 데이터 동기화 실행]
```

**처리:**
1. 입력: `2024-10-15 14:30:00`
2. 자동 변환: `20241015143000` (VARCHAR2의 경우)
3. 쿼리 실행:
   ```sql
   SELECT COUNT(*)
   FROM transactions
   WHERE tx_date > '20241015143000'
   ```
4. 누락 데이터 UPSERT

---

## 타입별 쿼리 비교

| 컬럼 타입 | Oracle 쿼리 | PostgreSQL 쿼리 |
|-----------|-------------|-----------------|
| **DATE** | `WHERE created_date > :last_sync` | `SELECT MAX(created_date)` |
| **TIMESTAMP** | `WHERE updated_at > :last_sync` | `SELECT MAX(updated_at)` |
| **VARCHAR2** | `WHERE tx_date > '20241015143000'` | `SELECT MAX(tx_date)` |

---

## 주의사항

### VARCHAR2 형식 요구사항

**✅ 지원 형식:**
- `YYYY-MM-DD HH:MI:SS` (예: `'2024-10-18 14:30:00'`)
- `YYYY-MM-DD HH:MI:SS 밀리초` (예: `'2024-10-18 14:30:00 345'`)
- `YYYY-MM-DD` (예: `'2024-10-18'`)
- `YYYYMMDDHHMMSS` (예: `'20241018143000'`)

**핵심 요구사항:**
- YYYY-MM-DD 형식 (앞자리부터 년-월-일 순서)
- 이 순서만 지키면 문자열 비교로 날짜 비교 가능

**⚠️ 비지원 형식:**
- `DD-MM-YYYY` (일이 앞에)
- `MM/DD/YYYY` (미국식)
- 기타 비표준 형식

### 성능 고려사항

**인덱스 생성 필수:**
```sql
# VARCHAR2 타임스탬프 컬럼에 인덱스 생성
CREATE INDEX idx_tx_date ON transactions(tx_date);
```

**이유:**
- 문자열 비교는 인덱스 없이 느림
- 대용량 테이블에서 필수

---

## 코드 동작 원리

### 1. 타입 자동 감지

```python
# src/core/sync_manager.py

# 컬럼 정보 조회
columns = self.oracle_conn.get_table_columns(owner, table_name)
timestamp_col_info = next((col for col in columns
                          if col['name'].upper() == timestamp_column.upper()), None)

# VARCHAR2 여부 확인
is_varchar = timestamp_col_info and 'VARCHAR' in timestamp_col_info['data_type'].upper()
```

### 2. 쿼리 생성

```python
if is_varchar:
    # VARCHAR2: 문자열 비교
    query = f"""
        SELECT {columns_str}
        FROM {owner}.{table_name}
        WHERE {timestamp_column} > '{last_sync}'
        ORDER BY {timestamp_column}
    """
    oracle_cursor.execute(query)
else:
    # DATE/TIMESTAMP: 바인드 변수
    query = f"""
        SELECT {columns_str}
        FROM {owner}.{table_name}
        WHERE {timestamp_column} > :last_sync
        ORDER BY {timestamp_column}
    """
    oracle_cursor.execute(query, {{'last_sync': last_sync}})
```

---

## 트러블슈팅

### 문제 1: 누락 데이터가 감지되지 않음

**원인:**
- VARCHAR2 형식이 다름
- 타임존 차이

**해결:**
```sql
# Oracle에서 데이터 확인
SELECT tx_date FROM transactions ORDER BY tx_date DESC FETCH FIRST 5 ROWS ONLY;

# PostgreSQL에서 데이터 확인
SELECT tx_date FROM transactions ORDER BY tx_date DESC LIMIT 5;

# 형식이 동일한지 확인
```

### 문제 2: 동기화가 너무 느림

**원인:**
- VARCHAR2 컬럼에 인덱스 없음

**해결:**
```sql
# 인덱스 생성
CREATE INDEX idx_timestamp ON table_name(timestamp_column);
```

### 문제 3: 문자열 비교 오류

**원인:**
- VARCHAR2 데이터에 NULL 또는 빈 문자열

**해결:**
```sql
# NULL 값 확인
SELECT COUNT(*) FROM table_name WHERE timestamp_column IS NULL;

# 빈 문자열 확인
SELECT COUNT(*) FROM table_name WHERE LENGTH(timestamp_column) < 14;

# 데이터 정리
UPDATE table_name
SET timestamp_column = '00000000000000'
WHERE timestamp_column IS NULL;
```

---

## 권장사항

### 1. 새 프로젝트

- ✅ **권장:** DATE 또는 TIMESTAMP 타입 사용
- ❌ **비권장:** VARCHAR2 타입

**이유:**
- 날짜 함수 사용 가능
- 인덱스 효율 좋음
- 타입 안정성

### 2. 기존 시스템 (VARCHAR2 사용 중)

- ✅ 그대로 사용 가능 (이 프로그램이 지원)
- ✅ 인덱스 생성 필수
- ⚠️ 형식 통일 확인 (YYYYMMDDHHMMSS)

### 3. 마이그레이션 시

**옵션 1: VARCHAR2 유지**
```sql
# Oracle
tx_date VARCHAR2(14)

# PostgreSQL
tx_date VARCHAR(14)
```

**옵션 2: TIMESTAMP로 변환 (권장)**
```sql
# Oracle
tx_date VARCHAR2(14)

# PostgreSQL
tx_date TIMESTAMP

# 변환 로직 필요
```

---

## 요약

| 기능 | DATE/TIMESTAMP | VARCHAR2 |
|------|----------------|----------|
| **자동 감지** | ✅ | ✅ |
| **증분 동기화** | ✅ | ✅ |
| **누락 데이터 동기화** | ✅ | ✅ |
| **문자열 비교** | ❌ | ✅ |
| **날짜 함수** | ✅ | ❌ |
| **인덱스 효율** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **권장 여부** | ✅ 권장 | ⚠️ 레거시 지원 |

**핵심:**
- 프로그램이 DATE, TIMESTAMP, VARCHAR2 모두 자동 지원
- 사용자는 컬럼명만 입력하면 됨
- VARCHAR2는 YYYYMMDDHHMMSS 형식 필수
- 인덱스 생성 권장

---
---

# `MIGRATION_RESUME_GUIDE.md`

# 마이그레이션 재개 기능 가이드

## 현재 방식의 문제점

### ❌ 문제 상황
```
Oracle → PostgreSQL 마이그레이션 중...
├─ 배치 1: 1000건 ✅ 완료
├─ 배치 2: 1000건 ✅ 완료
├─ 배치 3: 1000건 ✅ 완료
├─ 배치 4: 1000건 ❌ 오류 발생!
└─ 재시작 → 배치 1부터 다시 시작... 😢
```

**문제:**
- 이미 성공한 3000건도 다시 처리
- 시간 낭비
- 중복 INSERT 오류 가능

---

## 해결 방법

### 방법 1: Primary Key 기반 UPSERT (현재 사용 중)

**장점:**
- ✅ 중복 걱정 없음
- ✅ 재시작해도 안전
- ✅ 이미 존재하는 데이터는 UPDATE

**단점:**
- ⚠️ 모든 데이터를 다시 확인 (느림)
- ⚠️ Primary Key 필수

**코드:**
```sql
INSERT INTO table (col1, col2)
VALUES (val1, val2)
ON CONFLICT (pk_col)
DO UPDATE SET col2 = EXCLUDED.col2;
```

### 방법 2: 체크포인트 테이블 (추천)

**개념:**
```
_migration_checkpoint 테이블:
┌────────────┬─────────────┬──────────────┬──────────┐
│ table_name │ last_pk_val │ migrated_rows│ status   │
├────────────┼─────────────┼──────────────┼──────────┤
│ EMPLOYEES  │ 3000        │ 3000         │ running  │
└────────────┴─────────────┴──────────────┴──────────┘
```

**작동 방식:**
1. 마이그레이션 시작 → checkpoint 테이블 확인
2. 마지막 PK 값부터 재개
3. 1000건마다 checkpoint 업데이트
4. 실패 시 → checkpoint부터 재시작

**쿼리 예시:**
```sql
-- 재개 시
SELECT * FROM EMPLOYEES
WHERE EMPLOYEE_ID > 3000  # 마지막 체크포인트
ORDER BY EMPLOYEE_ID;
```

**장점:**
- ✅ 빠름 (이미 완료된 건 스킵)
- ✅ 정확한 재개 지점
- ✅ 진행 상황 시각화

**단점:**
- ⚠️ Primary Key 필수
- ⚠️ Primary Key가 순차적이어야 함

### 방법 3: ROWNUM/OFFSET 기반

**개념:**
```sql
-- 1차: OFFSET 0, LIMIT 1000
-- 2차: OFFSET 1000, LIMIT 1000
-- 3차: OFFSET 2000, LIMIT 1000
-- ...
```

**장점:**
- ✅ Primary Key 불필요

**단점:**
- ❌ 매우 느림 (OFFSET 커질수록)
- ❌ Oracle에서 비효율적

---

## 권장 방법

### 대용량 데이터 (100만+ 건)

**1단계: 범위 분할**
```python
# 날짜 범위로 나눠서 마이그레이션
migrator.migrate_with_date_range(
    owner="SYSTEM",
    table_name="ORDERS",
    date_column="ORDER_DATE",
    start_date="2024-01-01",
    end_date="2024-02-01"
)

# 다음 범위
migrator.migrate_with_date_range(
    start_date="2024-02-01",
    end_date="2024-03-01"
)
```

**2단계: 실패 시 해당 범위만 재시도**

### 중간 규모 데이터 (10만~100만 건)

**Primary Key 기반 UPSERT 사용:**
```python
# 재시작해도 안전 (자동 UPSERT)
migrator.migrate_table(
    owner="SYSTEM",
    table_name="EMPLOYEES"
)
```

### 소규모 데이터 (10만 건 미만)

**한 번에 마이그레이션:**
```python
# 빠르게 완료
migrator.migrate_table(
    owner="SYSTEM",
    table_name="SMALL_TABLE"
)
```

---

## 실전 예시

### 시나리오: 1억 건 주문 데이터 마이그레이션

```python
# 1. 월별로 분할
dates = [
    ("2024-01-01", "2024-02-01"),
    ("2024-02-01", "2024-03-01"),
    ("2024-03-01", "2024-04-01"),
    # ...
]

# 2. 각 범위별 마이그레이션
for start, end in dates:
    try:
        migrator.migrate_with_date_range(
            owner="SYSTEM",
            table_name="ORDERS",
            date_column="ORDER_DATE",
            start_date=start,
            end_date=end
        )
        print(f"✅ {start}~{end} 완료")
    except Exception as e:
        print(f"❌ {start}~{end} 실패: {e}")
        # 실패한 범위만 재시도
        continue
```

**장점:**
- 실패해도 해당 월만 재시도
- 병렬 처리 가능
- 진행 상황 명확

---

## GUI에서 사용 방법

### Tab 3: Migration

**일반 마이그레이션:**
- ☑ Overwrite existing table
- Batch Size: 1000
- [Start Migration] → 자동 UPSERT

**실패 시:**
1. 오류 메시지 확인
2. 문제 해결 (네트워크, 권한 등)
3. [Start Migration] 다시 클릭
4. ✅ 이미 있는 데이터는 자동 업데이트

**대용량 데이터:**
1. 날짜/범위별로 나눠서 여러 번 실행
2. WHERE 조건 활용
3. 각 범위별 검증

---

## 현재 구현 상태

### ✅ 구현됨
- 배치 처리
- 실패 시 개별 재시도
- UPSERT 지원 (동기화 모드)
- 진행률 추적

### 🚧 개발 예정
- 체크포인트 테이블
- 자동 범위 분할
- 병렬 마이그레이션

---

## 요약

| 방법 | 속도 | 안정성 | 재개 | PK 필요 |
|------|------|--------|------|---------|
| UPSERT | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Yes |
| Checkpoint | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Yes |
| OFFSET | ⭐ | ⭐⭐ | ⭐⭐⭐⭐ | No |
| 범위 분할 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | No |

**현재 추천:**
- **일반적인 경우**: UPSERT 방식 (재시작 안전)
- **대용량**: 날짜/범위 분할
- **향후**: 체크포인트 테이블 추가 예정

---
---

# `AUTO_CATCHUP_SYNC_GUIDE.md`

# 자동 캐치업 동기화 가이드

## 개요

증분 동기화 시작 시 PostgreSQL의 현재 상태를 확인하여 누락된 데이터를 자동으로 감지하고, 사용자에게 먼저 동기화할지 물어보는 기능입니다.

---

## 문제 상황

### 기존 방식의 불편함

```
Day 1 (10:00): 마이그레이션 완료
├─ Oracle: 1,000건
└─ PostgreSQL: 1,000건 ✅

Day 1 (10:00 ~ 12:00): 동기화 미실행
├─ Oracle: +500건 추가됨 (총 1,500건)
└─ PostgreSQL: 여전히 1,000건 ❌

Day 1 (12:00): 동기화 시작
└─ 문제: 10:00 ~ 12:00 사이 500건 누락!
```

**사용자 작업:**
1. 수동으로 누락 데이터 확인
2. "누락 데이터 동기화" 기능 사용
3. 마지막 시간 입력
4. 동기화 실행
5. 완료 후 정기 동기화 시작

---

## 새로운 자동 방식

### 자동 감지 및 제안

```
Day 1 (12:00): 동기화 시작 버튼 클릭

[자동 확인 중...]
📊 PostgreSQL 마지막 데이터: 2024-10-18 10:00:00
📈 누락된 데이터: 500건

❓ 정기 동기화를 시작하기 전에
   누락된 데이터를 먼저 동기화하시겠습니까?

• 예: 누락 데이터 동기화 → 정기 동기화 시작
• 아니오: 바로 정기 동기화 시작 (누락 데이터 무시)

[예] [아니오]
```

**사용자 선택:**
- **예:** 500건 동기화 → 정기 동기화 시작 (간격 10분)
- **아니오:** 바로 정기 동기화 시작 (500건은 영구 누락)

---

## 작동 원리

### 1. 증분 동기화 시작 시

```python
# 사용자가 "Start Sync" 버튼 클릭
start_sync()
    ↓
# 증분 모드 && 타임스탬프 컬럼 있음?
if sync_mode == INCREMENTAL and timestamp_column:
    ↓
    # 자동 갭 확인
    check_sync_gap()
        ↓
        # PostgreSQL MAX(timestamp) 조회
        pg_last_time = SELECT MAX(timestamp_column) FROM pg_table

        # Oracle에서 누락 건수 확인
        missing_count = SELECT COUNT(*) FROM table
                        WHERE timestamp_column > pg_last_time
        ↓
    # 누락 데이터 있음?
    if missing_count > 0:
        ↓
        # 사용자에게 확인 요청
        [팝업 표시]
            ↓
        # 사용자가 "예" 선택?
        if user_clicked_yes:
            ↓
            # 캐치업 동기화 실행
            run_catchup_sync()
            ↓
            [완료 메시지]
    ↓
# 정기 동기화 시작
start_regular_sync()
```

---

## 사용 예시

### 시나리오 1: 마이그레이션 후 다음 날 동기화

**Day 1 (09:00): 마이그레이션**
```
Oracle → PostgreSQL
총 100만 건 이관 완료
마지막 데이터: 2024-10-18 09:00:00
```

**Day 1 (09:00 ~ 18:00): 업무 계속**
```
Oracle에 신규 데이터 1만 건 추가
현재 총 101만 건
```

**Day 1 (18:00): 동기화 시작**

1. **Tab 4: Sync 설정**
   ```
   Sync Mode: Incremental (증분)
   Sync Interval: 10 minutes
   Timestamp Column: CREATED_DATE
   ```

2. **"Start Sync" 클릭**

3. **자동 팝업 표시**
   ```
   📊 PostgreSQL 마지막 데이터: 2024-10-18 09:00:00
   📈 누락된 데이터: 10,000건

   ❓ 정기 동기화를 시작하기 전에
      누락된 데이터를 먼저 동기화하시겠습니까?

   • 예: 누락 데이터 동기화 → 정기 동기화 시작
   • 아니오: 바로 정기 동기화 시작 (누락 데이터 무시)
   ```

4. **"예" 선택**

5. **캐치업 진행**
   ```
   [로그]
   [18:00:00] 증분 동기화: 누락 데이터 확인 중...
   [18:00:01] 캐치업 동기화 시작: 10,000건
   [18:00:15] ✅ 캐치업 완료: 10,000건 동기화

   [팝업]
   누락 데이터 동기화 완료!

   동기화된 행: 10,000건

   이제 정기 동기화를 시작합니다.
   ```

6. **정기 동기화 시작**
   ```
   [로그]
   [18:00:16] 정기 동기화 시작: T_ORDERS, 간격: 10분, 모드: incremental
   [18:10:16] 동기화 완료: T_ORDERS, 모드: incremental, 150행, 성공
   [18:20:16] 동기화 완료: T_ORDERS, 모드: incremental, 180행, 성공
   ...
   ```

---


### 시나리오 2: 누락 데이터 없음

**상황:**
- 마이그레이션 직후 바로 동기화 시작
- PostgreSQL 마지막 데이터가 최신

**동작:**
1. **"Start Sync" 클릭**

2. **자동 확인**
   ```
   [로그]
   [09:05:00] 증분 동기화: 누락 데이터 확인 중...
   [09:05:01] 누락 데이터 없음 - 정기 동기화 바로 시작
   [09:05:01] 동기화 시작: T_ORDERS, 간격: 10분, 모드: incremental
   ```

3. **팝업 표시 안 됨** (사용자 방해 없음)

---


### 시나리오 3: 사용자가 "아니오" 선택

**상황:**
- 누락 데이터 500건 있음
- 사용자가 나중에 수동으로 처리하고 싶음

**동작:**
1. **팝업에서 "아니오" 선택**

2. **즉시 정기 동기화 시작**
   ```
   [로그]
   [14:00:00] 증분 동기화: 누락 데이터 확인 중...
   [14:00:01] 누락 데이터 500건 감지 (사용자 건너뜀)
   [14:00:01] 정기 동기화 시작: T_ORDERS, 간격: 10분
   ```

3. **누락된 500건은 동기화 안 됨**
   - 나중에 수동으로 "누락 데이터 동기화" 기능 사용 가능

---

## 기능 상세

### 자동 감지 조건

**감지 실행:**
- ✅ 동기화 모드: **Incremental (증분)**
- ✅ 타임스탬프 컬럼 입력됨
- ✅ PostgreSQL 테이블에 데이터 존재

**감지 안 함:**
- ❌ 동기화 모드: Full 또는 Delete & Insert
- ❌ 타임스탬프 컬럼 미입력
- ❌ PostgreSQL 테이블 비어있음 (첫 마이그레이션)

### 갭 확인 로직

```python
# src/core/sync_manager.py

def check_sync_gap(self, owner, table_name, timestamp_column):
    # 1. PostgreSQL 마지막 타임스탬프 조회
    pg_last_time = SELECT MAX(timestamp_column) FROM pg_table

    # 2. 컬럼 타입 확인 (VARCHAR2 vs DATE/TIMESTAMP)
    is_varchar = check_column_type(timestamp_column)

    # 3. Oracle에서 누락 건수 확인
    if is_varchar:
        # VARCHAR2: 문자열 비교
        missing_count = SELECT COUNT(*)
                        WHERE timestamp_column > 'pg_last_time'
    else:
        # DATE/TIMESTAMP: 날짜 비교
        missing_count = SELECT COUNT(*)
                        WHERE timestamp_column > :pg_last_time

    # 4. 결과 반환
    return {
        'has_gap': missing_count > 0,
        'pg_last_time': pg_last_time,
        'missing_count': missing_count,
        'is_varchar': is_varchar
    }
```

### 캐치업 실행 로직

```python
# src/gui/main_window.py

if gap_info['has_gap']:
    # 사용자 확인
    reply = show_confirmation_dialog()

    if reply == YES:
        # 증분 동기화 한 번 실행
        result = sync_manager._incremental_sync(
            owner, table_name, timestamp_column
        )

        if result['success']:
            show_success_message(result['rows_affected'])
        else:
            show_error_message(result['error'])

# 정기 동기화 시작 (캐치업 여부 무관)
start_regular_sync()
```

---

## 수동 캐치업과 비교

### 자동 캐치업 (신규)

**특징:**
- ✅ 동기화 시작 시 자동 감지
- ✅ 시간 입력 불필요
- ✅ 누락 건수 자동 계산
- ✅ 한 번의 클릭으로 완료

**사용:**
```
1. Tab 4: Sync 설정
2. "Start Sync" 클릭
3. 팝업에서 "예" 선택
4. 완료!
```

---

### 수동 캐치업 (기존)

**특징:**
- ⚠️ 사용자가 직접 시간 입력
- ⚠️ 별도 버튼 클릭 필요
- ⚠️ 정기 동기화와 별개

**사용:**
```
1. Tab 4: Sync
2. "마지막 동기화 시간" 입력
3. "누락 데이터 동기화 실행" 클릭
4. 완료 후 다시 "Start Sync" 클릭
```

**언제 사용?**
- 정기 동기화 실행 중 누락 발견
- 특정 시간 범위만 동기화 필요

---

## 로그 예시

### 성공 케이스

```
[2024-10-18 14:00:00] 증분 동기화: 누락 데이터 확인 중...
[2024-10-18 14:00:01] 캐치업 동기화 시작: 10,000건
[2024-10-18 14:00:15] ✅ 캐치업 완료: 10,000건 동기화
[2024-10-18 14:00:16] 동기화 시작: T_ORDERS, 간격: 10분, 모드: incremental
```

### 누락 없음 케이스

```
[2024-10-18 09:05:00] 증분 동기화: 누락 데이터 확인 중...
[2024-10-18 09:05:01] 누락 데이터 없음 - 정기 동기화 바로 시작
[2024-10-18 09:05:01] 동기화 시작: T_ORDERS, 간격: 10분, 모드: incremental
```

### 사용자 거부 케이스

```
[2024-10-18 14:00:00] 증분 동기화: 누락 데이터 확인 중...
[2024-10-18 14:00:01] 동기화 시작: T_ORDERS, 간격: 10분, 모드: incremental
```

---

## 성능 영향

### 갭 확인 쿼리

**PostgreSQL:**
```sql
SELECT MAX(timestamp_column) FROM table_name;
```
- 인덱스 사용 시: **빠름** (< 1초)
- 인덱스 없을 시: **느림** (테이블 스캔)

**Oracle:**
```sql
SELECT COUNT(*)
FROM table_name
WHERE timestamp_column > :pg_last_time;
```
- 인덱스 사용 시: **빠름** (< 1초)
- 인덱스 없을 시: **매우 느림** (수십 초)

### 권장사항

**인덱스 생성:**
```sql
# Oracle
CREATE INDEX idx_timestamp ON table_name(timestamp_column);

# PostgreSQL
CREATE INDEX idx_timestamp ON table_name(timestamp_column);
```

**예상 시간:**
```
인덱스 있음:
- 갭 확인: 1초
- 캐치업 (1만 건): 10~15초
- 총: 약 15초

인덱스 없음:
- 갭 확인: 30초+
- 캐치업 (1만 건): 10~15초
- 총: 약 45초+
```

---

## FAQ

### Q1. 누락 데이터가 너무 많으면 어떻게 되나요?

**A:** 캐치업 시간이 오래 걸릴 수 있습니다.

**권장:**
- 100만 건 이상: 수동으로 날짜 범위 분할
- 10만~100만 건: 자동 캐치업 사용 가능
- 1만 건 이하: 빠르게 완료

**대용량 데이터 처리:**
```python
# 날짜 범위별로 나눠서 수동 실행
ranges = [
    ('2024-10-01', '2024-10-10'),
    ('2024-10-10', '2024-10-15'),
    ('2024-10-15', '2024-10-18')
]

for start, end in ranges:
    # 각 범위별 마이그레이션 실행
    ...
```

---


### Q2. "아니오"를 선택하면 영구적으로 누락되나요?

**A:** 네, 증분 동기화에서는 과거 데이터를 자동으로 가져오지 않습니다.

**해결 방법:**
1. 수동 "누락 데이터 동기화" 기능 사용
2. 또는 Full 동기화 한 번 실행

---


### Q3. 캐치업 중 오류가 발생하면?

**A:** 정기 동기화는 계속 진행됩니다.

**동작:**
```
캐치업 실패
    ↓
[경고 팝업 표시]
    ↓
정기 동기화 시작 (중단 안 됨)
```

**로그:**
```
[14:00:15] 캐치업 동기화 실패: ORA-12154: TNS:could not resolve...
[14:00:15] 정기 동기화 시작: T_ORDERS, 간격: 10분, 모드: incremental
```

---


### Q4. VARCHAR2 타임스탬프 컬럼도 지원하나요?

**A:** 네, 자동으로 감지하고 처리합니다.

**지원:**
- DATE, TIMESTAMP: 날짜 비교
- VARCHAR2: 문자열 비교 (YYYYMMDDHHMMSS 형식)

**참고:** [VARCHAR2_TIMESTAMP_SUPPORT.md](VARCHAR2_TIMESTAMP_SUPPORT.md)

---

## 비활성화 방법

자동 캐치업을 원하지 않는 경우:

**옵션 1: 타임스탬프 컬럼 비우기**
```
Timestamp Column: [비워두기]
```
→ 전체 동기화로 전환됨

**옵션 2: Full 모드 사용**
```
Sync Mode: Full (전체)
```
→ 자동 캐치업 안 함

**옵션 3: 팝업에서 "아니오" 선택**
→ 바로 정기 동기화 시작

---

## 요약

| 기능 | 자동 캐치업 | 수동 캐치업 |
|------|-------------|-------------|
| **실행 시점** | 동기화 시작 시 | 수동 버튼 클릭 |
| **시간 입력** | 불필요 (자동) | 필요 |
| **건수 확인** | 자동 | 수동 |
| **편의성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **정확성** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **사용 시점** | 첫 동기화 시작 | 동기화 실행 중 |

**핵심 장점:**
1. ✅ 한 번의 클릭으로 완료
2. ✅ 시간 입력 불필요
3. ✅ 누락 데이터 자동 감지
4. ✅ 정기 동기화 전 자동 실행
5. ✅ VARCHAR2 컬럼 자동 지원

**사용자 경험:**
```
기존 방식:
1. 동기화 시작
2. 누락 발견
3. 수동으로 시간 계산
4. 누락 데이터 동기화 버튼 클릭
5. 다시 동기화 시작

새 방식:
1. 동기화 시작
2. 팝업에서 "예" 클릭
3. 완료!
```
