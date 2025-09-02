from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout,  QHBoxLayout # type: ignore
from app.helpers import ColorBox

class ForegroundTab(QWidget):
    def __init__(self, changeForegroundCallback):
        super().__init__()
        self.changeForegroundCallback = changeForegroundCallback
        layout = QVBoxLayout()
        
        label = QLabel("Foreground options")
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
                row_layout.addWidget(ColorBox(lambda c: self.changeForegroundCallback(c), color))
            row_layout.addStretch()
            grid.addLayout(row_layout)
        
        layout.addLayout(grid)
        layout.addStretch()  # Add space at bottom
        
        self.setLayout(layout)
