import numpy as np 
from scipy import interpolate
class Environment:
    '''
    The 'Enviroment' class contains functions that are used for creating ocean' enviroment where particles are
    moving in the visual field of a seal. Seal is the center of particles' cloud in cartesian space. The depth 
    limit of the ocean is -70 m. 
    @param groundLevel  float  default: -70.0
        the depth of an ocean [m] that is limited by the value of -70 [m].
    '''

    def __init__(self,simObj):
         '''
         @param groundLevel  float  default: -70.0
        the depth of an ocean [m] that is limited by the value of -70 [m].
        '''
        self.simObj = simObj
        self.oceanSurface = 0
        self.oceanDepth = -70
        self.activeMovement = True 
        self.visible        = True 
        self.absPosition = np.array([2,1,-7.0]) # needs to be taken from partcile class in turbidity 
        self.waterCurrent = np.array([0.0,2.0,0.0]) # just a simple example will be changed later 
        self.waterCurrentMode = 'static'

    def getWaterCurrent(self):
        """
        should be defined as moving vector (x.y.z) which should change dependent on position in 3D world ? 
        dependen on all 3 dimensions ? 
        look for waterCurrent values in paper ??
        """

        if self.waterCurrentMode == 'static':
            return self.waterCurrent
        elif self.waterCurrentMode == 'interp':
            return self.interpolateCurrent()
        else:
            print('This should be a real error / unkown mode')
    
    def interpolateCurrent(self):
    #  WorldCoordinates:
    #  x = np.array(-1000,1000,0,1) from -1000m to 1000 m in 10cm steps
    #  y = np.array(-1000,1000,0,1)
    #  edges of coordinate system beeing (-1000,-1000),(-1000,1000),(1000,-1000),(1000,1000)
    #  waterCrurenCoordinates:
    #  watercurrent at the edges beeing  
    #  (2,-1),(2,-2),(1,-1),(1,-2)
    #  x = np.array(2,1,0.1)
    #  y = np.array(-1,-2,0.1)
    
    from scipy import interpolate
    x = np.arange(-1000,1000,0,1)
    y = np.arange(-1000,1000,0,1)
    xx, yy = np.meshgrid(x, y)
    z = np.sin(xx**2+yy**2)
    f = interpolate.interp2d(x, y, z, kind='cubic')
    #Now use the obtained interpolation function and plot the result:
    #
    xnew = np.arange(2,1,0.1)
    ynew = np.arange(-1,-2,0.1)
    znew = f(xnew, ynew)
    plt.plot(x, z[0, :], 'ro-', xnew, znew[0, :], 'b-')
    plt.show()

    def creatObstacles(self,parObj):
    """
    this function is creating specific Obstacles representing rectangluar colums from oceanDepth to oceanSurface
    for now this is manually defined and only consists of one single Obstacle. Would need to be multplied to list 
    of obstacles. --> checkActiveMovement function und SealStateCheck need to take all obstacles into account ? HOW? 
    
    make two lists:
    obstacle list 
    checkobstacle list
    """
    obstacle[x,y,r,ri]

    r =  2 #radius of the object / objectMagnitute
    ri =  r -0.1 #inner invisible radius of object
    op = np.array([1,2])  #center of the object defined by x and y  
    m = np.linalg.norm(parObj.absPosition[0,1]-op)    
    # if clause placed in check visbility and check Active Movement ? how does this work for several Obstacles 
    # if m > r :
    #     visible == True and activeMovement == True 
    # elif m < ri :
    #     visible == False and activeMovement == False 
    # else:
    #     visibile == True and activeMovement == False
    
    def checkVisibility(self,parObj):
       """
       The 'checkVisibility' function checks if position of particle is inside of a visual field of 
       a seal. Particles are not visible above 0 [m] and below -70,0 [m] (z axis or absPosition[2]), 
       and if their position is same as a position of obstacle. 
       """
       if parObj.absPosition[2] >= self.oceanSurface or parObj.absPosition[2] <= self.oceanDepth-0.1: # how to get self.absoultePosition from turbidity.particles ? or does it go the other way ? 
           parObj.visible = False
       else: 
           parObj.visible = True
           for obstacle in self.obstacleList:
               particleObstacleDist = np.linalg.norm(parObj.absPosition[0:2]-obstacle[0:2]) 
               if particleObstacleDist < obstacle[3]:
                    parObj.visible = False

           


    def checkActiveMovement(self,parObj): 

        """
        The checkActiveMovement function defines which particles are moving and which are stationary.
        Those particles with a self.position[2](z value) between -70[m] and -70.1[m] are stationary. 
        Those that are between 0 and -70[m] are moving according to the randomWalk function. Also, particles
        which position is the same as position of obsticles are not moving. 
        """
        if self.visible == True:
            if parObj.absPosition[2]<= self.oceanDepth:
                self.activeMovement = False
            else: 
                self.activeMovement = True
                particleObstacleDist = np.linalg.norm(parObj.absPosition[0:2]-obstacle[0:2]) 
               if particleObstacleDist <= obstacle[2]:
                    parObj.activeMovement = False
        else:
            self.activeMovement = False  
           
    def particleStateCheck(self,parObj):

        """
        The particleStateCheck function calls the information for the visibility and active movement
        state of the particle.
        """
        ### for particles in ParticleObjectList() for loop calling turbidity funciton ? 
        self.checkVisibility(parObj)
        self.checkActiveMovement(parObj)

    def SealStateCheck(self, sealObj):

        ### for sealPosition in Seal_agend ??? 
        if self.sealPosition[2] > 0 or self.sealPosition[2] <= -70 or self.left <= self.sealPosition[0] <= self.right and self.front <= self.sealPosition[1] <= self.back:
            self.activeSealMovement = False
            #seal steps needs to go down (self.sealStep[2])
        else:
            self.activeSealMovement == True
    
