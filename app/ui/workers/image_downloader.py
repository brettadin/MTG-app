from PySide6.QtCore import QThread, Signal


class ImageDownloadWorker(QThread):
    image_loaded = Signal(str, bytes)  # uuid, image bytes
    image_error = Signal(str, str)     # uuid, error

    def __init__(self, scryfall_client, scryfall_id: str, uuid: str, size: str = None, face: str = 'front', parent=None):
        super().__init__(parent)
        self.scryfall_client = scryfall_client
        self.scryfall_id = scryfall_id
        self.uuid = uuid
        self.size = size
        self.face = face

    def run(self):
        try:
            image_data = self.scryfall_client.download_card_image(self.scryfall_id, self.size, self.face)
            if image_data:
                self.image_loaded.emit(self.uuid, image_data)
            else:
                self.image_error.emit(self.uuid, 'No image data')
        except Exception as e:
            self.image_error.emit(self.uuid, str(e))
