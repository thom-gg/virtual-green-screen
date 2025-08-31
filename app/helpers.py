import sys
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QStackedWidget, QTabWidget,QPushButton

)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QKeySequence, QImage, QColor, QIcon, QPainter, QFont

class ColorBox(QPushButton):
    """A clickable color box widget"""
    
    def __init__(self, callback, color: str, size: int = 40):
        super().__init__()
        self.color = color
        self.setFixedSize(size, size)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        
        if color.lower() == "transparent" or color.lower() == "original":
            self.setText('🚫' if color.lower() == "transparent" else '📼')
            font = QFont()
            font.setPointSize(int(size * 0.8)) 
            self.setFont(font)
            bgStyle = "background: transparent;"
        
        else:
            bgStyle = f"background: {color};"
        
        self.setStyleSheet(f"""
            QPushButton {{
                {bgStyle}
                border: 2px solid #ddd;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                border: 2px solid #999;
            }}
            QPushButton:pressed {{
                border: 3px solid #333;
            }}
        """)
                
        self.clicked.connect(lambda: callback(self.color))


def qimage_to_numpy(qimage: QImage) -> np.ndarray:
    """Convert QImage to NumPy array."""
    qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)  # ensure 4 channels (RGBA)
    width = qimage.width()
    height = qimage.height()
    
    # Access the raw buffer
    ptr = qimage.bits()
    
    # Convert to NumPy array (height, width, channels)
    arr = np.array(ptr, dtype=np.uint8).reshape((height, width, 4))
    return arr


def numpy_to_qimage(arr: np.ndarray) -> QImage:
    """Convert NumPy array to QImage."""
    if arr.ndim == 2:  # Grayscale
        h, w = arr.shape
        bytes_per_line = w
        qimage = QImage(arr.data, w, h, bytes_per_line, QImage.Format_Grayscale8)
    elif arr.ndim == 3:
        h, w, ch = arr.shape
        if ch == 3:
            # RGB888
            bytes_per_line = 3 * w
            qimage = QImage(arr.data, w, h, bytes_per_line, QImage.Format_RGB888)
        elif ch == 4:
            # RGBA8888
            bytes_per_line = 4 * w
            qimage = QImage(arr.data, w, h, bytes_per_line, QImage.Format_RGBA8888)
        else:
            raise ValueError("Unsupported channel count: {}".format(ch))
    else:
        raise ValueError("Invalid array shape: {}".format(arr.shape))

    return qimage.copy()  # copy to detach from numpy buffer