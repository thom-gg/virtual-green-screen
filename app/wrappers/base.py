from abc import ABC, abstractmethod
from PySide6.QtGui import  QImage, QColor # type: ignore
import numpy as np
from .. import helpers

class BackgroundRemover(ABC):
    """Wrapper around a model that defines methods to compute mask as a np array from an original np array representing the image"""

    def __init__(self):
        self.original = None
        self.mask = None

    @abstractmethod
    def loadModel(self):
        pass

    @abstractmethod
    def runModel(self, image: QImage):
        pass

    def getImage(self, background: dict = {"type": "color", "value": "original"}, foreground: dict = {"type": "color", "value": "original"}):
        # Do operations on numpy array
        if background["type"] == "image":
            # bg == rgba
            bg = helpers.load_image_as_array(background["value"], self.original.shape[1], self.original.shape[0])
            if self.original.shape[-1] == 3:
                bg = bg[:,:,:3]
        elif background["type"] == "color":
            if background["value"] == 'original':
                bg = self.original
            else:
                bgColor = QColor(background["value"])
                if self.original.shape[-1] == 4:
                    bg = np.full_like(self.original, (bgColor.red(),bgColor.green(),bgColor.blue(), bgColor.alpha()), dtype=np.float32)
                else:
                    bg = np.full_like(self.original, (bgColor.red(),bgColor.green(),bgColor.blue()), dtype=np.float32)

        if foreground["type"] == "image":
            fg = helpers.load_image_as_array(foreground["value"], self.original.shape[1], self.original.shape[0])
            if self.original.shape[-1] == 3:
                fg = fg[:,:,:3]
        elif foreground["type"] == "color":
            if foreground["value"] == 'original':
                fg = self.original
            else:
                fgColor = QColor(foreground["value"])
                if self.original.shape[-1] == 4:
                    fg = np.full_like(self.original, (fgColor.red(),fgColor.green(),fgColor.blue(), fgColor.alpha()), dtype=np.float32)
                else:
                    fg = np.full_like(self.original, (fgColor.red(),fgColor.green(),fgColor.blue()), dtype=np.float32)

        # broadcast mask. for each value in the mask, it goes from x to [x] 
        # and numpy will automatically broadcast it to [x,x,x,x] to multiply with [r,g,b,a] element-wise
        mask = self.mask[:,:,np.newaxis]
        # res = fg * mask + bg * (1-mask)
        res = fg.astype(np.float32) * mask + bg * (1 - mask)

        # Convert to uint8 for OpenCV
        res = res.astype(np.uint8)

        return res
        