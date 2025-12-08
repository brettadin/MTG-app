"""
Card Image Display and Caching for MTG Deck Builder

Manages card image display with automatic downloading and caching.
Integrates with Scryfall API for high-quality card images.

Usage:
    from app.ui.card_image_display import CardImageWidget, ImageCache
    
    cache = ImageCache()
    widget = CardImageWidget(cache)
    widget.load_card_image("Lightning Bolt", "M21")
"""

import logging
from pathlib import Path
from typing import Optional
from PySide6.QtCore import Qt, Signal, QThread, QObject, QUrl
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QFrame, QHBoxLayout
from PySide6.QtGui import QPixmap, QImage, QPainter, QColor, QFont
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from urllib.parse import quote
import hashlib

logger = logging.getLogger(__name__)


class ImageDownloader(QObject):
    """
    Background thread for downloading card images.
    
    Signals:
        download_complete: Emitted when download finishes (url, image_data)
        download_failed: Emitted when download fails (url, error)
    """
    
    download_complete = Signal(str, bytes)
    download_failed = Signal(str, str)
    
    def __init__(self):
        """Initialize image downloader."""
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        logger.debug("ImageDownloader initialized")
    
    def download_image(self, url: str):
        """
        Download image from URL.
        
        Args:
            url: Image URL
        """
        request = QNetworkRequest(QUrl(url))
        request.setAttribute(QNetworkRequest.CacheLoadControlAttribute, QNetworkRequest.PreferCache)
        
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self._handle_reply(reply, url))
        
        logger.debug(f"Downloading image: {url}")
    
    def _handle_reply(self, reply: QNetworkReply, url: str):
        """Handle network reply."""
        if reply.error() == QNetworkReply.NoError:
            image_data = reply.readAll().data()
            self.download_complete.emit(url, image_data)
            logger.debug(f"Downloaded {len(image_data)} bytes from {url}")
        else:
            error_msg = reply.errorString()
            self.download_failed.emit(url, error_msg)
            logger.error(f"Download failed: {error_msg}")
        
        reply.deleteLater()


class ImageCache:
    """
    Cache for card images to avoid re-downloading.
    """
    
    def __init__(self, cache_dir: str = "data/image_cache"):
        """
        Initialize image cache.
        
        Args:
            cache_dir: Directory for cached images
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self.memory_cache: dict = {}
        self.max_memory_cache = 50  # Keep 50 images in memory
        
        logger.info(f"ImageCache initialized: {self.cache_dir}")
    
    def get_cache_path(self, url: str) -> Path:
        """Get cache file path for URL."""
        # Hash URL for filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        return self.cache_dir / f"{url_hash}.jpg"
    
    def is_cached(self, url: str) -> bool:
        """Check if image is cached."""
        if url in self.memory_cache:
            return True
        
        return self.get_cache_path(url).exists()
    
    def get_cached_image(self, url: str) -> Optional[QPixmap]:
        """
        Get cached image.
        
        Args:
            url: Image URL
            
        Returns:
            QPixmap if cached, None otherwise
        """
        # Check memory cache
        if url in self.memory_cache:
            logger.debug(f"Image found in memory cache: {url}")
            return self.memory_cache[url]
        
        # Check disk cache
        cache_path = self.get_cache_path(url)
        if cache_path.exists():
            pixmap = QPixmap(str(cache_path))
            if not pixmap.isNull():
                # Add to memory cache
                self._add_to_memory_cache(url, pixmap)
                logger.debug(f"Image loaded from disk cache: {cache_path}")
                return pixmap
        
        return None
    
    def cache_image(self, url: str, image_data: bytes) -> bool:
        """
        Cache image data.
        
        Args:
            url: Image URL
            image_data: Raw image bytes
            
        Returns:
            True if successful
        """
        try:
            # Save to disk
            cache_path = self.get_cache_path(url)
            cache_path.write_bytes(image_data)
            
            # Add to memory cache
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            if not pixmap.isNull():
                self._add_to_memory_cache(url, pixmap)
            
            logger.debug(f"Cached image: {cache_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to cache image: {e}")
            return False
    
    def _add_to_memory_cache(self, url: str, pixmap: QPixmap):
        """Add image to memory cache with LRU eviction."""
        if len(self.memory_cache) >= self.max_memory_cache:
            # Remove oldest (first) item
            first_key = next(iter(self.memory_cache))
            del self.memory_cache[first_key]
        
        self.memory_cache[url] = pixmap
    
    def clear_cache(self):
        """Clear all cached images."""
        # Clear memory
        self.memory_cache.clear()
        
        # Clear disk
        for file in self.cache_dir.glob("*.jpg"):
            file.unlink()
        
        logger.info("Image cache cleared")


class CardImageWidget(QLabel):
    """
    Widget for displaying card images with loading indicator.
    
    Signals:
        image_loaded: Emitted when image loaded successfully (card_name)
        image_failed: Emitted when image loading failed (card_name, error)
    """
    
    image_loaded = Signal(str)
    image_failed = Signal(str, str)
    
    def __init__(
        self,
        image_cache: Optional[ImageCache] = None,
        width: int = 250,
        height: int = 350,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize card image widget.
        
        Args:
            image_cache: ImageCache instance
            width: Image width
            height: Image height
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.image_cache = image_cache or ImageCache()
        self.downloader = ImageDownloader()
        self.current_url: Optional[str] = None
        
        # Setup widget
        self.setFixedSize(width, height)
        self.setFrameShape(QFrame.Box)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 2px solid #5a4a9e; background-color: #1a1625;")
        
        # Show placeholder
        self._show_placeholder()
        
        # Connect downloader signals
        self.downloader.download_complete.connect(self._on_download_complete)
        self.downloader.download_failed.connect(self._on_download_failed)
        
        logger.debug("CardImageWidget initialized")
    
    def load_card_image(
        self,
        card_name: Optional[str] = None,
        scryfall_id: Optional[str] = None,
        set_code: Optional[str] = None,
        scryfall_client = None
    ):
        """
        Load and display card image.
        
        Args:
            card_name: Card name
            set_code: Optional set code for specific printing
            scryfall_client: ScryfallClient instance for URL lookup
        """
        self.current_card_name = card_name
        
        # Show loading state
        self._show_loading(card_name)
        
        # Get image URL
        # If scryfall_id provided and client is passed, use CDN URL
        url = None
        if scryfall_client and scryfall_id:
            # Ask the client for a normal-size image by Scryfall id
            try:
                url = scryfall_client.get_card_image_url(scryfall_id, size='normal')
            except TypeError:
                # Backwards compatibility: some clients may accept (id, set_code)
                url = scryfall_client.get_card_image_url(scryfall_id, set_code)
        elif scryfall_client and card_name and hasattr(scryfall_client, 'get_card_image_by_name'):
            # Optional helper on client
            url = scryfall_client.get_card_image_by_name(card_name, set_code)
        else:
            # Fallback: construct named API URL which returns image
            url = self._construct_scryfall_url(card_name, set_code)
        
        if not url:
            self._show_error("Image URL not found")
            self.image_failed.emit(card_name, "URL not found")
            return
        
        self.current_url = url
        
        # Check cache first
        cached_image = self.image_cache.get_cached_image(url)
        if cached_image:
            self._display_image(cached_image)
            self.image_loaded.emit(card_name)
            return
        
        # Download image
        self.downloader.download_image(url)
    
    def _construct_scryfall_url(self, card_name: Optional[str], set_code: Optional[str] = None) -> Optional[str]:
        """Construct Scryfall image URL."""
        # Use named API endpoint
        base_url = "https://api.scryfall.com/cards/named"
        if not card_name:
            return None
        params = f"?exact={quote(card_name)}&format=image&version=normal"
        
        if set_code:
            params += f"&set={set_code.lower()}"
        
        return base_url + params
    
    def _on_download_complete(self, url: str, image_data: bytes):
        """Handle successful download."""
        if url != self.current_url:
            return  # Old request
        
        # Cache image
        self.image_cache.cache_image(url, image_data)
        
        # Display image
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)
        
        if not pixmap.isNull():
            self._display_image(pixmap)
            self.image_loaded.emit(self.current_card_name)
        else:
            self._show_error("Invalid image data")
            self.image_failed.emit(self.current_card_name, "Invalid image")
    
    def _on_download_failed(self, url: str, error: str):
        """Handle download failure."""
        if url != self.current_url:
            return
        
        self._show_error(f"Failed to load image:\n{error}")
        self.image_failed.emit(self.current_card_name, error)
    
    def _display_image(self, pixmap: QPixmap):
        """Display image with scaling."""
        scaled = pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.setPixmap(scaled)
    
    def _show_placeholder(self):
        """Show placeholder when no image loaded."""
        self.setText("No card selected")
        self.setStyleSheet("border: 2px solid #5a4a9e; background-color: #1a1625; color: #7a6abd;")
    
    def _show_loading(self, card_name: str):
        """Show loading indicator."""
        self.setText(f"Loading {card_name}...")
        self.setStyleSheet("border: 2px solid #5a4a9e; background-color: #1a1625; color: #ffd700;")
    
    def _show_error(self, message: str):
        """Show error message."""
        self.setText(message)
        self.setStyleSheet("border: 2px solid #d13438; background-color: #1a1625; color: #ff6b6b;")
    
    def clear_image(self):
        """Clear current image and show placeholder."""
        self.current_url = None
        self.current_card_name = None
        self.clear()
        self._show_placeholder()


class CardImagePanel(QWidget):
    """
    Panel with card image and metadata.
    
    Combines CardImageWidget with card name, set, and rarity labels.
    """
    
    def __init__(
        self,
        image_cache: Optional[ImageCache] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize card image panel.
        
        Args:
            image_cache: ImageCache instance
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.image_cache = image_cache or ImageCache()
        self.setup_ui()
        
        logger.debug("CardImagePanel initialized")
    
    def setup_ui(self):
        """Setup the UI."""
        layout = QVBoxLayout(self)
        
        # Card name
        self.name_label = QLabel("No card selected")
        self.name_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)
        
        # Card image
        self.image_widget = CardImageWidget(self.image_cache)
        layout.addWidget(self.image_widget, 0, Qt.AlignCenter)
        
        # Set and rarity info
        info_layout = QHBoxLayout()
        
        self.set_label = QLabel("")
        self.set_label.setFont(QFont("Keyrune", 14))
        info_layout.addWidget(self.set_label)
        
        info_layout.addStretch()
        
        self.rarity_label = QLabel("")
        self.rarity_label.setFont(QFont("Arial", 10, QFont.Bold))
        info_layout.addWidget(self.rarity_label)
        
        layout.addLayout(info_layout)
    
    def load_card(
        self,
        card_name: str,
        set_code: Optional[str] = None,
        rarity: Optional[str] = None,
        scryfall_client = None
    ):
        """
        Load and display card.
        
        Args:
            card_name: Card name
            set_code: Set code
            rarity: Card rarity
            scryfall_client: ScryfallClient instance
        """
        self.name_label.setText(card_name)
        
        if set_code:
            from app.utils.mtg_symbols import set_code_to_symbol
            self.set_label.setText(set_code_to_symbol(set_code))
        else:
            self.set_label.setText("")
        
        if rarity:
            from app.utils.rarity_colors import apply_rarity_style
            self.rarity_label.setText(rarity.title())
            apply_rarity_style(self.rarity_label, rarity, light_mode=True)
        else:
            self.rarity_label.setText("")
        
        # Use keyword args to avoid positional mismatch between callers
        self.image_widget.load_card_image(card_name=card_name, set_code=set_code, scryfall_client=scryfall_client)
    
    def clear(self):
        """Clear panel."""
        self.name_label.setText("No card selected")
        self.set_label.setText("")
        self.rarity_label.setText("")
        self.image_widget.clear_image()


# Module initialization
logger.info("Card image display module loaded")
