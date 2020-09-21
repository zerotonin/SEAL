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
        self.minutes = 5 #length of trajectroy list per second, giving information about trajectroys with a speed 
        # od m/s or deg/s
        self.traIDX = []
        self.divePitch = []

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
        while len(self.traIDX)<self.traLen:
            randomTransitionNumber = random.random()
            newPM = np.where(transProbCS[currentPM,:]>= randomTransitionNumber)
            newPM = random.choice(newPM)[0]
            currentPM = newPM 
            self.traIDX.append(protoMov[newPM])
        print(self.traIDX[1:20])
        print(len(self.traIDX))

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
            
        elif mode == 'vShape':
            self.traLen = 37 #framse -> 185 sec
            self.vShapeDive()
            
        else:
            print('Unkown dive type: ' + mode)

    def uShapeDive(self):
        
        '''
        this function randomly choses pitch vectors according to the 4 
        phases of a uShaped dive (data taken from figure 16 (see def.genrator
        each phase is dicribed with an gaussian function by mean and std that 
        were calculated from the dive data from figure 16. and for each 5 seconds
        one random value is taken. 
        '''
        uShapeDiveSurfaceLen = 10 #frames (degree/0.2sec)
        uShapeDiveDownLen = 4 #frames (degree/0.2sec)
        uShapeDiveStraightLen = 51 #frames (degree/0.2sec)
        uShapeDiveUpLen = 12 #frames (degree/0.2sec)
        #print(uShapeDiveUpMean,uShapeDiveUpVar) 
        self.uShapeDiveSurfaceTra = np.random.normal(loc=-79.639515, scale=12.78034071, size=None)
        self.uShapeDiveDownTra = np.random.normal(loc=63.9146825, scale=8.36629103, size=None)
        self.uShapeDiveStraightTra = np.random.normal(loc=8.36629103, scale=5.5529812, size=None)
        self.uShapeDiveUpTra = np.random.normal(loc=-68.64291923, scale=15.63982373, size=None)
        #print(uShapeDiveSurfaceTra)

        while len(self.divePitch)<self.traLen:
            if len(self.divePitch) < uShapeDiveSurfaceLen:
                pitch = self.uShapeDiveSurfaceTra
            elif uShapeDiveSurfaceLen <= len(self.divePitch) < (uShapeDiveSurfaceLen+uShapeDiveDownLen):
                pitch = self.uShapeDiveDownTra
            elif (uShapeDiveSurfaceLen+uShapeDiveDownLen) <= len(self.divePitch) < (uShapeDiveSurfaceLen+uShapeDiveDownLen+uShapeDiveStraightLen):
                pitch = self.uShapeDiveStraightTra 
            else: 
                pitch = self.uShapeDiveUpTra # get random size and position
            self.divePitch.append(pitch)


        print(self.divePitch)
        print(len(self.divePitch))
        #zProfileUShapedDive:

        uShapeDive = np.genfromtxt ('uShapeDiveDepthPitch.csv',usecols=(1), delimiter=",") #0-10
        uShapeDiveLift = uShapeDive[1:]- uShapeDive[:-1] #lift from frame to frame 0.2 m/s

        uShapeDiveThrusLift = np.c_[ np.zeros(len(uShapeDiveLift)),uShapeDiveLift ] 
        print(uShapeDiveThrusLift)

    
    def vShapeDive(self):
        vShapeDiveSurfaceLen = 11 #frames (degree/0.2sec)
        vShapeDiveDownLen = 14 #frames (degree/0.2sec)
        vShapeDiveUpLen = 12 #frames (degree/0.2sec)

        self.vShapeDiveSurfaceTra = np.random.normal(loc= -74.53024727, scale=7.65994214, size=None)
        self.vShapeDiveDownTra = np.random.normal(loc=17.04128714, scale=25.74478444, size=None)
        self.vShapeDiveUpTra = np.random.normal(loc=-49.06783, scale=28.94055575, size=None)

        while len(self.divePitch)<self.traLen:
            if len(self.divePitch) < vShapeDiveSurfaceLen:
                self.pitch = self.vShapeDiveSurfaceTra
            elif vShapeDiveSurfaceLen <= len(self.divePitch) < (vShapeDiveSurfaceLen+vShapeDiveDownLen):
                self.pitch = self.vShapeDiveDownTra
            else: 
                self.pitch = self.vShapeDiveUpTra # get random size and position
            self.divePitch.append(self.pitch)
        print(self.divePitch)
        
        vShapeDive = np.genfromtxt ('vShapeDiveDepthPitch.csv',skip_header=1,usecols=(1), delimiter=",") #0-10
        vShapeDiveLift = vShapeDive[1:]- vShapeDive[:-1] #lift from frame to frame 0.2 m/s

        vShapeDiveThrusLift = np.c_[ np.zeros(len(vShapeDiveLift)),vShapeDiveLift ] 
        print(vShapeDiveThrusLift)
