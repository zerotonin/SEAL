import turbidity, seal_agent,copy
import numpy as np

class SEAL_SIM:
    def __init__(self):
        self.sps = 100 # samples per second
        self.waterCurrent = np.array([0.0,2.0,0.0]) # velocity in meter per second will be transformed into an evironment object
        self.seal = seal_agent.Seal(self)
        self.pCloud = turbidity.Cloud(self)
        

    def cloudInit(self,modus):
        if modus == 'random':
            seal.pCloud.add_particles()
        else:
            print('Unknown mode ' + modus + '. Cloud was not initialised ')
    
    def meterPerSecond2meterPerSample(self,velocity):
        # THis function should be inherited
        return copy.deepcopy(velocity/self.sps)
    
        
    

    def simulate_sample(self):
        # move da seal
        self.seal.MoveSeal()
        # move da particles
        self.pCloud.moveParticles()


