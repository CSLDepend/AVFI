import numpy as np

class OutputFaultModel(object):
    def __init__(self,prob,frame_delay):
        self.inject_prob = prob
        self.frames_to_delay = frame_delay
        self.controls_buffer=[]
        self.delay_counter=0

    def get_name(self):
        pass

    def inject(self,controls):
        pass
    
    def getFramesToDelay(self):
        #changed for workshop paper
        return self.frames_to_delay
        #return int(np.random.normal(5,2))
    
class ControlPassThrough(OutputFaultModel):
    def get_name(self):
        return "CtrlPass"

    def inject(self,controls):
        #Available Controls
        #controls.steer
        #controls.throttle
        #controls.brake
        #Other available controls
        #controls.hand_brake
        #controls.reverse
        return controls

class ControlRandomInjector(OutputFaultModel):
    def get_name(self):
        return "CtrlRnd_"+str(self.inject_prob)+"_"+str(self.frames_to_delay)

    def inject(self,controls):
        r = np.random.rand()
        if(self.inject_prob>r):
            acc= np.random.randint(2)
            if(acc==1):
                controls.throttle = np.random.rand()
            else:
                controls.brake = np.random.rand()        

            controls.steer = np.random.rand()
            direction = np.random.randint(2)
            if(direction==1):
                controls.steer=controls.steer*-1
            print("Injected")
        return controls

class ControlDelayInjector(OutputFaultModel):
    def get_name(self):
        return "CtrlDly_"+str(self.inject_prob)+"_"+str(self.frames_to_delay)
    def inject(self,controls):
        if(self.delay_counter>0):
            self.delay_counter-=1
            self.controls_buffer.append(controls)
            controls = self.controls_buffer[0]
            print("Delaying:",self.delay_counter)
        
        elif(self.delay_counter<=0 and self.controls_buffer):
            old_control = self.controls_buffer.pop(0)
            controls=old_control
            print("Restoring:",len(self.controls_buffer))

        else:
            r = np.random.uniform(0,1)
            if(self.inject_prob>r):
                self.frames_to_delay = self.getFramesToDelay()
                self.delay_counter=self.frames_to_delay

        return controls

    
class ControlDropInjector(OutputFaultModel):
    def get_name(self):
        return "CtrlDrp_"+str(self.inject_prob)+"_"+str(self.frames_to_delay)

    def inject(self,controls):
        if(self.delay_counter>0):
            self.delay_counter-=1
            controls = self.controls_buffer[0]
            print("Delaying:",self.delay_counter)
        
        elif(self.delay_counter<=0 and self.controls_buffer):
            self.controls_buffer.pop(0)

        else:
            r = np.random.uniform(0,1)
            if(self.inject_prob>r):
                self.controls_buffer.append(controls)
                self.frames_to_delay = self.getFramesToDelay()
                self.delay_counter=self.frames_to_delay

        return controls
