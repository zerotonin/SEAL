import numpy as np
import random, copy
from utilities import mathUtils
from scipy.ndimage import gaussian_filter1d
from scipy import signal

class ProtMov: 
    """
    The ProtMov class generators prototypical movements discribed with 6 vectors inbetween 
    each frame beeing 2 translational trajectroies (thrust,slip,lift)
    and three rotational trajectories (yaw,pitch,roll). 
    """

    def __init__(self,simObj):
        """
        this function set the default values for dive duration and takes
        the values for the temporal resolutipn and oceanDepth from the 
        simObj class

        @param simObj                   string default: none
           string that gives a name: simulation object.
        @param sps                      float default: none
            defines the number of samples simulated per second
        @param oceanDepth               float default: none
            defines the ocean depth of the environment [m]
        @param mathUtils                ? default: True
            creates a shortcut to the mathUtils class stored in 
            utilities.py
        @param origDiveFPS              float default: 0.2
            defines the original temporal resolution of the diveDate
            (zProfile and pitch values)
        @param origVideoFPS             float default: 25
            defines the orginal temporal resolution of the surface videos
            for seal movement (thrust,slip,yaw) 
        @param traIDX                   list default: none
            list of thrust(m/s),Slip(m/s),Yaw(m/s) values per second
        @param mode                     str default: 'random'
            mode defining which dive shape should be simulated
            (uShape or vShape)
        @param traLenSec                float default: 240
            sets the length of the dive in seconds
        @param traLen                   floar default: none
            calculates the length of the dive in samples    
        @param diveShapeU               dict 
            defines a dictionary for the 5 different phases of a uShaped
            dive with 5 values 
            (0) duration normalised to total duration
            (1) mean pitch angle [deg]  (2)  standard deviation of the mean [deg] 
            (3)  mean z-profil [m/s]    (4) standard deviation of z-profile [m/s])
        @param diveShapeV               dict
            defines a dictionary for the 5 differen phases of a vShaped dive
            in this case the straight phase is defined by a length of zero
            samples since it is not present in vShaped dives. 
        """
        self.simObj        = simObj
        self.sps           = simObj.sps #shorthand LINKED
        self.oceanDepth    = simObj.environment.oceanDepth #shorthand LINKED
        self.mathUtils     = mathUtils()
        self.origDiveFPS   = 0.2 # the orginal data was recorded every 5th second 
        self.origVideoFPS  = 25 # video fps of the original footage
        self.traIDX        = []
        self.pmIDX         = []
        self.mode          = 'random'
        self.traLenSec     = 240
        self.traLen        = self.traLenSec*self.sps 
        self.thrust        = []
        self.slip          = []
        self.yaw           = []
        self.yawAngle      = []
        self.zProfile      = []
        self.pitchAngle    = []
        self.xProfile      = np.zeros(shape=(self.traLen,))
        self.yProfile      = np.zeros(shape=(self.traLen,))  
        self.posTrajectory = None
        self.positions     = positions
        self.angles        = angles 
        self.sealHeading   = list()
        self.xheading      = list()
        self.yheading      = list()
        self.zheading      = list()


        # dive phases are keywords for a tupel consisting of 0) duration normalised to total duration
        # 1) mean pitch angle [deg]  2)  standard deviation of the mean [deg] 3)  mean z-profil [m/s]
        # 4) standard deviation of z-profile [m/s]. We inverted the sign of the pitch values from the 
        # original data, so that they now fit the international definition of the pitch angle
        self.diveShapeU = {'surface'  :(10.0/77.0, 79.639515  ,12.78034071 ,0.003492857142857107  ,0.012394484328836674),
                           'down'     :(14.0/77.0, -63.9146825  ,8.36629103  ,-0.99880133333333     ,0.05321871641526968),
                           'straight' :(65.0/77.0, -8.36629103  ,5.5529812   ,0.0024724705882352887 ,0.029324291568831443),
                           'up'       :(77.0/77.0,68.64291923 ,15.63982373 ,0.24612163636363638   ,0.40711433143914316),
                           'surface2' :(77.0/77.0, 79.639515  ,12.78034071 ,0.003492857142857107  ,0.012394484328836674)} # surface 2 is a bonus duration if up wards swimming ends before its duration
        
        self.diveShapeV = {'surface'  :(11.0/36.0, 74.53024727,7.65994214  ,-0.005039636363636366 ,0.0280961935023646),        
                           'down'     :(25.0/36.0, -17.04128714 ,25.74478444 ,-0.23516400000000004  ,0.17638583527291268),
                           'straight' :(25.0/36.0, 0.0         ,0.0         ,0.0                   ,0.0 ),
                           'up'       :(36.0/36.0, 49.06783    ,28.94055575 ,0.301                 ,0.28513959297018016),
                           'surface2' :(36.0/36.0, 74.53024727 ,7.65994214  ,-0.005039636363636366 ,0.0280961935023646)} # surface 2 is a bonus duration if up wards swimming ends before its duration

    def generator2(self):
        """
        this function randomly chooses between uShape and vShapes dives.
        dependent on the diveType it sets the corresponding phases (surface, down, straight
        up,surface2) to their percentage of time each of the phases last.
        Data taken from "Forschungsverbund MINOSplus - Weiterführender Arbeiten an Seevögeln
        und Meeressäugern zur Bewertung von Offshore - Windkraftanlagen Teilvorhaben TP6 
        – „Seehunde in See“ – Untersuchungen zur räumlichen und zeitlichen Nutzung 
        der Nordsee durch Seehunde im Zusammenhang mit der Entwicklung von 
        OffshoreWindenergieanlagen" depth and pitch Data taken from figure 16.
        It calculates thrus, slip and yaw values as well as zProfile and pitch values.
        From this dataSet the x,y,z positions are calculated by a 2D rotation matrix
        and the sealStep thrust,slip,lift,yaw,pitch,roll by a 3D rotation matrix.
        """
        if self.mode == 'random':
            self.mode = random.choice(('uShape','vShape'))

        if  self.mode == 'uShape':
            currentDive = copy.deepcopy(self.diveShapeU)
        elif self.mode == 'vShape':
            currentDive = copy.deepcopy(self.diveShapeV)
        else:
            print('Unkown dive type: ' + self.mode)
            raise ValueError  # shorthand for 'raise ValueError()'

        # create a HMM based trajectory for thrust slip and yaw VELOCITIES!
        # the resulting data is already in meters per sample
        self.thrust , self.slip , self.yaw = self.createThrustSlipYaw()

        # yaw velocity to yaw angle
        self.yawAngle = np.cumsum(self.yaw/self.sps)

        # get X-Y-positions
        # this transforms self.thrust and self.slip to the X and y position in world coordinates
        self.fromThrustSlipTRA2XYcoordinatesTRA()

        # Z-POSITION AND Pitch-ANGLE in meter or angle with sps frequency
        self.zProfile ,self.pitchAngle = self.createLiftPitch(currentDive)
        #print('interpolated PitchAngle', self.pitchAngle)
        #print(self.zProfile)
        
        # check for flying seals!
        self.zProfile[np.where(self.zProfile >0)] = -0.00001
        #print(self.zProfile)
        
        # combine both trajectories
        self.mergeLiftPitch_ThrustYawSlip()#(thurst,slip,lift,yaw,pitch)

    def fromThrustSlipTRA2XYcoordinatesTRA(self):
        """
        This function creates the x and y profiles by rotating the 2D thrust and slip vector with 
        a rotation matrix of yaw.
        """
        
        
 
        for frameI in range(self.traLen-1):
            temp = self.mathUtils.agentBasedVels2worldBasedCoords(
                np.array([self.thrust[frameI],self.slip[frameI]]),np.deg2rad(self.yawAngle[frameI]),
                '2D')
            self.xProfile[frameI+1] = self.xProfile[frameI] + temp[0]/self.sps # this is done because the values are in m/sec and should be in m/sample
            self.yProfile[frameI+1] = self.yProfile[frameI] + temp[1]/self.sps # this is done because the values are in m/sec and should be in m/sample
            
    def mergeLiftPitch_ThrustYawSlip(self):
        """
        This function merges the before calculates values for thrust, slip,
        lift, yaw and pitch. 
        Therefore positional trajectories are calculates and the velocity step 
        trajectory in seal coordinates and per second are calculated by rotating
        them around a 3D rotation axis.
        The seal trajectories in m/s or def/s for each seal step are stored in the 
        velTra list.
        """
        # filter zProfile as the original data had low temporal resolution
        self.zProfile   = gaussian_filter1d(self.zProfile, 3)
        self.pitchAngle = gaussian_filter1d(self.pitchAngle, 30)

        # Make positional trajectory in m, rad, witrh all six degrees of freedom. Roll is set to zero as it ix not defined.
        self.posTrajectory = np.vstack((self.xProfile,self.yProfile,self.zProfile,np.deg2rad(self.yawAngle),np.deg2rad(self.pitchAngle), np.zeros(shape=self.traLen)))  
        self.posTrajectory = self.posTrajectory.transpose()

        # Now we have to calculate the velocity step trajectory, both,  in seal coordinates and per second.
        self.velTra = list()
        for frameI in np.arange(1,self.traLen):
            rawSpeeds = np.diff(self.posTrajectory[frameI-1:frameI+1,:],axis= 0) # get difference of position and orientation per frame        
            rotVel  = rawSpeeds[0][3:]*self.sps 
            #eprint(rotVel)
            #erotStart = np.array([np.deg2rad(self.yawAngle[0]),np.deg2rad(self.pitchAngle[0]),0])*self.sps
            #eprint(rotStart)
            #erotVel  = np.vstack((rotStart,rotVel)) # change to angle velocity from rad/frame to rad/sec
            # calculate rotation matrix for animal orientation. So that we can calculate thrust slip lift from the difference of X,Y,Z coordinates
            R = self.mathUtils.getRotMatrix3D(self.posTrajectory[frameI-1,3],self.posTrajectory[frameI-1,4],self.posTrajectory[frameI-1,5],mode='passive') 
            transVel = np.dot(R,rawSpeeds[0][0:3]) # diff x,y,z -> thrust slip lift
            transVel = transVel*self.sps # change to angle velocity from m/frame to m/sec
            # save everything to vel tra
            self.velTra.append(np.hstack((transVel,rotVel)))
            
        self.velTra = np.array(self.velTra)
    
    def getPositionAndAngelTrajectoryFromVelTrajectory(self):
        """
        This function calculates the angle(deg) and postion(m) data from the angleVelocity(deg/s) and 
        directionVelocity(m/s) data. For the angles the cumulative sum of the angleVelocities
        over the time of the dive is calculates. As for the positions the directionVectors from 
        seal point of view needed to be rotated around yaw and pitch in order to get the position 
        values in the world coordinates system(x,y,z)
    
        """
        testAngle = np.array([np.deg2rad(self.yawAngle[0]),np.deg2rad(self.pitchAngle[0]),0])
        testVelAngle = self.velTra[:,3:]/self.sps
        angles = np.vstack((testAngle,testVelAngle))
        angles = np.cumsum(angles,axis=0)
        positions = np.zeros(shape=(self.velTra.shape[0]+1,3))

        for frameI in range(self.velTra.shape[0]):
            positions[frameI+1,:] = self.mathUtils.agentBasedVels2worldBasedCoords(
                                np.array(self.velTra[frameI,0:3]/self.sps),angles[frameI,:],'3D')
     
        self.positions = positions 
        self.angles    = angles 

    def createLiftPitch(self, currentDive):
        """
        Dependent on the before defined phases and their duration the dive simulation 
        defines number of samples to run in each phase. Dependent on the phase the pitch 
        and zProfile values are calculates based on the mean and standard deviation defined
        in the diveShapeU and diveShapeV tuple
        """
        phaseKeys = list(currentDive.keys())
        
        currentPhase = 0
        zProfile     = [0]# to create z-profile that we can diff afterwards
        pitchAngle   = [0]
        bonusDur     = 0

        diveLen = int(np.round(self.traLenSec * self.origDiveFPS))

        for frameI in range(diveLen+1): 

            # This if clause regulates the change of diving phases. A diving phase ends when
            # either the duration runs out or the animals z-profile gets out of bounds (0, ocean
            # depth). Because the dives have a certain angle, long trajectories might produce
            # shorter than anticipated dive phases. The rest duration of the phase is carried
            # as a bonus to the following phas (straight or surface2). Surface2 is only their
            # to produce trajectories of properlength
            
            currentKey          = phaseKeys[currentPhase]
            currentPhaseTimeOut = int(np.ceil(currentDive[currentKey][0]*diveLen + bonusDur))

            if frameI > currentPhaseTimeOut and currentPhase < 5:
                currentPhase += 1
                bonusDur      = 0
                #print(currentPhase,frameI,currentPhaseTimeOut,'frame out')
            
            elif currentPhase == 1 and zProfile[-1] <= self.oceanDepth+0.5:
                currentPhase += 1
                bonusDur = currentDive[currentKey][0]*self.origDiveFPS -frameI
                #print(currentPhase,frameI,currentPhaseTimeOut,'depth out')

            elif currentPhase == 3 and zProfile[-1] >= 0:
                currentPhase += 1
                bonusDur = currentDive[currentKey][0]*self.origDiveFPS -frameI
                #print(currentPhase,frameI,currentPhaseTimeOut,'surface out')
            else: 
                #print(currentPhase,frameI,currentPhaseTimeOut,'go on')
                pass
            currentPitch  =np.random.normal(loc=currentDive[currentKey][1], scale=currentDive[currentKey][2], size=None)
            currentZshift =np.random.normal(loc=currentDive[currentKey][3], scale=currentDive[currentKey][4], size=None)

            pitchAngle.append(currentPitch)
            # here we transform from velocities to positions 
            zProfile.append(zProfile[-1] + currentZshift/self.origDiveFPS )
            # extreme cases
            if zProfile[-1] < self.oceanDepth:
                zProfile[-1] = self.oceanDepth+0.1
            elif zProfile[-1] > 0:
                zProfile[-1] = 0
        #print('pitchAngleList : ', pitchAngle)

        return self.resample_by_interpolation(zProfile,self.origDiveFPS,self.sps),self.resample_by_interpolation(pitchAngle,self.origDiveFPS,self.sps)

    def createThrustSlipYaw(self):
        """
        Taken Prototypical Movements from analyized video data by Frederike Hanke. 
        Giving information about Thrust,Slip and Yaw. The data from the videos were
        used to creat clusters of prototypical movements. This was done with k-means 
        clustering and the number of clusters was set to 50.

        @return thrust,slip,yaw in m/s or deg/s
        """
        #import Prototypical Movements (k=50),giving information about thrust,slip,yaw
        protoMov = np.genfromtxt ('protoMov.csv', delimiter=",")
        #import distribution percentage of the 50 clusters. Given as numbers from 0-1 (equal to 0-100%)
        distributionCS = np.genfromtxt ('distributionCS.csv', delimiter=",")
        #import transition probability from each Prototypical Movement to another
        transProbCS = np.genfromtxt ('transProbCS.csv', delimiter=",")        

        pmTraLen = int(np.round(self.traLenSec*self.origVideoFPS))

        randomNumbers = np.random.rand(pmTraLen+1)   # defines number betwen 0 and 1. the corresponding distributionCS is taken as start PM
        currentPM = np.where(distributionCS>= randomNumbers[0])
        currentPM = currentPM[0][0]
        self.traIDX.append(protoMov[currentPM])
        self.pmIDX = list()
        self.pmIDX.append(currentPM)

        #get random new PM fitting to the transitionProbabilities
        for i in range(pmTraLen): #length of dive in seconds 
            randomTransitionNumber = randomNumbers[i+1]
            newPM = np.where(transProbCS[currentPM,:]>= randomTransitionNumber)
            newPM = newPM[0][0]
            currentPM = newPM 
            self.traIDX.append(protoMov[newPM]) #traIDX = [thrust(m),Slip(m),Yaw(m)]
            self.pmIDX.append(currentPM)

        self.traIDX = np.array(self.traIDX)
        #resampling from video fps to sps
        thrust = self.resample_by_interpolation(self.traIDX[:,0],self.origVideoFPS,self.sps), 
        slip   = self.resample_by_interpolation(self.traIDX[:,1],self.origVideoFPS,self.sps), 
        yaw   = self.resample_by_interpolation(self.traIDX[:,2],self.origVideoFPS,self.sps)
        
        return thrust[0],slip[0],yaw

    def resampleData2TraLen(self,data):
        """
        This function resamples given data into trajectory length.Resamples x to num samples using
        Fourier method along the given axis.The resampled signal starts at the same value as x 
        but is sampled with a spacing of len(x) / num * (spacing of x). Because a Fourier method
        is used, the signal is assumed to be periodic.

        @returns resampled data with a length of traLen 
        """
        return signal.resample(data,self.traLen) 

    def resample_by_interpolation(self,signal, input_fs, output_fs):
        """
        The diving (depth sensor) and cruising data (Videos) were recorded at
        0.2 Hz and respectively 25 Hz. Especially in the case of the prototypical
        movements (PM), this renders each PM to be 40ms long. Therefore we have 
        to create the PM sequence in 25 Hz and than resample the resulting trajectory
        to a frequency of our simulation. Note the PM sequence cannot be resampled as
        it is a quantized (classes) and not continues data format.

        @return interpolated Data with a length of traLen
        """
        scale = output_fs / input_fs
        # calculate new length of sample
        n = round(len(signal) * scale)

        # use linear interpolation
        # endpoint keyword means than linspace doesn't go all the way to 1.0
        # If it did, there are some off-by-one errors
        # e.g. scale=2.0, [1,2,3] should go to [1,1.5,2,2.5,3,3]
        # but with endpoint=True, we get [1,1.4,1.8,2.2,2.6,3]
        # Both are OK, but since resampling will often involve
        # exact ratios (i.e. for 44100 to 22050 or vice versa)
        # using endpoint=False gets less noise in the resampled sound
        resampled_signal = np.interp(
            np.linspace(0.0, 1.0, n, endpoint=False),  # where to interpret
            np.linspace(0.0, 1.0, len(signal), endpoint=False),  # known positions
            signal,  # known data points
        )
        return self.resampleData2TraLen(resampled_signal) # to assure trajectory length

    def getSealHeading(self,headingVector=np.array([10,0,0])):
        """
        This function creats a 3D heading vector by rotating the 
        heading vector by the thrust pitch and roll angles.
        """
        for frameI in range(self.angles.shape[0]):

            self.sealHeading.append(self.mathUtils.agentBasedVels2worldBasedCoords(headingVector,self.angles[frameI,:],'3D')) 
            
        self.sealHeading = np.array(self.sealHeading)
        #print(self.sealHeading[0:10])
        #print(len(self.sealHeading)) #is 60001 this is too big 
        self.xheading = self.sealHeading[0]
        self.yheading = self.sealHeading[1]
        self.zheading = self.sealHeading[2]