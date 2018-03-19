import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import atexit
import copy
#Update this path to point to ffmpeg.exe
plt.rcParams['animation.ffmpeg_path'] = "E:\\ffmpeg\\bin\\ffmpeg.exe"
#Matplotlib animation
ims=[]
fig = plt.figure()

def saveVideo():
    ani = animation.ArtistAnimation(fig,ims, interval = 50)
    mywriter = animation.FFMpegWriter(fps=20)
    ani.save('test.mp4',writer=mywriter)

atexit.register(saveVideo)

class FaultInjector(object):
    def __init__(self,input_fm_in):
        self.input_fm = input_fm_in

    def corruptControls(self,control_data):
        return control_data

    def corruptSensors(self,sensor_data):
        sensor_data['CameraRGB']._converted_data=self.input_fm.inject(sensor_data['CameraRGB'].data)
        ims.append([plt.imshow(sensor_data['CameraRGB'].data,animated=True)])
        return sensor_data