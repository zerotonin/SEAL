import turbidity, seal_agent,copy,environment
import numpy as np

class SEAL_SIM:
    def __init__(self):
        self.sps = 100 # samples per second
        self.envirnoment = environment.environment(self) # velocity in meter per second will be transformed into an evironment object
        self.seal = seal_agent.Seal(self)
        self.pCloud = turbidity.Cloud(self)
        self.pCloud.add_particles()
            
    def meterPerSecond2meterPerSample(self,velocity):
        # THis function should be inherited
        return copy.deepcopy(velocity/self.sps)
    
    def simulate_sample(self):
        # create a step
        self.seal.createSealStep('45down')
        print(self.seal.sealStep)
        # move da particles
        self.pCloud.moveParticles()
        print(self.seal.sealStep)
        # move da seal
        self.seal.MoveSeal()


