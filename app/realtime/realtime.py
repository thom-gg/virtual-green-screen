
from PySide6.QtWidgets import  QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout, QTabWidget, QCheckBox, QComboBox, QSizePolicy # type: ignore
from PySide6.QtCore import Slot, Qt # type: ignore
from PySide6.QtGui import QImage, QPixmap, QCloseEvent # type: ignore
from app.wrappers.u2net_wrapper import U2NetWrapper
from app import helpers
from app.background_editor import BackgroundTab
from app.foreground_editor import ForegroundTab
from app.realtime.video_widget import VideoWidget
from app.realtime.camera_worker import CameraWorker
from PySide6.QtMultimedia import QMediaDevices # type: ignore

import pyvirtualcam # type: ignore
import numpy as np


class RealTimeProcessing(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)

        self.selected_webcam = 0
        self.webcams_id = ["Default"]
        self.webcam_combobox = QComboBox()
        self.webcam_combobox.activated.connect(self.changeWebcam)
        self.webcam_combobox.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.webcam_combobox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(self.webcam_combobox,alignment=Qt.AlignHCenter)
        
        self.target_fps = 15
        
        self.video_widget = VideoWidget(80,50)
        layout.addWidget(self.video_widget, alignment=Qt.AlignHCenter)
        self.hardwareMaxLabel = QLabel("")
        layout.addWidget(self.hardwareMaxLabel)


        sliderWrapper = QHBoxLayout()
        
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1000)
        self.slider.setTickInterval(10)
        self.slider.setValue(self.target_fps)

        self.slider.valueChanged.connect(self.handleSliderEvent)
        
        
        self.fpsLabel = QLabel("")
        self.fpsLabel.setText(str(self.slider.value()) + " fps")

        sliderWrapper.addWidget(self.slider, alignment=Qt.AlignVCenter)
        sliderWrapper.addWidget(self.fpsLabel,alignment=Qt.AlignVCenter)
        
        options = QHBoxLayout()
        options.addLayout(sliderWrapper)
        self.virtualCamCheckbox = QCheckBox("Send to virtual webcam")
        self.virtualCamCheckbox.checkStateChanged.connect(self.toggleVirtualWebcam)
        options.addWidget(self.virtualCamCheckbox)
        layout.addLayout(options)
        self.virtualWebcamEnabled = False

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(BackgroundTab(self.changeBackground), "1️⃣ Background")
        self.tab_widget.addTab(ForegroundTab(self.changeForeground), "2️⃣ Foreground")
        layout.addWidget(self.tab_widget)

        self.setLayout(layout)
        
        self.all_bgRemover = [{"wrapperClass": U2NetWrapper, "parameters": ['u2net', 160]},
                              ]
        
        selectedBgRemover = self.all_bgRemover[0]
        self.bgRemover = selectedBgRemover['wrapperClass'](*selectedBgRemover["parameters"])
        self.bgRemover.loadModel()

        

        # Set window properties
        self.setWindowTitle("Real-time Webcam Display")
        self.resize(800, 600)
    def changeBackground(self, color: dict):
        self.camera_worker.currentBackground = color
    def changeForeground(self, color: dict):
        self.camera_worker.currentForeground = color

    def handleSliderEvent(self, value):
        self.fpsLabel.setText(str(value) + " fps")
        self.camera_worker.setTargetFps(value)
        self.target_fps = value

    def setHardwareMaxFps(self, maxFps):
        self.hardwareMaxFps = maxFps
        self.hardwareMaxLabel.setText("Max hardware fps: "+ str(maxFps))
        self.slider.setMaximum(maxFps)  

    def setWebcamResolution(self, width, height):
        print("Setting resolution to width ", width, " and height " , height)
        self.webcamWidth = int(width)
        self.webcamHeight = int(height)
        

    def startWebcam(self):
        # Create a new worker and start it
        self.fetchWebcams()

        self.camera_worker = CameraWorker(self.selected_webcam, self.bgRemover, self.target_fps, self.setHardwareMaxFps, self.setWebcamResolution)
        self.camera_worker.frame_ready.connect(self.updateFrame)
        self.camera_worker.start()
        
    def fetchWebcams(self):
        devices = QMediaDevices.videoInputs()
        webcams = [d.description() for d in devices]
        
        self.all_webcams = webcams
        self.webcam_combobox.clear()
        for w in webcams:
            self.webcam_combobox.addItem(w)
        self.webcam_combobox.adjustSize()


    def changeWebcam(self, index: int):
        if index == self.selected_webcam:
            return
        self.selected_webcam = index # kinda praying that webcam index corresponds to the order fetched by QMediaDevices
        self.stopWebcam()
        self.startWebcam()
      

    def stopWebcam(self):
        # Tell the worker to stop running, it will reach the end of its running loop and terminate itself
        if hasattr(self,"camera_worker"):
            self.camera_worker.stop()
       
    def closeEvent(self, event: QCloseEvent):
        if hasattr(self,"cam"):
            self.virtualWebcamEnabled = False
            self.cam.close()
        self.stopWebcam()
        event.accept()

    
    @Slot(QImage)
    def updateFrame(self, img: np.ndarray):
        print("Update frame shape", img.shape)
        # Receiving a processed frame, updating it in the UI
        self.video_widget.updateFrame(QPixmap.fromImage(helpers.numpy_to_qimage(img)))
        if self.virtualWebcamEnabled:
            print("sending to virtual webcam")
            self.cam.send(img)
            self.cam.sleep_until_next_frame()

    def toggleVirtualWebcam(self, state):
        if state == Qt.CheckState.Checked:
            self.virtualWebcamEnabled = True
            try:
                self.cam = pyvirtualcam.Camera(width=self.webcamWidth, height=self.webcamHeight, fps=self.hardwareMaxFps)
            except Exception as e:
                print(e)
                self.virtualWebcamEnabled = False
                self.virtualCamCheckbox.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.virtualWebcamEnabled = False
            if hasattr(self, "cam"):
                del self.cam