import numpy as np 
from scipy.interpolate import RegularGridInterpolator
import math as m
#from scipy import interpolate

class environment:
    '''
    The 'Environment' class contains functions that are used for creating ocean' enviroment where particles are
    moving in the visual field of a seal. Seal is the center of particles' cloud in cartesian space. The default 
    depth limit of the ocean is -70 m. Ocean in the environment contains obstacles that should be bypassed by the seal.
    The obstacle is surrounded by visible but inactive particles and the core of the obstacle - invisible and 
    inactive particles
    '''

    def __init__(self,simObj):
        '''
        This function initializes the simulation of an 3D ocean, where upper and lower bondaries are limited by 
        0 and the oceanDepth[m]. Within the ocean coordinate system the seal is simulating a dive.
        During the simulation the Seal is the constant centers of the particle Cloud. 
        
        @param simObj                   str default: none
            the name of the environment simulation.
        @param oceanSurface             float default: 0.0
            the upper limit of the ocean's surface [m]
        @param oceanDepth               float default: -70.0
            the lower bottom limit of the ocean - 70 [m]
        @param oceanLimit               list default: (-70[m],70[m])
            the limitation of the coordinate system for x and y dimension
        @param activeMovement           bool default: True
            defines boundaries of the ocean' space, where partciles move actively. 
            Active movement of particles is true for ocean depth with the limit - 0 [m] to -70 [m],
            and true when particles are not in the area of obstacle.
        @param visible                  bool default: True
            particles are visible in the water for seal, and form opic flow. They are not
            visible above 0 [m] and below -70,1 [m] and if their position is same as a position of obstacle.
        @ param waterCurrent            array default: none
            the position of a water current in the space of an ocean.
        @ param waterCurrentMode        str default: none
            the state of the water current in the ocean.  
        @param obstacleList             list default: none
            list of obstacles within the ocean environment
        @param observableObstacleList   list default: none       
            list of obstacles in sight of the seal agent 
        @param maxObstacles             float default: 200
            the number of obstacles to create in the ocean environment
        '''
        self.simObj                 = simObj #name
        self.oceanSurface           = 0 # [m]
        self.oceanDepth             = -70 # [m]
        self.oceanLimit             = (-70,70) # [m]
        self.activeMovement         = True 
        self.visible                = True 
        self.waterCurrent           = np.array([0.0,2.0,0.0]) # just a simple example will be changed later 
        self.waterCurrentMode       = 'static'
        self.obstacleList           = []
        self.observableObstacleList = []
        self.maxObstacles           = 200

    def getWaterCurrent(self):
        """
        This function creates a water current dependent on the waterCurrent Mode.

        If the waterCurrent Mode is static the user defined 3D waterCurrent is 
        used in order to move the particles.
        If the waterCurrent Mode is interpolated the getWaterCurrent_interp function
        is called calculating interpolated currents for the seal position for 
        each step.

        @return 3D waterCurrent 
        """
        if self.waterCurrentMode == 'static':
            return self.waterCurrent
        elif self.waterCurrentMode == 'interp':
            return self.getWaterCurrent_interp()
        else:
            print('This should be a real error / unkown mode')

    def setCurrents(self,currents= np.zeros(shape=(8,3))):
        """
        This function sets a data matrix for an interpolated
        current simulation in the ocean environment.

        It sets specific 3D current [m/s] (built out of thrust, slip and
        lift values) for every edge of the simulation (8).

               (0,0,0)-----------------(1,0,0)
                  /|                      /|
                 / |                     / |
           (0,1,0)-|---------------(1,1,0) | 
                |(0,0,1)----------------|-(1,0,1) 
                | /                     |  /
                |/                      | /
             (0,1,1)-----------------(1,1,1)    

        With a GridInterpolation this calculates interploated currents at any
        given position within the environment.
        """
        data=(np.zeros(shape=(2,2,2)),np.zeros(shape=(2,2,2)),np.zeros(shape=(2,2,2)))
        for i in range(0,3):
            # initialise 4D matrix in which the three components
            # of a current force are divide other the fourth dimension.
            # Hence the first dimension represent thrust, the second slip
            # and the third lift. The first three dimensions represent 
            # the edges of our environment with the lower left hind 
            # corner being [0,0,0].

            data[i][0][0][0] = currents[0,i]
            data[i][1][0][0] = currents[1,i]
            data[i][0][1][0] = currents[2,i]
            data[i][1][1][0] = currents[3,i]
            data[i][0][0][1] = currents[4,i]
            data[i][1][0][1] = currents[5,i]
            data[i][0][1][1] = currents[6,i]
            data[i][1][1][1] = currents[7,i]

        # supportVectors
        x = np.array([self.oceanLimit[0],self.oceanLimit[1]]) 
        y = np.array([self.oceanLimit[0],self.oceanLimit[1]]) 
        z = np.array([self.oceanDepth,self.oceanSurface])
        self.waterCurrentFunc =(RegularGridInterpolator((x, y, z), data[0]),RegularGridInterpolator((x, y, z), data[1]),RegularGridInterpolator((x, y, z), data[2]))
        self.waterCurrentMode = 'interp'

    def getWaterCurrent_interp(self):
        """
        This function calcuates the waterCurrent at the sealPosition based
        on the interpolated current matrix created in setCurrents.
        """
        pos = self.simObj.seal.sealPosition
        self.waterCurrent = np.array([self.waterCurrentFunc[0]((pos[0],pos[1],pos[2])),
                                      self.waterCurrentFunc[1]((pos[0],pos[1],pos[2])),
                                      self.waterCurrentFunc[2]((pos[0],pos[1],pos[2]))])

    def creatObstacles(self):
        """
        This function is creating specific obstacles representing circular colums 
        from oceanDepth to oceanSurface. Each obstacle hold information of 
        its position(initialCoord[x,y]), its radius (r) and inner radius(ri(r-10cm)).
        """
        while len(self.obstacleList)<self.maxObstacles:
               obstacle = self.randomInit() # get random x,y,radius and innerradius
               self.obstacleList.append(obstacle) # initialise obstacles(initialCoord[x,y],r,ri) and add to list

    def randomInit(self):
        """
        The 'randomInit' function returns a list of random sized obstacles within a size range 
        of 10cm to 10m radius.
        
        @returns 'initialCoord' as a random vector (x,y) with a range from -5000m to 5000m, radius[m] 
                  and innerRadius[m]  
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
            # it should not be maxVectorMagnitue of particle cloud but specific distance a seal could still
            # detect obstacle, 
            if np.linalg.norm(self.simObj.seal.sealPosition[0:2]-obstacle[0])- (obsatcle[1]/m.tan(0.08666666667)- obstacle[1] < 0:
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
        the sealStatecheck function defines activeSealMovement to be true or false. Only those sealPositions
        that have a activeSealMovement will be activly moved in the sealAgend class.
        The Seals active movement is false if the agends is above water or below the seafloor or within an 
        obstacle.
        """
        if sealObj.sealPosition[2] >= self.oceanSurface or sealObj.sealPosition[2] <= self.oceanDepth:
            sealObj.activeSealMovement = False
            #seal steps needs to go down (self.sealStep[2])
        else:
            sealObj.activeSealMovement = True
            sealObstacleDist = np.linalg.norm(sealObj.position[0:2]-obstacle[0])
            if sealObstacleDist <= obstacle[1]:
                sealObj.activeSealMovement = False 
                print([seal in object])
    
