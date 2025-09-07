from PySide6.QtWidgets import QApplication, QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,QPushButton, QFrame# type: ignore

from PySide6.QtCore import Qt, QTimer # type: ignore
from PySide6.QtGui import QPixmap # type: ignore
from app.offline.image_widget import ImageWidget
from app.background_editor import BackgroundTab
from app.foreground_editor import ForegroundTab
from app import helpers
import numpy as np

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
        self.copy_button.setCursor(Qt.PointingHandCursor)
        self.copy_button.setStyleSheet("""
        QPushButton {
            padding: 0px;
            margin: 0px;
            border: 1px solid #424242;
            border-radius: 6px;
            }
        """)
        self.copy_button.clicked.connect(self.copyImage)

        self.download_button = QPushButton()
        self.download_button.setText("💾")
        self.download_button.setToolTip("Download image")
        self.download_button.setFixedSize(40, 40)
        self.download_button.setCursor(Qt.PointingHandCursor)

        self.download_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.download_button.setStyleSheet("""
        QPushButton {
            padding: 0px;
            margin: 0px;
            border: 1px solid #424242;
            border-radius: 6px;
            }
        """)
        self.download_button.clicked.connect(self.downloadImage)


        button_layout.addStretch()
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.copy_button)
        layout.addLayout(button_layout)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(BackgroundTab(self.changeBackground), "1️⃣ Background")
        self.tab_widget.addTab(ForegroundTab(self.changeForeground), "2️⃣ Foreground")
        layout.addWidget(self.tab_widget)
   
        self.setLayout(layout)
        self.currentBackground = {"type": "color", "value": "original"}
        self.currentForeground = {"type": "color", "value": "original"}
    
    def updateBgRemover(self, newBgRemover):
        # save original image from previous bgRemover object
        original_image = self.bgRemover.original
        # update bgRemover
        self.bgRemover = newBgRemover
        # recompute image
        if isinstance(original_image, np.ndarray): # (if original_image != None)
            self.bgRemover.runModel(original_image)
            self.updateImage()

    def changeBackground(self, color: dict):
        self.currentBackground = color
        self.updateImage()
    def changeForeground(self, color: dict):
        self.currentForeground = color
        self.updateImage()
    
    def updateImage(self):
        newImage = self.bgRemover.getImage(background=self.currentBackground, foreground=self.currentForeground)
        qImage = helpers.numpy_to_qimage(newImage)
        self.image_widget.setImage(qImage)

    def setImage(self, image):
        self.image_widget.setImage(image)

    def copyImage(self):
        prevText = self.copy_button.text()
        self.copy_button.setText('✅')
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(QPixmap.fromImage(self.image_widget.getImage()))
        QTimer.singleShot(500, lambda: self.copy_button.setText(prevText))

    def downloadImage(self):
        pixmap = QPixmap.fromImage(self.image_widget.getImage())
        file_name, _ = QFileDialog.getSaveFileName(
            None,
            "Save Image",
            "",
            "PNG Image (*.png);;JPEG Image (*.jpg);;Bitmap Image (*.bmp)"
        )
        prevText = self.download_button.text()

        if file_name:
            if not file_name.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
                file_name += ".png"
            
            if file_name.lower().endswith(".png"):
                format = "PNG"
            elif file_name.lower().endswith((".jpg", ".jpeg")):
                format = "JPG"
            elif file_name.lower().endswith(".bmp"):
                format = "BMP"
            else:
                format = "PNG"

            if pixmap.save(file_name, format):
                print("Image saved successfully!")
                self.download_button.setText("✅")
                QTimer.singleShot(500, lambda: self.download_button.setText(prevText))
                return
            else:
                print("Failed to save image!")
        self.download_button.setText("❌")
        QTimer.singleShot(1000, lambda: self.download_button.setText(prevText))