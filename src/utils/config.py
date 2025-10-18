"""
설정 관리 모듈
"""

import json
import keyring
from pathlib import Path
from typing import Optional, Dict
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """설정 파일 관리 클래스"""

    def __init__(self, config_dir: str = 'config'):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.profiles_file = self.config_dir / 'profiles.json'
        self.key_file = self.config_dir / '.key'
        self.settings_file = self.config_dir / 'settings.json'

    def _get_encryption_key(self) -> bytes:
        """암호화 키 가져오기 또는 생성"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
            # 파일 권한 제한 (Unix 계열)
            try:
                self.key_file.chmod(0o600)
            except:
                pass
            return key

    def encrypt_password(self, password: str) -> str:
        """비밀번호 암호화"""
        key = self._get_encryption_key()
        f = Fernet(key)
        return f.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password: str) -> str:
        """비밀번호 복호화"""
        key = self._get_encryption_key()
        f = Fernet(key)
        return f.decrypt(encrypted_password.encode()).decode()

    def save_profile(self, profile_name: str, config: Dict):
        """프로파일 저장"""
        profiles = self.load_profiles()

        # 비밀번호 암호화
        if 'oracle' in config and 'password' in config['oracle']:
            config['oracle']['password'] = self.encrypt_password(config['oracle']['password'])

        if 'postgres' in config and 'password' in config['postgres']:
            config['postgres']['password'] = self.encrypt_password(config['postgres']['password'])

        profiles[profile_name] = config

        with open(self.profiles_file, 'w') as f:
            json.dump(profiles, f, indent=2)

        logger.info(f"프로파일 저장됨: {profile_name}")

    def load_profiles(self) -> Dict:
        """모든 프로파일 로드"""
        if not self.profiles_file.exists():
            return {}

        with open(self.profiles_file, 'r') as f:
            return json.load(f)

    def load_profile(self, profile_name: str) -> Optional[Dict]:
        """특정 프로파일 로드 및 복호화"""
        profiles = self.load_profiles()
        config = profiles.get(profile_name)

        if not config:
            return None

        # 비밀번호 복호화
        if 'oracle' in config and 'password' in config['oracle']:
            config['oracle']['password'] = self.decrypt_password(config['oracle']['password'])

        if 'postgres' in config and 'password' in config['postgres']:
            config['postgres']['password'] = self.decrypt_password(config['postgres']['password'])

        return config

    def delete_profile(self, profile_name: str):
        """프로파일 삭제"""
        profiles = self.load_profiles()
        if profile_name in profiles:
            del profiles[profile_name]
            with open(self.profiles_file, 'w') as f:
                json.dump(profiles, f, indent=2)
            logger.info(f"프로파일 삭제됨: {profile_name}")

    def list_profiles(self) -> list:
        """프로파일 목록"""
        profiles = self.load_profiles()
        return list(profiles.keys())

    def save_last_profile(self, profile_name: str):
        """마지막 사용 프로파일 저장"""
        settings = self.load_settings()
        settings['last_profile'] = profile_name
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        logger.info(f"마지막 프로파일 저장: {profile_name}")

    def load_last_profile(self) -> Optional[str]:
        """마지막 사용 프로파일 로드"""
        settings = self.load_settings()
        return settings.get('last_profile')

    def load_settings(self) -> Dict:
        """설정 파일 로드"""
        if not self.settings_file.exists():
            return {}
        with open(self.settings_file, 'r') as f:
            return json.load(f)
