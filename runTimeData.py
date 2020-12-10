
import numpy as np
class runTimeData:
    '''
    '''
    def __init__(self):
        self.sps                    = 20
        self.oceanSurface           = 0 # [m] linkable
        self.oceanDepth             = -70 # [m] linkable
        self.oceanLimit             = (-70,70) # [m] linkable
        self.waterCurrent           = np.array([0.0,0.1,0.0]) # just a simple example will be changed later 
        self.waterCurrentMode       = 'static'
        self.maxObstacles           = 200
        self.mode                   = 'random'
        self.traLenSec              = 240
        self.traLen                 = self.traLenSec*self.sps 
        self.velTra                 = list()        
        self.sealPosition           = np.zeros(shape = 3) #centre of the coordinate system of the Seal in disctance to (0,0,0) of world
        self.sealOrientation        = np.zeros(shape = 3)  # orientation as yaw pitch roll
        self.sealStep               = np.zeros(shape =6) # change of position and orientation
        self.sealTrajectory         = list() # public??
        self.diveType               = 'vShape', # descri
        self.durSec                 = 240, # duration of
        self.currentType            = 'static'
        self.currentStaticVel       = (0.0,2.0,0.0),
        self.oceanDepth             = -70,
        self.amountOfObstacles      = 100,
        self.max_particles          = 270,
        self.particleSizeRange      = (.00002,0.00016),
        self.cloudRadius            = 0.0018, 

    def setParameter(self, parameterName, parameterValue):
        '''
        '''
        if parameterName == 'sps':
            self.sps = parameterValue
    def getParameter(self):
        '''
        '''




