"""
Rebuild the index (delete and recreate).
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from app.logging_config import setup_logging
import logging

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    # Load configuration
    config = Config()
    
    # Set up logging
    log_config = config.logging_config
    setup_logging(
        log_dir=log_config.get('log_dir', 'logs'),
        app_log=log_config.get('index_log', 'logs/build_index.log'),
        level=log_config.get('level', 'INFO')
    )
    
    # Get database path
    db_path = Path(config.get('database.db_path'))
    
    # Delete existing database
    if db_path.exists():
        logger.info(f"Deleting existing database: {db_path}")
        db_path.unlink()
    
    # Delete version file
    version_file = Path(config.get('database.index_version_file'))
    if version_file.exists():
        logger.info(f"Deleting version file: {version_file}")
        version_file.unlink()
    
    # Import and run build_index
    from build_index import IndexBuilder
    
    builder = IndexBuilder(config)
    builder.build()


if __name__ == '__main__':
    main()
