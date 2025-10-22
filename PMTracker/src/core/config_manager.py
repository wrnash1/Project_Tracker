import os
import configparser
from pathlib import Path
from cryptography.fernet import Fernet
import base64

class ConfigManager:
    """Manages application configuration and encrypted credentials"""

    def __init__(self):
        self.config_dir = Path.home() / 'PMTracker' / 'config'
        self.config_file = self.config_dir / 'config.ini'
        self.key_file = self.config_dir / 'key.key'
        self.config = configparser.ConfigParser()

        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Initialize encryption
        self.cipher = self._init_encryption()

        # Load or create config
        self._load_config()

    def _init_encryption(self):
        """Initialize Fernet encryption"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                key = f.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(key)
        return Fernet(key)

    def _load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            self.config.read(self.config_file)
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Create default configuration file"""
        self.config['Database'] = {
            'oracle_host': 'f1btpap-scan.verizon.com/NARPROD',
            'oracle_user': 'splunkveep_nar',
            'oracle_password': '',
            'sqlite_path': str(self.config_dir / 'pmtracker.db')
        }

        self.config['Application'] = {
            'theme': 'light',
            'auto_save': 'true',
            'tts_enabled': 'true',
            'update_check': 'true',
            'update_url': 'G:/PMTracker/latest_version.txt'
        }

        self.config['ML'] = {
            'delay_model_path': 'resources/models/delay_predictor.h5',
            'risk_model_path': 'resources/models/risk_classifier.h5',
            'retrain_threshold_days': '90'
        }

        self.config['Integrations'] = {
            'slack_enabled': 'false',
            'webex_enabled': 'false',
            'google_enabled': 'false'
        }

        self.save_config()

    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            self.config.write(f)

    def get(self, section, key, fallback=None):
        """Get configuration value"""
        return self.config.get(section, key, fallback=fallback)

    def set(self, section, key, value):
        """Set configuration value"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        self.save_config()

    def get_encrypted(self, section, key):
        """Get and decrypt a sensitive value"""
        encrypted_value = self.config.get(section, key, fallback='')
        if encrypted_value:
            return self.cipher.decrypt(encrypted_value.encode()).decode()
        return ''

    def set_encrypted(self, section, key, value):
        """Encrypt and store a sensitive value"""
        encrypted_value = self.cipher.encrypt(value.encode()).decode()
        self.set(section, key, encrypted_value)

    def get_oracle_config(self):
        """Get Oracle database configuration"""
        return {
            'host': self.get('Database', 'oracle_host'),
            'user': self.get('Database', 'oracle_user'),
            'password': self.get_encrypted('Database', 'oracle_password')
        }

    def get_sqlite_path(self):
        """Get SQLite database path"""
        return Path(self.get('Database', 'sqlite_path'))
