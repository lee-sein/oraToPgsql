"""
로깅 유틸리티
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import colorlog


def setup_logger(name: str = 'oraToPgsql', log_dir: str = 'logs', level=logging.INFO):
    """
    로거 설정

    Args:
        name: 로거 이름
        log_dir: 로그 파일 디렉토리
        level: 로그 레벨

    Returns:
        logging.Logger
    """
    # 로그 디렉토리 생성
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 기존 핸들러 제거
    if logger.handlers:
        logger.handlers.clear()

    # 파일 핸들러
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_handler = logging.FileHandler(
        log_path / f'migration_{timestamp}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # 콘솔 핸들러 (컬러 출력)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s %(message)s',
        datefmt='%H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    console_handler.setFormatter(console_formatter)

    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
