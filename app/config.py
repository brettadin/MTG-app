"""
Configuration management.
"""

import yaml
import os
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class Config:
    """
    Application configuration manager.
    """
    
    def __init__(self, config_path: str = "config/app_config.yaml"):
        """
        Load configuration from YAML file.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self._config: Dict[str, Any] = {}
        self.load()
    
    def load(self):
        """Load configuration from file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            self._config = self._get_default_config()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._config = self._get_default_config()
    
    def save(self):
        """Save current configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config, f, default_flow_style=False)
            logger.info(f"Saved configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-separated key.
        
        Args:
            key: Configuration key (e.g., 'database.db_path')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        parts = key.split('.')
        value = self._config
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value by dot-separated key.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        parts = key.split('.')
        config = self._config
        
        for part in parts[:-1]:
            if part not in config:
                config[part] = {}
            config = config[part]
        
        config[parts[-1]] = value
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'mtgjson': {
                'csv_directory': 'libraries/csv',
                'json_sets_directory': 'libraries/json/AllSetFiles',
                'all_printings_json': 'libraries/json/AllPrintings.json',
                'all_identifiers_json': 'libraries/json/AllIdentifiers.json',
                'version_tag': 'mtgjson-v5'
            },
            'database': {
                'db_path': 'data/mtg_index.sqlite',
                'index_version_file': 'data/INDEX_VERSION.json'
            },
            'scryfall': {
                'api_base_url': 'https://api.scryfall.com',
                'image_base_url': 'https://cards.scryfall.io',
                'default_image_size': 'large',
                'rate_limit': 10,
                'enable_image_cache': True,
                'image_cache_dir': 'data/image_cache',
                'max_cache_size_mb': 500
            },
            'logging': {
                'log_dir': 'logs',
                'app_log': 'logs/app.log',
                'index_log': 'logs/build_index.log',
                'level': 'INFO',
                'max_size_mb': 10,
                'backup_count': 5
            },
            'ui': {
                'window_title': 'MTG Deck Builder',
                'default_width': 1400,
                'default_height': 900,
                'theme': 'system',
                'search_result_limit': 100,
                'show_card_previews': True
                ,
                'test_mode': bool(os.getenv('MTG_TEST_MODE', False))
            }
        }
    
    @property
    def mtgjson(self) -> Dict[str, Any]:
        """Get MTGJSON configuration."""
        return self._config.get('mtgjson', {})
    
    @property
    def database(self) -> Dict[str, Any]:
        """Get database configuration."""
        return self._config.get('database', {})
    
    @property
    def scryfall(self) -> Dict[str, Any]:
        """Get Scryfall configuration."""
        return self._config.get('scryfall', {})
    
    @property
    def logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self._config.get('logging', {})
    
    @property
    def ui(self) -> Dict[str, Any]:
        """Get UI configuration."""
        return self._config.get('ui', {})
