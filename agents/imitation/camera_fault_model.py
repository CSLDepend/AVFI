import numpy as np

class CameraFaultModel(object):
    def inject(self,InputImage):
        pass

class PassThrough(CameraFaultModel):
    def inject(self,InputImage):
        return InputImage

class Occlusion(CameraFaultModel):
    def mod_fn(self,value,row,col):
        pass
    def inject(self,InputImage):
        InputImage.flags.writeable = True
        return self.mod_fn(InputImage)

#Occulusion Classes
class SolidOcclusion(Occlusion):
    def __init__(self, x_in, y_in, dx_in, dy_in):
        self.x=x_in
        self.y=y_in
        self.x_max=self.x+dx_in
        self.y_max=self.y+dy_in

    def mod_fn(self,InputImage):
        InputImage[self.x:self.x_max,self.y:self.y_max,:] = 0
        return InputImage

class TransparentOcclusion(Occlusion):
    def __init__(self, x_in, y_in, dx_in, dy_in):
        self.x=x_in
        self.y=y_in
        self.x_max=self.x+dx_in
        self.y_max=self.y+dy_in

    def mod_fn(self,InputImage):
        InputImage[self.x:self.x_max,self.y:self.y_max,:] = InputImage[self.x:self.x_max,self.y:self.y_max,:]*0.5
        return InputImage
