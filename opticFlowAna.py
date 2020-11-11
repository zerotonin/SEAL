import numpy as np 
from utilities import mathUtils
from scipy.interpolate import RegularGridInterpolator
#from scipy import interpolate
import copy, matplotlib
import matplotlib.pyplot as plt 
from ai import cs

class opticFlowAnalysis:
    ''' 
    this class takes the created particlesList with its trajectory information from every particle,
    and the seal trajectories in order to analyze the ability of the seal to perceive optic flow 
    at any given timepoint during the dive. Additionally it plots optic flow field during single 
    seal steps.
    '''

    def __init__(self,simObj):
        """
        this class takes the trajectroy data from the particles and seal_agent to analyze the optic flow

        @param simObj                  ? default= none
        @param particleList            ? default= none
            the particleList is a shortcut to the particleObjectList creates in the 
            Cloud class stored in turbidity.py
        @param sealTrajectories        ? default= none
            the sealTrajectories is a shortcut to the sealTrajectories stores in the 
            seal class in SEAL_SIM stored in SEAL_SIM.py
        """
        self.simObj = simObj
        self.particleList = simObj.pCloud.partclObjList
        self.sealTrajectories = simObj.seal.sealTrajectory
        self.r_querrList = []
        self.rMagnitudeList  = []
    
    def createOpticFlow(self):
        """
        this function plotts a 2D optic flow field for a single sealStep, by calculating the 
        magnitute ot the movement vector from the oldPosition of the particle to the newPosition 
        for phi and z (ignoring the radius, since the retina only has 2 dimensions)
        """
        fig = plt.figure() 
        ax = fig.add_subplot(111) 
        for pObject in self.particleList: # po should be (oldPosition, newPosition, status) of particle per movement
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
        The optimising function of the evolution of optic flow analysis is min((r_0+r_1)/2 - R)
        (r0+r1)/2 = r_querr
        So we sort our particle according to r_querr and R (derivedR) 
        than for each particle we determin their difference in distance rank
        if particle x is the 212th furthes away from the seal in the r_querr ranking 
        and the 150th furthest away in the R ranking this makes an error of 62
        for this seal step the median error of all particles will be our quality value
        R = norm(phi1_-phi_0, z_1-z_0)
        """

        for pObject in self.particleList:
            """
            (r0+r1)/2 = r_querr
            """
            oldPosition = pObject.trajectory[0][0] # (radius, phi, z)
            newPosition = pObject.trajectory[0][1] # (radius, phi, z)
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
        r   = axial distance or radial distance
        phi = angle between the reference dircetion on the choosen plane and the line from the origin to the porjection of point P on the plane
        z   = height
        """
        r, phi, z = cs.cart2cyl(x=cartPosition[0], y=cartPosition[1], z=cartPosition[2])
        return np.array([r, phi, z]) 
        
    def rotateParticleStep2SealHeading(self,particleTrajStep,sealPositionStep):
        
        sealPositionOld = sealPositionStep[0]
        sealPositionNew = sealPositionStep[1]
        
        # This rotation matrix rotates the particle from world coordinates
        # into a position relative to the seals orientation
        rotMatOld = mathUtils.getRotMatrix3D(sealPositionOld[4],sealPositionOld[5],0) # because we have no roll
        # This rotation matrix does the same but after performing the seal step
        # Warning maybe use negative angles unsure ...
        rotMatNew = mathUtils.getRotMatrix3D(sealPositionNew[4],sealPositionNew[5],0) # because we have no roll

        # getting correctly position particle pre seal step
        partclPosOld = np.dot(rotMatOld,particleTrajStep[0]))
        # getting correctly position particle pre seal step
        partclPosNew = np.dot(rotMatNew,particleTrajStep[1]))

        return (partclPosOld,partclPosNew)
    
    def absParticlePos2cylsealCoord(self,particleTrajEntry,sealTrajEntry):
        if particleTrajEntry[2] == True:
            # rotate 3D cartesian coordinates to seal orientation
            relPartPosCart = self.rotateParticleStep2SealHeading(particleTrajEntry,sealTrajEntry)
            # transfrom from cartesian into cylindrical
            return (self.cartTra2cylTra(relPartPosCart[0]),self.cartTra2cylTra(relPartPosCart[1]))
        else: 
            return None

    
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

    
    def articlePos2OFvector(self): # rename
        """
        This function rotates/assures particle cloud so that the seal orientation is az = 0 el 0
        """
        #to do :
        #P_t0 = (x,y,z)
        #P_t1 =(x1,y1,z1)
        #P_t1(x,y,z) * RotMat(-yaw,-pitch,-roll)
        for pObject in self.particleList:

            oldPosition = pObject.trajectory[0][0] # (radius, phi, z)
            newPosition = pObject.trajectory[0][1] # (radius, phi, z)

            #rotate newPosition negative to seal rotation
            for i in self.sealTrajectories:
                #sealRotation
                sealYaw = (self.sealTrajectories[i+1][1][0])-(self.sealTrajectories[i][1][0]) # seal trajectory in sample i, SealOrientation, yaw
                sealPitch = (self.sealTrajectories[i+1][1][1])-(self.sealTrajectories[i][1][1])
                sealRoll = 0

                R = self.mathUtils.getRotMatrix3D(sealYaw,sealPitch,sealRoll)
            
            newPosition = newPosition*R


        #-yaw = YAW SEEHUND ZEIT X+1 - YAW SEEHUND ZEIT X
        #-YAW = velStep/sps


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




