import matplotlib.pyplot as plt

class FaultInjector(object):
    def __init__(self,input_fm_in):
        self.camera_img=None
        self.input_fm = input_fm_in
        plt.ion()

    def corruptControls(self,control_data):
        return control_data

    def corruptSensors(self,sensor_data):
        sensor_data['CameraRGB']._converted_data=self.input_fm.inject(sensor_data['CameraRGB'].data)
        if(self.camera_img == None):
            self.camera_img = plt.imshow(sensor_data['CameraRGB'].data)
        self.camera_img.set_data(sensor_data['CameraRGB'].data)
        plt.draw()
        plt.pause(0.01)
        return sensor_data