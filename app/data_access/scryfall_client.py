"""
Client for Scryfall API interactions.
"""

import logging
import time
from typing import Optional
from pathlib import Path
import httpx

logger = logging.getLogger(__name__)


class ScryfallClient:
    """
    Client for fetching card images and data from Scryfall.
    """
    
    def __init__(self, config: dict):
        """
        Initialize Scryfall client.
        
        Args:
            config: Configuration dictionary with Scryfall settings
        """
        self.api_base = config.get('api_base_url', 'https://api.scryfall.com')
        self.image_base = config.get('image_base_url', 'https://cards.scryfall.io')
        self.default_size = config.get('default_image_size', 'large')
        self.rate_limit = config.get('rate_limit', 10)
        self.enable_cache = config.get('enable_image_cache', True)
        self.cache_dir = Path(config.get('image_cache_dir', 'data/image_cache'))
        
        self._last_request_time = 0
        self._min_request_interval = 1.0 / self.rate_limit
        
        if self.enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _rate_limit_wait(self):
        """Enforce rate limiting between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            sleep_time = self._min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self._last_request_time = time.time()
    
    def get_card_image_url(
        self,
        scryfall_id: str,
        size: Optional[str] = None,
        face: str = 'front'
    ) -> Optional[str]:
        """
        Get Scryfall image URL for a card.
        
        Args:
            scryfall_id: Scryfall UUID for the card
            size: Image size (small, normal, large, png, art_crop, border_crop)
            face: Card face for double-faced cards (front, back)
            
        Returns:
            Image URL or None if invalid
        """
        if not scryfall_id:
            return None
        
        size = size or self.default_size
        
        # Scryfall image URL pattern
        # Format: https://cards.scryfall.io/{size}/{face}/{dir1}/{dir2}/{id}.jpg
        dir1 = scryfall_id[0]
        dir2 = scryfall_id[1]
        
        # Determine file extension based on size
        ext = 'png' if size == 'png' else 'jpg'
        
        url = f"{self.image_base}/{size}/{face}/{dir1}/{dir2}/{scryfall_id}.{ext}"
        logger.debug(f"Generated image URL: {url}")
        
        return url
    
    def download_card_image(
        self,
        scryfall_id: str,
        size: Optional[str] = None,
        face: str = 'front'
    ) -> Optional[bytes]:
        """
        Download card image from Scryfall.
        
        Args:
            scryfall_id: Scryfall UUID for the card
            size: Image size
            face: Card face for double-faced cards
            
        Returns:
            Image bytes or None if download failed
        """
        url = self.get_card_image_url(scryfall_id, size, face)
        if not url:
            return None
        
        # Check cache first
        if self.enable_cache:
            cache_path = self._get_cache_path(scryfall_id, size, face)
            if cache_path.exists():
                logger.debug(f"Loading image from cache: {cache_path}")
                return cache_path.read_bytes()
        
        # Download from Scryfall
        try:
            self._rate_limit_wait()
            
            with httpx.Client() as client:
                response = client.get(url, timeout=30.0)
                response.raise_for_status()
                
                image_data = response.content
                logger.info(f"Downloaded image for {scryfall_id} ({len(image_data)} bytes)")
                
                # Cache if enabled
                if self.enable_cache:
                    cache_path = self._get_cache_path(scryfall_id, size, face)
                    cache_path.parent.mkdir(parents=True, exist_ok=True)
                    cache_path.write_bytes(image_data)
                    logger.debug(f"Cached image to: {cache_path}")
                
                return image_data
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to download image from {url}: {e}")
            return None
    
    def get_card_data(self, scryfall_id: str) -> Optional[dict]:
        """
        Fetch card data from Scryfall API.
        
        Args:
            scryfall_id: Scryfall UUID for the card
            
        Returns:
            Card data dictionary or None if failed
        """
        url = f"{self.api_base}/cards/{scryfall_id}"
        
        try:
            self._rate_limit_wait()
            
            with httpx.Client() as client:
                response = client.get(url, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Fetched card data for {scryfall_id}")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Failed to fetch card data from {url}: {e}")
            return None
    
    def search_cards(self, query: str, page: int = 1) -> Optional[dict]:
        """
        Search for cards using Scryfall API.
        
        Args:
            query: Scryfall search query
            page: Page number (1-indexed)
            
        Returns:
            Search results dictionary or None if failed
        """
        url = f"{self.api_base}/cards/search"
        params = {
            'q': query,
            'page': page
        }
        
        try:
            self._rate_limit_wait()
            
            with httpx.Client() as client:
                response = client.get(url, params=params, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                logger.info(f"Search returned {data.get('total_cards', 0)} results")
                return data
                
        except httpx.HTTPError as e:
            logger.error(f"Search failed: {e}")
            return None
    
    def _get_cache_path(self, scryfall_id: str, size: str, face: str) -> Path:
        """Get cache file path for an image."""
        ext = 'png' if size == 'png' else 'jpg'
        filename = f"{scryfall_id}_{size}_{face}.{ext}"
        return self.cache_dir / filename
    
    def clear_cache(self):
        """Clear the image cache directory."""
        if not self.enable_cache or not self.cache_dir.exists():
            return
        
        count = 0
        for file in self.cache_dir.glob('*'):
            if file.is_file():
                file.unlink()
                count += 1
        
        logger.info(f"Cleared {count} files from image cache")
