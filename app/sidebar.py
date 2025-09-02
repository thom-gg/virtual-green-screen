import os
from PySide6.QtWidgets import  QWidget, QVBoxLayout,QPushButton, QSizePolicy #type: ignore
from PySide6.QtCore import Qt, QSize # type: ignore
from PySide6.QtGui import QIcon # type: ignore

class Sidebar(QWidget):
    def __init__(self, params):
        super().__init__()
        self.params = params
        

        wrapper = QVBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setStyleSheet("background-color: #0e0e11;")
        
        containerLayout = QVBoxLayout()
        containerLayout.setContentsMargins(10, 10, 10, 10)  # Some padding


        self.buttons = []
        self.selectedIndex = 0

        assetsFolder = os.path.join(os.path.dirname(__file__), "assets/")
        for idx, b in enumerate(self.params):
            btn = QPushButton(b["title"])
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(45)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            path = os.path.join(assetsFolder, b["file"])
            btn.setIcon(QIcon(path))
            btn.setIconSize(QSize(20, 20))

            btn.setToolTip(b["tooltip"])
            btn.setStyleSheet(self.defaultStyle())
            btn.setLayoutDirection(Qt.LeftToRight)  # icon left, text right
            btn.setCheckable(True)

            btn.clicked.connect(lambda checked, id=idx: self.handleSelect(id))

            containerLayout.addWidget(btn)
            self.buttons.append(btn)
       

        containerLayout.addStretch() 
        container.setLayout(containerLayout)
        # Add the container to main layout
        wrapper.addWidget(container)
        self.setLayout(wrapper)

    def defaultStyle(self):
        return """
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 5px 12px;
                text-align: left;
                color: #ffffff;
                background-color: transparent;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2a2930;
            }
        """
    def selectedStyle(self):
        return """
            QPushButton {
                border: none;
                border-radius: 8px;
                padding: 5px 12px;
                text-align: left;
                color: #ffffff;
                background-color: #313039;
                font-weight: bold;
            }
        """

    def handleSelect(self, newIndex: int):
        if newIndex == self.selectedIndex:
            return
        self.updateStyle(newIndex)
        self.params[newIndex]["onClick"]()

    def updateStyle(self, newIndex: int):
        # Reset old
        self.buttons[self.selectedIndex].setStyleSheet(self.defaultStyle())
        # Highlight new
        self.buttons[newIndex].setStyleSheet(self.selectedStyle())
        self.selectedIndex = newIndex
        
