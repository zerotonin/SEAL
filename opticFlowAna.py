import numpy as np 
from utilities import mathUtils
from scipy.interpolate import RegularGridInterpolator
#from scipy import interpolate
import copy, matplotlib
import matplotlib.pyplot as plt 
from ai import cs
from tqdm import tqdm
import math as m

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

        @param simObj                   
            shortCut to the simulated Object 
        @param mathUtils               utilities.mathUtils
            creates a shortcut to the mathUtils class stored in utilities.py

        @param particleList            list default: none
            the particleList is a shortcut to the particleObjectList creates in the 
            Cloud class stored in turbidity.py
        @param sealTrajectories        array default: none
            the sealTrajectories is a shortcut to the sealTrajectories stores in the 
            seal class in SEAL_SIM stored in SEAL_SIM.py
        @param traLen                  int default: none
            number of samples per simulation
            
        @param anaDataList             list default: none
            creates a list holding information about
            distTrueList,distOFestList,partSphereList,OFvectorList
        @param distRankDiff            list default: none
            a list of the distance rank difference between the 
            distance of the particle movement and the percieved shift 
            on the seals retina (OFvector)
        """
        # objects from other classes
        self.simObj         = simObj
        self.mathUtils      = mathUtils()
        # public objects
        self.particleList   = simObj.pCloud.partclObjList #mutable
        self.sealTrajectory = simObj.runTimeData.getParameter('sealTrajectory') #mutable
        self.traLen         = simObj.runTimeData.getParameter('traLen') #mutable
        # private objects
        self.anaDataList    = list()
        self.distRankDiff   = list()
        #initialize data
        self.opticFlowAbility()
        
    

    def plotOpticFlow(self,frame, showStartEnd = True, viewField = False, projectionType = 'polar'):
        """
        This function plotts a 2D optic flow field for a single sealStep, by calculating the 
        magnitute ot the movement vector from the oldPosition of the particle to the newPosition 
        for theta and phi (ignoring the radius, since the retina only has 2 dimensions)
        This functions plot old and new position in a geographical projection.
        https://matplotlib.org/3.1.0/gallery/subplots_axes_and_figures/geo_demo.html
        """
        fig = plt.figure() 
        if projectionType == 'polar':
            ax = fig.add_subplot(111, projection = 'hammer')
        else:
            ax = fig.add_subplot(111)
        #ax.axis('equal') 
        #for specific frame it calcultates the magnitute between the old and new position of each visibile? particle
        for i in range(len(self.particleList)): # po should be (oldPosition, newPosition, status) of particle per movement
            direct = self.anaDataList[frame][3][i]
            if  self.anaDataList[frame][2][i] != None: # richtungsvector between frames
                X = self.anaDataList[frame][2][i][0][2] # phi
                Y = self.anaDataList[frame][2][i][0][1] # theta
                U = direct[2] # phi direction
                V = direct[1] # theta direction
                ax.quiver(X,Y,U,V,angles ='xy',scale_units='xy', scale =1,width=0.001, color='gray', alpha=0.5, zorder=2)
            else:
                pass
        if showStartEnd == True:
            thetaList, phiList = self.create2DParticleDistributionList(0,frame)
            ax.scatter(phiList, thetaList, color = 'red')
            postThetaList, postPhiList = self.create2DParticleDistributionList(1,frame)
            ax.scatter(postPhiList,postThetaList, color='green')

        if viewField == True:
            ax.set_xlim(-1.815,1.815) # visual field from -104 to 104° horizontally
            ax.set_ylim(-0.209,1.204) # vidual field from−12°to+69°vertically
        
        if viewField == False:
            x = ([-1.815,-1.815,1.815,1.815,-1.815])
            y = ([-0.209,1.204,1.204,-0.209,-0.209])
            ax.plot(x,y, zorder=1, color= 'forestgreen')    

        ax.set_xlabel('azimuth [deg]')
        ax.set_ylabel('elevation [deg]')
        plt.grid(True)
        plt.show() 

    def create2DParticleDistributionList(self,prePost, frame):
        """
        This function creats theta and phi list for the theta(x) and phi(height) values of the particles from
        the sphereindric particle positions at a given frame for either the oldPosition (prePost = 0)
        or the new Position (prePost = 1)

        @return thetaList and phiList holding information about the azimuth and height
        """
        thetaList = list()
        phiList = list()

        for i in range(len(self.particleList)):
            if self.anaDataList[frame][2][i] != None:
                thetaList.append(self.anaDataList[frame][2][i][prePost][1])
                phiList.append(self.anaDataList[frame][2][i][prePost][2])
            else: 
                thetaList.append(None)
                phiList.append(None)
        return thetaList, phiList





    def opticFlowAbility(self):
        """das
        The particle position is denoted in a spherical coordinate system.
        The spherical coordinate system is defiend as:
            r     = the distance to the coordinate origin (aka seal) [m]
            theta = the 3D polar angle relative to z-axis
            phi   = the 3D azimuthal angle, relative to the x-axis for the 3D vector projected onto the xy plane
        For each "step" of the seal we have two particle positions, one before (t0) and one after the step (t1).
        Hence there is a r_0, theta_0, and phi_0, as well as a r_1, theta_1, and phi_1.
        In Optic flow analysis the animal uses the difference between (theta_0,phi_0) and (theta_1,phi_1) to derive R.
        Thus, (r_0+r_1)/2 - R should be minimal for situations in which the animal can detect depth through optic flow
        p0 = (r_0,theta_0,phi_0)
        p1 = (r_1,theta_1,phi_1)
        The optimising function of the evolution of optic flow analysis is min((r_0+r_1)/2 - R)
        (r0+r1)/2 = r_querr
        So we sort our particle according to r_querr and R (derivedR) 
        than for each particle we determin their difference in distance rank
        if particle x is the 212th furthes away from the seal in the r_querr ranking 
        and the 150th furthest away in the R ranking this makes an error of 62op 
        for this seal step the median error of all particles will be our quality value
        R = norm(theta1_-theta_0, phi_1-phi_0)
        """
        for frameI in tqdm(range(int(self.traLen-1)),desc='calculating OF'):
            distTrueList  = list()
            distOFestList = list()
            partSphereList   = list()
            OFvectorList  = list()
            
            for pObjectI in range(len(self.particleList)):
                # calculate OpticFlow data            
                sphereParticle, OFvector, distance, OFdistanceEst = self.analyseSingleParticleOF(frameI,pObjectI)
                distTrueList.append(distance)
                distOFestList.append(OFdistanceEst)
                partSphereList.append(sphereParticle)
                OFvectorList.append(OFvector)
                
            self.anaDataList.append([distTrueList,distOFestList,partSphereList,OFvectorList])                
            self.distRankDiff.append(self.calcDistanceRankDiff(distTrueList,distOFestList))

    def calcDistanceRankDiff(self,distTrue,distEstOF):
        """
        This function calculates the distance rank difference between the 
        trueDistance moved by the particles and the estimates distance moved
        by the 2D shift on the retina

        @return rankDiff between estimated and true distance
        """
        # clear list of None and build np.arry
        distEstOF_clean = np.array([dist for dist in distEstOF if dist >= 0.0])
        distTrue_clean = np.array([dist for dist in distTrue if dist >= 0.0])
        # These functions return the indices of a sorted list Therefore it is the relative distance rank. 
        # Note that the closest particle is ranked on 1st place in the true distance, but it will elicit 
        # the largest optic flow vector, therefore we have to flip the ranks of one list. We decided to do
        # so by inverting the distance estimated by the norm of the OF vector. Thereby the largest OF vector
        # norm (OFN) becomes the smallest value (1/OFN).
        trueIDX = np.argsort(distTrue_clean)
        estIDX = np.argsort(distEstOF_clean**-1) 
        rankDiff = abs(estIDX -trueIDX)

        return rankDiff

    def cart2spheric(self,cartPosition):
        """
        This function converts cartisian coordinates into spherical coordinates,
        where the seal center stay position (0,0,0).
        https://pypi.org/project/ai.cs/
        r     = axial distance or radial distance
        theta = polar angle ?
        phi   = angle between the reference dircetion on the choosen plane and
                the line from the origin to the porjection of point P on the plane

        @return array of cartisian coordinates
        """
        r, theta, phi = cs.cart2sp(x=cartPosition[0], y=cartPosition[1], z=cartPosition[2])

        return np.array([r, theta, phi]) 

    def analyseSingleParticleOF(self,frameNo,partclNo):
        """
        This function creates the OF vector for each particle
        at a given frame(sample). 

        @returns spherical coordinates from particle, 
                 optic flow vector of particle
                 distance particle moved
                 and opticFlow estimates distance particle moved
        """
        #get particle step position
        particleTrajEntry = self.particleList[partclNo].trajectory[frameNo]

        if particleTrajEntry[2] == True:
            #get seal step orientations
            if frameNo == 0:
                sealOrientationStep=(self.sealTrajectory[frameNo][3:],self.sealTrajectory[frameNo+1][3:])
            else:
                sealOrientationStep=(self.sealTrajectory[frameNo-1][3:],self.sealTrajectory[frameNo][3:])

            # in this function the particle position are rotated so that they align with the animals 
            # orientation. Furthermore they transfer from a 3-D cartesian coordinate sytem into a 3-D
            # sphereindirical coordinate systemeal
            sphereParticle = self.absParticlePos2spheresealCoord(particleTrajEntry,sealOrientationStep)

            #now calculate the OF vector and the resulting distance and distance estimate
            OFvector,distance,OFdistanceEst = self.getDistancesFromsphereParticles(sphereParticle) 

            return sphereParticle, OFvector, distance, OFdistanceEst 
        else:
            return -1.0, -1.0, -1.0, -1.0
        
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
        print(rotMatOld,rotMatNew)
        # getting correctly position particle pre seal step
        partclPosOld = np.dot(rotMatOld,particleTrajStep[0])
        # getting correctly position particle pre seal step
        partclPosNew = np.dot(rotMatNew,particleTrajStep[1])

        return (partclPosOld,partclPosNew)
    
    def absParticlePos2spheresealCoord(self,particleTrajEntry,sealTrajEntry):
        """
        This function activates the rotation of particle to the seal heading 
        and afterwards converts the cartisian coordinates to spherical 
        coordinates

        @return old and new particle position from seals point of view in 
                spherical coordinates
        """
        # rotate 3D cartesian coordinates to seal orientation
        relPartPosCart = self.rotateParticleStep2SealHeading(particleTrajEntry,sealTrajEntry)

        # transfrom from cartesian into spherical
        return (self.cart2spheric(relPartPosCart[0]),self.cart2spheric(relPartPosCart[1]))

    def getDistancesFromsphereParticles(self,sphereParticles): 
        """
        This function  
        """
        
        distance_groundTruth = (sphereParticles[0][0]+sphereParticles[1][0])/2
        
        """
        magnitude between the particle before and after sealMovement,
        describing the shift on the retina for optic flow

        ofVec = sphP2-sphP1 
        |ofVec(1)| > pi -> mod(ofVec(1),pi)*-1
        |ofVec(2)| > pi/2 -> mod(ofVec(2),pi/2)*-1 
        """
        OFvector = np.subtract(sphereParticles[1],sphereParticles[0]) # magnitude of 2D vector p1(phi,z) to p2(phi,z)
        


        if np.linalg.norm(OFvector[1]) > np.pi/2:
            #OFvector[2]= OFvector[2]*-1
            if OFvector[1] < 0:
                OFvector[1]= -(OFvector[1]%(np.pi/2))*-1
                OFvector
            else: 
                OFvector[1]= (OFvector[1]%(np.pi/2))*-1    

        if np.linalg.norm(OFvector[2]) > np.pi:
            #OFvector[2]= OFvector[2]*-1
            if OFvector[2] < 0:
                OFvector[2]= -(OFvector[2]%(np.pi))*-1
            else: 
                OFvector[2]= (OFvector[2]%(np.pi))*-1    
        
        OFvector = OFvector
        distance_OFestimate = np.linalg.norm(OFvector)
        
        return OFvector,distance_groundTruth,distance_OFestimate
         
    def cartTra2sphereTra(self,cartTra):
        '''
        This function is not used ?
        '''
        sphereTra = list()
        for frame in cartTra:
            #translate oldPosition from cartasian to sphereindircal coordinate system
            oldPosition = self.cart2spheric(frame[0])
            #translate newPosition from cartasian to spherical coordinate system
            newPosition = self.cart2spheric(frame[1])
            sphereTra.append((oldPosition,newPosition,frame[2]))
        return sphereTra

    def testVisibility(self):
        """
        This test can be later used to find resolutable particles
        for the optic flow calculation
                a                      / a \
        b = ----------  alpha = arctan|  - |
            tan(alpha)                 \ b/
        """
        for particle in self.particleList:

            vecNorm = np.linalg.norm(particle.position) 
            
            angleSize = np.rad2deg(np.arctan(particle.size/vecNorm)) 
            print(angleSize> 0.86,vecNorm,angleSize)




