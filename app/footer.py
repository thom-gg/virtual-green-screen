from PySide6.QtWidgets import  QWidget, QHBoxLayout, QPushButton, QSizePolicy, QLabel, QComboBox, QListView #type: ignore
from PySide6.QtCore import  QRect # type: ignore
from app.wrappers import all_models

class Footer(QWidget):

    def __init__(self, updateModelCallback):
        super().__init__()
        self.updateModelCallback = updateModelCallback

        wrapper = QHBoxLayout()
        wrapper.setContentsMargins(0, 0, 0, 0)

        container = QWidget()
        container.setObjectName("Container")
        container.setStyleSheet("#Container {border-top: 1px solid grey;}")
        
        containerLayout = QHBoxLayout()
        containerLayout.setContentsMargins(10, 10, 10, 10)

        containerLayout.addStretch()
        containerLayout.addWidget(QLabel("Model:"))

        self.selectedModel = 0
        modelList = UpwardComboBox()
        modelList.addItems([m['name'] for m in all_models])
        modelList.setStyleSheet("color: white;")
        modelList.activated.connect(self.updateModel)
        containerLayout.addWidget(modelList)


        container.setLayout(containerLayout)
        # Add the container to main layout
        wrapper.addWidget(container)
        self.setLayout(wrapper)

    def updateModel(self, index: int):
        if index == self.selectedModel:
            return
        self.selectedModel = index
        self.updateModelCallback(all_models[index])

class UpwardComboBox(QComboBox):
    def showPopup(self):
        view = QListView()
        self.setView(view)  # use QListView as the popup
        # Compute popup geometry to appear above the combo
        popup_height = self.view().sizeHintForRow(0) * self.count() + 2 * self.view().frameWidth()
        global_pos = self.mapToGlobal(self.rect().topLeft())
        popup_rect = QRect(global_pos.x(), global_pos.y() - popup_height, self.width(), popup_height)
        self.view().setGeometry(popup_rect)
        super().showPopup()