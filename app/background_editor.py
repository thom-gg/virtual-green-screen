from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout, QHBoxLayout # type: ignore
from PySide6.QtCore import Qt, QSize # type: ignore
from PySide6.QtGui import QPixmap # type: ignore
from app.helpers import ColorBox
import os


class BackgroundBox(QLabel):
    def __init__(self, img_path, callback, size=(160, 90), parent=None):
        super().__init__(parent)
        self.img_path = img_path
        self.callback = callback

        # Load preview pixmap (scaled to 16:9 thumbnail)
        pixmap = QPixmap(img_path)
        if not pixmap.isNull():
            self.setPixmap(pixmap.scaled(
                QSize(*size),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            ))

        self.setFixedSize(*size)
        self.setStyleSheet("border: 2px solid #ddd; border-radius: 6px;")
        self.setAlignment(Qt.AlignCenter)

        # Make clickable
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.callback({'type': 'image', 'value': self.img_path})

class BackgroundTab(QWidget):
    def __init__(self, changeBackgroundCallback):
        super().__init__()
        self.changeBackgroundCallback = changeBackgroundCallback
        layout = QVBoxLayout()
        
        label = QLabel("Background options")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        
        layout.addWidget(QLabel("Colors"))
        layout.addLayout(self.initColorsGrid())

        layout.addWidget(QLabel("Backgrounds"))

        layout.addLayout(self.initBackgroundsGrid())
        layout.addStretch()  # Add space at bottom
        
        self.setLayout(layout)

    def initColorsGrid(self):

        colors = ["original", "transparent", "red", "green", "black", "white", "purple"]
        itemsPerLine = 10

        grid = QVBoxLayout()
        for rowIdx in range( (len(colors) + itemsPerLine - 1) // itemsPerLine):
            row_layout = QHBoxLayout()
            for colIdx in range(itemsPerLine):
                idx = rowIdx * itemsPerLine + colIdx
                if (idx >= len(colors)):
                    break
                color = colors[idx]
                row_layout.addWidget(ColorBox(self.changeBackgroundCallback, color))
            row_layout.addStretch()
            grid.addLayout(row_layout)
        return grid

    def initBackgroundsGrid(self):
        itemsPerLine = 8

        bgGrid = QVBoxLayout()

        # Load all files in assets/backgrounds
        bg_dir = os.path.join(os.path.dirname(__file__), "assets/backgrounds")
        files = [os.path.join(bg_dir, f) for f in os.listdir(bg_dir)
                 if f.lower().endswith((".png", ".jpg", ".jpeg"))]

        for row_idx in range((len(files) + itemsPerLine - 1) // itemsPerLine):
            row_layout2 = QHBoxLayout()
            for col_idx in range(itemsPerLine):
                idx = row_idx * itemsPerLine + col_idx
                if idx >= len(files):
                    break
                img_path = files[idx]
                row_layout2.addWidget(
                    BackgroundBox(img_path, self.changeBackgroundCallback, size=(80, 45))
                )
            row_layout2.addStretch()
            bgGrid.addLayout(row_layout2)
        return bgGrid

      
