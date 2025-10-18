
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from src.utils.config import ConfigManager

PROFILE_NAME = 'css_test'

# 1. Initialize ConfigManager
config_manager = ConfigManager()

# 2. Load existing profile
profile_data = config_manager.load_profile(PROFILE_NAME)
if not profile_data:
    print(f"Error: Profile '{PROFILE_NAME}' not found.")
    sys.exit(1)

# 3. Update Oracle config for Thick Mode for 11g XE
oracle_config = profile_data.get('oracle', {})
oracle_config['sid'] = 'XE'  # Use the SID the user provided
oracle_config['service_name'] = ''
oracle_config['thick_mode'] = True # MUST be True for 11g
oracle_config['instant_client_dir'] = 'C:\\path\\to\\your\\instantclient_11_2' # Reinstate the placeholder
oracle_config['user'] = 'cssown'
oracle_config['password'] = 'cssadmin'

profile_data['oracle'] = oracle_config

# 4. Save the profile
config_manager.save_profile(PROFILE_NAME, profile_data)

print(f"Profile '{PROFILE_NAME}' has been reconfigured for Oracle 11g XE (Thick Mode).")
