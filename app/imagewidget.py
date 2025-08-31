from PySide6.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QFileDialog, QStackedWidget, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QKeySequence, QImage


class ImageWidget(QLabel):
    def __init__(self, image: QImage = None, width_pct: float = None, height_pct: float = None):
        super().__init__()

        self._original_image = image
        self._width_pct = width_pct
        self._height_pct = height_pct

        self.setAlignment(Qt.AlignCenter)


        # self.setStyleSheet("""
        #     border: 2px solid #aaa;
        # """)


        if self._original_image:
            self._updatePixmap()

    def setImage(self, image: QImage):
        self._original_image = image
        self._updatePixmap()

    def getImage(self):
        return self._original_image

    def resizeEvent(self, event):
        print("in resize event")
        print(event)
        self._updatePixmap()
        super().resizeEvent(event)

    def _updatePixmap(self):
        if not self._original_image:
            return
        print("Updating pixmap")
        target_width = self.width()
        target_height = self.height()
        
        if self._width_pct and self.parentWidget():
            target_width = int(self.parentWidget().width() * self._width_pct)

        if self._height_pct and self.parentWidget():
            target_height = int(self.parentWidget().height() * self._height_pct)
        print("self.parentWidget width = ", self.parentWidget().width())
        print("target_width = ", target_width)
        print("target height = ", target_height)
        # self.resize(target_width, target_height)

        pixmap = QPixmap.fromImage(self._original_image).scaled(
            target_width,
            target_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        self.setPixmap(pixmap)