import os
from pathlib import Path

from app.data_access.scryfall_client import ScryfallClient


def test_scryfall_client_uses_cache(tmp_path):
    config = {
        'image_cache_dir': str(tmp_path),
        'enable_image_cache': True,
        'image_base_url': 'https://example.com'
    }
    client = ScryfallClient(config)

    scryfall_id = 'abcde12345'
    size = 'large'
    face = 'front'
    cache_path = client._get_cache_path(scryfall_id, size, face)

    # Create a fake cache file
    fake_bytes = b'FAKEIMAGEBYTES'
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_bytes(fake_bytes)

    # Now call download_card_image and it should load from cache
    image = client.download_card_image(scryfall_id, size=size, face=face)
    assert image == fake_bytes
