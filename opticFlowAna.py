import numpy as np 
from scipy.interpolate import RegularGridInterpolator
#from scipy import interpolate
import copy, matplotlib
import matplotlib.pyplot as plt 
from ai import cs

class opticFlowAnalysis:
    '''
    '''

    def __init__(self,simObj):
        self.simObj = simObj
        self.particleList = simObj.pCloud.partclObjList
    
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
    
    def cart2cylindric(self,cartPosition):
        """
        https://pypi.org/project/ai.cs/
        r = axial distance or radial distance
        phi = angle between the reference dircetion on the choosen plane and the line from the origin to the porjection of point P on the plane
        z = height
        #translate oldPosition from cartasian to cylindircal coordinate system
        oldPosition = self.cart2cylindric(oldPosition)
        #translate newPosition from cartasian to cylindrical coordinate system
        newPosition = self.cart2cylindric(newPosition)
        """
        r, phi, z = cs.cart2cyl(x=cartPosition[0], y=cartPosition[1], z=cartPosition[2])
        return np.array([r, phi, z]) #depth r can be ignore. 

    def particlePos2OFvector(self,particlePosition):
        pass
    
    def cartTra2cylTra(self,cartTra):
        '''
        This function 
        '''
        cylTra = list()
        for frame in cartTra:
            #translate oldPosition from cartasian to cylindircal coordinate system
            oldPosition = self.cart2cylindric(frame[0])
            #translate newPosition from cartasian to cylindrical coordinate system
            newPosition = self.cart2cylindric(frame[1])
            cylTra.append((oldPosition,newPosition,frame[2]))
        return cylTra

    
    def rotateFlowField2SealHeading(self):
        """
        This function rotates/assures particle cloud so that the seal orientation is az = 0 el 0
        """

        pass

    def testVisibility(self):
        """
        This test can be later used to find resolutable particles
        for the optic flow calculation
                a                      / a \
        b = ----------  alpha = arctan|  - |
            tan(alpha)                 \ b/
        """
        for particle in self.particleList:
            print
            vecNorm = np.linalg.norm(particle.position) 
            
            angleSize = np.rad2deg(np.arctan(particle.size/vecNorm)) 
            print(angleSize> 0.86,vecNorm,angleSize)
