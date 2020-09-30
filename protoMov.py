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


    def generator2(self,mode,traLenSec):
        '''
        this function randomly chooses between uShape and vShapes dives.
        dependent on the diveType it sets the corresponding lenght
        of the dive (traLen) to a specific number of frames (0.2fps)
        Data taken from "Forschungsverbund MINOSplus - Weiterführende Arbeiten an Seevögeln
        und Meeressäugern zur Bewertung von Offshore - Windkraftanlagen Teilvorhaben TP6 
        – „Seehunde in See“ – Untersuchungen zur räumlichen und zeitlichen Nutzung 
        der Nordsee durch Seehunde im Zusammenhang mit der Entwicklung von 
        OffshoreWindenergieanlagen" depth and pitch Data taken from figure 16.
        '''
        self.traLen    = traLenSec*self.sps
        self.traDurSec = traLenSec

        if mode == 'random':
            mode = ('uShape','vShape')
            mode = random.choice(mode)

        if  mode == 'uShape':
            currentDive = copy.deepcopy(self.diveShapeU)
        elif mode == 'vShape':
            currentDive = copy.deepcopy(self.diveShapeV)
        else:
            print('Unkown dive type: ' + mode)
            raise ValueError  # shorthand for 'raise ValueError()'


        # create a HMM based trajectory for thrust slip and yaw VELOCITIES
        self.thrust , self.slip , self.yaw = self.createThrustSlipYaw()


        # Z-POSITION AND Pitch-ANGLE
        self.zProfile ,self.pitchAngle = self.createLiftPitch(currentDive)
        
        # combine both trajectories
        self.velTra =self.mergeLiftPitch_ThrustYawSlip(self.zProfile,self.pitchAngle,self.thrust,self.slip,self.yaw)


 
    
    def mergeLiftPitch_ThrustYawSlip(self,zProfil,pitchAngle,thrust,slip,yaw):

        #positional values to velocities in m/s or deg/s || filtered by 3 sigma gauss
        zVel = np.diff(gaussian_filter1d(zProfil, 3))*self.sps 
        pVel = np.diff(gaussian_filter1d(pitchAngle, 6)) # this is allready deg per frame

        newThrust = list()
        newLift   = list()

        # rotate velocities accordingly
        for frameI in range(self.traLen):
            R = self.mathUtils.getRotMatrix2D(np.deg2rad(pitchAngle[frameI]))
            temp = np.dot(R,np.array([thrust[frameI],zVel[frameI]]))
            newThrust.append(temp[0])
            newLift.append(temp[1])

        return  np.transpose(np.vstack((np.array(newThrust),slip,np.array(newLift),yaw,pVel)))

    
    def getPositionAndAngelsFromVel(self):

        angles = np.cumsum(self.velTra[:,3:]/self.sps,axis=0)
        angles = np.deg2rad(angles)
        positions = np.zeros(shape=(self.velTra.shape[0]+1,3))

        for frameI in range(self.velTra.shape[0]):

            R = self.mathUtils.getRotMatrix3D(angles[frameI,0]*-1,angles[frameI,1]*-1,0)
            positions[frameI+1,:] = np.dot(R,np.array(self.velTra[frameI,0:3]))

        self.positions = positions
        self.angles    = angles
            
    def createLiftPitch(self, currentDive):

        phases = list(currentDive.keys())
        currentPhase = 0
        zProfile     = [0]# to create z-profile that we can diff afterwards
        pitchAngle   = [0]
        bonusDur     = 0

        diveLen = int(np.round(self.traDurSec * self.origDiveFPS))

        for frameI in range(diveLen): 

            # This if clause regulates the change of diving phases. A diving phase ends when
            # either the duration runs out or the animals z-profile gets out of bounds (0, ocean
            # depth). Because the dives have a certain angle, long trajectories might produce
            # shorter than anticipated dive phases. The rest duration of the phase is carried
            # as a bonus to the following phas (straight or surface2). Surface2 is only their
            # to produce trajectories of properlength

            if frameI > currentDive[phases[currentPhase]][0]*diveLen + bonusDur and currentPhase < 5:
                currentPhase += 1
                bonusDur      = 0
                print(currentPhase,frameI,zProfile[-1])
            
            elif currentPhase == 1 and zProfile[-1] <= self.oceanDepth+0.5:
                currentPhase += 1
                bonusDur = currentDive[phases[currentPhase]][0]*self.origDiveFPS -frameI
                print(currentPhase,frameI,zProfile[-1])

            elif currentPhase == 3 and zProfile[-1] >= 0:
                currentPhase += 1
                bonusDur = currentDive[phases[currentPhase]][0]*self.origDiveFPS -frameI
                print(currentPhase,frameI,zProfile[-1])
            else: 
                print(currentPhase,frameI,zProfile[-1],'done')

            currentPitch  =np.random.normal(loc=currentDive[phases[currentPhase]][1], scale=currentDive[phases[currentPhase]][2], size=None)
            currentZshift =np.random.normal(loc=currentDive[phases[currentPhase]][3], scale=currentDive[phases[currentPhase]][4], size=None)

            pitchAngle.append(currentPitch)
            zProfile.append(zProfile[-1] + currentZshift/self.sps )
            # extreme cases
            if zProfile[-1] < self.oceanDepth:
                zProfile[-1] = self.oceanDepth+0.1
            elif zProfile[-1] > 0:
                zProfile[-1] = 0
        


        return self.resample_by_interpolation(zProfile,self.origDiveFPS,self.sps),self.resample_by_interpolation(pitchAngle,self.origDiveFPS,self.sps)

    def createThrustSlipYaw(self):
        """
        Taken Prototypical Movements from analyized video data by Frederike Hanke. 
        Giving information about Thrust,Slip and Yaw.
        """
        '''import Prototypical Movements (k=200)'''
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
        '''Returns given data resampled into trajectory length '''
        return signal.resample(data,self.traLen)


    def resample_by_interpolation(self,signal, input_fs, output_fs):

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
        return self.resampleData2TraLen(resampled_signal)


