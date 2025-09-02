import numpy as np
from PySide6.QtWidgets import QPushButton #type: ignore
from PySide6.QtCore import Qt # type: ignore
from PySide6.QtGui import QImage, QFont #type: ignore
import cv2

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
                padding: 0;
                margin: 0;
            }}
            QPushButton:hover {{
                border: 2px solid #999;
            }}
            QPushButton:pressed {{
                border: 3px solid #333;
            }}
        """)
                
        self.clicked.connect(lambda: callback({"type": "color", "value": self.color}))


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


def load_image_as_array(path, target_width, target_height):
    # Read image in BGR format
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError(f"Could not load image: {path}")

    # Ensure 4 channels (if no alpha, add fully opaque)
    if img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)

    # Convert BGRA -> RGBA
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGBA)
    h, w, _ = img.shape

    # --- Resize (zoom if too small) ---
    # Scale factor to make sure image is at least as large as target
    scale = max(target_width / w, target_height / h)
    new_w, new_h = int(w * scale), int(h * scale)

    resized = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # --- Crop to exact target size (center crop) ---
    start_x = (new_w - target_width) // 2
    start_y = (new_h - target_height) // 2
    cropped = resized[start_y:start_y+target_height, start_x:start_x+target_width]

    return cropped