import turbidity, seal_agent,copy,environment,utilities
import numpy as np
import matplotlib
import matplotlib.pyplot as plt 

class SEAL_SIM:
    def __init__(self):
        self.sps         = 1 # samples per second
        self.environment = environment.environment(self) # velocity in meter per second will be transformed into an evironment object
        self.seal        = seal_agent.Seal(self)
        self.pCloud      = turbidity.Cloud(self)
        self.pCloud.add_particles()
        self.plot        = utilities.plotUtils()
        self.math        = utilities.mathUtils()
        self.turbidity   = turbidity
        
            
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

    def createOpticFlow(self):
        fig = plt.figure() 
        ax = fig.add_subplot(111) 
        for pObject in self.pCloud.partclObjList: # po should be (oldPosition, newPosition, status) of particle per movement
            oldPosition = pObject.trajectory[0][0]
            print('oldPosition is ', oldPosition)
            newPosition = pObject.trajectory[0][1]
            print('new position is ', newPosition)
            direct = np.subtract(newPosition,oldPosition) # richtungsvector between frames
            X = oldPosition[1] # phi
            Y = oldPosition[2] # z
            U = direct[1] # phi direction
            V = direct[2] # z direction
            ax.quiver(X,Y,U,V)
        plt.show()     
        
        # particle.trajectory saves the old and new position of the particles after every sealMovement, how to apply cart2sphere function on this list ?)s

    def opticFlowAbility(self):
        """
        The particle position is denoted in a cylindrical coordinate system.
        The cylindrical coordinate system is defiend as:
            r   = the distance to the coordinate origin (aka seal) [m]
            phi = the azimuth [degress]
            z   = elevation [m] ?
        For each "step" of the seal we have two particle positions, one before (t0) and one after the step (t1).
        Hence there is a r_0, phi_0, and z_0, as well as a r_1, phi_1, and z_1.
        In Optic flow analysis the animal uses the difference between (phi_0,z_0) and (phi_1,z_1) to derive R.
        Thus, (r_0+r_1)/2 - R should be minimal for situations in which the animal can detect depth through optic flow
        p0 = (r_0,phi_0,z_0)
        p1 = (r_1,phi_1,z_1)
        The optimising functio of the evolution of optic flow analysis is min((r_0+r_1)/2 - R)
        The optimising functio of the evolution of optic flow analysis is min(|(r_0+r_1)/2 - R|)
        (r0+r1)/2 = r_querr
        So we sort our particle according to r_querr and R (derivedR) than for each particle we determin their difference in distance rank
        if particle x is zthe 212th furthes away from the seal in the r_querr ranking and the 150th furthest away in the R ranking this makes an error of 62
        for this seal step the median error of all particles will be our quality value
        R = norm(pih1_-phi_0, z_1-z_0)
        """
        self.r_querrList = []
        self.rMagnitudeList  = []
        print(len(self.pCloud.partclObjList))
        for pObject in self.pCloud.partclObjList:
            """
            (r0+r1)/2 = r_querr
            """
            oldPosition = pObject.trajectory[0][0]
            newPosition = pObject.trajectory[0][1]
            r_querr = (oldPosition[0]-newPosition[0])/2
            self.r_querrList.append(r_querr)
            self.r_querrList.sort()
            
            """
            magnitude between the particle before and after sealMovement,
            describing the shift on the retina for optic flow
            """

            direct = np.subtract(newPosition[1:3],oldPosition[1:3]) # magnitude of 2D vector p1(phi,z) to p2(phi,z)
            rMagnitude = np.linalg.norm(direct)
            self.rMagnitudeList.append(rMagnitude)
            self.rMagnitudeList.sort()

        print(self.r_querrList)
        print(len(self.r_querrList))
        print('##############################################')
        print(self.rMagnitudeList) 