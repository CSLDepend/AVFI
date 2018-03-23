import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import copy
import os
import sys
#Update this path to point to ffmpeg.exe
if sys.platform.startswith('win'):
    plt.rcParams['animation.ffmpeg_path'] = "E:\\ffmpeg\\bin\\ffmpeg.exe"
#Matplotlib animation

class FaultInjector(object):
    def __init__(self,input_fm_in,city):
        self.input_fm = input_fm_in
        self.city=city
        #Animation
        self.ims=[]
        self.fig = plt.figure()

    def get_injector_name(self):
        return self.input_fm.get_name()

    def corruptControls(self,control_data):
        return control_data

    def corruptSensors(self,sensor_data):
        sensor_data['CameraRGB']._converted_data=self.input_fm.inject(sensor_data['CameraRGB'].data)
        self.ims.append([plt.imshow(sensor_data['CameraRGB'].data,animated=True)])
        return sensor_data

    def saveVideo(self):
        dirname='videos'
        os.makedirs(dirname, exist_ok=True)
        ani = animation.ArtistAnimation(self.fig,self.ims, interval = 50)
        mywriter = animation.FFMpegWriter(fps=20)
        ani.save(os.path.join(dirname,self.city+self.get_injector_name()+'.mp4'),writer=mywriter)
