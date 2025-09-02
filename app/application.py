import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QStackedWidget # type: ignore

from app.sidebar import Sidebar
from app.realtime.realtime import RealTimeProcessing
from qt_material import apply_stylesheet # type: ignore
from app.offline.offline import OfflineProcessing


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual green screen")
        self.resize(1100, 768)
        
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        self.layout.setSpacing(0)
       
        self.mainContainer = QStackedWidget()
        self.offlineProcessing = OfflineProcessing()
        self.realTimeProcessing = RealTimeProcessing()
        self.mainContainer.addWidget(self.offlineProcessing)
        self.mainContainer.addWidget(self.realTimeProcessing)
        self.mainContainer.setCurrentWidget(self.offlineProcessing) 
    
        sidebarParams = [{"file": "galerie_color.png", "onClick": self.switchToOffline, "title": "Offline", "tooltip": "Offline processing (images / videos)"},
                    {"file": "camera.png", "onClick": self.switchToRealTime, "title": "Webcam", "tooltip": "Real time processing (webcam)"}]
     
        sidebar = Sidebar(sidebarParams)
        
        self.layout.addWidget(sidebar, 10)
        self.layout.addWidget(self.mainContainer, 90)
        self.setLayout(self.layout)
    
    def switchToRealTime(self):
        self.realTimeProcessing.startWebcam()
        self.mainContainer.setCurrentWidget(self.realTimeProcessing)

    def switchToOffline(self):
        self.mainContainer.setCurrentWidget(self.offlineProcessing)
        self.realTimeProcessing.stopWebcam()

    def closeEvent(self, event):
        self.realTimeProcessing.closeEvent(event)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()

    themePath = os.path.join(os.path.dirname(__file__), "themes", "theme.xml")
    apply_stylesheet(app, theme=themePath)
    
    window.show()
    sys.exit(app.exec())
