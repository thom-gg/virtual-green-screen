from PySide6.QtWidgets import QLabel, QWidget, QVBoxLayout,  QStackedWidget # type: ignore
from PySide6.QtCore import Qt # type: ignore
from PySide6.QtGui import  QFont # type: ignore
from app.offline.dropzone import  DropZoneWrapper
from app.offline.process_image import ProcessImage
from app.wrappers.u2net_wrapper import U2NetWrapper

class OfflineProcessing(QWidget):
    def __init__(self):
        super().__init__()

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
        self.c_processImage.setImage(image)
        self.mainContainer.setCurrentWidget(self.c_processImage) 

        self.bgRemover.runModel(image)