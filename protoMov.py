import numpy as np
import random
from importlib import reload 
    
class ProtMov: 
    """
    the seal class holds informations about the seal agent in the 3D cartisian world, simulating 
    the ocean. It holds infomation about the seals position, orientation,and it active movement, 
    defined by habor seal typical trajectories taken from video data.
    """
    def __init__(self,simObj):

        self.simObj = simObj
        self.traIDX = []
        self.divePitch = []
        self.uShapeDiveThrustLiftRot = []

   

    def generator (self):
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
        mode = ('uShape','vShape')
        mode = random.choice(mode)
        print(mode)
        if mode == 'uShape':
            self.traLen = 77 #frames -> 385 sec
            self.uShapeDive()
            self.createThrustSlipYaw()
            
        elif mode == 'vShape':
            self.traLen = 36 #framse -> 185 sec
            self.vShapeDive()
            self.createThrustSlipYaw()
        
            
        else:
            print('Unkown dive type: ' + mode)

    def uShapeDive(self):
        
        '''
        this function randomly chooses pitch vectors according to the 4 
        phases of a uShaped dive (data taken from figure 16 (see def.generator)
        each phase is dicribed with an gaussian function by mean and std that 
        were calculated from the dive data from figure 16. and for each 5 seconds
        one random value is taken. 
        '''
        uShapeDiveSurfaceLen = 10 #frames (degree/0.2sec)
        uShapeDiveDownLen = 4 #frames (degree/0.2sec)
        uShapeDiveStraightLen = 51 #frames (degree/0.2sec)
        uShapeDiveUpLen = 12 #frames (degree/0.2sec)

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
        
        
        self.createThrustLiftPitch(self.divePitch,'uShape')
        
    def vShapeDive(self):
        '''
        this function randomly chooses pitch vectors according to the 4 
        phases of a vShaped dive (data taken from figure 16 (see def.generator)
        each phase is dicribed with an gaussian function by mean and std that 
        were calculated from the dive data from figure 16. and for each 5 seconds
        one random value is taken. 
        '''
        vShapeDiveSurfaceLen = 11 #frames (degree/0.2sec)
        vShapeDiveDownLen = 14 #frames (degree/0.2sec)
        vShapeDiveUpLen = 11 #frames (degree/0.2sec)

        while len(self.divePitch)<self.traLen:
            if len(self.divePitch) < vShapeDiveSurfaceLen:
                self.pitch = np.random.normal(loc= -74.53024727, scale=7.65994214, size=None)
            elif vShapeDiveSurfaceLen <= len(self.divePitch) < (vShapeDiveSurfaceLen+vShapeDiveDownLen):
                self.pitch = np.random.normal(loc=17.04128714, scale=25.74478444, size=None)
            else: 
                self.pitch = np.random.normal(loc=-49.06783, scale=28.94055575, size=None) # get random size and position
            self.divePitch.append(self.pitch)
        self.createThrustLiftPitch(self.divePitch,'vShape',)



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
        '''preallocatio'''
        

        '''get start prototype'''
        randomNumber = random.random() # defines number betwen 0 and 1. the corresponding distributionCS is taken as start PM
        currentPM = np.where(distributionCS>= randomNumber)
        currentPM = random.choice(currentPM)[0]
        self.traIDX.append(protoMov[currentPM])

        '''get random new PM fitting to the transitionProbabilities'''
        while len(self.traIDX)<(self.traLen*5): #length of dive in seconds 
            randomTransitionNumber = random.random()
            newPM = np.where(transProbCS[currentPM,:]>= randomTransitionNumber)
            newPM = random.choice(newPM)[0]
            currentPM = newPM 
            self.traIDX.append(protoMov[newPM]) #traIDX = [thrust(m),Slip(m),Yaw(m)]
        print(self.traIDX[1:20])
        print(len(self.traIDX))

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
            Dive = np.genfromtxt ('uShapeDiveDepthPitch.csv',usecols=(1), delimiter=",") #0-10
            
        elif mode == 'vShape':
            Dive = np.genfromtxt ('vShapeDiveDepthPitch.csv',usecols=(1), delimiter=",") #0-10

        DiveLift = Dive[1:]- Dive[:-1] #lift from frame to frame 0.2 m/s
        DiveLift = np.interp(np.arange(0,(self.traLen*5),1), np.arange(0,(self.traLen*5),5), DiveLift)
        self.divePitch = np.interp(np.arange(0,(self.traLen*5),1), np.arange(0,(self.traLen*5),5), self.divePitch)

        DiveThrustLiftPitch = np.c_[ np.zeros(len(DiveLift)),DiveLift,self.divePitch ] 
        print(DiveThrustLiftPitch)
        for row in DiveThrustLiftPitch:
            theta = np.radians(row[2]) #how to call self.pitch for each colum ? 
            c = np.cos(theta)
            s = np.sin(theta)
            R = np.array(((c, -s), (s, c)))
            row[0:2] = np.dot(R,row[0:2])
        print(DiveThrustLiftPitch) #gives [thrust(0.2m/s),lift(0.2m/s),pitch(0.2degree/s)]