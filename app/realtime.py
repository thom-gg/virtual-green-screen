import sys
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSizePolicy
from PySide6.QtCore import QTimer, QSize, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QCloseEvent
from PySide6.QtCore import Qt
from app.wrappers.u2net_wrapper import U2NetWrapper
from app import helpers
import time

class CameraWorker(QThread):
    frame_ready = Signal(QImage)

    def __init__(self, bgRemover):
        super().__init__()
        self.bgRemover = bgRemover
        self.running = True
        print("In worker init")
        

    def run(self):
        print("Starting to run thread")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.running = True
        prev_time = time.time()

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue
            # Convert BGR → RGB
            print("Running frame in camera worker")
            

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bgRemover.runModel(rgb_frame)
            newImage = self.bgRemover.getImage(background='original', foreground='transparent')            
            curr_time = time.time()
            fps = 1 / (curr_time - prev_time)
            prev_time = curr_time
            cv2.putText(newImage, f'FPS: {fps:.2f}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                    1, (0, 255, 0), 2, cv2.LINE_AA)
            qImage = helpers.numpy_to_qimage(newImage)


            self.frame_ready.emit(qImage)
        if self.cap.isOpened():
            self.cap.release()
        print("Camera worker is done running")

    def stop(self):
        self.running = False
        self.wait()
        if self.cap.isOpened():
            self.cap.release()

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
        
        self.all_bgRemover = [{"wrapperClass": U2NetWrapper, "parameters": ['u2net', 160]},
                              ]
        
        selectedBgRemover = self.all_bgRemover[0]
        self.bgRemover = selectedBgRemover['wrapperClass'](*selectedBgRemover["parameters"])
        self.bgRemover.loadModel()

        # Set window properties
        self.setWindowTitle("Real-time Webcam Display")
        self.resize(800, 600)

    def startWebcam(self):
        # Create a new worker and start it
        self.camera_worker = CameraWorker(self.bgRemover)
        self.camera_worker.frame_ready.connect(self.updateFrame)
        self.camera_worker.start()

      

    def stopWebcam(self):
        # Tell the worker to stop running, it will reach the end of its running loop and terminate itself
        if hasattr(self,"camera_worker"):
            self.camera_worker.stop()
       
    def closeEvent(self, event: QCloseEvent):
        self.stopWebcam()
        event.accept()

    
    @Slot(QImage)
    def updateFrame(self, qimg):
        # Receiving a processed frame, updating it in the UI
        self.video_widget.updateFrame(QPixmap.fromImage(qimg))

    

            

