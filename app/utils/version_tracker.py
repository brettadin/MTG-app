"""
Version tracking for MTGJSON data and index builds.
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VersionTracker:
    """
    Tracks MTGJSON data versions and index build information.
    """
    
    def __init__(self, version_file: str = "data/INDEX_VERSION.json"):
        """
        Initialize version tracker.
        
        Args:
            version_file: Path to version tracking file
        """
        self.version_file = Path(version_file)
        self.version_file.parent.mkdir(parents=True, exist_ok=True)
    
    def save_version_info(
        self,
        mtgjson_version: str,
        mtgjson_date: str,
        card_count: int,
        set_count: int,
        build_time: float,
        additional_info: Optional[Dict[str, Any]] = None
    ):
        """
        Save version and build information.
        
        Args:
            mtgjson_version: MTGJSON version string
            mtgjson_date: MTGJSON build date
            card_count: Number of cards indexed
            set_count: Number of sets indexed
            build_time: Time taken to build index (seconds)
            additional_info: Additional metadata
        """
        info = {
            'mtgjson_version': mtgjson_version,
            'mtgjson_date': mtgjson_date,
            'card_count': card_count,
            'set_count': set_count,
            'build_time_seconds': build_time,
            'build_timestamp': datetime.now().isoformat(),
            'additional_info': additional_info or {}
        }
        
        try:
            with open(self.version_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2)
            logger.info(f"Saved version info to {self.version_file}")
        except Exception as e:
            logger.error(f"Failed to save version info: {e}")
    
    def load_version_info(self) -> Optional[Dict[str, Any]]:
        """
        Load version information.
        
        Returns:
            Version info dictionary or None if not found
        """
        if not self.version_file.exists():
            return None
        
        try:
            with open(self.version_file, 'r', encoding='utf-8') as f:
                info = json.load(f)
            logger.info(f"Loaded version info from {self.version_file}")
            return info
        except Exception as e:
            logger.error(f"Failed to load version info: {e}")
            return None
    
    def check_version_mismatch(self, current_mtgjson_version: str) -> bool:
        """
        Check if current MTGJSON version differs from indexed version.
        
        Args:
            current_mtgjson_version: Current MTGJSON version
            
        Returns:
            True if versions differ
        """
        info = self.load_version_info()
        if not info:
            return True  # No index exists
        
        indexed_version = info.get('mtgjson_version', '')
        return indexed_version != current_mtgjson_version
    
    def get_index_age_days(self) -> Optional[float]:
        """
        Get age of index in days.
        
        Returns:
            Age in days or None if no index
        """
        info = self.load_version_info()
        if not info or 'build_timestamp' not in info:
            return None
        
        try:
            build_time = datetime.fromisoformat(info['build_timestamp'])
            age = datetime.now() - build_time
            return age.total_seconds() / 86400  # Convert to days
        except Exception as e:
            logger.error(f"Failed to calculate index age: {e}")
            return None
