"""
메인 GUI 윈도우
"""

import sys
import logging
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QTableWidget, QTableWidgetItem, QComboBox, QSpinBox,
    QMessageBox, QProgressBar, QGroupBox, QCheckBox, QFileDialog,
    QFrame, QFormLayout, QGridLayout, QHeaderView, QAbstractItemView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from src.core.db_connection import OracleConfig, PostgresConfig, OracleConnection, PostgresConnection
from src.core.ddl_converter import DDLConverter
from src.core.data_migrator import DataMigrator, MigrationProgress
from src.core.sync_manager import SyncManager, SyncMode, SyncStatus
from src.utils.config import ConfigManager
from PyQt5.QtCore import QTimer

logger = logging.getLogger(__name__)


class MigrationWorker(QThread):
    """백그라운드 마이그레이션 작업 스레드"""
    progress_updated = pyqtSignal(object)  # MigrationProgress 객체
    finished = pyqtSignal(object)  # 최종 결과
    error = pyqtSignal(str)  # 오류 메시지

    def __init__(self, migrator, owner, table_name):
        super().__init__()
        self.migrator = migrator
        self.owner = owner
        self.table_name = table_name

    def run(self):
        try:
            result = self.migrator.migrate_table(
                self.owner,
                self.table_name,
                progress_callback=lambda prog: self.progress_updated.emit(prog)
            )
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"마이그레이션 오류: {str(e)}")
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """메인 윈도우"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Oracle to PostgreSQL Migration Tool")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        self.config_manager = ConfigManager()
        self.oracle_conn = None
        self.postgres_conn = None
        self.migration_worker = None
        self.sync_manager = None
        self.sync_status_timer = QTimer()
        self.sync_status_timer.timeout.connect(self.update_sync_status)

        self.apply_modern_style()
        self.init_ui()

    def apply_modern_style(self):
        """모던하고 세련된 스타일 적용"""
        style = """
        /* 전역 스타일 */
        QWidget {
            font-size: 14px;
            font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
            background-color: #f5f6fa;
        }

        QMainWindow {
            background-color: #f5f6fa;
        }

        /* 탭 위젯 */
        QTabWidget::pane {
            border: 2px solid #dcdde1;
            border-radius: 8px;
            background-color: white;
            padding: 10px;
        }

        QTabBar::tab {
            background-color: #dcdde1;
            color: #2f3640;
            padding: 12px 30px;
            margin-right: 4px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-size: 15px;
            font-weight: 600;
            min-width: 120px;
        }

        QTabBar::tab:selected {
            background-color: white;
            color: #0984e3;
            border-bottom: 3px solid #0984e3;
        }

        QTabBar::tab:hover {
            background-color: #e1e2e6;
        }

        /* 그룹박스 */
        QGroupBox {
            font-size: 16px;
            font-weight: 600;
            color: #2f3640;
            border: 2px solid #dcdde1;
            border-radius: 8px;
            margin-top: 16px;
            padding-top: 20px;
            background-color: white;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            left: 20px;
            padding: 4px 12px;
            background-color: white;
            color: #0984e3;
        }

        /* 레이블 */
        QLabel {
            font-size: 14px;
            color: #2f3640;
            background-color: transparent;
        }

        /* 입력 필드 */
        QLineEdit {
            padding: 10px 12px;
            border: 2px solid #dcdde1;
            border-radius: 6px;
            background-color: white;
            color: #2f3640;
            font-size: 14px;
            selection-background-color: #0984e3;
            selection-color: white;
        }

        QLineEdit:focus {
            border: 2px solid #0984e3;
            background-color: #f8f9fa;
            color: #2f3640;
        }

        QLineEdit:disabled {
            background-color: #ecf0f1;
            color: #95a5a6;
        }

        /* 콤보박스 */
        QComboBox {
            padding: 10px 12px;
            border: 2px solid #dcdde1;
            border-radius: 6px;
            background-color: white;
            color: #2f3640;
            font-size: 14px;
        }

        QComboBox:focus {
            border: 2px solid #0984e3;
            color: #2f3640;
        }

        QComboBox::drop-down {
            border: none;
            width: 30px;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid #2f3640;
            margin-right: 10px;
        }

        QComboBox QAbstractItemView {
            border: 2px solid #dcdde1;
            border-radius: 6px;
            background-color: white;
            color: #2f3640;
            selection-background-color: #0984e3;
            selection-color: white;
            padding: 6px;
            font-size: 14px;
        }

        /* 스핀박스 */
        QSpinBox {
            padding: 10px 12px;
            border: 2px solid #dcdde1;
            border-radius: 6px;
            background-color: white;
            color: #2f3640;
            font-size: 14px;
        }

        QSpinBox:focus {
            border: 2px solid #0984e3;
            color: #2f3640;
        }

        /* 버튼 */
        QPushButton {
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            background-color: #0984e3;
            color: white;
            font-size: 15px;
            font-weight: 600;
            min-width: 100px;
        }

        QPushButton:hover {
            background-color: #0770c4;
        }

        QPushButton:pressed {
            background-color: #055fa0;
        }

        QPushButton:disabled {
            background-color: #b2bec3;
            color: #636e72;
        }

        /* 체크박스 */
        QCheckBox {
            font-size: 14px;
            color: #2f3640;
            spacing: 8px;
            background-color: transparent;
        }

        QCheckBox::indicator {
            width: 20px;
            height: 20px;
            border: 2px solid #dcdde1;
            border-radius: 4px;
            background-color: white;
        }

        QCheckBox::indicator:checked {
            background-color: #0984e3;
            border-color: #0984e3;
            image: none;
        }

        QCheckBox::indicator:hover {
            border-color: #0984e3;
        }

        /* 텍스트 에디트 */
        QTextEdit {
            border: 2px solid #dcdde1;
            border-radius: 6px;
            background-color: white;
            color: #2f3640;
            font-size: 13px;
            padding: 10px;
        }

        QTextEdit:focus {
            border: 2px solid #0984e3;
            color: #2f3640;
        }

        /* 테이블 */
        QTableWidget {
            border: 2px solid #dcdde1;
            border-radius: 6px;
            background-color: white;
            color: #2f3640;
            gridline-color: #ecf0f1;
            font-size: 14px;
        }

        QTableWidget::item {
            padding: 8px;
            border-bottom: 1px solid #ecf0f1;
            color: #2f3640;
        }

        QTableWidget::item:selected {
            background-color: #e1f0ff;
            color: #2f3640;
        }

        QHeaderView::section {
            background-color: #2f3640;
            color: white;
            padding: 12px;
            border: none;
            font-size: 14px;
            font-weight: 600;
        }

        /* 프로그레스 바 */
        QProgressBar {
            border: 2px solid #dcdde1;
            border-radius: 6px;
            text-align: center;
            background-color: white;
            color: #2f3640;
            height: 28px;
            font-size: 14px;
            font-weight: 600;
        }

        QProgressBar::chunk {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #00b894, stop:1 #00cec9);
            border-radius: 4px;
        }

        /* 스크롤바 */
        QScrollBar:vertical {
            border: none;
            background-color: #f5f6fa;
            width: 12px;
            margin: 0;
        }

        QScrollBar::handle:vertical {
            background-color: #b2bec3;
            border-radius: 6px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #636e72;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar:horizontal {
            border: none;
            background-color: #f5f6fa;
            height: 12px;
            margin: 0;
        }

        QScrollBar::handle:horizontal {
            background-color: #b2bec3;
            border-radius: 6px;
            min-width: 30px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #636e72;
        }

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }

        /* 메시지박스 */
        QMessageBox {
            font-size: 14px;
            background-color: white;
        }

        QMessageBox QPushButton {
            min-width: 80px;
            padding: 10px 20px;
        }
        """
        self.setStyleSheet(style)

    def init_ui(self):
        """UI 초기화"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # 탭 위젯
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # 각 탭 생성
        self.create_home_tab() # 홈 탭 먼저 생성
        self.create_connection_tab()
        self.create_table_selection_tab()
        self.create_migration_tab()
        self.create_sync_tab()
        self.create_log_tab()

        # 탭 변경 시 이벤트 연결
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # 마지막 프로파일 자동 로드
        self.load_last_profile_auto()

    def create_home_tab(self):
        """홈 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        tab.setLayout(layout)

        # 프로파일 관리
        profile_group = QGroupBox("Profile Management")
        profile_group.setMaximumWidth(800)
        profile_layout = QHBoxLayout()
        profile_group.setLayout(profile_layout)

        self.profile_combo = QComboBox()
        self.load_profiles()
        profile_layout.addWidget(QLabel("Profile:"))
        profile_layout.addWidget(self.profile_combo)

        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_profile)
        profile_layout.addWidget(load_btn)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_profile)
        profile_layout.addWidget(save_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_profile)
        profile_layout.addWidget(delete_btn)
        layout.addWidget(profile_group)

        # 작업 선택
        task_group = QGroupBox("Select Task")
        task_group.setMaximumWidth(800)
        task_layout = QHBoxLayout()
        task_group.setLayout(task_layout)

        migrate_btn = QPushButton("Start New Migration")
        migrate_btn.setStyleSheet("font-size: 18px; padding: 20px;")
        migrate_btn.clicked.connect(self._go_to_migration)
        task_layout.addWidget(migrate_btn)

        sync_btn = QPushButton("Start/Manage Sync")
        sync_btn.setStyleSheet("font-size: 18px; padding: 20px;")
        sync_btn.clicked.connect(self._go_to_sync)
        task_layout.addWidget(sync_btn)
        layout.addWidget(task_group)

        self.tabs.addTab(tab, "0. Home")

    def _go_to_migration(self):
        """마이그레이션 탭들로 이동"""
        self.tabs.setCurrentIndex(1) # "1. Connection" 탭으로 이동

    def _go_to_sync(self):
        """동기화 탭으로 이동"""
        self.tabs.setCurrentIndex(4) # "4. Sync" 탭으로 이동


    def on_tab_changed(self, index):
        """탭이 변경될 때 호출됩니다. 2번 탭으로 전환 시 Oracle 사용자 이름을 스키마 필드에 자동으로 채웁니다."""
        # 탭 인덱스 1은 "2. Table Selection" 탭입니다.
        if index == 1:
            oracle_user = self.oracle_user.text()
            if oracle_user:
                self.schema_input.setText(oracle_user.upper())
                self.log(f"Oracle 사용자 이름 '{oracle_user.upper()}'를 스키마 필드에 자동으로 설정했습니다.")


    def create_connection_tab(self):
        """연결 설정 탭"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Oracle과 PostgreSQL을 가로로 나란히 배치
        db_connections_layout = QHBoxLayout()

        # Oracle 연결 설정
        oracle_group = QGroupBox("Oracle")
        oracle_layout = QVBoxLayout()
        oracle_group.setLayout(oracle_layout)

        self.oracle_host = self._create_input_row(oracle_layout, "Host:", "localhost")
        self.oracle_port = self._create_input_row(oracle_layout, "Port:", "1521")
        self.oracle_sid = self._create_input_row(oracle_layout, "SID:", "ORCL")
        self.oracle_service = self._create_input_row(oracle_layout, "Service Name:", "")
        self.oracle_user = self._create_input_row(oracle_layout, "User:", "")
        self.oracle_password = self._create_input_row(oracle_layout, "Password:", "", password=True)

        # Thick 모드 설정
        thick_layout = QHBoxLayout()
        self.oracle_thick_mode = QCheckBox("Thick Mode (Oracle 11g)")
        self.oracle_thick_mode.setChecked(False)
        thick_layout.addWidget(self.oracle_thick_mode)
        oracle_layout.addLayout(thick_layout)

        instant_client_layout = QHBoxLayout()
        instant_client_layout.addWidget(QLabel("Instant Client:"))
        self.oracle_instant_client = QLineEdit()
        instant_client_layout.addWidget(self.oracle_instant_client)
        browse_btn = QPushButton("...")
        browse_btn.setMaximumWidth(50)
        browse_btn.clicked.connect(self.browse_instant_client)
        instant_client_layout.addWidget(browse_btn)
        oracle_layout.addLayout(instant_client_layout)

        # Oracle 연결 테스트 버튼
        oracle_test_btn = QPushButton("Test Connection")
        oracle_test_btn.clicked.connect(self.test_oracle_connection)
        oracle_layout.addWidget(oracle_test_btn)

        db_connections_layout.addWidget(oracle_group)

        # PostgreSQL 연결 설정
        postgres_group = QGroupBox("PostgreSQL")
        postgres_layout = QVBoxLayout()
        postgres_group.setLayout(postgres_layout)

        self.postgres_host = self._create_input_row(postgres_layout, "Host:", "localhost")
        self.postgres_port = self._create_input_row(postgres_layout, "Port:", "5432")
        self.postgres_database = self._create_input_row(postgres_layout, "Database:", "postgres")
        self.postgres_schema = self._create_input_row(postgres_layout, "Schema:", "public")
        self.postgres_user = self._create_input_row(postgres_layout, "User:", "postgres")
        self.postgres_password = self._create_input_row(postgres_layout, "Password:", "", password=True)

        # PostgreSQL 연결 테스트 버튼
        postgres_test_btn = QPushButton("Test Connection")
        postgres_test_btn.clicked.connect(self.test_postgres_connection)
        postgres_layout.addWidget(postgres_test_btn)

        db_connections_layout.addWidget(postgres_group)

        layout.addLayout(db_connections_layout)

        layout.addStretch()

        self.tabs.addTab(tab, "1. Connection")

    def create_table_selection_tab(self):
        """테이블 선택 탭"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # 스키마 선택
        schema_layout = QHBoxLayout()
        schema_layout.addWidget(QLabel("Schema (Owner):"))
        self.schema_input = QLineEdit()
        schema_layout.addWidget(self.schema_input)
        load_tables_btn = QPushButton("Load Tables")
        load_tables_btn.clicked.connect(self.load_tables)
        schema_layout.addWidget(load_tables_btn)
        layout.addLayout(schema_layout)

        # 테이블 목록
        self.table_list = QTableWidget()
        self.table_list.setColumnCount(3)
        self.table_list.setHorizontalHeaderLabels(["Table Name", "Rows", "Comment"])
        self.table_list.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_list.setSelectionMode(QTableWidget.SingleSelection)
        self.table_list.itemSelectionChanged.connect(self.on_table_selected)
        layout.addWidget(self.table_list)

        # 테이블 상세 정보
        detail_group = QGroupBox("Table Details")
        detail_layout = QVBoxLayout()
        detail_group.setLayout(detail_layout)

        self.table_detail_text = QTextEdit()
        self.table_detail_text.setReadOnly(True)
        self.table_detail_text.setMaximumHeight(200)
        detail_layout.addWidget(self.table_detail_text)

        layout.addWidget(detail_group)

        self.tabs.addTab(tab, "2. Table Selection")

    def create_migration_tab(self):
        """마이그레이션 탭"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # DDL 미리보기
        ddl_group = QGroupBox("DDL Preview")
        ddl_layout = QVBoxLayout()
        ddl_group.setLayout(ddl_layout)

        generate_ddl_btn = QPushButton("Generate DDL")
        generate_ddl_btn.clicked.connect(self.generate_ddl)
        ddl_layout.addWidget(generate_ddl_btn)

        self.ddl_text = QTextEdit()
        self.ddl_text.setFont(QFont("Courier New", 10))
        ddl_layout.addWidget(self.ddl_text)

        layout.addWidget(ddl_group)

        # 마이그레이션 설정
        migration_settings_group = QGroupBox("Migration Settings")
        migration_settings_layout = QVBoxLayout()
        migration_settings_group.setLayout(migration_settings_layout)

        self.overwrite_checkbox = QCheckBox("Overwrite existing table")
        migration_settings_layout.addWidget(self.overwrite_checkbox)

        batch_layout = QHBoxLayout()
        batch_layout.addWidget(QLabel("Batch Size:"))
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(100, 10000)
        self.batch_size_spin.setValue(1000)
        self.batch_size_spin.setSingleStep(100)
        batch_layout.addWidget(self.batch_size_spin)
        batch_layout.addStretch()
        migration_settings_layout.addLayout(batch_layout)

        layout.addWidget(migration_settings_group)

        # 실행 버튼
        button_layout = QHBoxLayout()
        self.start_migration_btn = QPushButton("Start Migration")
        self.start_migration_btn.clicked.connect(self.start_migration)
        button_layout.addWidget(self.start_migration_btn)

        self.cancel_migration_btn = QPushButton("Cancel")
        self.cancel_migration_btn.setEnabled(False)
        self.cancel_migration_btn.clicked.connect(self.cancel_migration)
        button_layout.addWidget(self.cancel_migration_btn)

        layout.addLayout(button_layout)

        # 진행 상황
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Ready")
        layout.addWidget(self.progress_label)

        self.tabs.addTab(tab, "3. Migration")

    def create_sync_tab(self):
        """동기화 탭 생성"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        tab.setLayout(layout)

        self.status_card_style_template = (
            "QFrame#StatusCard {{"
            "background-color: {bg};"
            "border: 1px solid #dcdde1;"
            "border-radius: 12px;"
            "padding: 18px;"
            "}}"
        )

        title_label = QLabel("자동 동기화")
        title_label.setStyleSheet("font-size: 22px; font-weight: 700; color: #2f3640;")
        layout.addWidget(title_label)

        subtitle_label = QLabel("Oracle과 PostgreSQL 사이의 동기화 현황을 한눈에 확인하세요.")
        subtitle_label.setWordWrap(True)
        subtitle_label.setStyleSheet("color: #636e72; font-size: 13px;")
        layout.addWidget(subtitle_label)

        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(16)
        self.sync_state_value, self.sync_status_card = self._create_status_card(
            metrics_layout, "상태", "대기 중"
        )
        self.sync_current_table_value, _ = self._create_status_card(
            metrics_layout, "대상 테이블", "미선택"
        )
        self.sync_total_runs_value, _ = self._create_status_card(
            metrics_layout, "누적 실행", "0회"
        )
        self.sync_success_rate_value, _ = self._create_status_card(
            metrics_layout, "성공률", "—"
        )
        metrics_layout.addStretch()
        layout.addLayout(metrics_layout)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        config_group = QGroupBox("동기화 설정")
        config_group_layout = QVBoxLayout()
        config_group.setLayout(config_group_layout)

        config_form = QFormLayout()
        config_form.setSpacing(12)
        config_form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.sync_interval_combo = QComboBox()
        self.sync_interval_combo.addItems([
            "10 minutes",
            "30 minutes",
            "1 hour",
            "2 hours",
            "6 hours",
            "12 hours",
            "24 hours"
        ])
        self.sync_interval_combo.setCurrentIndex(0)
        config_form.addRow("동기화 주기", self.sync_interval_combo)

        self.sync_mode_combo = QComboBox()
        self.sync_mode_combo.addItems([
            "Incremental (증분) - 변경분만 반영",
            "Full (전체) - 전체 데이터 재동기화",
            "Delete & Insert - 전체 삭제 후 재삽입"
        ])
        self.sync_mode_combo.setCurrentIndex(0)
        self.sync_mode_combo.currentIndexChanged.connect(self.on_sync_mode_changed)
        config_form.addRow("동기화 모드", self.sync_mode_combo)

        self.mode_description = QLabel()
        self.mode_description.setWordWrap(True)
        self.mode_description.setStyleSheet("color: #636e72; background-color: #f0f4ff; border-radius: 6px; padding: 8px;")
        config_form.addRow("모드 안내", self.mode_description)

        self.timestamp_column_input = QLineEdit()
        self.timestamp_column_input.setPlaceholderText("예: CREATED_DATE, UPDATED_AT (증분 동기화에 필요)")
        config_form.addRow("타임스탬프 컬럼", self.timestamp_column_input)

        catchup_row_widget = QWidget()
        catchup_row_layout = QHBoxLayout()
        catchup_row_layout.setContentsMargins(0, 0, 0, 0)
        catchup_row_layout.setSpacing(8)
        catchup_row_widget.setLayout(catchup_row_layout)

        self.catchup_datetime_input = QLineEdit()
        self.catchup_datetime_input.setPlaceholderText("YYYY-MM-DD 또는 YYYY-MM-DD HH:MM:SS")
        catchup_row_layout.addWidget(self.catchup_datetime_input)

        self.catchup_btn = QPushButton("누락분 채우기")
        self.catchup_btn.clicked.connect(self.run_catchup_sync)
        self.catchup_btn.setStyleSheet("background-color: #FF9800; color: white; font-weight: bold;")
        catchup_row_layout.addWidget(self.catchup_btn)

        config_form.addRow("Catch-up 시작", catchup_row_widget)

        catchup_help = QLabel("초기 마이그레이션 이후 누락된 데이터를 지정 시점부터 다시 채웁니다.")
        catchup_help.setStyleSheet("color: #95a5a6; font-size: 12px;")
        catchup_help.setWordWrap(True)

        config_group_layout.addLayout(config_form)
        config_group_layout.addWidget(catchup_help)

        button_layout = QHBoxLayout()
        self.start_sync_btn = QPushButton("동기화 시작")
        self.start_sync_btn.clicked.connect(self.start_sync)
        self.start_sync_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 12px 24px;")
        button_layout.addWidget(self.start_sync_btn)

        self.stop_sync_btn = QPushButton("중지")
        self.stop_sync_btn.clicked.connect(self.stop_sync)
        self.stop_sync_btn.setEnabled(False)
        self.stop_sync_btn.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 12px 24px;")
        button_layout.addWidget(self.stop_sync_btn)
        button_layout.addStretch()
        config_group_layout.addLayout(button_layout)

        content_layout.addWidget(config_group, 2)

        status_group = QGroupBox("실시간 상태")
        status_group_layout = QVBoxLayout()
        status_group.setLayout(status_group_layout)

        status_grid = QGridLayout()
        status_grid.setVerticalSpacing(12)
        status_grid.setHorizontalSpacing(16)

        status_grid.addWidget(self._create_status_caption("성공 / 실패"), 0, 0)
        self.sync_success_breakdown_value = QLabel("0 / 0")
        self.sync_success_breakdown_value.setStyleSheet("font-size: 15px; font-weight: 600; color: #2f3640;")
        status_grid.addWidget(self.sync_success_breakdown_value, 0, 1)

        status_grid.addWidget(self._create_status_caption("마지막 동기화"), 1, 0)
        self.sync_last_sync_value = QLabel("—")
        self.sync_last_sync_value.setStyleSheet("font-size: 14px; color: #2f3640;")
        status_grid.addWidget(self.sync_last_sync_value, 1, 1)

        status_grid.addWidget(self._create_status_caption("다음 실행 예정"), 2, 0)
        self.sync_next_sync_value = QLabel("—")
        self.sync_next_sync_value.setStyleSheet("font-size: 14px; color: #2f3640;")
        status_grid.addWidget(self.sync_next_sync_value, 2, 1)

        status_group_layout.addLayout(status_grid)

        self.sync_error_style_muted = (
            "color: #636e72; font-size: 12px; border: 1px dashed #dcdde1; "
            "background-color: #f8f9fb; border-radius: 6px; padding: 8px;"
        )
        self.sync_error_style_alert = (
            "color: #d35400; font-size: 12px; border: 1px solid #ffb074; "
            "background-color: #fff4e6; border-radius: 6px; padding: 8px;"
        )

        self.sync_last_error_label = QLabel()
        self.sync_last_error_label.setWordWrap(True)
        status_group_layout.addWidget(self.sync_last_error_label)
        status_group_layout.addStretch()

        content_layout.addWidget(status_group, 1)

        layout.addLayout(content_layout)

        history_group = QGroupBox("동기화 히스토리")
        history_layout = QVBoxLayout()
        history_group.setLayout(history_layout)

        self.sync_history_table = QTableWidget()
        self.sync_history_table.setColumnCount(5)
        self.sync_history_table.setHorizontalHeaderLabels(["시간", "테이블", "모드", "적용 건수", "상태"])
        header = self.sync_history_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setDefaultSectionSize(140)
        self.sync_history_table.verticalHeader().setVisible(False)
        self.sync_history_table.setAlternatingRowColors(True)
        self.sync_history_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sync_history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        history_layout.addWidget(self.sync_history_table)

        layout.addWidget(history_group)

        self._reset_sync_status_ui()
        self.tabs.addTab(tab, "4. Sync")


    def _create_status_card(self, layout, title, initial_value):
        """작은 지표 카드 위젯 생성"""
        card = QFrame()
        card.setObjectName("StatusCard")
        card.setStyleSheet(self.status_card_style_template.format(bg="#ffffff"))
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet("color: #7f8c8d; font-size: 12px; font-weight: 600;")
        value_label = QLabel(initial_value)
        value_label.setStyleSheet("color: #2f3640; font-size: 22px; font-weight: 700;")

        card_layout.addWidget(title_label)
        card_layout.addWidget(value_label)
        card_layout.addStretch()

        layout.addWidget(card)
        return value_label, card

    def _create_status_caption(self, text):
        """상태 설명 레이블 생성"""
        label = QLabel(text)
        label.setStyleSheet("color: #7f8c8d; font-size: 12px; font-weight: 600;")
        return label

    def _reset_sync_status_ui(self):
        """동기화 상태 UI 초기화"""
        self._set_status_card_state(False, "대기 중")
        self.sync_current_table_value.setText("미선택")
        self.sync_total_runs_value.setText("0회")
        self.sync_success_rate_value.setText("—")
        self.sync_success_breakdown_value.setText("0 / 0")
        self.sync_last_sync_value.setText("—")
        self.sync_next_sync_value.setText("—")
        self._set_last_error(None)

    def _set_status_card_state(self, is_running, label=None):
        """상태 카드 색상 및 텍스트 업데이트"""
        if label is None:
            label = "진행 중" if is_running else "대기 중"
        background = "#e8f5e9" if is_running else "#ffffff"
        text_color = "#27ae60" if is_running else "#7f8c8d"

        self.sync_status_card.setStyleSheet(self.status_card_style_template.format(bg=background))
        self.sync_state_value.setText(label)
        self.sync_state_value.setStyleSheet(f"color: {text_color}; font-size: 22px; font-weight: 700;")

    def _set_last_error(self, error_text):
        """최근 오류 텍스트 및 스타일 적용"""
        if error_text:
            self.sync_last_error_label.setText(error_text)
            self.sync_last_error_label.setStyleSheet(self.sync_error_style_alert)
        else:
            self.sync_last_error_label.setText("최근 오류가 없습니다.")
            self.sync_last_error_label.setStyleSheet(self.sync_error_style_muted)

    def _format_iso_datetime(self, iso_value):
        """ISO 형식 문자열을 사람이 읽기 쉬운 형태로 변환"""
        if not iso_value:
            return "—"
        from datetime import datetime
        try:
            dt = datetime.fromisoformat(iso_value)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            return iso_value

    def create_log_tab(self):
        """로그 탭"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", 9))
        layout.addWidget(self.log_text)

        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(lambda: self.log_text.clear())
        layout.addWidget(clear_btn)

        self.tabs.addTab(tab, "5. Logs")

    def _create_input_row(self, parent_layout, label_text, default_value="", password=False):
        """입력 필드 행 생성 헬퍼"""
        layout = QHBoxLayout()
        layout.addWidget(QLabel(label_text))
        line_edit = QLineEdit(default_value)
        if password:
            line_edit.setEchoMode(QLineEdit.Password)
        layout.addWidget(line_edit)
        parent_layout.addLayout(layout)
        return line_edit

    def browse_instant_client(self):
        """Instant Client 디렉토리 선택"""
        dir_path = QFileDialog.getExistingDirectory(self, "Select Oracle Instant Client Directory")
        if dir_path:
            self.oracle_instant_client.setText(dir_path)

    def test_oracle_connection(self):
        """Oracle 연결 테스트"""
        try:
            config = self.get_oracle_config()
            conn = OracleConnection(config)

            if conn.test_connection():
                QMessageBox.information(self, "Success", "Oracle 연결 성공!")
                self.log("Oracle 연결 테스트 성공")
            else:
                QMessageBox.warning(self, "Failed", "Oracle 연결 실패")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"연결 오류:\n{str(e)}")
            self.log(f"Oracle 연결 오류: {str(e)}")

    def test_postgres_connection(self):
        """PostgreSQL 연결 테스트"""
        try:
            config = self.get_postgres_config()
            conn = PostgresConnection(config)

            if conn.test_connection():
                QMessageBox.information(self, "Success", "PostgreSQL 연결 성공!")
                self.log("PostgreSQL 연결 테스트 성공")
            else:
                QMessageBox.warning(self, "Failed", "PostgreSQL 연결 실패")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"연결 오류:\n{str(e)}")
            self.log(f"PostgreSQL 연결 오류: {str(e)}")

    def get_oracle_config(self) -> OracleConfig:
        """Oracle 설정 가져오기"""
        sid = self.oracle_sid.text() if self.oracle_sid.text() else None
        service_name = self.oracle_service.text() if self.oracle_service.text() else None
        instant_client_dir = self.oracle_instant_client.text() if self.oracle_instant_client.text() else None

        return OracleConfig(
            host=self.oracle_host.text(),
            port=int(self.oracle_port.text()),
            sid=sid,
            service_name=service_name,
            user=self.oracle_user.text(),
            password=self.oracle_password.text(),
            thick_mode=self.oracle_thick_mode.isChecked(),
            instant_client_dir=instant_client_dir
        )

    def get_postgres_config(self) -> PostgresConfig:
        """PostgreSQL 설정 가져오기"""
        return PostgresConfig(
            host=self.postgres_host.text(),
            port=int(self.postgres_port.text()),
            database=self.postgres_database.text(),
            schema=self.postgres_schema.text(),
            user=self.postgres_user.text(),
            password=self.postgres_password.text()
        )

    def load_profiles(self):
        """프로파일 목록 로드"""
        self.profile_combo.clear()
        self.profile_combo.addItem("-- New Profile --")
        profiles = self.config_manager.list_profiles()
        self.profile_combo.addItems(profiles)

    def save_profile(self):
        """현재 설정을 프로파일로 저장"""
        profile_name, ok = self._input_dialog("Save Profile", "Profile Name:")
        if ok and profile_name:
            config = {
                'oracle': {
                    'host': self.oracle_host.text(),
                    'port': self.oracle_port.text(),
                    'sid': self.oracle_sid.text(),
                    'service_name': self.oracle_service.text(),
                    'user': self.oracle_user.text(),
                    'password': self.oracle_password.text(),
                    'thick_mode': self.oracle_thick_mode.isChecked(),
                    'instant_client_dir': self.oracle_instant_client.text()
                },
                'postgres': {
                    'host': self.postgres_host.text(),
                    'port': self.postgres_port.text(),
                    'database': self.postgres_database.text(),
                    'schema': self.postgres_schema.text(),
                    'user': self.postgres_user.text(),
                    'password': self.postgres_password.text()
                }
            }
            self.config_manager.save_profile(profile_name, config)
            self.load_profiles()
            QMessageBox.information(self, "Success", f"프로파일 '{profile_name}' 저장 완료")

    def load_profile(self):
        """프로파일 로드"""
        profile_name = self.profile_combo.currentText()
        if profile_name == "-- New Profile --":
            return

        config = self.config_manager.load_profile(profile_name)
        if config:
            # Oracle 설정 로드
            oracle = config.get('oracle', {})
            self.oracle_host.setText(oracle.get('host', ''))
            self.oracle_port.setText(oracle.get('port', '1521'))
            self.oracle_sid.setText(oracle.get('sid', ''))
            self.oracle_service.setText(oracle.get('service_name', ''))
            self.oracle_user.setText(oracle.get('user', ''))
            self.oracle_password.setText(oracle.get('password', ''))
            self.oracle_thick_mode.setChecked(oracle.get('thick_mode', False))
            self.oracle_instant_client.setText(oracle.get('instant_client_dir', ''))

            # PostgreSQL 설정 로드
            postgres = config.get('postgres', {})
            self.postgres_host.setText(postgres.get('host', ''))
            self.postgres_port.setText(postgres.get('port', '5432'))
            self.postgres_database.setText(postgres.get('database', ''))
            self.postgres_schema.setText(postgres.get('schema', 'public'))
            self.postgres_user.setText(postgres.get('user', ''))
            self.postgres_password.setText(postgres.get('password', ''))

            # 마지막 프로파일로 저장
            self.config_manager.save_last_profile(profile_name)

            self.log(f"프로파일 로드: {profile_name}")

    def load_last_profile_auto(self):
        """마지막 프로파일 자동 로드"""
        last_profile = self.config_manager.load_last_profile()
        if last_profile and last_profile in self.config_manager.list_profiles():
            # 콤보박스에서 해당 프로파일 선택
            index = self.profile_combo.findText(last_profile)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
                # 프로파일 로드
                config = self.config_manager.load_profile(last_profile)
                if config:
                    # Oracle 설정 로드
                    oracle = config.get('oracle', {})
                    self.oracle_host.setText(oracle.get('host', ''))
                    self.oracle_port.setText(oracle.get('port', '1521'))
                    self.oracle_sid.setText(oracle.get('sid', ''))
                    self.oracle_service.setText(oracle.get('service_name', ''))
                    self.oracle_user.setText(oracle.get('user', ''))
                    self.oracle_password.setText(oracle.get('password', ''))
                    self.oracle_thick_mode.setChecked(oracle.get('thick_mode', False))
                    self.oracle_instant_client.setText(oracle.get('instant_client_dir', ''))

                    # PostgreSQL 설정 로드
                    postgres = config.get('postgres', {})
                    self.postgres_host.setText(postgres.get('host', ''))
                    self.postgres_port.setText(postgres.get('port', '5432'))
                    self.postgres_database.setText(postgres.get('database', ''))
                    self.postgres_schema.setText(postgres.get('schema', 'public'))
                    self.postgres_user.setText(postgres.get('user', ''))
                    self.postgres_password.setText(postgres.get('password', ''))

                    self.log(f"마지막 프로파일 자동 로드: {last_profile}")

    def delete_profile(self):
        """프로파일 삭제"""
        profile_name = self.profile_combo.currentText()
        if profile_name == "-- New Profile --":
            return

        reply = QMessageBox.question(
            self, "Delete Profile",
            f"'{profile_name}' 프로파일을 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.config_manager.delete_profile(profile_name)
            self.load_profiles()
            self.log(f"프로파일 삭제: {profile_name}")

    def load_tables(self):
        """테이블 목록 로드"""
        try:
            owner = self.schema_input.text().upper()
            if not owner:
                QMessageBox.warning(self, "Warning", "스키마 이름을 입력하세요")
                return

            # Oracle 연결
            config = self.get_oracle_config()
            self.oracle_conn = OracleConnection(config)
            self.oracle_conn.connect()

            # 테이블 조회
            tables = self.oracle_conn.get_tables(owner)

            # 테이블 목록 표시
            self.table_list.setRowCount(len(tables))
            for i, table in enumerate(tables):
                self.table_list.setItem(i, 0, QTableWidgetItem(table['name']))
                self.table_list.setItem(i, 1, QTableWidgetItem(str(table['rows'] or 0)))
                self.table_list.setItem(i, 2, QTableWidgetItem(table['comment'] or ''))

            self.log(f"{len(tables)}개 테이블 로드 완료")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"테이블 로드 오류:\n{str(e)}")
            self.log(f"테이블 로드 오류: {str(e)}")

    def on_table_selected(self):
        """테이블 선택 시"""
        selected_items = self.table_list.selectedItems()
        if not selected_items:
            return

        table_name = self.table_list.item(selected_items[0].row(), 0).text()
        owner = self.schema_input.text().upper()

        try:
            # 컬럼 정보 조회
            columns = self.oracle_conn.get_table_columns(owner, table_name)
            pk = self.oracle_conn.get_primary_key(owner, table_name)
            indexes = self.oracle_conn.get_indexes(owner, table_name)

            # 상세 정보 표시
            detail = f"Table: {table_name}\n\n"
            detail += "Columns:\n"
            for col in columns:
                detail += f"  - {col['name']}: {col['data_type']}"
                if col.get('length'):
                    detail += f"({col['length']})"
                elif col.get('precision'):
                    detail += f"({col['precision']},{col['scale']})"
                detail += " NOT NULL" if not col['nullable'] else ""
                detail += "\n"

            if pk:
                detail += f"\nPrimary Key: {', '.join(pk['columns'])}\n"

            if indexes:
                detail += "\nIndexes:\n"
                for idx in indexes:
                    unique = "UNIQUE " if idx['unique'] else ""
                    detail += f"  - {unique}{idx['name']}: {', '.join(idx['columns'])}\n"

            self.table_detail_text.setText(detail)

        except Exception as e:
            self.log(f"테이블 상세 정보 조회 오류: {str(e)}")

    def generate_ddl(self):
        """DDL 생성"""
        selected_items = self.table_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "테이블을 선택하세요")
            return

        table_name = self.table_list.item(selected_items[0].row(), 0).text()
        owner = self.schema_input.text().upper()

        try:
            # 테이블 정보 조회
            columns = self.oracle_conn.get_table_columns(owner, table_name)
            pk = self.oracle_conn.get_primary_key(owner, table_name)
            indexes = self.oracle_conn.get_indexes(owner, table_name)

            # DDL 변환
            converter = DDLConverter()
            ddl = converter.generate_full_ddl(table_name, columns, pk, indexes)

            self.ddl_text.setText(ddl)
            self.log(f"DDL 생성 완료: {table_name}")

            # 경고 확인
            warnings = converter.validate_conversion(columns)
            if warnings:
                warning_text = "\n".join(warnings)
                QMessageBox.warning(self, "Conversion Warnings", warning_text)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"DDL 생성 오류:\n{str(e)}")
            self.log(f"DDL 생성 오류: {str(e)}")

    def start_migration(self):
        """마이그레이션 시작"""
        selected_items = self.table_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "테이블을 선택하세요")
            return

        table_name = self.table_list.item(selected_items[0].row(), 0).text()
        owner = self.schema_input.text().upper()

        try:
            # PostgreSQL 연결
            postgres_config = self.get_postgres_config()
            self.postgres_conn = PostgresConnection(postgres_config)
            self.postgres_conn.connect()

            # 기존 테이블 확인
            if self.postgres_conn.table_exists(table_name.lower()):
                if self.overwrite_checkbox.isChecked():
                    self.postgres_conn.drop_table(table_name.lower())
                    self.log(f"기존 테이블 삭제: {table_name}")
                else:
                    QMessageBox.warning(self, "Warning", "테이블이 이미 존재합니다. 덮어쓰기 옵션을 활성화하세요.")
                    return

            # DDL 실행
            ddl = self.ddl_text.toPlainText()
            if not ddl:
                QMessageBox.warning(self, "Warning", "먼저 DDL을 생성하세요")
                return

            self.postgres_conn.execute_ddl(ddl)
            self.log("테이블 생성 완료")

            # 데이터 마이그레이션 시작
            batch_size = self.batch_size_spin.value()
            migrator = DataMigrator(self.oracle_conn, self.postgres_conn, batch_size)

            self.migration_worker = MigrationWorker(migrator, owner, table_name)
            self.migration_worker.progress_updated.connect(self.on_migration_progress)
            self.migration_worker.finished.connect(self.on_migration_finished)
            self.migration_worker.error.connect(self.on_migration_error)

            self.start_migration_btn.setEnabled(False)
            self.cancel_migration_btn.setEnabled(True)

            self.migration_worker.start()
            self.log("데이터 마이그레이션 시작")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"마이그레이션 시작 오류:\n{str(e)}")
            self.log(f"마이그레이션 오류: {str(e)}")

    def cancel_migration(self):
        """마이그레이션 취소"""
        if self.migration_worker:
            self.migration_worker.migrator.cancel()
            self.log("마이그레이션 취소 요청")

    def on_migration_progress(self, progress: MigrationProgress):
        """마이그레이션 진행 상황 업데이트"""
        percentage = progress.get_progress_percentage()
        self.progress_bar.setValue(int(percentage))

        elapsed = progress.get_elapsed_time()
        self.progress_label.setText(
            f"Progress: {progress.migrated_rows:,} / {progress.total_rows:,} rows "
            f"({percentage:.1f}%) - Elapsed: {elapsed:.1f}s"
        )

    def on_migration_finished(self, progress: MigrationProgress):
        """마이그레이션 완료"""
        self.start_migration_btn.setEnabled(True)
        self.cancel_migration_btn.setEnabled(False)

        summary = progress.get_summary()
        message = f"마이그레이션 완료!\n\n"
        message += f"총 행 수: {summary['total_rows']:,}\n"
        message += f"이관 완료: {summary['migrated_rows']:,}\n"
        message += f"실패: {summary['failed_rows']:,}\n"
        message += f"성공률: {summary['success_rate']:.2f}%\n"
        message += f"소요 시간: {summary['elapsed_time']:.1f}초"

        QMessageBox.information(self, "Migration Complete", message)
        self.log(message)

    def on_migration_error(self, error_message: str):
        """마이그레이션 오류"""
        self.start_migration_btn.setEnabled(True)
        self.cancel_migration_btn.setEnabled(False)
        QMessageBox.critical(self, "Migration Error", error_message)
        self.log(f"마이그레이션 오류: {error_message}")

    def log(self, message: str):
        """로그 출력"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")
        logger.info(message)

    def _input_dialog(self, title: str, label: str):
        """입력 다이얼로그"""
        from PyQt5.QtWidgets import QInputDialog
        text, ok = QInputDialog.getText(self, title, label)
        return text, ok

    def start_sync(self):
        """동기화 시작"""
        selected_items = self.table_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "테이블을 선택하세요")
            return

        table_name = self.table_list.item(selected_items[0].row(), 0).text()
        owner = self.schema_input.text().upper()

        try:
            # 연결 확인 및 생성
            if not self.oracle_conn or not self.oracle_conn.connection:
                config = self.get_oracle_config()
                self.oracle_conn = OracleConnection(config)
                self.oracle_conn.connect()

            if not self.postgres_conn or not self.postgres_conn.connection:
                postgres_config = self.get_postgres_config()
                self.postgres_conn = PostgresConnection(postgres_config)
                self.postgres_conn.connect()

            # 동기화 간격 추출
            interval_text = self.sync_interval_combo.currentText()
            if "10 minutes" in interval_text:
                interval_minutes = 10
            elif "30 minutes" in interval_text:
                interval_minutes = 30
            elif "1 hour" in interval_text:
                interval_minutes = 60
            elif "2 hours" in interval_text:
                interval_minutes = 120
            elif "6 hours" in interval_text:
                interval_minutes = 360
            elif "12 hours" in interval_text:
                interval_minutes = 720
            else:  # 24 hours
                interval_minutes = 1440

            # 동기화 모드 선택
            mode_text = self.sync_mode_combo.currentText()
            if "Incremental" in mode_text:
                sync_mode = SyncMode.INCREMENTAL
            elif "Full" in mode_text:
                sync_mode = SyncMode.FULL
            else:
                sync_mode = SyncMode.DELETE_INSERT

            # 타임스탬프 컬럼
            timestamp_column = self.timestamp_column_input.text().strip()
            if not timestamp_column and sync_mode == SyncMode.INCREMENTAL:
                QMessageBox.warning(
                    self, "Warning",
                    "증분 동기화에는 타임스탬프 컬럼이 필요합니다.\n전체 동기화로 전환됩니다."
                )

            # 증분 동기화 시작 전 자동 갭 확인
            if sync_mode == SyncMode.INCREMENTAL and timestamp_column:
                self.log("증분 동기화: 누락 데이터 확인 중...")
                temp_sync_manager = SyncManager(self.oracle_conn, self.postgres_conn)
                gap_info = temp_sync_manager.check_sync_gap(owner, table_name, timestamp_column)

                if gap_info.get('has_gap'):
                    pg_last_time = gap_info['pg_last_time']
                    missing_count = gap_info['missing_count']

                    # 마지막 시간 형식 변환
                    if isinstance(pg_last_time, str):
                        last_time_str = pg_last_time
                    else:
                        last_time_str = pg_last_time.strftime('%Y-%m-%d %H:%M:%S')

                    # 사용자에게 확인
                    reply = QMessageBox.question(
                        self, "누락 데이터 감지",
                        f"📊 PostgreSQL 마지막 데이터: {last_time_str}\n"
                        f"📈 누락된 데이터: {missing_count:,}건\n\n"
                        f"❓ 정기 동기화를 시작하기 전에\n"
                        f"   누락된 데이터를 먼저 동기화하시겠습니까?\n\n"
                        f"• 예: 누락 데이터 동기화 → 정기 동기화 시작\n"
                        f"• 아니오: 바로 정기 동기화 시작 (누락 데이터 무시)",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.Yes
                    )

                    if reply == QMessageBox.Yes:
                        # 캐치업 동기화 실행
                        self.log(f"캐치업 동기화 시작: {missing_count:,}건")
                        result = temp_sync_manager._incremental_sync(owner, table_name, timestamp_column)

                        if result['success']:
                            self.log(f"✅ 캐치업 완료: {result['rows_affected']:,}건 동기화")
                            QMessageBox.information(
                                self, "캐치업 완료",
                                f"누락 데이터 동기화 완료!\n\n"
                                f"동기화된 행: {result['rows_affected']:,}건\n\n"
                                f"이제 정기 동기화를 시작합니다."
                            )
                        else:
                            QMessageBox.warning(
                                self, "캐치업 실패",
                                f"누락 데이터 동기화 실패:\n{result.get('error')}\n\n"
                                f"정기 동기화는 계속 진행됩니다."
                            )
                else:
                    self.log("누락 데이터 없음 - 정기 동기화 바로 시작")

            # 동기화 매니저 생성 및 시작
            self.sync_manager = SyncManager(self.oracle_conn, self.postgres_conn)
            self.sync_manager.start_sync(
                owner, table_name, interval_minutes, sync_mode,
                timestamp_column if timestamp_column else None,
                callback=self.on_sync_completed
            )

            # UI 업데이트
            self.start_sync_btn.setEnabled(False)
            self.stop_sync_btn.setEnabled(True)

            # 상태 업데이트 타이머 시작
            self.sync_status_timer.start(5000)  # 5초마다 업데이트
            self._set_status_card_state(True)
            self.sync_current_table_value.setText(table_name)
            totals = self.sync_manager.status
            self.sync_total_runs_value.setText(f"{totals.total_syncs:,}회")
            self.sync_success_rate_value.setText("—")
            self.sync_success_breakdown_value.setText(f"{totals.successful_syncs:,} / {totals.failed_syncs:,}")
            self.sync_last_sync_value.setText("—")
            self.sync_next_sync_value.setText("—")
            self._set_last_error(None)
            self.update_sync_status()

            self.log(f"동기화 시작: {table_name}, 간격: {interval_minutes}분, 모드: {sync_mode.value}")
            QMessageBox.information(
                self, "Sync Started",
                f"동기화가 시작되었습니다.\n\n"
                f"테이블: {table_name}\n"
                f"간격: {interval_text}\n"
                f"모드: {mode_text}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"동기화 시작 오류:\n{str(e)}")
            self.log(f"동기화 시작 오류: {str(e)}")

    def on_sync_mode_changed(self, index):
        """동기화 모드 변경 시"""
        self.update_mode_description(index)

    def update_mode_description(self, index):
        """모드 설명 업데이트"""
        descriptions = [
            "⚡ 증분: 타임스탬프 기반으로 변경된 데이터만 동기화 (빠름, 삭제 미반영)",
            "🔄 전체: 테이블 전체를 재동기화 (느림, 삭제 반영, 완전 동기화)",
            "🔨 삭제+삽입: 테이블을 재생성 후 전체 데이터 삽입 (가장 느림, 스키마 변경 반영)"
        ]
        self.mode_description.setText(descriptions[index])

    def stop_sync(self):
        """동기화 중지"""
        if not self.sync_manager:
            return

        try:
            self.sync_manager.stop_sync()
            self.sync_status_timer.stop()

            self.start_sync_btn.setEnabled(True)
            self.stop_sync_btn.setEnabled(False)

            self.log("동기화 중지를 요청했습니다.")
            self.update_sync_status()
            self._set_status_card_state(False, "중지됨")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"동기화 중지 오류:\n{str(e)}")

    def run_catchup_sync(self):
        """누락 데이터 동기화 실행"""
        selected_items = self.table_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "테이블을 먼저 선택하세요 (Tab 2)")
            return

        table_name = self.table_list.item(selected_items[0].row(), 0).text()
        owner = self.schema_input.text().upper()

        catchup_time = self.catchup_datetime_input.text().strip()
        if not catchup_time:
            QMessageBox.warning(self, "Warning", "마지막 동기화 시간을 입력하세요\n예: 2024-10-15 14:30:00")
            return

        timestamp_column = self.timestamp_column_input.text().strip()
        if not timestamp_column:
            QMessageBox.warning(self, "Warning", "타임스탬프 컬럼을 입력하세요\n예: CREATED_DATE")
            return

        try:
            # 연결 확인
            if not self.oracle_conn or not self.oracle_conn.connection:
                config = self.get_oracle_config()
                self.oracle_conn = OracleConnection(config)
                self.oracle_conn.connect()

            if not self.postgres_conn or not self.postgres_conn.connection:
                postgres_config = self.get_postgres_config()
                self.postgres_conn = PostgresConnection(postgres_config)
                self.postgres_conn.connect()

            # 컬럼 타입 확인
            columns = self.oracle_conn.get_table_columns(owner, table_name)
            timestamp_col_info = next((col for col in columns if col['name'].upper() == timestamp_column.upper()), None)
            is_varchar = timestamp_col_info and 'VARCHAR' in timestamp_col_info['data_type'].upper()

            # 누락 데이터 수 확인
            oracle_cursor = self.oracle_conn.connection.cursor()

            if is_varchar:
                # VARCHAR2 컬럼: 문자열 비교 (그대로 사용)
                # 형식: 'YYYY-MM-DD HH:MI:SS', 'YYYY-MM-DD HH:MI:SS 밀리초', 'YYYY-MM-DD' 등
                query = f"""
                    SELECT COUNT(*)
                    FROM {owner}.{table_name}
                    WHERE {timestamp_column} > '{catchup_time}'
                """
                oracle_cursor.execute(query)
            else:
                # DATE/TIMESTAMP 컬럼: TO_TIMESTAMP 사용
                query = f"""
                    SELECT COUNT(*)
                    FROM {owner}.{table_name}
                    WHERE {timestamp_column} > TO_TIMESTAMP(:catchup_time, 'YYYY-MM-DD HH24:MI:SS')
                """
                oracle_cursor.execute(query, {'catchup_time': catchup_time})

            missing_count = oracle_cursor.fetchone()[0]
            oracle_cursor.close()

            if missing_count == 0:
                QMessageBox.information(self, "Info", "누락된 데이터가 없습니다!")
                return

            # 확인 메시지
            reply = QMessageBox.question(
                self, "Catchup Sync",
                f"누락된 데이터: {missing_count:,}건\n\n"
                f"마지막 동기화: {catchup_time}\n"
                f"현재 시간까지의 데이터를 동기화하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

            # 동기화 실행
            self.log(f"누락 데이터 동기화 시작: {missing_count:,}건")

            from src.core.sync_manager import SyncManager, SyncMode
            sync_manager = SyncManager(self.oracle_conn, self.postgres_conn)

            # 임시로 증분 동기화 실행 (한 번만)
            result = sync_manager._incremental_sync(owner, table_name, timestamp_column)

            if result['success']:
                QMessageBox.information(
                    self, "Success",
                    f"누락 데이터 동기화 완료!\n\n"
                    f"동기화된 행: {result['rows_affected']:,}건"
                )
                self.log(f"누락 데이터 동기화 완료: {result['rows_affected']:,}건")
            else:
                QMessageBox.warning(self, "Error", f"동기화 실패:\n{result.get('error')}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"누락 데이터 동기화 오류:\n{str(e)}")
            self.log(f"누락 데이터 동기화 오류: {str(e)}")

    def update_sync_status(self):
        """동기화 상태 갱신"""
        if not self.sync_manager:
            return

        status = self.sync_manager.get_status()

        self._set_status_card_state(status['is_running'])

        if status['current_table']:
            self.sync_current_table_value.setText(status['current_table'])
        else:
            fallback = "대기 중" if status['is_running'] else "미선택"
            self.sync_current_table_value.setText(fallback)

        total_syncs = status['total_syncs']
        self.sync_total_runs_value.setText(f"{total_syncs:,}회")

        if total_syncs > 0:
            self.sync_success_rate_value.setText(f"{status['success_rate']:.1f}%")
        else:
            self.sync_success_rate_value.setText("—")

        self.sync_success_breakdown_value.setText(
            f"{status['successful_syncs']:,} / {status['failed_syncs']:,}"
        )

        self.sync_last_sync_value.setText(self._format_iso_datetime(status['last_sync_time']))
        self.sync_next_sync_value.setText(self._format_iso_datetime(status['next_sync_time']))

        self._set_last_error(status['last_error'])

    def on_sync_completed(self, status: SyncStatus, result: dict):
        """동기화 완료 콜백"""
        # 히스토리 테이블에 추가
        row = self.sync_history_table.rowCount()
        self.sync_history_table.insertRow(row)

        from datetime import datetime
        time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        table_name = status.current_table or 'N/A'
        mode = result.get('mode', 'N/A')
        rows = result.get('rows_affected', 0)
        status_str = '성공' if result.get('success') else '실패'

        self.sync_history_table.setItem(row, 0, QTableWidgetItem(time_str))
        self.sync_history_table.setItem(row, 1, QTableWidgetItem(table_name))
        self.sync_history_table.setItem(row, 2, QTableWidgetItem(mode))
        self.sync_history_table.setItem(row, 3, QTableWidgetItem(str(rows)))
        self.sync_history_table.setItem(row, 4, QTableWidgetItem(status_str))

        # 로그 기록
        self.log(f"동기화 완료: {table_name}, 모드: {mode}, {rows}행, {status_str}")

    def closeEvent(self, event):
        """윈도우 닫을 때"""
        # 동기화 중지
        if self.sync_manager and self.sync_manager.status.is_running:
            self.sync_manager.stop_sync()

        # 타이머 중지
        if self.sync_status_timer.isActive():
            self.sync_status_timer.stop()

        # 연결 종료
        if self.oracle_conn:
            self.oracle_conn.close()
        if self.postgres_conn:
            self.postgres_conn.close()

        event.accept()


def main():
    """메인 함수"""
    from src.utils.logger import setup_logger
    setup_logger()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
