import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel # type: ignore

from app.sidebar import Sidebar
from app.footer import Footer
from app.realtime.realtime import RealTimeProcessing
from qt_material import apply_stylesheet # type: ignore
from app.offline.offline import OfflineProcessing


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual green screen")
        self.resize(1100, 768)
        
        
        self.layout = QVBoxLayout(self) # Contains main layout + footer
        self.layout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        self.layout.setSpacing(0)

        self.mainLayout = QHBoxLayout() # contains sidebar + mainContainer
        self.mainLayout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom
        self.mainLayout.setSpacing(0)
       
        self.mainContainer = QStackedWidget()
        self.offlineProcessing = OfflineProcessing()
        self.realTimeProcessing = RealTimeProcessing()
        self.mainContainer.addWidget(self.offlineProcessing)
        self.mainContainer.addWidget(self.realTimeProcessing)
        self.mainContainer.setCurrentWidget(self.offlineProcessing) 
    
        sidebarParams = [{"file": "galerie_color.png", "onClick": self.switchToOffline, "title": "Offline", "tooltip": "Offline processing (images / videos)"},
                    {"file": "camera.png", "onClick": self.switchToRealTime, "title": "Webcam", "tooltip": "Real time processing (webcam)"}]
     
        sidebar = Sidebar(sidebarParams)
        
        self.mainLayout.addWidget(sidebar, 10)
        self.mainLayout.addWidget(self.mainContainer, 90)


        mainLayoutWidget = QWidget() # wrapper around the main layout
        mainLayoutWidget.setLayout(self.mainLayout)
        footer = Footer(self.updateModelCallback)

        self.layout.addWidget(mainLayoutWidget, 96)
        self.layout.addWidget(footer, 4)


        self.setLayout(self.layout)

    def updateModelCallback(self, modelInfos: dict):
        self.realTimeProcessing.updateModel(modelInfos)
        self.offlineProcessing.updateModel(modelInfos)
    
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

    themePath = os.path.join(os.path.dirname(__file__), "themes", "theme.xml")
    apply_stylesheet(app, theme=themePath)

    window = MainWindow()

    
    window.show()
    sys.exit(app.exec())
