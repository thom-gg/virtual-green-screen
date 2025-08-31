import sys
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import Qt



class VideoWidget(QLabel):
    def __init__(self, width_pct: float, height_pct: float):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("border: 1px solid red;")
        self.setText("No video feed")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # avoid that it expands

        self.width_pct = width_pct
        self.height_pct = height_pct
        
        self.setMinimumSize(320, 240)
    
    def updateFrame(self, pixmap: QPixmap):
        if pixmap and not pixmap.isNull():
            # Scale the pixmap to fit the widget while maintaining aspect ratio
            scaled_pixmap = pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.setPixmap(scaled_pixmap)
    
    def sizeHint(self):
        """Provide size hint based on parent and percentage values"""
        if self.parent():
            parent_size = self.parent().size()
            width = int(parent_size.width() * self.width_pct / 100)
            height = int(parent_size.height() * self.height_pct / 100)
            return QSize(width, height)
        return QSize(320, 240)  # Default size
    
    def minimumSizeHint(self):
        """Provide minimum size hint"""
        return QSize(160, 120)
    
   

    

class RealTimeProcessing(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        
        self.video_widget = VideoWidget(80,50)
        layout.addWidget(self.video_widget, alignment=Qt.AlignHCenter)
        
        self.setLayout(layout)
        
        # Set up a timer to update frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        
        # Set window properties
        self.setWindowTitle("Real-time Webcam Display")
        self.resize(800, 600)

    def startWebcam(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            self.video_label.setText("Error: Could not open webcam")
            return  
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # reduce buffer size to 1
        # start timer
        self.timer.start(100)

    def stopWebcam(self):
        self.timer.stop()
        self.cap.release()
        self.cap = None
    
    def update_frame(self):
        print("updating frame")
        """Capture and display a new frame from the webcam"""
        ret, frame = self.cap.read()
        
        if ret:
            # Convert the frame from BGR to RGB (OpenCV uses BGR by default)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get frame dimensions
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            
            # Create QImage from the frame
            qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            # Convert QImage to QPixmap and display it
            pixmap = QPixmap.fromImage(qt_image)
            self.video_widget.updateFrame(pixmap)
            
    
    def closeEvent(self, event):
        """Clean up resources when the widget is closed"""
        if hasattr(self, 'timer'):
            self.timer.stop()
        
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        
        event.accept()

