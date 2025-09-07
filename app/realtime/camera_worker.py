import cv2
from PySide6.QtCore import QThread, Signal #type: ignore

import time

import numpy as np

class CameraWorker(QThread):
    frame_ready = Signal(np.ndarray)

    def __init__(self, webcamId, bgRemover, target_fps, setHardwareMaxCallback, setWebcamResolution):
        super().__init__()
        self.webcamId = webcamId
        self.bgRemover = bgRemover
        self.nextBgRemover = None
        self.running = True
        print("In worker init")
        self.target_fps = target_fps
        self.setHardwareMaxCallback = setHardwareMaxCallback
        self.setWebcamResolution = setWebcamResolution

        self.currentBackground = {"type": "color", "value": "original"}
        self.currentForeground = {"type": "color", "value": "original"}
        
    def setBgRemover(self, newBgRemover):
        # Put it in a specific variable to be replaced during next iteration of the loop
        self.nextBgRemover = newBgRemover

    def run(self):
        print("Starting to run thread")
        self.cap = cv2.VideoCapture(self.webcamId)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.actualMaxFps = self.cap.get(cv2.CAP_PROP_FPS) # if its smaller than 60 opencv will have clamped it down
        self.setHardwareMaxCallback(self.actualMaxFps)
        self.setWebcamResolution(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.running = True

        while self.running and self.cap.isOpened():
            if self.nextBgRemover != None: # changing model
                self.bgRemover = self.nextBgRemover
                self.nextBgRemover = None

            frame_start = time.time()

            ret, frame = self.cap.read()
            if not ret:
                continue
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.bgRemover.runModel(rgb_frame)
            newImage = self.bgRemover.getImage(background=self.currentBackground, foreground=self.currentForeground)            
            
            self.frame_ready.emit(newImage)

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