#!/usr/bin/env python3
"""
Oracle to PostgreSQL Migration Tool
메인 실행 파일
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.utils.logger import setup_logger

__version__ = '1.0.0'


def main():
    """메인 함수"""
    # 로거 설정
    logger = setup_logger()
    logger.info(f"Oracle to PostgreSQL Migration Tool v{__version__}")
    logger.info("프로그램 시작")

    # PyQt 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName("Oracle to PostgreSQL Migration Tool")
    app.setApplicationVersion(__version__)

    # 메인 윈도우 생성 및 표시
    window = MainWindow()
    window.show()

    # 이벤트 루프 실행
    return_code = app.exec_()

    logger.info("프로그램 종료")
    sys.exit(return_code)


if __name__ == '__main__':
    main()
