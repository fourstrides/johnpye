#!/usr/bin/env python3
"""
Configuration Manager for the John Pye Auctions Tracker.

Handles loading and managing configuration settings, credentials, and
application parameters.
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigManager:
    """Manages application configuration and credentials."""
    
    def __init__(self, config_file: str = "../config/settings.json"):
        """Initialize the configuration manager."""
        self.config_file = config_file
        self.config_data: Dict[str, Any] = {}
        self.load_config()
        load_dotenv()
    
    def load_config(self):
        """Load configuration from JSON file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config_data = json.load(f)
            else:
                # Create default config if file doesn't exist
                self.create_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.create_default_config()
    
    def create_default_config(self):
        """Create default configuration settings."""
        self.config_data = {
            "monitoring": {
                "check_interval_seconds": 300,  # 5 minutes
                "headless_browser": True,
                "max_retries": 3,
                "timeout_seconds": 30
            },
            "notifications": {
                "enabled": True,
                "email_notifications": False,
                "bid_increase_threshold": 10.0,  # Minimum increase to notify
                "ending_soon_threshold_minutes": 60
            },
            "data_storage": {
                "save_historical_data": True,
                "cleanup_old_data_days": 30,
                "export_format": "csv"
            },
            "browser": {
                "user_agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "window_width": 1920,
                "window_height": 1080,
                "implicit_wait": 10
            }
        }
        self.save_config()
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config_data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_username(self) -> str:
        """Get the username from environment variables."""
        username = os.getenv('JOHNPYE_USERNAME')
        if not username:
            raise ValueError("JOHNPYE_USERNAME environment variable not set")
        return username
    
    def get_password(self) -> str:
        """Get the password from environment variables."""
        password = os.getenv('JOHNPYE_PASSWORD')
        if not password:
            raise ValueError("JOHNPYE_PASSWORD environment variable not set")
        return password
    
    def get_check_interval(self) -> int:
        """Get the monitoring check interval in seconds."""
        return self.config_data.get('monitoring', {}).get('check_interval_seconds', 300)
    
    def get_headless_mode(self) -> bool:
        """Get whether to run browser in headless mode."""
        return self.config_data.get('monitoring', {}).get('headless_browser', True)
    
    def get_max_retries(self) -> int:
        """Get maximum number of retries for failed operations."""
        return self.config_data.get('monitoring', {}).get('max_retries', 3)
    
    def get_timeout(self) -> int:
        """Get timeout for web operations in seconds."""
        return self.config_data.get('monitoring', {}).get('timeout_seconds', 30)
    
    def get_notifications_enabled(self) -> bool:
        """Get whether notifications are enabled."""
        return self.config_data.get('notifications', {}).get('enabled', True)
    
    def get_email_notifications_enabled(self) -> bool:
        """Get whether email notifications are enabled."""
        return self.config_data.get('notifications', {}).get('email_notifications', False)
    
    def get_bid_increase_threshold(self) -> float:
        """Get minimum bid increase amount to trigger notifications."""
        return self.config_data.get('notifications', {}).get('bid_increase_threshold', 10.0)
    
    def get_ending_soon_threshold(self) -> int:
        """Get threshold in minutes for 'ending soon' notifications."""
        return self.config_data.get('notifications', {}).get('ending_soon_threshold_minutes', 60)
    
    def get_user_agent(self) -> str:
        """Get the user agent string for browser."""
        return self.config_data.get('browser', {}).get('user_agent', 
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    def get_window_size(self) -> tuple:
        """Get browser window size as (width, height)."""
        browser_config = self.config_data.get('browser', {})
        width = browser_config.get('window_width', 1920)
        height = browser_config.get('window_height', 1080)
        return (width, height)
    
    def get_implicit_wait(self) -> int:
        """Get implicit wait time for Selenium."""
        return self.config_data.get('browser', {}).get('implicit_wait', 10)
    
    def should_save_historical_data(self) -> bool:
        """Get whether to save historical tracking data."""
        return self.config_data.get('data_storage', {}).get('save_historical_data', True)
    
    def get_cleanup_threshold_days(self) -> int:
        """Get number of days after which to cleanup old data."""
        return self.config_data.get('data_storage', {}).get('cleanup_old_data_days', 30)
    
    def get_export_format(self) -> str:
        """Get the preferred export format for data."""
        return self.config_data.get('data_storage', {}).get('export_format', 'csv')
    
    def update_setting(self, section: str, key: str, value: Any):
        """Update a specific configuration setting."""
        if section not in self.config_data:
            self.config_data[section] = {}
        self.config_data[section][key] = value
        self.save_config()
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """Get a specific configuration setting."""
        return self.config_data.get(section, {}).get(key, default)
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all configuration settings."""
        return self.config_data.copy()
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        self.create_default_config()