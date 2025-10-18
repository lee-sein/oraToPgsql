
import sys
import os
import json

# Add project root to path to allow imports
sys.path.insert(0, os.path.abspath('.'))

from src.utils.config import ConfigManager

# 1. Initialize ConfigManager
config_manager = ConfigManager()

# 2. Define the new profile configuration
# Based on the user's request for Oracle 11g
new_profile_config = {
    "oracle": {
        "host": "localhost",
        "port": "1521",
        "sid": "ORCL11G",
        "service_name": "",
        "user": "cssown",
        "password": "cssadmin", # This will be encrypted by save_profile
        "thick_mode": True,
        "instant_client_dir": "C:\\path\\to\\your\\instantclient_11_2" # User needs to change this
    },
    "postgres": { # Add a placeholder postgres config from the 'test' profile
        "host": "localhost",
        "port": "5432",
        "database": "postgres",
        "schema": "public",
        "user": "postgres",
        "password": "password" # This will also be encrypted
    }
}

# 3. Save the new profile
profile_name = 'css_test'
config_manager.save_profile(profile_name, new_profile_config)

print(f"Successfully created new profile named '{profile_name}'.")
