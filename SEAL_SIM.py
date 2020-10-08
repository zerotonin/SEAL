import turbidity, seal_agent,copy,environment,utilities
import numpy as np

class SEAL_SIM:
    def __init__(self):
        self.sps         = 1 # samples per second
        self.environment = environment.environment(self) # velocity in meter per second will be transformed into an evironment object
        self.seal        = seal_agent.Seal(self)
        self.pCloud      = turbidity.Cloud(self)
        self.pCloud.add_particles()
        self.plot        = utilities.plotUtils()
        self.math        = utilities.mathUtils()
        
            
    def meterPerSecond2meterPerSample(self,velocity):
        # THis function should be inherited
        return copy.deepcopy(velocity/self.sps)
    
    def simulate_sample(self):
        # create a step
        self.seal.createSealStep('45down')
        print(self.seal.sealStep)
        # move da particles
        self.pCloud.moveParticles()
        for po in self.pCloud.partclObjList:  
            print(po.position)
        # move da seal
        self.seal.MoveSeal()

        # particle.trajectory saves the old and new position of the particles after every sealMovement, how to apply cart2sphere function on this list ?)