import sys
from PySide6.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QStackedWidget, QTabWidget,QPushButton

)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QKeySequence, QImage, QPalette, QColor, QFont
from app.dropzone import DropZone, DropZoneWrapper
from app.imagewidget import ImageWidget
from app.background_editor import BackgroundTab
from app.foreground_editor import ForegroundTab
from app.sidebar import Sidebar
from app.wrappers.u2net_wrapper import U2NetWrapper
from app.realtime import RealTimeProcessing
from app import helpers
class ProcessImage(QWidget):

    def __init__(self, bgRemover):
        super().__init__()
        layout = QVBoxLayout()
        self.bgRemover = bgRemover

        # Add widgets to layout
        self.image_widget = ImageWidget(width_pct=1, height_pct=0.56)
        layout.addWidget(self.image_widget)

        # Add download and copy buttons
        button_layout = QHBoxLayout()

        self.copy_button = QPushButton()
        self.copy_button.setText("📋")
        self.copy_button.setToolTip("Copy to clipboard")
        self.copy_button.setFixedSize(40, 40)
        self.copy_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.copy_button.clicked.connect(self.copyImage)

        self.download_button = QPushButton()
        self.download_button.setText("💾")
        self.download_button.setToolTip("Download image")
        self.download_button.setFixedSize(40, 40)
        self.download_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)


        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.copy_button)

        layout.addLayout(button_layout)
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(BackgroundTab(self.changeBackground), "1️⃣ Background")
        self.tab_widget.addTab(ForegroundTab(self.changeForeground), "2️⃣ Foreground")
        layout.addWidget(self.tab_widget)
   


        self.setLayout(layout)
        self.currentBackground = 'original'
        self.currentForeground = 'original'

    def changeBackground(self, color: str):
        self.currentBackground = color
        self.updateImage()
    def changeForeground(self, color: str):
        self.currentForeground = color
        self.updateImage()
    
    def updateImage(self):
        newImage = self.bgRemover.getImage(background=self.currentBackground, foreground=self.currentForeground)
        qImage = helpers.numpy_to_qimage(newImage)
        self.image_widget.setImage(qImage)

    def setImage(self, image):
        """Forward image to ImageWidget"""
        self.image_widget.setImage(image)

    def copyImage(self):
        prevText = self.copy_button.text()
        self.copy_button.setText('✅')
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(QPixmap.fromImage(self.image_widget.getImage()))
        QTimer.singleShot(500, lambda: self.copy_button.setText(prevText))


    



class OfflineProcessing(QWidget):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Virtual green screen")
        # self.resize(1100, 768)

        layout = QVBoxLayout(self)

        self.all_bgRemover = [{"wrapperClass": U2NetWrapper, "parameters": ['u2net']},
                              {"wrapperClass": U2NetWrapper, "parameters": ['u2netp']}]
        
        selectedBgRemover = self.all_bgRemover[0]
        self.bgRemover = selectedBgRemover['wrapperClass'](*selectedBgRemover["parameters"])
        self.bgRemover.loadModel()


        title_label = QLabel("Offline processing")
        font = QFont()
        font.setPointSize(16)   # make it bigger
        font.setBold(True)      # make it bold
        title_label.setFont(font)
        layout.addWidget(title_label, alignment=Qt.AlignHCenter)

        self.mainContainer = QStackedWidget()
        layout.addWidget(self.mainContainer)

        self.c_dropZone = DropZoneWrapper(self.fileUploadCallback)
        self.c_processImage = ProcessImage(self.bgRemover)

        self.mainContainer.addWidget(self.c_dropZone)

        
        self.mainContainer.addWidget(self.c_processImage)
        self.mainContainer.setCurrentWidget(self.c_dropZone)
        self.setLayout(layout)
    
    def fileUploadCallback(self, image):
        print("Called callback")
        self.c_processImage.setImage(image)
        self.mainContainer.setCurrentWidget(self.c_processImage) 

        self.bgRemover.runModel(image)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual green screen")
        self.resize(1100, 768)
        
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#040406"))
        self.setPalette(palette)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)  # left, top, right, bottom


        self.mainContainer = QStackedWidget()

       
        self.offlineProcessing = OfflineProcessing()
        self.realTimeProcessing = RealTimeProcessing()
        self.mainContainer.addWidget(self.offlineProcessing)
        self.mainContainer.addWidget(self.realTimeProcessing)
        self.mainContainer.setCurrentWidget(self.offlineProcessing)        
        

        sidebarParams = [{"file": "galerie_color.png", "onClick": self.switchToOffline, "tooltip": "Offline processing"},
                    {"file": "camera.png", "onClick": self.switchToRealTime, "tooltip": "Real time (webcam)"}]
        sidebar = Sidebar(sidebarParams)


        self.layout.addWidget(sidebar, 7.5) # 5 %
        self.layout.addWidget(self.mainContainer, 92.5) # 95%
        self.setLayout(self.layout)
    
    def switchToRealTime(self):
        print("Switch to real time processing")
        self.mainContainer.setCurrentWidget(self.realTimeProcessing)
        self.realTimeProcessing.startWebcam()
    def switchToOffline(self):
        self.mainContainer.setCurrentWidget(self.offlineProcessing)
        self.realTimeProcessing.stopWebcam()

    def closeEvent(self, event):
        self.realTimeProcessing.closeEvent(event)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
