from PySide6.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QFileDialog, QStackedWidget, QPushButton, QGridLayout, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QKeySequence, QImage, QColor
from app.helpers import ColorBox

class BackgroundTab(QWidget):
    def __init__(self, changeBackgroundCallback):
        super().__init__()
        self.changeBackgroundCallback = changeBackgroundCallback
        layout = QVBoxLayout()
        
        label = QLabel("Background options")
        label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(label)
        
        
 
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
                row_layout.addWidget(ColorBox(lambda c: self.changeBackgroundCallback(c), color))
            row_layout.addStretch()
            grid.addLayout(row_layout)
        
        layout.addLayout(grid)
        layout.addStretch()  # Add space at bottom
        
        self.setLayout(layout)
