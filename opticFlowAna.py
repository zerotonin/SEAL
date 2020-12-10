import numpy as np 
from utilities import mathUtils
from scipy.interpolate import RegularGridInterpolator
#from scipy import interpolate
import copy, matplotlib
import matplotlib.pyplot as plt 
from ai import cs
from tqdm import tqdm

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

        @param simObj                  str default: none
            the name of the environment simulation.
        @param mathUtils               ? default: 
            creates a shortcut to the mathUtils class stored in utilities.py
        @param particleList            ? default: none
            the particleList is a shortcut to the particleObjectList creates in the 
            Cloud class stored in turbidity.py
        @param sealTrajectories        ? default: none
            the sealTrajectories is a shortcut to the sealTrajectories stores in the 
            seal class in SEAL_SIM stored in SEAL_SIM.py
        @param anaDataList             list default: none
            creates a list holding information about
            distTrueList,distOFestList,partCylList,OFvectorList
        @param distRankDiff            list default: none
            a list of the distance rank differenc between the 
            distance of the particle movement and the percieved shift 
            on the seals retina (OFvector)
        """
        self.simObj         = simObj
        self.mathUtils      = mathUtils()
        self.particleList   = simObj.pCloud.partclObjList #mutable
        self.sealTrajectory = simObj.seal.sealTrajectory #mutable
        self.anaDataList  = list()
        self.distRankDiff = list()
    
    def createOpticFlow(self,frame):
        """
        This function plotts a 2D optic flow field for a single sealStep, by calculating the 
        magnitute ot the movement vector from the oldPosition of the particle to the newPosition 
        for phi and z (ignoring the radius, since the retina only has 2 dimensions)
        """
        fig = plt.figure() 
        ax = fig.add_subplot(111) 
        #for specific frame it calcultates the magnitute between the old and new position of each visibile? particle
        for i in range(len(self.particleList)): # po should be (oldPosition, newPosition, status) of particle per movement
            direct = self.anaDataList[frame][3][i]
            if  self.anaDataList[frame][2][i] != None: # richtungsvector between frames
                X = self.anaDataList[frame][2][i][0][1] # phi
                Y = self.anaDataList[frame][2][i][0][2] # z
                U = direct[0] # phi direction
                V = direct[1] # z direction
                ax.quiver(X,Y,U,V, angles ='xy',scale_units='xy', scale =1)
            else:
                pass
            
        plt.show() 

    def create2DParticleDistributionList(self,prePost, frame):
        """
        This function creats x and y list for the azimuth(x) and z(height) values of the particles from
        the cylindric particle positions at a given frame for either the oldPosition (prePost = 0)
        or the new Position (prePost = 1)

        @return xList and yList holding information about the azimuth and height
        """
        xList = list()
        yList = list()

        for i in range(len(self.particleList)):
            if self.anaDataList[frame][2][i] != None:
                xList.append(self.anaDataList[frame][2][i][prePost][1])
                yList.append(self.anaDataList[frame][2][i][prePost][2])
            else: 
                xList.append(None)
                yList.append(None)
        return xList, yList

    def plot2DparticleDist(self, frame):
        """
        This function plots the old and new positions of particles for a given frame
        it creates x and y list of the cylindric coordinates of the particles 
        with the create2DparticleDistributionList and plots the old positions
        in red and the new positions in green
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        xList, yList = self.create2DParticleDistributionList(0,frame)
        ax.scatter(xList, yList, color = 'red')
        postxList, postyList = self.create2DParticleDistributionList(1,frame)
        ax.scatter(postxList, postyList, color='green')
        ax.set_xlim(min(min(xList),min(postxList)),max(max(xList),max(postxList)))
        ax.set_ylim(min(min(yList),min(postyList)),max(max(yList),max(postyList)))
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
        and the 150th furthest away in the R ranking this makes an error of 62op 
        for this seal step the median error of all particles will be our quality value
        R = norm(phi1_-phi_0, z_1-z_0)
        """
        for frameI in tqdm(range(self.simObj.protoMove.traLen-1),desc='calculating OF'):
            distTrueList  = list()
            distOFestList = list()
            partCylList   = list()
            OFvectorList  = list()
            
            for pObjectI in range(len(self.particleList)):
                # calculate OpticFlow data            
                cylParticle, OFvector, distance, OFdistanceEst = self.analyseSingleParticleOF(frameI,pObjectI)
                distTrueList.append(distance)
                distOFestList.append(OFdistanceEst)
                partCylList.append(cylParticle)
                OFvectorList.append(OFvector)
                
            self.anaDataList.append([distTrueList,distOFestList,partCylList,OFvectorList])                
            self.distRankDiff.append(self.calcDistanceRankDiff(distTrueList,distOFestList))

    def calcDistanceRankDiff(self,distTrue,distEstOF):
        """
        This function calculates the distance rank difference between the 
        trueDistance moved by the particles and the estimates distance moved
        by the 2D shift on the retina

        @return rankDiff between estimated and true distance
        """
        # clear list of None and build np.arry
        distEstOF_clean = np.array([dist for dist in distEstOF if dist])
        distTrue_clean = np.array([dist for dist in distTrue if dist])
        # These functions return the indices of a sorted list Therefore it is the relative distance rank. 
        # Note that the closest particle is ranked on 1st place in the true distance, but it will elicit 
        # the largest optic flow vector, therefore we have to flip the ranks of one list. We decided to do
        # so by inverting the distance estimated by the norm of the OF vector. Thereby the largest OF vector
        # norm (OFN) becomes the smallest value (1/OFN).
        trueIDX = np.argsort(distTrue_clean)
        estIDX = np.argsort(distEstOF_clean**-1) 
        rankDiff = abs(estIDX -trueIDX)

        return rankDiff

    def cart2cylindric(self,cartPosition):
        """
        This function converts cartisian coordinates into cylindical coordinates,
        where the seal center stay position (0,0,0).
        https://pypi.org/project/ai.cs/
        r   = axial distance or radial distance
        phi = angle between the reference dircetion on the choosen plane and
              the line from the origin to the porjection of point P on the plane
        z   = height

        @return array of cartisian coordinates
        """
        r, phi, z = cs.cart2cyl(x=cartPosition[0], y=cartPosition[1], z=cartPosition[2])

        return np.array([r, phi, z]) 

    def analyseSingleParticleOF(self,frameNo,partclNo):
        """
        This function creates the OF vector for each particle
        at a given frame(sample). 

        @returns cylindric coordinates from particle, 
                 optic flow vector of particle
                 distance particle moved
                 and opticFlow estimates distance particle moved
        """
        #get particle step position
        particleTrajEntry = self.particleList[partclNo].trajectory[frameNo]

        if particleTrajEntry[2] == True:
            #get seal step orientations
            if frameNo == 0:
                sealOrientationStep=(self.sealTrajectory[frameNo][3:],self.sealTrajectory[frameNo][3:])
            else:
                sealOrientationStep=(self.sealTrajectory[frameNo-1][3:],self.sealTrajectory[frameNo][3:])

            # in this function the particle position are rotated so that they align with the animals 
            # orientation. Furthermore they transfer from a 3-D cartesian coordinate sytem into a 3-D
            # cylindirical coordinate systemeal
            cylParticle = self.absParticlePos2cylsealCoord(particleTrajEntry,sealOrientationStep)

            #now calculate the OF vector and the resulting distance and distance estimate
            OFvector,distance,OFdistanceEst = self.getDistancesFromCylParticles(cylParticle) 

            return cylParticle, OFvector, distance, OFdistanceEst 
        else:
            return None, None, None, None
        
    def rotateParticleStep2SealHeading(self,particleTrajStep,sealOrientationStep):
        """
        This function rotates the paricleStep to the Seals heading so the 
        particles are moving into the opposite direction from the seals heading
        This is done by a 3D rotation matrix around the old orientation of the 
        seal.

        @return old and new particle position from seals point of view in 
                cartisian coordinates
        """
        sealOrientationOld = sealOrientationStep[0]
        sealOrientationNew = sealOrientationStep[1]
        
        # This rotation matrix rotates the particle from world coordinates
        # into a position relative to the seals orientation
        rotMatOld = self.mathUtils.getRotMatrix3D(sealOrientationOld[0],sealOrientationOld[1],0) # because we have no roll
        # This rotation matrix does the same but after performing the seal step
        # Warning maybe use negative angles unsure ...
        rotMatNew = self.mathUtils.getRotMatrix3D(sealOrientationNew[0],sealOrientationNew[1],0) # because we have no roll

        # getting correctly position particle pre seal step
        partclPosOld = np.dot(rotMatOld,particleTrajStep[0])
        # getting correctly position particle pre seal step
        partclPosNew = np.dot(rotMatNew,particleTrajStep[1])

        return (partclPosOld,partclPosNew)
    
    def absParticlePos2cylsealCoord(self,particleTrajEntry,sealTrajEntry):
        """
        This function activates the rotation of particle to the seal heading 
        and afterwards converts the cartisian coordinates to cylindrical 
        coordinates

        @return old and new particle position from seals point of view in 
                cylindrical coordinates
        """
        # rotate 3D cartesian coordinates to seal orientation
        relPartPosCart = self.rotateParticleStep2SealHeading(particleTrajEntry,sealTrajEntry)

        # transfrom from cartesian into cylindrical
        return (self.cart2cylindric(relPartPosCart[0]),self.cart2cylindric(relPartPosCart[1]))

    def getDistancesFromCylParticles(self,cylParticles): 
        """
        This function 
        """
        
        distance_groundTruth = (cylParticles[0][0]+cylParticles[1][0])/2
        
        """
        magnitude between the particle before and after sealMovement,
        describing the shift on the retina for optic flow
        """
        OFvector = np.subtract(cylParticles[1][1:3],cylParticles[0][1:3]) # magnitude of 2D vector p1(phi,z) to p2(phi,z)
        distance_OFestimate = np.linalg.norm(OFvector)
        
        return OFvector,distance_groundTruth,distance_OFestimate
         
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




