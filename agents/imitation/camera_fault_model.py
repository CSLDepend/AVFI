import numpy as np

class CameraFaultModel(object):
    def inject(self,InputImage):
        pass

class PassThrough(CameraFaultModel):
    def inject(self,InputImage):
        return InputImage

class Occlusion(CameraFaultModel):
    def mod_fn(self,InputImage):
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

class Noise(CameraFaultModel):
    def mod_fn(self,InputImage):
        pass

    def inject(self,InputImage):
        return self.mod_fn(InputImage)

class SaltAndPepper(Noise):
    def __init__(self,s_vs_pIn=0.5,amountIn=0.004):
        self.s_vs_p = s_vs_pIn
        self.amount = amountIn

    def mod_fn(self,InputImage):
        row,col,ch = InputImage.shape
        s_vs_p = self.s_vs_p
        amount = self.amount
        out = np.copy(InputImage)
        # Salt mode
        num_salt = np.ceil(amount * InputImage.size * s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt))
                for i in InputImage.shape]
        out[coords] = 255
        # Pepper mode
        num_pepper = np.ceil(amount* InputImage.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper))
                for i in InputImage.shape]
        out[coords] = 0
        return out.astype(np.uint8)

class Gaussian(Noise):
    def __init__(self,meanIn=0,varIn=0.1):
        self.mean = meanIn
        self.var = varIn

    def mod_fn(self,InputImage):
        row,col,ch= InputImage.shape
        mean = self.mean
        var = self.var
        sigma = var**0.5
        gauss = np.random.normal(mean,sigma,(row,col,ch))*255
        gauss = gauss.reshape(row,col,ch)
        noisy = InputImage + gauss
        noisy = noisy.clip(0,255)
        return noisy.astype(np.uint8)

class Poisson(Noise):
    def mod_fn(self,InputImage):
        vals = len(np.unique(InputImage))
        vals = 2 ** np.ceil(np.log2(vals))
        noisy = np.random.poisson(InputImage * vals) / float(vals)
        return noisy.astype(np.uint8)

class Speckle(Noise):
    def mod_fn(self,InputImage):
        row,col,ch = InputImage.shape
        gauss = np.random.randn(row,col,ch)
        gauss = gauss.reshape(row,col,ch)        
        noisy = InputImage + InputImage * gauss
        noisy.clip(0,255)
        return noisy.astype(np.uint8)

class WaterDrop(Occlusion):
    #xR/yR = f_c/f_d 
    def __init__(self, x_c_in, y_c_in, h_in, w_in,xR_in,yR_in):
        self.x_c=x_c_in
        self.y_c=y_c_in
        self.h=h_in
        self.w=w_in
        self.xR=xR_in
        self.yR=yR_in

    def mod_fn(self,InputImage):
        x_range = range(int(self.x_c - self.h/2),int(np.ceil(self.x_c + self.h/2)+1)) #Rows
        y_range = range(int(self.y_c - self.w/2),int(np.ceil(self.y_c + self.w/2)+1)) #Cols

        out = np.copy(InputImage)

        for i in x_range:
            i_dis = -((i-self.x_c)*self.xR + self.x_c)
            for j in y_range:
                j_dis = -((j-self.y_c)*self.yR + self.y_c)
                if((i-self.x_c)**2 + (j-self.y_c)**2 <= (self.h/2)**2):

                    y_pixel_weight = j_dis - int(j_dis)
                    x_pixel_weight = i_dis - int(i_dis)

                    h_pixel_val1 = (1-y_pixel_weight)*InputImage[int(i_dis)][int(j_dis)][:] + (y_pixel_weight)*InputImage[int(i_dis)][int(j_dis)+1][:]
                    h_pixel_val2 = (1-y_pixel_weight)*InputImage[int(i_dis)+1][int(j_dis)][:] + (y_pixel_weight)*InputImage[int(i_dis)+1][int(j_dis)+1][:]

                    out[i][j][:]= (1-x_pixel_weight)*h_pixel_val1 + x_pixel_weight*h_pixel_val2

        return out.astype(np.uint8)