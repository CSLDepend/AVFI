import numpy as np
import scipy

max_camera_w = 800
max_camera_h = 600
randomize_freq = 10#frames/randomization

class CameraFaultModel(object):
    def __init__(self,prob):
        self.x = 0
        self.y = 0
        self.w = 100
        self.h = 100
        self.inject_prob = prob
        self.inject_counter=0

    def get_name(self):
        pass
    def inject(self,InputImage):
        pass
    def random_bound_box(self):
        self.x = np.random.randint(0,max_camera_h-99)
        self.y = np.random.randint(0,max_camera_w-99)
        self.h = np.random.randint(50,min(max_camera_h-self.x,300))
        self.w = np.random.randint(50,min(max_camera_w-self.y,300))

class PassThrough(CameraFaultModel):
    def get_name(self):
        return 'PassThrough'

    def inject(self,InputImage):
        return InputImage

class Occlusion(CameraFaultModel):
    def mod_fn(self,InputImage):
        pass

    def random_params(self):
        pass

    def inject(self,InputImage):
        r = np.random.rand()
        if(self.inject_prob<r):
            InputImage.flags.writeable = True
            ret_img=self.mod_fn(InputImage)
            self.inject_counter+=1
        else:
            ret_img=InputImage
        return ret_img

#Occulusion Classes
class SolidOcclusion(Occlusion):
    def get_name(self):
        return 'SolidOcclusion'

    def random_params(self):
        self.occ = 0

    def mod_fn(self,InputImage):
        if(self.inject_counter%randomize_freq==0):
            self.random_bound_box()
            self.random_params()
            self.inject_counter=0
        
        InputImage[self.x:self.x+self.w,self.y:self.y+self.h,:] = self.occ
        return InputImage

class TransparentOcclusion(Occlusion):
    def get_name(self):
        return 'TransparentOcclusion'

    def random_params(self):
        self.occ = np.random.uniform()

    def mod_fn(self,InputImage):
        if(self.inject_counter%randomize_freq==0):
            self.random_bound_box()
            self.random_params()
            self.inject_counter=0
        
        InputImage[self.x:self.x+self.w,self.y:self.y+self.h,:] \
            = InputImage[self.x:self.x+self.w,self.y:self.y+self.h,:]*self.occ
        return InputImage

class Noise(CameraFaultModel):
    def mod_fn(self,InputImage):
        pass

    def random_params(self):
        pass

    def inject(self,InputImage):
        r = np.random.rand()
        if(self.inject_prob<r):
            InputImage.flags.writeable = True
            ret_img=self.mod_fn(InputImage)
            self.inject_counter+=1
        else:
            ret_img=InputImage
        return ret_img

class SaltAndPepper(Noise):
    def get_name(self):
        return 'SaltAndPepper'

    def random_params(self):
        self.s_vs_p = np.random.uniform()
        self.amount = np.random.uniform(0,0.004)

    def mod_fn(self,InputImage):
        if(self.inject_counter%randomize_freq==0):
            self.random_params()
            self.inject_counter=0

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
    def get_name(self):
        return 'Gaussian'

    def random_params(self):
        self.mean = 0
        self.var = np.random.uniform()

    def mod_fn(self,InputImage):
        if(self.inject_counter%randomize_freq==0):
            self.random_params()
            self.inject_counter=0
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
    def get_name(self):
        return 'Poisson'

    def mod_fn(self,InputImage):
        vals = len(np.unique(InputImage))
        vals = 2 ** np.ceil(np.log2(vals))
        noisy = np.random.poisson(InputImage * vals) / float(vals)
        return noisy.astype(np.uint8)

class Speckle(Noise):
    def get_name(self):
        return 'Speckle'

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
        self.inject_prob=0
        self.inject_counter=0

    def create_new_droplet(self):
        self.x_c = np.random.randint(102,max_camera_h-52)
        self.y_c = np.random.randint(102,max_camera_w-52)
        self.h = np.random.randint(50,min(max_camera_h-self.x_c,self.x_c/2,300))
        self.w = np.random.randint(50,min(max_camera_w-self.y_c,self.y_c/2,300))

    def move_droplet_down(self):
        self.x_c+=5
        if (self.x_c+self.h/2+1 > max_camera_h):
            self.create_new_droplet()

    def get_name(self):
        return 'WaterDrop'

    def mod_fn(self,InputImage):
        #if(self.inject_counter%randomize_freq==0):
        self.move_droplet_down()
        #self.inject_counter=0

        x_range = range(int(self.x_c - self.h/2),int(np.ceil(self.x_c + self.h/2)+1)) #Rows
        y_range = range(int(self.y_c - self.w/2),int(np.ceil(self.y_c + self.w/2)+1)) #Cols

        out = np.copy(InputImage)

        for i in x_range:
            a_x = (self.x_c-i)**2/(self.h/2)**2
            b_x = 1 - a_x
            f_l_x = b_x*self.xR + a_x
            i_dis = -((i-self.x_c)*f_l_x + self.x_c)
            for j in y_range:
                a_y = (self.y_c-j)**2/(self.w/2)**2
                b_y = 1 - a_y
                f_l_y = b_y*self.yR + a_y
                j_dis = -((j-self.y_c)*f_l_y + self.y_c)
                if((i-self.x_c)**2 + (j-self.y_c)**2 <= (self.h/2)**2):
                    if(abs(j_dis)+2>max_camera_w or abs(i_dis)+2>max_camera_h):
                        out[i][j][:] = 0
                    else:
                        '''
                        y_pixel_weight = j_dis - int(j_dis)
                        x_pixel_weight = i_dis - int(i_dis)

                        h_pixel_val1 = (1-y_pixel_weight)*InputImage[int(i_dis)][int(j_dis)][:] + (y_pixel_weight)*InputImage[int(i_dis)][int(j_dis)+1][:]
                        h_pixel_val2 = (1-y_pixel_weight)*InputImage[int(i_dis)+1][int(j_dis)][:] + (y_pixel_weight)*InputImage[int(i_dis)+1][int(j_dis)+1][:]
                        out[i][j][:]= (1-x_pixel_weight)*h_pixel_val1 + x_pixel_weight*h_pixel_val2
                        '''
                        out[i][j][:] = InputImage[int(i_dis)][int(j_dis)][:]

        nrows,ncols,ch = out.shape
        row,col =  np.ogrid[:nrows,:ncols]
        cnt_row,cnt_col = self.x_c,self.y_c
        droplet_mask = ((row-cnt_row)**2 + (col-cnt_col)**2 < (self.h/2)**2)
        out[droplet_mask] = scipy.ndimage.gaussian_filter(out[droplet_mask],sigma=1)
        return out.astype(np.uint8)