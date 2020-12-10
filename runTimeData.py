
import numpy as np
class runTimeData:
    '''
    '''
    def __init__(self):
        self.sps                    = 20 # number of samples per second
        self.oceanSurface           = 0 # [m] linkable
        self.oceanDepth             = -70 # [m] linkable
        self.oceanLimit             = (-70,70) # [m] linkable
        self.waterCurrent           = np.array([0.0,0.1,0.0]) # just a simple example will be changed later 
        self.waterCurrentMode       = 'static' # static or interpolated
        self.maxObstacles           = 200
        self.mode                   = 'uShape' # needed when using self.divetype?
        self.traLenSec              = 240 # needed when using self.durSec?
        self.traLen                 = self.traLenSec*self.sps # number of samples
        self.velTra                 = list() # list of sealTrajectory per sample with (thrust,slip,lift,yaw,pitch,roll)        
        self.sealPosition           = np.zeros(shape = 3) #centre of the coordinate system of the Seal in disctance to (0,0,0) of world
        self.sealOrientation        = np.zeros(shape = 3)  # orientation as yaw pitch roll
        self.sealStep               = np.zeros(shape =6) # change of position and orientation
        self.sealTrajectory         = list() # public??
        self.diveType               = 'uShape', # descri
        self.durSec                 = 240, # duration of,
        self.currentType            = 'static'
        self.currentStaticVel       = (0.0,2.0,0.0),
        self.oceanDepth             = -70,
        self.amountOfObstacles      = 100,
        self.max_particles          = 270,
        self.particleSizeRange      = (.00002,0.00016),
        self.cloudRadius            = 0.0018, 

    def setParameter(self, parameterName, parameterValue):
        ''' 
        missing self.mode and self.traLenSec as its the sa,e as 
        self.diveType and durSec ?
        '''
        if parameterName == 'sps':
            self.sps 
        elif parameterName == 'oceanSurface':
            self.oceanSurface 
        elif parameterName == 'oceanDepth':
            self.oceanDepth 
        elif parameterName == 'oceanLimit':
            self.oceanLimit 
        elif parameterName == 'waterCurrent':
            self.waterCurrent 
        elif parameterName == 'waterCurrentMode':
            self.waterCurrentMode 
        elif parameterName == 'maxObstacles':
            self.maxObstacles 
        elif parameterName == 'traLen':
            self.traLen 
        elif parameterName == 'velTra ':
            self.velTra  
        elif parameterName == 'sealPosition':
            self.sealPosition 
        elif parameterName == 'sealOrientation':
            self.sealOrientation  
        elif parameterName == 'sealStep':
            self.sealStep  
        elif parameterName == 'sealTrajectory':
            self.sealTrajectory  
        elif parameterName == 'diveType':
            self.diveType  
        elif parameterName == 'durSec':
            self.durSec  
        elif parameterName == 'currentType':
            self.currentType  
        elif parameterName == 'currentStaticVel':
            self.currentStaticVel  
        elif parameterName == 'oceanDepth':
            self.oceanDepth  
        elif parameterName == 'amountOfObstacles':
            self.amountOfObstacles  
        elif parameterName == 'max_particles':
            self.max_particles  
        elif parameterName == 'particleSizeRange':
            self.particleSizeRange  
        elif parameterName == 'cloudRadius':
            self.cloudRadius  
        else:
            print('unknown parameter')

    def getParameter(self,parameterName):
        '''
        '''
        if parameterName == 'sps':
            return self.sps
        elif parameterName == 'oceanSurface':
            return self.oceanSurface
        elif parameterName == 'oceanDepth':
            return self.oceanDepth 
        elif parameterName == 'oceanLimit':
            return self.oceanLimit 
        elif parameterName == 'waterCurrent':
            return self.waterCurrent
        elif parameterName == 'waterCurrentMode':
            return self.waterCurrentMode 
        elif parameterName == 'maxObstacles':
            return self.maxObstacles 
        elif parameterName == 'traLen':
            return self.traLen 
        elif parameterName == 'velTra ':
            return self.velTra  
        elif parameterName == 'sealPosition':
            return self.sealPosition 
        elif parameterName == 'sealOrientation':
            return self.sealOrientation  
        elif parameterName == 'sealStep':
            return self.sealStep  
        elif parameterName == 'sealTrajectory':
            return self.sealTrajectory  
        elif parameterName == 'diveType':
            return self.diveType  
        elif parameterName == 'durSec':
            return self.durSec  
        elif parameterName == 'currentType':
            return self.currentType  
        elif parameterName == 'currentStaticVel':
            return self.currentStaticVel  
        elif parameterName == 'oceanDepth':
            return self.oceanDepth  
        elif parameterName == 'amountOfObstacles':
            return self.amountOfObstacles  
        elif parameterName == 'max_particles':
            return self.max_particles  
        elif parameterName == 'particleSizeRange':
            return self.particleSizeRange  
        elif parameterName == 'cloudRadius':
            return self.cloudRadius  
        else:
            print('unknown parameter')




