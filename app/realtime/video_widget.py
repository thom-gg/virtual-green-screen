

from PySide6.QtWidgets import QLabel #type: ignore
from PySide6.QtCore import QSize, Qt #type: ignore
from PySide6.QtGui import QPixmap #type: ignore


class VideoWidget(QLabel):
    def __init__(self, width_pct: float, height_pct: float):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText("No video feed")
        
        self.width_pct = width_pct
        self.height_pct = height_pct
        
        # Calculate the actual size immediately and set it as fixed
        initial_size = self.calculate_target_size()
        self.setFixedSize(initial_size)
    
    def calculate_target_size(self):
        """Calculate target size - call this when parent is available"""
        if self.parent():
            parent_size = self.parent().size()
            width = int(parent_size.width() * self.width_pct / 100)
            height = int(parent_size.height() * self.height_pct / 100)
            return QSize(max(width, 320), max(height, 240))  # Ensure minimum
        return QSize(320, 240)
    
    def showEvent(self, event):
        """When widget is shown, recalculate and set fixed size"""
        super().showEvent(event)
        if self.parent():
            target_size = self.calculate_target_size()
            self.setFixedSize(target_size)
    
    def updateFrame(self, pixmap: QPixmap):
        if pixmap and not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)