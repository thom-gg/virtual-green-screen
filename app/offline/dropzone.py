from PySide6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QFileDialog,QSizePolicy # type: ignore
from PySide6.QtCore import Qt # type: ignore
from PySide6.QtGui import QKeySequence, QImage # type: ignore
import os 

class DropZone(QLabel):
    def __init__(self, callback):
        super().__init__("Drag & Drop a file here\nClick to Browse\nOr Paste (Ctrl+V)")
        self.callback = callback
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                font-size: 16px;
                padding: 40px;
            }
            QLabel:hover {
                border: 2px dashed #0078d7;
            }
        """)
        self.setAcceptDrops(True)
        self.setFocusPolicy(Qt.StrongFocus)  # make sure widget can receive key events
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resizeEvent(self, event):
        """Adjust size relative to parent"""
        if self.parent():
            parent_size = self.parent().size()
            new_width = int(parent_size.width() * 0.5)   # 50% of parent width
            new_height = int(parent_size.height() * 0.2) # 20% of parent height
            self.setFixedSize(new_width, new_height)
        super().resizeEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.handle_file(file_path)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Select a file", "", 
                "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
            )
            if file_path:
                self.handle_file(file_path)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):  # check for Ctrl+V / Cmd+V
            clipboard = QApplication.clipboard()
            if clipboard.mimeData().hasImage():  # if clipboard contains an image
                image = clipboard.image() # type QtGui.QImage
                print("Type of pasted image:", type(image))
                self.callback(image)
            

    def handle_file(self, file_path):
        image = QImage(file_path)   # load image from file

        if image.isNull():
            print("Failed to load image")
        else:
            print(f"Loaded image: {image.width()}x{image.height()}")
            self.callback(image)

class DropZoneWrapper(QWidget):
    def __init__(self, callback):
        super().__init__()
        self.layout = QVBoxLayout()

        self.layout.addStretch()
        line1 = QLabel("Remove the background")
        primaryTextColor = os.environ["QTMATERIAL_PRIMARYTEXTCOLOR"]
        line1.setStyleSheet("QLabel {font-size: 40px; color: "+primaryTextColor+"; }")
        line1.setProperty("class", "secondary-text")

        self.layout.addWidget(line1, alignment=Qt.AlignHCenter)

        line2 = QLabel("of an image or a video")
        line2.setStyleSheet("""QLabel {font-size: 20px;}""")
        self.layout.addWidget(line2, alignment=Qt.AlignHCenter)

        self.layout.addSpacing(20)
        self.layout.addWidget(DropZone(callback), alignment=Qt.AlignHCenter)
        self.layout.addSpacing(10)
        self.layout.addWidget(QLabel("automatically using an AI Salient Object Detection model"), alignment=Qt.AlignHCenter)
        self.layout.addStretch()

        self.setLayout(self.layout)