from typing import List
from PySide6.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QFileDialog, QStackedWidget, QPushButton, QGridLayout, QHBoxLayout
)
from PySide6.QtGui import QIcon, QPixmap, QColor, QPalette
from PySide6.QtCore import Qt
import os

class Sidebar(QWidget):
    def __init__(self, params: List[dict]):
        super().__init__()
        self.params = params


        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#0e0e11"))
        self.setPalette(palette)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 50, 0, 0)
        layout.setSpacing(10)

        self.buttons = []
        self.selectedIndex = 0
        
        
        assetsFolder = os.path.join(os.path.dirname(__file__), "assets/")
        for idx,b in enumerate(self.params):
            btn = QPushButton()
            btn.setFixedSize(40, 40) 
            path = os.path.join(assetsFolder, b["file"])
            btn.setIcon(QIcon(path))
            btn.setIconSize(btn.size() * 0.8)
            btn.setToolTip(b["tooltip"])
            btn.clicked.connect(lambda checked, id=idx: self.handleSelect(id))
                            
            btn.setCursor(Qt.PointingHandCursor)
            layout.addWidget(btn,alignment=Qt.AlignHCenter)
            self.buttons.append(btn)

        self.updateStyle(newIndex=self.selectedIndex)
        layout.addStretch()  # Add space at bottom
        
        self.setLayout(layout)

    def handleSelect(self, newIndex: int):
        if (newIndex == self.selectedIndex):
            return
        self.updateStyle(newIndex)
        self.params[newIndex]["onClick"]()

    def updateStyle(self, newIndex: int):
        # Reset old button
        self.buttons[self.selectedIndex].setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0px;
                border-radius: 8px;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #313039;
            }
        """)

        # Update new button
        self.buttons[newIndex].setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0px;
                border-radius: 8px;
                background-color: #313039;
            }                       
        """)
        self.selectedIndex = newIndex



