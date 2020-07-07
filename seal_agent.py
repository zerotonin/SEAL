import numpy as np
import copy
class Seal: 
    """
    the seal class holds informations about the seal agent in the 3D cartisian world, simulating 
    the ocean. It holds infomation about the seals position, orientation,and it active movement, 
    defined by habor seal typical trajectories taken from video data.
    """
    def __init__(self,simObj):

        self.simObj = simObj
        self.sealPosition = np.zeros(shape = 3) #centre of the coordinate system of the Seal in disctance to (0,0,0) of world
        self.sealOrientation = np.zeros(shape = 3)  # orientation as yaw pitch roll
        self.sealStep = np.zeros(shape =6) # change of position and orientation
        self.sealTrajectory = list()
        self.activeSealMovement = True
        """
        @param simObj               string default: none
           string that gives a name: simulation object.           
        @param sealPosition         default: np.zeros(shape=3)
            seal Position gives a specifi x,y,z position for the seal 
            starting at the surface of the ocean at startPosition(0,0,0)
        @param sealOrientation      default: np.zeros(shape=3)
            orientation is defined by three values between 0 and 2pi 
            decribing pitch, yaw and roll ? 
        @param sealStep             default: np.zeros(shape=6)
            sealstep is defined by a movingVector of the agendt
            with x,y,z beeing between -5 and 5 and and 
            the respective sealOrientation values
        @param sealTrajectory       list default: none
            a list saving the sealPosition and sealOrientation for each sealStep
        @param activeSealMovement   bool default: True 
            the seal agend is actively moving while below the oceanSurface(z=0)
            and the oceanFloor(-70)
        """
    def SealStateCheck(self):
        """
        the SealStateCheck checks the position of the seal. Only if the position 
        is within the watercolum of the ocean the activeSealMovement bool is True. 
        This is needed to imply active movement of the seal agent.
        """
        if self.sealPosition[2] > 0 or self.sealPosition[2] <= -70:
            self.activeSealMovement = False
            #seal steps needs to go down (self.sealStep[2])
        else:
            self.activeSealMovement == True
    

    def createSealStep(self,mode):
        """
        In order to ensure a divepattern, starting at the ocean surface, going down, and 
        goingt up again ending at the surface again three differen sealSteps are define.
        To test we definde a straight down dive and a 45down dive. otherwise the sealSteps
        will be randomly defined with the x y z values beeing limited between-5 and 5 m.
        This will be change later to connect it to haborSealDiveData to simulate real 
        seal like steps.
        """
        if mode == 'random':
            self.createRandomStep()
        elif mode == 'straightDown':
            self.sealStep = np.array([0.,0.,-10.0,0.,0.,0.])
        elif mode == '45down':
            self.sealStep = np.array([5.0,0.,-5.0,0.,0.,0.])
        else:
            print('Unkown step type: ' + mode)

    def createRandomStep(self):
        """
        creating random sealStep consisting of randomly choosen StepCoordinates x,y,z 
        beeing limited betweem -5 and 5m, defining the direction and lenght of the step,
        AND randomly choosen orientation of the seal during this step defines by yaw pitch
        and roll values beeing limited to 0 to 2pi.
        """
        sealStepCoordinates = np.random.uniform(-5,5,size = (3)) #randomly choosen stepSize 
        sealStepOrientation = np.random.uniform(0,np.pi*2,size = (3)) #ramdomly chooses orientation of step 
        self.sealStep = np.concatenate((sealStepCoordinates, sealStepOrientation), axis=None)
        

    def MoveSeal(self): # function to simulate dive (series of seal trajectories)
        """
        this function should safe a sealTrajectory list listing all endPosition after each sealStep for a single dive
        in correct order. sealStep holding information for x,y,z direction of MovingVector as well as
        yaw,pitch,roll (orientation of the seal)
        """    
        if self.activeSealMovement == True:

            
        
            #self.sealPosition = self.sealPosition+self.sealStep[0:3]
            self.sealPosition += self.sealStep[0:3] # new Seal Position after one sealStep/Movement
            SealPosition = copy.deepcopy(self.sealPosition)
            self.sealOrientation += self.sealStep[3:6] # new sealOrientation after each sealStep (should be the same as during the   step?)
            SealOrientation = copy.deepcopy(self.sealOrientation)

            print(self.sealStep,SealPosition,SealOrientation)
            print("=======================================================")

            self.sealTrajectory.append((SealPosition,SealOrientation))
        else :
            self.activeSealMovement = False
