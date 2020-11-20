import numpy as np
import random, copy
from utilities import mathUtils
from scipy.ndimage import gaussian_filter1d
from scipy import signal

class ProtMov: 
    """
    The ProtMov class generators prototypical movements discribed with 5 vectors inbtween 
    each frame beeing thrust, lift, slip, pitch and yaw 
    """
    def __init__(self,simObj):
        self.simObj       = simObj
        self.sps          = simObj.sps #shorthand
        self.oceanDepth   = simObj.environment.oceanDepth #shorthand
        self.mathUtils    = mathUtils()
        self.origDiveFPS  = 0.2 # the orginal data was recorded every 5th second 
        self.origVideoFPS = 25
        self.traIDX       = []
        self.divePitch    = []
        self.mode         = 'random'
        self.traLenSec    = 240
        self.traLen       = self.traLenSec*self.sps 
        self.traDurSec    = None 

        # dive phases are keywords for a tupel consisting of 0) duration normalised to total duration
        # 1) mean pitch angle [deg]  2)  standard deviation of the mean [deg] 3)  mean z-profil [m/s]
        # 4) standard deviation of z-profile [m/s]
        self.diveShapeU = {'surface'  :(10.0/77.0, -79.639515  ,12.78034071 ,0.003492857142857107  ,0.012394484328836674),
                           'down'     :(14.0/77.0, 63.9146825  ,8.36629103  ,-0.99880133333333     ,0.05321871641526968),
                           'straight' :(65.0/77.0, 8.36629103  ,5.5529812   ,0.0024724705882352887 ,0.029324291568831443),
                           'up'       :(77.0/77.0,-68.64291923 ,15.63982373 ,0.24612163636363638   ,0.40711433143914316),
                           'surface2' :(77.0/77.0, -79.639515  ,12.78034071 ,0.003492857142857107  ,0.012394484328836674)} # surface 2 is a bonus duration if up wards swimming ends before its duration
        
        
        self.diveShapeV = {'surface'  :(11.0/36.0, -74.53024727,7.65994214  ,-0.005039636363636366 ,0.0280961935023646),        
                           'down'     :(25.0/36.0, 17.04128714 ,25.74478444 ,-0.23516400000000004  ,0.17638583527291268),
                           'straight' :(25.0/36.0, 0.0         ,0.0         ,0.0                   ,0.0 ),
                           'up'       :(36.0/36.0,-49.06783    ,28.94055575 ,0.301                 ,0.28513959297018016),
                           'surface2' :(36.0/36.0 -74.53024727 ,7.65994214  ,-0.005039636363636366 ,0.0280961935023646)} # surface 2 is a bonus duration if up wards swimming ends before its duration


    def generator2(self):
        '''
        this function randomly chooses between uShape and vShapes dives.
        dependent on the diveType it sets the corresponding phases (surface, down, straight
        up,surface2) to their percentage of time each of the phases last.
        Data taken from "Forschungsverbund MINOSplus - Weiterführender Arbeiten an Seevögeln
        und Meeressäugern zur Bewertung von Offshore - Windkraftanlagen Teilvorhaben TP6 
        – „Seehunde in See“ – Untersuchungen zur räumlichen und zeitlichen Nutzung 
        der Nordsee durch Seehunde im Zusammenhang mit der Entwicklung von 
        OffshoreWindenergieanlagen" depth and pitch Data taken from figure 16.

        '''
        
        self.traDurSec = self.traLenSec

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
        self.yawAngle = np.cumsum(self.yaw)

        # get X-Y-positions
        self.fromThrustSlip2XYcoordinates()

        # Z-POSITION AND Pitch-ANGLE in meter or angle with sps frequency
        self.zProfile ,self.pitchAngle = self.createLiftPitch(currentDive)
        print(self.zProfile)
        # check for flying seals!
        self.zProfile[np.where(self.zProfile >0)] = -0.00001
        print(self.zProfile)
        

        # combine both trajectories
        self.velTra =self.mergeLiftPitch_ThrustYawSlip(self.zProfile,self.pitchAngle,self.thrust,self.slip,self.yaw)#(thurst,slip,lift,yaw,pitch)
        #print(self.velTra[0:10])

        self.velTra =self.velTra*self.sps

    def fromThrustSlip2XYcoordinates(self):
        '''
        This function creates the x and y profiles by rotating the 2D thrust and slip vector with 
        a rotation matrix of yaw.
        '''
        self.xProfile = np.zeros(shape=(self.traLen,))
        self.yProfile = np.zeros(shape=(self.traLen,))
 
        for frameI in range(self.traLen-1):
            R = self.mathUtils.getRotMatrix2D(np.deg2rad(self.yawAngle[frameI])*-1)
            temp = np.dot(R,np.array([self.thrust[frameI],self.slip[frameI]]))
            self.xProfile[frameI+1] = self.xProfile[frameI] + temp[0]/self.sps
            self.yProfile[frameI+1] = self.yProfile[frameI] + temp[1]/self.sps
            
    
    def mergeLiftPitch_ThrustYawSlip(self,zProfil,pitchAngle,thrust,slip,yaw):
        '''
        this function merges the before calculates values for thrust, slip,
        lift, yaw and pitch. Roll is considered to be 0. Since lift(zProfile)
        values are taken from the coordinate system point of view, the thrust and lift
        values need to be rotated by a rotation matrix arround the pitch angle in order 
        to get the movement from the seals point of view.
        WHY did we set sigma to 3 for zProfile and to 6 fpr pitch values?
        '''

        #positional values to velocities in m/sample or deg/sample || filtered by 3 sigma gauss
        zVel = np.diff(gaussian_filter1d(zProfil, 3))
        zVel = np.append(0,zVel) # added a start value of 0 to have a length of self.traLen again
        pVel = np.diff(pitchAngle) # this is allready deg per frame
        pVel = np.append(0,pVel )# added a start value of 0 to have a length of self.traLen again

        newThrust = list()
        newLift   = list()

        # rotate velocities accordingly
        for frameI in range(self.traLen):
            R = self.mathUtils.getRotMatrix2D(np.deg2rad(pitchAngle[frameI]))
            temp = np.dot(R,np.array([thrust[frameI],zVel[frameI]]))
            newThrust.append(temp[0])
            newLift.append(temp[1])

        return  np.transpose(np.vstack((np.array(newThrust),slip,np.array(newLift),yaw,pVel))) #(thurst,slip,lift,yaw,pitch)

    
    def getPositionAndAngelsFromVel(self):
        '''
        this function the angle(deg) and postion(m) data from the angleVelocity(deg/s) and 
        directionVelocity(m/s) data. For the angles the cumulative sum of the angleVelocities
        over the time of the dive is calculates. As for the positions the directionVectors from 
        seal point of view needed to be rotated around yaw and pitch in order to get the position 
        values in the world coordinates system(x,y,z)
        '''

        angles = np.cumsum(self.velTra[:,3:]/self.sps,axis=0)
        angles = np.deg2rad(angles)
        positions = np.zeros(shape=(self.velTra.shape[0]+1,3))

        for frameI in range(self.velTra.shape[0]):

            R = self.mathUtils.getRotMatrix3D(angles[frameI,0],angles[frameI,1],0)#why -1 ?
            positions[frameI+1,:] = np.dot(R,np.array(self.velTra[frameI,0:3]/self.sps)) 

        self.positions = positions # how are we considering the start position of the seal in relation to the ocean coordinate system?
        self.angles    = angles #now in rad instead of degree ? 
            
    def createLiftPitch(self, currentDive):
        '''
        dependent on the before definde phases and their duration the dive simulation 
        defines number of frame to run in each phase. Dependent on the phase the pitch 
        and zProfile values are calculates based on the mean and standard deviation defined
        in the diveShapeU and diveShapeV tuple
        '''

        phaseKeys = list(currentDive.keys())
        
        currentPhase = 0
        zProfile     = [0]# to create z-profile that we can diff afterwards
        pitchAngle   = [0]
        bonusDur     = 0

        diveLen = int(np.round(self.traDurSec * self.origDiveFPS))

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
                print(currentPhase,frameI,currentPhaseTimeOut,'frame out')
            
            elif currentPhase == 1 and zProfile[-1] <= self.oceanDepth+0.5:
                currentPhase += 1
                bonusDur = currentDive[currentKey][0]*self.origDiveFPS -frameI
                print(currentPhase,frameI,currentPhaseTimeOut,'depth out')

            elif currentPhase == 3 and zProfile[-1] >= 0:
                currentPhase += 1
                bonusDur = currentDive[currentKey][0]*self.origDiveFPS -frameI
                print(currentPhase,frameI,currentPhaseTimeOut,'surface out')
            else: 
                print(currentPhase,frameI,currentPhaseTimeOut,'go on')

            currentPitch  =np.random.normal(loc=currentDive[currentKey][1], scale=currentDive[currentKey][2], size=None)
            currentZshift =np.random.normal(loc=currentDive[currentKey][3], scale=currentDive[currentKey][4], size=None)

            pitchAngle.append(currentPitch)
            zProfile.append(zProfile[-1] + currentZshift/self.origDiveFPS )
            # extreme cases
            if zProfile[-1] < self.oceanDepth:
                zProfile[-1] = self.oceanDepth+0.1
            elif zProfile[-1] > 0:
                zProfile[-1] = 0

        return self.resample_by_interpolation(zProfile,self.origDiveFPS,self.sps),self.resample_by_interpolation(pitchAngle,self.origDiveFPS,self.sps)

    def createThrustSlipYaw(self):
        """
        Taken Prototypical Movements from analyized video data by Frederike Hanke. 
        Giving information about Thrust,Slip and Yaw. The data from the videos were
        used to creat clusters of prototypical movements. This was done with k-means 
        clustering and the number of clusters was set to 150.
        """
        '''import Prototypical Movements (k=200),giving information about thrust,slip,yaw'''
        protoMov = np.genfromtxt ('protoMov.csv', delimiter=",")
        '''import distribution percentage of the 200 clusters. Given as numbers from 0-1 (equal to 0-100%)'''
        distributionCS = np.genfromtxt ('distributionCS.csv', delimiter=",")
        '''import transition probability from each Prototypical Movement to another'''
        transProbCS = np.genfromtxt ('transProbCS.csv', delimiter=",")        
        '''preallocation'''
        
        '''get start prototype'''
        
        pmTraLen = int(np.round(self.traDurSec*self.origVideoFPS))

        randomNumbers = np.random.rand(pmTraLen+1)   # defines number betwen 0 and 1. the corresponding distributionCS is taken as start PM
        currentPM = np.where(distributionCS>= randomNumbers[0])
        currentPM = currentPM[0][0]
        self.traIDX.append(protoMov[currentPM])
        self.pmIDX = list()
        self.pmIDX.append(currentPM)

        '''get random new PM fitting to the transitionProbabilities'''
        for i in range(pmTraLen): #length of dive in seconds 
            randomTransitionNumber = randomNumbers[i+1]
            newPM = np.where(transProbCS[currentPM,:]>= randomTransitionNumber)
            newPM = newPM[0][0]
            # a bad hack for the old clustering ...cluster a new with 150 classes
            if newPM > 197:
                newPM = 197
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
        '''Returns given data resampled into trajectory length.Resamples x to num samples using
         Fourier method along the given axis.The resampled signal starts at the same value as x 
         but is sampled with a spacing of len(x) / num * (spacing of x). Because a Fourier method
          is used, the signal is assumed to be periodic. '''
        return signal.resample(data,self.traLen) #which data ? 


    def resample_by_interpolation(self,signal, input_fs, output_fs):
        '''
        The diving (depth sensor) and cruising data (Videos) were recorded at
        0.2 Hz and respectively 25 Hz. Especially in the case of the prototypical
        movements (PM), this renders each PM to be 40ms long. Therefore we have 
        to create the PM sequence in 25 Hz and than resample the resulting trajectory
        to a frequency of our simulation. Note the PM sequence cannot be resampled as
        it is a quantized (classes) and not continues data format.
        '''
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



    def getSealHeading(self):

        sealHeading =list()
        for frameI in range(self.velTra.shape[0]):

            R = self.mathUtils.getRotMatrix3D(self.angles[frameI,0],self.angles[frameI,1],0, mode='passive')
            sealHeading.append(np.dot(R,np.array([10,0,0]))) 
            
        self.sealHeading = np.array(sealHeading)
        #print(self.sealHeading[0:10])
        #print(len(self.sealHeading)) #is 60001 this is too big 
        self.xheading = self.sealHeading[0]
        self.yheading = self.sealHeading[1]
        self.zheading = self.sealHeading[2]