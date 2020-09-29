import numpy as np
import random, copy
from importlib import reload 
    
class ProtMov: 
    """
    The ProtMov class generators prototypical movements discribed with 5 vectors inbtween 
    each frame beeing thrust, lift, slip, pitch and yaw 
    """
    def __init__(self,simObj):
        self.simObj      = simObj
        self.sps         = simObj.sps #shorthand
        self.oceanDepth  = simObj.environment.oceanDepth #shorthand
        self.origDiveFPS = 0.2 # the orginal data was recorded every 5th second 
        self.traIDX      = []
        self.divePitch   = []

        # dive phases are keywords for a tupel consisting of 0) duration normalised to total duration
        # 1) mean pitch angle [deg]  2)  standard deviation of the mean [deg] 3)  mean z-profil [m/s]
        # 4) standard deviation of z-profile [m/s]
        self.diveShapeU = {'surface'  :(10.0/77.0, -79.639515,12.78034071 ,0.003492857142857107  ,0.012394484328836674),
                           'down'     :( 4.0/77.0, 63.9146825,8.36629103  ,-25,-0.99880133333333 ,0.05321871641526968),
                           'straight' :(51.0/77.0, 8.36629103,5.5529812   ,0.0024724705882352887 ,0.029324291568831443),
                           'up'       :(12.0/77.0,-68.64291923,15.63982373,0.24612163636363638   ,0.40711433143914316),
                           'surface2' :(0.0, -79.639515,12.78034071 ,0.003492857142857107  ,0.012394484328836674)} # surface 2 is a bonus duration if up wards swimming ends before its duration
        
        
        self.diveShapeV = {'surface'  :(11.0/36.0, -74.53024727,7.65994214, -0.005039636363636366,0.0280961935023646),        
                           'down'     :(14.0/36.0, 17.04128714 ,25.74478444,-0.23516400000000004 ,0.17638583527291268),
                           'straight' :(0        ,0            ,0          ,0                    ,0),
                           'up'       :(11.0/36.0,-49.06783    ,28.94055575,0.301                ,0.28513959297018016),
                           'surface2' :(0.0, -74.53024727,7.65994214, -0.005039636363636366,0.0280961935023646)} # surface 2 is a bonus duration if up wards swimming ends before its duration


    def generator2 (self,mode,traLenSec):
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
        self.traLen = traLenSec*self.sps

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


        # create a HMM based trajectory for thrust slip and yaw
        self.createThrustSlipYaw()


        self.createThrustLiftPitch(self.divePitch,'vShape',self.thrust)


        self.diveProtoMov= np.c_[[i[0:2] for i in self.DiveThrustLiftPitch],self.slip,[i[2] for i in self.DiveThrustLiftPitch],self.yaw] # [thrust(m/s),lift(m/s),slip(m/s),pitch(degree/s),yaw(degree/s)]
        print(self.diveProtoMov)
        print(len(self.diveProtoMov))


    def generatorPitchLift(self, currentDive):

        diveFPSinSPS = self.sps/self.origDiveFPS
        phases = currentDive.keys()
        currentPhase = 0
        zProfile     = []
        bonusDur     = 0

        for frameI in range(self.traLen+1): # +1 to create z-profile that we can diff afterwards

            # This if clause regulates the change of diving phases. A diving phase ends when
            # either the duration runs out or the animals z-profile gets out of bounds (0, ocean
            # depth). Because the dives have a certain angle, long trajectories might produce
            # shorter than anticipated dive phases. The rest duration of the phase is carried
            # as a bonus to the following phas (straight or surface2). Surface2 is only their
            # to produce trajectories of properlength

            if frameI > currentDive[phases[currentPhase]][0]*self.sps + bonusDur:
                currentPhase += 1
                bonusDur      = 0
            
            elif currentPhase == 1 and zProfile[-1] <= self.oceanDepth+0.5:
                currentPhase += 1
                bonusDur = currentDive[phases[currentPhase]][0]*self.sps -frameI

            elif currentPhase == 3 and zProfile[-1] >= 0:
                currentPhase += 1
                bonusDur = currentDive[phases[currentPhase]][0]*self.sps -frameI
            




    def generator (self,mode,traLenSec):
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
        self.traLen = traLenSec*self.sps

        if mode == 'random':
            mode = ('uShape','vShape')
            mode = random.choice(mode)

        if mode == 'uShape':
            self.traLen = 77 #frames -> 385 sec
            self.uShapeDive()
            self.createThrustSlipYaw()
            self.createThrustLiftPitch(self.divePitch,'uShape',self.thrust)  
        elif mode == 'vShape':
            self.traLen = 36 #frames -> 185 sec
            self.vShapeDive()
            self.createThrustSlipYaw()
            self.createThrustLiftPitch(self.divePitch,'vShape',self.thrust)
        else:
            print('Unkown dive type: ' + mode)
            raise ValueError  # shorthand for 'raise ValueError()'
        self.diveProtoMov= np.c_[[i[0:2] for i in self.DiveThrustLiftPitch],self.slip,[i[2] for i in self.DiveThrustLiftPitch],self.yaw] # [thrust(m/s),lift(m/s),slip(m/s),pitch(degree/s),yaw(degree/s)]
        print(self.diveProtoMov)
        print(len(self.diveProtoMov))
        
    def uShapeDive(self):
        
        '''
        this function randomly chooses pitch vectors according to the 4 
        phases of a uShaped dive (data taken from figure 16 (see def.generator)
        each phase is dicribed with an gaussian function by mean and std that 
        were calculated from the dive data from figure 16. and for each 5 seconds
        one random value is taken. 
        '''
        uShapeDiveSurfaceLen  = 10 #frames (degree/0.2sec)
        uShapeDiveDownLen     = 4  #frames (degree/0.2sec)
        uShapeDiveStraightLen = 51 #frames (degree/0.2sec)
        uShapeDiveUpLen       = 12 #frames (degree/0.2sec)

        while len(self.divePitch)<self.traLen:
            if len(self.divePitch) < uShapeDiveSurfaceLen:
                pitch = np.random.normal(loc=-79.639515, scale=12.78034071, size=None)
            elif uShapeDiveSurfaceLen <= len(self.divePitch) < (uShapeDiveSurfaceLen+uShapeDiveDownLen):
                pitch = np.random.normal(loc=63.9146825, scale=8.36629103, size=None)
            elif (uShapeDiveSurfaceLen+uShapeDiveDownLen) <= len(self.divePitch) < (uShapeDiveSurfaceLen+uShapeDiveDownLen+uShapeDiveStraightLen):
                pitch = np.random.normal(loc=8.36629103, scale=5.5529812, size=None) 
            else: 
                pitch = np.random.normal(loc=-68.64291923, scale=15.63982373, size=None) # get random size and position
            self.divePitch.append(pitch)
        
    def vShapeDive(self):
        '''
        this function randomly chooses pitch vectors according to the 4 
        phases of a vShaped dive (data taken from figure 16 (see def.generator)
        each phase is dicribed with an gaussian function by mean and std that 
        were calculated from the dive data from figure 16. and for each 5 seconds
        one random value is taken. 
        '''
        vShapeDiveSurfaceLen = 11 #frames (degree/0.2sec)
        vShapeDiveDownLen    = 14 #frames (degree/0.2sec)
        vShapeDiveUpLen      = 11 #frames (degree/0.2sec)

        while len(self.divePitch)<self.traLen:
            if len(self.divePitch) < vShapeDiveSurfaceLen:
                self.pitch = np.random.normal(loc= -74.53024727, scale=7.65994214, size=None)
            elif vShapeDiveSurfaceLen <= len(self.divePitch) < (vShapeDiveSurfaceLen+vShapeDiveDownLen):
                self.pitch = np.random.normal(loc=17.04128714, scale=25.74478444, size=None)
            else: 
                self.pitch = np.random.normal(loc=-49.06783, scale=28.94055575, size=None) # get random size and position
            self.divePitch.append(self.pitch)



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
        randomNumber = random.random() # defines number betwen 0 and 1. the corresponding distributionCS is taken as start PM
        currentPM = np.where(distributionCS>= randomNumber)
        currentPM = random.choice(currentPM)[0]
        self.traIDX.append(protoMov[currentPM])

        '''get random new PM fitting to the transitionProbabilities'''
        while len(self.traIDX)<(self.traLen): #length of dive in seconds 
            randomTransitionNumber = random.random()
            newPM = np.where(transProbCS[currentPM,:]>= randomTransitionNumber)
            newPM = random.choice(newPM)[0]
            currentPM = newPM 
            self.traIDX.append(protoMov[newPM]) #traIDX = [thrust(m),Slip(m),Yaw(m)]
        self.thrust = [i[0] for i in self.traIDX]
        self.slip = [i[1] for i in self.traIDX]
        self.yaw = [i[2] for i in self.traIDX]

    def createThrustLiftPitch(self,divePitch,mode,thrust):
        '''
        this function takes the before created pitch values for a u or vShape dive and 
        generates a diveDepth list with the same length. The lift values between every 5 sec 
        is calculated by subtracting the first value from the second value and so on. 
        Next a array is created with Thrust set to 0, the lift and pitch values[0,thrust(m),pitch(deg)]
        In order to get the correct thrust,lift movements acording to the pitch values we need 
        to rotate the coordinate system by pitch in oder to get the movement from the seal_agents
        point of view. This is done with a rotation Matrix :
                    cos(pitch)  -sin(pitch)
        R(pitch) =  sin(pitch)  cos(pitch)
        the new thrust and lift vector created by this rotation matrix is calculated with:
        R(pitch) * (thrust(0), lift) --> (thrust',lift')
        '''
        if mode == 'uShape':
            Dive = np.genfromtxt ('uShapeDiveDepthPitch.csv',usecols=(1), delimiter=",")   
        elif mode == 'vShape':
            Dive = np.genfromtxt ('vShapeDiveDepthPitch.csv',usecols=(1), delimiter=",")

        DiveLift = Dive[1:]- Dive[:-1] #lift from frame to frame 0.2 m/s
        DiveLift = np.interp(np.arange(0,(self.traLen*5),1), np.arange(0,(self.traLen*5),5), DiveLift)
        self.divePitch = np.interp(np.arange(0,(self.traLen*5),1), np.arange(0,(self.traLen*5),5), self.divePitch)
        self.DiveThrustLiftPitch = np.c_[thrust,DiveLift,self.divePitch ] 
        for row in self.DiveThrustLiftPitch:
            theta = np.radians(row[2]) #how to call self.pitch for each colum ? 
            c = np.cos(theta)
            s = np.sin(theta)
            R = np.array(((c, -s), (s, c)))
            row[0:2] = np.dot(R,row[0:2])
        