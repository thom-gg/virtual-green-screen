import sys
import cv2
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QSizePolicy, QSlider, QHBoxLayout
from PySide6.QtCore import QTimer, QSize, QThread, Signal, Slot
from PySide6.QtGui import QImage, QPixmap, QCloseEvent
from PySide6.QtCore import Qt
from app.wrappers.u2net_wrapper import U2NetWrapper
from app import helpers
import time

class CameraWorker(QThread):
    frame_ready = Signal(QImage)

    def __init__(self, bgRemover, target_fps, setHardwareMaxCallback):
        super().__init__()
        self.bgRemover = bgRemover
        self.running = True
        print("In worker init")
        self.target_fps = target_fps
        self.setHardwareMaxCallback = setHardwareMaxCallback
        

    def run(self):
        print("Starting to run thread")
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.actualMaxFps = self.cap.get(cv2.CAP_PROP_FPS) # if its smaller than 60 opencv will have clamped it down
        self.setHardwareMaxCallback(self.actualMaxFps)

        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.running = True

        while self.running and self.cap.isOpened():
            frame_start = time.time()

            ret, frame = self.cap.read()
            if not ret:
                continue
            

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bgRemover.runModel(rgb_frame)
            newImage = self.bgRemover.getImage(background='original', foreground='transparent')            
            
            qImage = helpers.numpy_to_qimage(newImage)


            self.frame_ready.emit(qImage)

            # if necessary wait before next iteration
            elapsed = time.time() - frame_start
            wait = (1.0 / self.target_fps) - elapsed
            if wait > 0:
                time.sleep(wait)
        if self.cap.isOpened():
            self.cap.release()
        print("Camera worker is done running")

    def setTargetFps(self, target_fps):
        self.target_fps = min(self.actualMaxFps, target_fps)

    def stop(self):
        self.running = False
        self.wait()
        if self.cap.isOpened():
            self.cap.release()

class VideoWidget(QLabel):
    def __init__(self, width_pct: float, height_pct: float):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
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

        self.target_fps = 15
        
        self.video_widget = VideoWidget(80,50)
        layout.addWidget(self.video_widget, alignment=Qt.AlignHCenter)
        self.hardwareMaxLabel = QLabel("")
        layout.addWidget(self.hardwareMaxLabel)


        sliderWrapper = QHBoxLayout()
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(10)
        self.slider.setValue(self.target_fps)

        self.slider.valueChanged.connect(self.handleSliderEvent)
        
        
        self.fpsLabel = QLabel("")
        self.fpsLabel.setText(str(self.slider.value()) + " fps")

        sliderWrapper.addWidget(self.slider)
        sliderWrapper.addWidget(self.fpsLabel)
        layout.addLayout(sliderWrapper)
        self.setLayout(layout)
        
        self.all_bgRemover = [{"wrapperClass": U2NetWrapper, "parameters": ['u2net', 32]},
                              ]
        
        selectedBgRemover = self.all_bgRemover[0]
        self.bgRemover = selectedBgRemover['wrapperClass'](*selectedBgRemover["parameters"])
        self.bgRemover.loadModel()

        

        # Set window properties
        self.setWindowTitle("Real-time Webcam Display")
        self.resize(800, 600)
    
    def handleSliderEvent(self, value):
        self.fpsLabel.setText(str(value) + " fps")
        self.camera_worker.setTargetFps(value)
        self.target_fps = value

    def setHardwareMaxFps(self, maxFps):
        self.hardwareMaxFps = maxFps
        self.hardwareMaxLabel.setText("Max hardware fps: "+ str(maxFps))
        self.slider.setMaximum(maxFps)

    def startWebcam(self):
        # Create a new worker and start it
        self.camera_worker = CameraWorker(self.bgRemover, self.target_fps, self.setHardwareMaxFps)
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
        

    

            

