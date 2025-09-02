from app.wrappers.base import BackgroundRemover
import os
from app.models import U2NET, U2NETP
import torch # type: ignore
from PySide6.QtGui import  QImage # type: ignore
import app.helpers as helpers
from torch.autograd import Variable # type: ignore
import cv2 as cv
import numpy as np

class U2NetWrapper(BackgroundRemover):
    """This class works for both the U2NET model and its ligther version U2NETP"""
    def __init__(self, model_name: str = "u2net", rescale_size: int = 320):
        super().__init__()
        self.model_name = model_name
        self.rescale_size = rescale_size

    def loadModel(self):
        print("In load model")
        model_path = os.path.join(os.path.dirname(__file__), "../models/" + self.model_name + ".pth")
        if self.model_name == "u2net":
            net = U2NET(3,1)
        else:
            net = U2NETP(3,1)

        if torch.cuda.is_available():
            net.load_state_dict(torch.load(model_path))
            net.cuda()
        else:
            net.load_state_dict(torch.load(model_path, map_location='cpu'))

        self.net = net

    def runModel(self, image: QImage | np.ndarray):
        self.net.eval()
        if isinstance(image, QImage):
            np_image = helpers.qimage_to_numpy(image)
        if isinstance(image, np.ndarray):
            np_image = image
        # Preprocess
        tensor = self.to_tensor_lab(self.cv2_rescale(np_image, self.rescale_size))
        # Run model
        input = tensor.unsqueeze(0)
        input = input.type(torch.FloatTensor)

        if torch.cuda.is_available():
            input = Variable(input.cuda())
        else:
            input = Variable(input)
        with torch.no_grad():
            d1,d2,d3,d4,d5,d6,d7= self.net(input)

        pred = d1[:,0,:,:]
        pred = self.normPRED(pred)

        # Store original, and prediction mask scaled up (so we can quickly change background and foreground)
        self.original = np_image
        predict = pred

        predict = predict.squeeze()
        predict_np = predict.cpu().data.numpy()
    
        mask_np = cv.resize(predict_np, (self.original.shape[1], self.original.shape[0]), interpolation=cv.INTER_LINEAR)
        self.mask = mask_np

    def cv2_rescale(self, image: np.ndarray, output_size: int):
        img = cv.resize(image,(output_size,output_size),interpolation=cv.INTER_LINEAR)
        return img

    def to_tensor_lab(self, image: np.ndarray):
        tmpImg = np.zeros((image.shape[0],image.shape[1],3))
        image = image/np.max(image) # normalize [0,255] into [0,1]
        # Channel-wise normalisation
        if image.shape[2]==1: #grayscale
            tmpImg[:,:,0] = (image[:,:,0]-0.485)/0.229
            tmpImg[:,:,1] = (image[:,:,0]-0.485)/0.229
            tmpImg[:,:,2] = (image[:,:,0]-0.485)/0.229
        else: #rgb
            tmpImg[:,:,0] = (image[:,:,0]-0.485)/0.229
            tmpImg[:,:,1] = (image[:,:,1]-0.456)/0.224
            tmpImg[:,:,2] = (image[:,:,2]-0.406)/0.225
        tmpImg = tmpImg.transpose((2, 0, 1)) #comply with the format expected by pytorch

        return torch.from_numpy(tmpImg)
    
    def normPRED(self, d):
        ma = torch.max(d)
        mi = torch.min(d)

        dn = (d-mi)/(ma-mi)

        return dn