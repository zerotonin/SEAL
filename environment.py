import numpy as np 
from scipy.interpolate import RegularGridInterpolator
#from scipy import interpolate

class environment:
    '''
    The 'Environment' class contains functions that are used for creating ocean' enviroment where particles are
    moving in the visual field of a seal. Seal is the center of particles' cloud in cartesian space. The depth 
    limit of the ocean is -70 m. Ocean in the environment contains obstacles that should be bypassed by the seal.
    The obstacle is surrounded by visible but inactive particles and the core of the obstacle - invisible and 
    inactive particles
    '''

    def __init__(self,simObj):

        '''
        @param groundLevel  float  default: -70.0
        the depth of an ocean [m] that is limited by the value of -70 [m].

        
        This function initializes the simulation of ocean. Where upper and lower bondaries are limited by the 
        depth of -70[m]. Inside if the ocean seals are places. Seals are centers of clouds with particles 
        that are moved by brownian motion and water current. 
        @param simObj     str default: none
        the name of the environment simulation.
        @param oceanSurface    float default: 0.0
        the upper limit of the ocean's surface [m]
        @param oceanDepth      float default: -70.0
        the lower bottom limit of the ocean - 70 [m]
        @param activeMovement  bool default: True
           defines boundaries of the ocean' space, where partciles move actively. 
           Active movement of particles is true for ocean depth with the limit - 0 [m] to -70 [m],
           and true when particles are not in the area of obstacle.
        @param visible         bool default: True
           particles are visible in the water for seal, and form opic flow. They are not
           visible above 0 [m] and below -70,1 [m] and if their position is same as a position of obstacle.
        @ param absPosition array default: none
           the absolute space position in the cartasian system coordinate in the ocean, x,y,z.
        @ param waterCurrent  array default: none
           the position of a water current in the space of an ocean.
        @ param waterCurrentMode srt default: none
          the state of the water current in the ocean.         
        '''
        self.simObj = simObj #name
        self.oceanSurface = 0 # [m]
        self.oceanDepth = -70 # [m]
        self.oceanLimit = (-70,70) # [m]
        self.activeMovement = True 
        self.visible        = True 
        self.absPosition = np.array([2,1,-7.0]) # needs to be taken from partcile class in turbidity 
        self.waterCurrent = np.array([0.0,2.0,0.0]) # just a simple example will be changed later 
        self.waterCurrentMode = 'static'
        self.obstacleList = []
        self.observableObstacleList = []

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
    

    def setCurrents(self,currents= np.zeros(shape=(8,3))):
        
        # data matrix for interpolation

        for i in range(0,3):
            # initialise 4D matrix in which the three components
            # of a current force are divide other the fourth dimension.
            # Hence the first dimension represent thrust, the second slip
            # and the third lift. The first three dimensions represent 
            # the edges of our environment with the lower left hind 
            # corner being [0,0,0].
            data=np.zeros(shape=(2,2,2,3))

            data[0][0][0][i] = currents[0,i]
            data[1][0][0][i] = currents[1,i]
            data[0][1][0][i] = currents[2,i]
            data[1][1][0][i] = currents[3,i]
            data[0][0][1][i] = currents[4,i]
            data[1][0][1][i] = currents[5,i]
            data[0][1][1][i] = currents[6,i]
            data[1][1][1][i] = currents[7,i]

        # supportVectors
        x = np.array([self.oceanLimit[0],self.oceanLimit[1],self.oceanLimit[0],self.oceanLimit[1],self.oceanLimit[0],self.oceanLimit[1],self.oceanLimit[0],self.oceanLimit[1]]) 
        y = np.array([self.oceanLimit[0],self.oceanLimit[0],self.oceanLimit[1],self.oceanLimit[1],self.oceanLimit[0],self.oceanLimit[0],self.oceanLimit[1],self.oceanLimit[1]]) 
        z = np.array([self.oceanDepth,self.oceanDepth,self.oceanDepth,self.oceanDepth,self.oceanSurface, self.oceanSurface,self.oceanSurface, self.oceanSurface])

        self.waterCurrentFunc =(RegularGridInterpolator((x.sort(), y.sort(), z.sort()), data[0]),RegularGridInterpolator((x, y, z), data[1]),RegularGridInterpolator((x, y, z), data[2]))
    
    def getWaterCurrent_interp(self):

        pos = self.simObj.sealPosition
        self.waterCurrent = np.array([self.waterCurrentFunc[0](pos[0],pos[1],pos[2]),
                                      self.waterCurrentFunc[1](pos[0],pos[1],pos[2]),
                                      self.waterCurrentFunc[2](pos[0],pos[1],pos[2])])
    

    def interpolateCurrent(self):
        """
        WorldCoordinates:
        (-1000,-1000,0),(-1000,1000,0),(1000,-1000,0),(1000,1000,0)
        (-1000,-1000,-70),(-1000,1000,-70),(1000,-1000,-70),(1000,1000,-70)
        
        """
        self.setCurrents()
        self.getWaterCurrent_interp()
    
        

    def creatObstacles(self):
        """
        this function is creating specific Obstacles representing circular colums from oceanDepth to oceanSurface

        obstacle(initialCoord[x,y],r,ri)
        """
    
        self.maxObstacles = 200
        
        while len(self.obstacleList)<self.maxObstacles:
               obstacle = self.randomInit() # get random x,y,radius and innerradius
               self.obstacleList.append(obstacle) # initialise obstacles(initialCoord[x,y],r,ri) and add to list

    def randomInit(self):
        """
        The 'randomInit' function returns a list of random sized obstacles within a size range 
        of 10cm to 10m radius.
        And in returns 'initialCoord' as a random vector (x,y) with a range from -5000m to 5000m
        """  
        radius = np.random.uniform(0.1,10.0, size=(1)) # set size to 10cm to 10m radius
        initialCoord = np.random.uniform(-5000,5000,size = (2)) # random vector (x,y,) from -5km to 5km 
        return (initialCoord,radius,radius-0.1)

    def checkObstacleDistance(self):
        """
        this function checks if the obstacles is in sight of the seal. Only if the magnitute from the obstacle to the seal
        subtracktd by the radius of the obstacle and the radius of the particleCloud is < 0 the obstacle is in sight 
        of the seal and therefore needs to be checked for visibility and active movement 
        """
        for obstacle in self.obstacleList:
            if np.linalg.norm(self.simObj.seal.sealPosition[0:2]-obstacle[0])- self.simObj.pCloud.maxVectorMagnitue- obstacle[1] < 0:
                self.observableObstacleList.append(obstacle)
    
    def checkVisibility(self,parObj):
        """
        The 'checkVisibility' function checks if position of particle is inside of a visual field of 
        a seal. Particles are not visible above 0 [m] and below -70,0 [m] (z axis or absPosition[2]), 
        and if their position is witin the inner radius of an obstacle in sight of the seal. 
        """
        if parObj.absPosition[2] >= self.oceanSurface or parObj.absPosition[2] <= self.oceanDepth-0.1: # how to get self.absoultePosition from turbidity.particles ? or does it go the other way ? 
            parObj.visible = False
        else: 
            parObj.visible = True
            for obstacle in self.observableObstacleList:
                particleObstacleDist = np.linalg.norm(parObj.absPosition[0:2]-obstacle[0]) #obstale[0] = (x,y)
                if particleObstacleDist < obstacle[2]: #obstacle[2] = inner radius
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
                for obstacle in self.observableObstacleList:
                    particleObstacleDist = np.linalg.norm(parObj.absPosition[0:2]-obstacle[0]) #obstale[0] = (x,y) 
                    if particleObstacleDist <= obstacle[1]: #obstacle[1] = radius
                        parObj.activeMovement = False
        else:
            self.activeMovement = False  
           
    def particleStateCheck(self,parObj):
        """
        The particleStateCheck function calls the information for the visibility and active movement
        state of the particle.
        """
        self.checkVisibility(parObj)
        self.checkActiveMovement(parObj)

    def SealStateCheck(self, sealObj):
        """
        the sealStatecheck function defines activeSealMovement to be true or false. Only those sealpositions
        that have a activeSealMovement will be activly moved in the sealAgend class.
        The Seals active movement is false if the agends is above water or below the seafloor or within an 
        obstacle.
        The possibility for this movements ending in such a position needs to be impossible. HOW ? 

        """
        if sealObj.sealPosition[2] >= self.oceanSurface or sealObj.sealPosition[2] <= self.oceanDepth:
            sealObj.activeSealMovement = False
            #seal steps needs to go down (self.sealStep[2])
        else:
            sealObj.activeSealMovement == True
            sealObstacleDist = np.linalg.norm(sealObj.position[0:2]-obstacle[0])
            if sealObstacleDist <= obstacle[1]:
                sealObj.activeSealMovement == False 
    
