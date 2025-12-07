import pytest
from PySide6.QtWidgets import QApplication
import time

from app.ui.workers.image_downloader import ImageDownloadWorker


class FakeScryfallClient:
    def download_card_image(self, scryfall_id, size=None, face='front'):
        # Return small fake PNG bytes
        return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"


def test_image_worker_emits_loaded_signal(qtbot):
    client = FakeScryfallClient()
    worker = ImageDownloadWorker(client, 'fake-id', 'uuid-123')

    results = {}

    def on_loaded(uuid, data):
        results['loaded'] = True
        results['uuid'] = uuid
        results['data'] = data

    def on_error(uuid, error):
        results['error'] = (uuid, error)

    worker.image_loaded.connect(on_loaded)
    worker.image_error.connect(on_error)
    # Run synchronously in tests to avoid threading complexity
    worker.run()

    assert results.get('loaded', False) is True
    assert results.get('uuid') == 'uuid-123'
    assert isinstance(results.get('data'), (bytes, bytearray))


def test_image_worker_emits_error_signal(qtbot):
    class BadScryfallClient:
        def download_card_image(self, scryfall_id, size=None, face='front'):
            raise RuntimeError("Network error")

    client = BadScryfallClient()
    worker = ImageDownloadWorker(client, 'bad-id', 'uuid-err')

    results = {}

    def on_loaded(uuid, data):
        results['loaded'] = True

    def on_error(uuid, error):
        results['error'] = (uuid, error)

    worker.image_loaded.connect(on_loaded)
    worker.image_error.connect(on_error)
    # Run synchronously in tests to avoid threading complexity
    worker.run()

    assert 'error' in results
    assert results['error'][0] == 'uuid-err'
