import numpy as np
import copy, csv, random
from utilities import mathUtils
class Seal: 
    """
    The seal class holds informations about the seal agent in the 3D cartisian world, simulating 
    the ocean. It holds infomation about the seals position, orientation,and it active movement, 
    defined by habor seal typical trajectories taken from video data.
    """
    def __init__(self,simObj):
        """
        @param simObj                       string default: none
           string that gives a name: simulation object.   
        @param mathUtils            utilities.mathUtils
            shortcut for the mathUtils class in utilities.py   

        @param sealPosition                 default: np.zeros(shape=3)
            seal Position gives a specifi x,y,z position for the seal 
            starting at the surface of the ocean at startPosition(0,0,0)
        @param sealOrientation              default: np.zeros(shape=3)
            orientation is defined by three values between 0 and 2pi 
            decribing pitch, yaw and roll  
        @param sealStep                  default: np.zeros(shape=6)
            sealstep is defined by a movingVector of the agent
            with x,y,z  and the respective sealOrientation values
        @param sealTrajectory            list default: none
            a list saving the sealPosition and sealOrientation for each sealStep

        @param activeSealMovement           bool default: True 
            the seal agend is actively moving while below the oceanSurface(z=0)
            and the oceanFloor(-70)
        @param trajectoryRecording          bool default: False
            Since the Seal Trajectory is allready simulated and saved in the protoMove
            class the recording of the identical seal trajectory within the seal agent
            class is set to false in order to make the simulation faster. 
        """
        # objects from other classes
        self.simObj                 = simObj
        self.mathUtils              = mathUtils()
        # public objects
        self.sealPosition           = simObj.runTimeData.getParameter('sealPosition') #centre of the coordinate system of the Seal in disctance to (0,0,0) of world
        self.sealOrientation        = simObj.runTimeData.getParameter('sealOrientation')  # orientation as yaw pitch roll
        self.sealStep               = simObj.runTimeData.getParameter('sealStep') # change of position and orientation
        self.sealTrajectory         = simObj.runTimeData.getParameter('sealTrajectory') # public
        # private objects
        self.activeSealMovement     = True
        self.trajectoryRecording    = False # usually set to false as the protMov class already creates an entire trajectory

    def SealStateCheck(self):
        """
        the SealStateCheck checks the position of the seal. Only if the position 
        is within the watercolum of the ocean the activeSealMovement bool is True. 
        This is needed to imply active movement of the seal agent.
        """
        if self.sealPosition[2] > 0 or self.sealPosition[2] <= -70:
            self.activeSealMovement = False
        else:
            self.activeSealMovement = True

    def testCreateSealStep(self,mode):
        """
        This function creats basic seal steps to test the simulation.
        In order to ensure a divepattern, starting at the ocean surface, going down, and 
        goingt up again ending at the surface again three differen sealSteps are defined.
        To test we definde a straight down dive and a 45down dive. otherwise the sealSteps
        will be randomly defined with the x y z values beeing limited between-5 and 5 m.
        This will be change later to connect it to haborSealDiveData to simulate real 
        seal like steps.
        """
        if mode == 'random':
            self.testCreateRandomStep()
        elif mode == 'straightDown':
            self.sealStep = np.array([0.,0.,-10.0,0.,0.,0.])
        elif mode == '45down':
            self.sealStep = np.array([5.0,0.,-5.0,0.,0.,0.])
        else:
            print('Unkown step type: ' + mode)

    def testCreateRandomStep(self):
        """
        Creating random sealStep consisting of randomly choosen StepCoordinates x,y,z 
        beeing limited betweem -5 and 5m, defining the direction and lenght of the step,
        AND randomly choosen orientation of the seal during this step defines by yaw pitch
        and roll values beeing limited to 0 to 2pi.
        this function was used to test the other parametwer of the simulation throughout the 
        creation.
        """
        sealStepCoordinates = np.random.uniform(-5,5,size = (3)) #randomly choosen stepSize 
        sealStepOrientation = np.random.uniform(0,np.pi*2,size = (3)) #ramdomly chooses orientation of step 
        self.sealStep = np.column_stack((sealStepCoordinates, sealStepOrientation))#random combination of translational and rotational trajectories
        
        print(len(self.sealStep))   
        print(self.sealStep)     

    def MoveSeal(self): # function to simulate dive (series of seal trajectories)
        """
        This function moves the seal in the world coordinate system dependen on its 
        active state. For each step the sealPosition and orientation is saved in 
        the sealTrajectory list.
        """    
        self.SealStateCheck()
        
        if self.activeSealMovement == True:
            #update position, orientation, and step
            self.sealPosition = self.simObj.runTimeData.getParameter('sealPosition')
            self.sealOrientation = self.simObj.runTimeData.getParameter('sealOrientation')
            self.sealStep = self.simObj.runTimeData.getParameter('sealStep')
            # calculate m/s to m/sample
            presentStep = self.simObj.meterPerSecond2meterPerSample(self.sealStep)
            
            self.sealPosition += self.mathUtils.agentBasedVels2worldBasedCoords(presentStep[0:3],self.sealOrientation,'3D') # new Seal Position after one sealStep/Movement
            self.simObj.runTimeData.setParameter('sealPosition', self.sealPosition)
            self.sealOrientation += presentStep[3:6] # new sealOrientation after each sealStep (should be the same as during the   step?
            self.simObj.runTimeData.setParameter('sealOrientation', self.sealOrientation)
            
            SealOrientation = copy.deepcopy(self.sealOrientation)
            SealPosition = copy.deepcopy(self.sealPosition)
            
            if self.trajectoryRecording == True:            
                self.sealTrajectory =np.vstack((self.sealTrajectory,np.hstack((SealPosition,SealOrientation))))
                self.simObj.runTimeData.setParameter('sealTrajectory',self.sealTrajectory)
        else :
            self.activeSealMovement = False
