# Virtual Green Screen app

This is a desktop application to remove / modify the background on images or in realtime on the webcam.

![](./figures/app_example.png)

### Usage
Start the application by running

```python3 -m app.application```

### Image Segmentation
The image segmentation is done using the U^2-Net model from Xuebin Qin et al.   

Official repository: [https://github.com/letmaik/pyvirtualcam](https://github.com/xuebinqin/U-2-Net)

#### Showcase:
![](./figures/showcase.png)

### Virtual webcam
Processed realtime webcam stream can be used in other applications (Discord, Zoom, ...), using the `pyvirtualcam` package that'll use the OBS Virtual Webcam stream. 

This package doesn't work on latest MacOS releases, because OBS Virtual Webcam changed behavior.

Repository: [https://github.com/letmaik/pyvirtualcam](https://github.com/letmaik/pyvirtualcam)

