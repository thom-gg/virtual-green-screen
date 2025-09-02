from PySide6.QtWidgets import QLabel # type: ignore
from PySide6.QtCore import Qt # type: ignore
from PySide6.QtGui import QPixmap, QImage # type: ignore


class ImageWidget(QLabel):
    def __init__(self, image: QImage = None, width_pct: float = 100., height_pct: float = 100.):
        super().__init__()

        self._original_image = image
        self._width_pct = width_pct
        self._height_pct = height_pct

        self.setAlignment(Qt.AlignCenter)

        if self._original_image:
            self._updatePixmap()

    def setImage(self, image: QImage):
        self._original_image = image
        self._updatePixmap()

    def getImage(self):
        return self._original_image

    def resizeEvent(self, event):
        self._updatePixmap()
        super().resizeEvent(event)

    def _updatePixmap(self):
        if not self._original_image:
            return

        target_width = self.width()
        target_height = self.height()
        
        if self._width_pct and self.parentWidget():
            target_width = int(self.parentWidget().width() * self._width_pct)

        if self._height_pct and self.parentWidget():
            target_height = int(self.parentWidget().height() * self._height_pct)
      

        pixmap = QPixmap.fromImage(self._original_image).scaled(
            target_width,
            target_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(pixmap)