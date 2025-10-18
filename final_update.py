
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from src.utils.config import ConfigManager

PROFILE_NAME = 'css_test'
CLIENT_PATH = 'c:\\instantclient_11_2'

# 1. Initialize ConfigManager
config_manager = ConfigManager()

# 2. Load existing profile
profile_data = config_manager.load_profile(PROFILE_NAME)
if not profile_data:
    print(f"Error: Profile '{PROFILE_NAME}' not found.")
    sys.exit(1)

# 3. Update Oracle config with the correct path
oracle_config = profile_data.get('oracle', {})
oracle_config['instant_client_dir'] = CLIENT_PATH
profile_data['oracle'] = oracle_config

# 4. Save the profile
config_manager.save_profile(PROFILE_NAME, profile_data)

print(f"Profile '{PROFILE_NAME}' has been updated with the Oracle Instant Client path: {CLIENT_PATH}")
