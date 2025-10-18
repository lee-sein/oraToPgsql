
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
from src.utils.config import ConfigManager

PROFILE_NAME = 'css_test'

# 1. Initialize ConfigManager
config_manager = ConfigManager()

# 2. Load the existing profile to get current data
profile_data = config_manager.load_profile(PROFILE_NAME)
if not profile_data:
    print(f"Error: Profile '{PROFILE_NAME}' not found.")
    sys.exit(1)

# 3. Update Oracle config for Thin Mode with new credentials
oracle_config = profile_data.get('oracle', {})
oracle_config['sid'] = 'XE'
oracle_config['service_name'] = '' # Explicitly clear service name
oracle_config['thick_mode'] = False
oracle_config.pop('instant_client_dir', None) # Remove instant client dir as it's not needed
oracle_config['user'] = 'cssown'
oracle_config['password'] = 'cssadmin' # Set the password to be re-encrypted

# 4. Put the updated oracle config back into the profile data
profile_data['oracle'] = oracle_config

# 5. Save the entire profile back, which handles encryption
config_manager.save_profile(PROFILE_NAME, profile_data)

print(f"Profile '{PROFILE_NAME}' updated to use Oracle Thin Mode with SID 'XE'.")
