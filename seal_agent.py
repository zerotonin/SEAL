import numpy as np
import copy
class Seal: 
    def __init__(self,simObj):

        self.simObj = simObj
        self.sealPosition = np.zeros(shape = 3) #centre of the coordinate system of the Seal in disctance to (0,0,0) of world
        self.sealOrientation = np.zeros(shape = 3)  # orientation as yaw pitch roll
        self.sealStep = np.zeros(shape =6) # change of position and orientation
        self.sealTrajectory = list()
        self.activeSealMovement = True

    def print(self):
        return 'Hello World'

    def SealStateCheck(self):
        if self.sealPosition[2] > 0 or self.sealPosition[2] <= -70:
            self.activeSealMovement = False
            #seal steps needs to go down (self.sealStep[2])
        else:
            self.activeSealMovement == True
    

    def createSealStep(self,mode):
        if mode == 'random':
            self.createRandomStep()
        elif mode == 'straightDown':
            self.sealStep = np.array([0.,0.,-10.0,0.,0.,0.])
        elif mode == '45down':
            self.sealStep = np.array([5.0,0.,-5.0,0.,0.,0.])
        else:
            print('Unkown step type: ' + mode)

    def createRandomStep(self):
        sealStepCoordinates = np.random.uniform(-5,5,size = (3)) #randomly choosen stepSize 
        sealStepOrientation = np.random.uniform(0,np.pi*2,size = (3)) #ramdomly chooses orientation of step 
        self.sealStep = np.concatenate((sealStepCoordinates, sealStepOrientation), axis=None)
        

    def MoveSeal(self): # function to simulate dive (series of seal trajectories)
        """
        this function should safe a sealTrajectory list listing all endPosition after each sealStep for a single dive
        in correct order. sealStep holding information for x,y,z direction of vector as well as
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


###########################################
#the newly created self.sealStep needs to be inherited by the particle  class or Cloud class to run the particleMovement #function 
###########################################