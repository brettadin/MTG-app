"""
MTG Deck Builder Application

Main entry point for the application.
"""

import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.config import Config
from app.logging_config import setup_logging
from app.ui.integrated_main_window import IntegratedMainWindow

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    # Load configuration
    config = Config()
    
    # Set up logging
    log_config = config.logging_config
    setup_logging(
        log_dir=log_config.get('log_dir', 'logs'),
        app_log=log_config.get('app_log', 'logs/app.log'),
        level=log_config.get('level', 'INFO'),
        max_size_mb=log_config.get('max_size_mb', 10),
        backup_count=log_config.get('backup_count', 5)
    )
    
    logger.info("Starting MTG Deck Builder application")
    
    # Check if database exists
    db_path = Path(config.get('database.db_path'))
    if not db_path.exists():
        logger.warning("Database not found. Please run scripts/build_index.py first.")
        print("\n" + "=" * 60)
        print("DATABASE NOT FOUND")
        print("=" * 60)
        print("\nPlease build the index first by running:")
        print("  python scripts/build_index.py")
        print("\nThis will create the searchable database from MTGJSON data.")
        print("=" * 60 + "\n")
        return 1
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("MTG Deck Builder")
    app.setOrganizationName("MTG Deck Builder")
    
    # Create and show main window with all features integrated
    window = IntegratedMainWindow(config)
    window.show()
    
    logger.info("Application window displayed")
    
    # Run application
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
