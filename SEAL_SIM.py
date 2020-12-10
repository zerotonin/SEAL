import turbidity, seal_agent,copy,environment,utilities,protoMov,runTimeData
from tqdm import tqdm
import numpy as np

class SEAL_SIM:
    """
    Class 'SEAL_SIM' connects all other classes to run the simulation. As masterregulator it
    sets the user parameters for the simulation and runs the simulation accordingly. As
    an output it saves a sealVelTra list with the trajectroies of the seal-agent throughout the 
    dive simulation and the simulation parameter dictionary saving all usere settings for the simulation
    """
    def __init__(self):
        """
        This function initialises the sample per seconds,and connects the environment class, 
        the particle class, the particle cloud class , the seal agent class and the protoMov class,
        in order to transfor all important information between the classes to simulate a seal dive 
        and gain information about the optic flow perception at any point during the dive.

        @param simParameterDict     dict  
            creates a Dictionary with default values for the type of dive (u or v shape), 
            the dive duration, the current type (static or interpolated), the depth of the ocean,
            the amount of obstacles, maximal number of particles beeing simulated, size range of 
            theses particles and the radius of the particle cloud.
        @param sps                  float default: none
            defines the number of samples simulated per second
        @param environment          ? default: none
            creates a shortcut to the environment class stored in 
            environment.py
        @param seal                 ? default: none
            creates a shortcut to the Seal class stored in 
            seal_agent.py
        @param pCloud               ? default: none
            creates a shortcut to the Cloud class stored in 
            turbidity.py
        @param plot                 ? default: True
            creates a shortcut to the plotUtils class stored in 
            utilities.py
        @param math                 ? default: True
            creates a shortcut to the mathUtils class stored in 
            utilities.py
        @param protoMove             ? default: ?
            creates a shortcut to the protoMov class stored in 
            protomov.py
        @param sealVelTra           ? default:none
            the created seal trajectories in the protomov class are stored in a list
        """
        # public objects
        self.simParameterDict = {'sps'               : 20,
                                 'diveType'          : 'vShape', # description and unit if av
                                 'durSec'            : 240, # duration of the simulation in seconds
                                 'currentType'       : 'static',
                                 'currentStaticVel'  : (0.0,2.0,0.0),
                                 'oceanDepth'        : -70,
                                 'amountOfObstacles' : 100,
                                 'max_particles'     : 270,
                                 'particleSizeRange' : (.00002,0.00016),
                                 'cloudRadius'       : 0.0018, 
                                 }
        self.sps         = 20 # samples per second
        # objects from other classes
        self.environment = environment.environment(self) # velocity in meter per second will be transformed into an evironment object
        self.seal        = seal_agent.Seal(self)
        self.pCloud      = turbidity.Cloud(self)
        self.pCloud.add_particles()
        self.plot        = utilities.plotUtils()
        self.math        = utilities.mathUtils()
        self.protoMove   = protoMov.ProtMov(self)
        self.runTimeData = runTimeData.runTimeData(self)
        # private?
        self.sealVelTra = list()
        
    def meterPerSecond2meterPerSample(self,velocity):
        """
        This function calculates the velocity per sample with the velocity per second,
        to be used for the  

        @return velocity per sample
        """
        # THis function should be inherited
        return copy.deepcopy(np.array(velocity)/self.sps)
    
    #def simulate_sample(self):
    #    """
    #    can be deleted ? wAS JUST TO TRY THE SIMULATION
    #    """
    #    # create a step
    #    self.seal.createSealStep('45down')
    #    print(self.seal.sealStep)
    #    # move da particles
    #    self.pCloud.moveParticles()
    #    for po in self.pCloud.partclObjList:  
    #        print(po.position)
    #    # move da seal
    #    self.seal.MoveSeal()

    def runSimulation(self):
        """
        This function initiates the simulation to run. 
        
        It calls the setParameters function to set the environment and the particle cloud. 
        Next it creates the obstacles in the environment class according to the user setting.
        It generates seal trajectories to simulate a typical seal dive and saves 
        them in the sealVelTra list. for each step of the seal agent the particles
        in the particle Cloud are moving in the opposite direction and the particle positons 
        are saved.
        """
        #set environment and particle cloud
        self.setParameters()
        self.environment.creatObstacles() #create obstacle if maxObsticales >0
        #get trajectory
        self.protoMove.generator2()
        # set the seal class to the trajectories of the protoMove class
        self.sealVelTra = self.protoMove.velTra # steps needed for movement
        self.seal.sealTrajectory  = self.protoMove.posTrajectory # save trajectory to avoid trajectory recording by seal class
        self.seal.sealPosition    = copy.deepcopy(self.protoMove.posTrajectory[0,0:3]) # get initial value
        self.seal.sealOrientation = copy.deepcopy(self.protoMove.posTrajectory[0,3:])  # get initial value
        #run trajectory through particle cloud
        for step in tqdm(self.sealVelTra,'running simulation'):
            # get a step from the step trajectory
            self.seal.sealStep = step
            # at this time point the seal has its old position but a new step
            # so let's move the particles accordingly
            self.pCloud.moveParticles()
            # move the seal to new position
            self.seal.MoveSeal()
            # check if the seal left the environment
            if self.seal.activeSealMovement == False:
                print("Seal left simulation environment! o.O")
                break
        print(self.protoMove.posTrajectory[0,:])

    def userDefParametersCLI(self):
        """
        This function opens a command line interface, asking the user to set 9 parameters,
        which are a needed to simulate specified seal dives.

        1. diveType, choosing between vShape and uShape dives
        2. dive duration, defining the duration of the dive in seconds
        3. currentType, choosing between static or interpolated currents
        4. currentStaticVal, defining x,y,and z velocities for static currents
        5. oceanDepth, setting the depth of the ocean
        6. amount of Obstacles, setting the number of obstacles simulated in the enviornment
        7. max_Particles, setting the number of particles simulated in the particleCloud
        8. particleSizeRange, setting the lower and upper limits for the size of particles in mm ?
        9. cloudRadius, setting the Radius of the particleCloud surrounding the seal_agent
        Next, it sets the user defined parameters in the specidifc classes, needed for the 
        simulation.
        """
        self.simParameterDict['sps']               = float(self.CLI_dialg_num('Set SPS', '20'))
        self.simParameterDict['diveType']          = self.CLI_dialg_choiceText('What dive Type schould be simulated ?', 'vShape', ['uShape','vShape'])
        self.simParameterDict['durSec']            = float(self.CLI_dialg_num('How long should the dive simulation last?', '240'))    
        self.simParameterDict['currentType']       = self.CLI_dialg_choiceText('What kind of current should be simulates? ', 'static', ['static','interp'])
        if self.simParameterDict['currentType'] == 'static':
            current_X = float(self.CLI_dialg_num('Set x-velocity in m/s:','0.0'))
            current_Y = float(self.CLI_dialg_num('Set y-velocity in m/s:','2.0'))
            current_Z = float(self.CLI_dialg_num('Set z-velocity in m/s:','0.0'))
            self.simParameterDict['currentStaticVel'] = (current_X,current_Y,current_Z)
        else:
            # add standard cases after intial tests
            print("For the interpolated type, you need to define the different currents in a tetraheder or choose one of the standard cases")
        self.simParameterDict['oceanDepth']        = float(self.CLI_dialg_num('Set a depth of the oceans', '-70'))
        self.simParameterDict['amountOfObstacles'] = int(self.CLI_dialg_num('How many obstacle should be simulates in the environment? ', '100'))
        self.simParameterDict['max_particles']     = int(self.CLI_dialg_num('How many particles should be simulates in the particleCloud? ', '270'))
        self.simParameterDict['particleSizeRange'] = (float(self.CLI_dialg_num('Set smallest Particle Size', '.00002')), float(self.CLI_dialg_num('Set biggest Particel Size', '0.00016')))
        self.simParameterDict['cloudRadius']       = float(self.CLI_dialg_num('Set radius of the Cloud', '0.0018'))
     
        print(self.simParameterDict)
        self.setParameters()

    def setParameters(self):
        """
        This function sets the user defined parameter to the according parameters in the different classes
        needed to run the simulation
        """
        self.sps                          = self.simParameterDict['sps']
        self.protoMove.mode               = self.simParameterDict['diveType']
        self.protoMove.traLenSec          = self.simParameterDict['durSec']
        self.environment.waterCurrentMode = self.simParameterDict['currentType']
        if self.simParameterDict['currentType'] == 'static':
            self.environment.waterCurrent     = self.simParameterDict['currentStaticVel']
        self.environment.oceanDepth       = self.simParameterDict['oceanDepth']
        self.environment.maxObstacles     = self.simParameterDict['amountOfObstacles']
        self.pCloud.max_particles         = self.simParameterDict['max_particles']
        self.pCloud.sizeRange             = self.simParameterDict['particleSizeRange']
        self.pCloud.maxVectorMagnitude    = self.simParameterDict['cloudRadius']

    def setParametersInRunTimeData(self):

        self.runTimeData.setParameter('sps', float(self.CLI_dialg_num('Set SPS', '20')))
        self.runTimeData.setParameter('diveType',self.CLI_dialg_choiceText('What dive Type schould be simulated ?', 'vShape', ['uShape','vShape']))
        self.runTimeData.setParameter('durSec',float(self.CLI_dialg_num('How long should the dive simulation last?', '240')))    
        self.runTimeData.setParameter('currentType',self.CLI_dialg_choiceText('What kind of current should be sim)ulates? ', 'static', ['static','interp']))
        if self.runTimeData.currentType == 'static':
            current_X = float(self.CLI_dialg_num('Set x-velocity in m/s:','0.0'))
            current_Y = float(self.CLI_dialg_num('Set y-velocity in m/s:','2.0'))
            current_Z = float(self.CLI_dialg_num('Set z-velocity in m/s:','0.0'))
            self.runTimeData.setParameter('currentStaticVel', (current_X,current_Y,current_Z))
        else:
            # add standard cases after intial tests
            print("For the interpolated type, you need to define the different currents in a tetraheder or choose one of the standard cases")
        self.runTimeData.setParameter('oceanDepth',float(self.CLI_dialg_num('Set a depth of the oceans', '-70')))
        self.runTimeData.setParameter('amountOfObstacles',int(self.CLI_dialg_num('How many obstacle should be simulates in the environment? ', '100')))
        self.runTimeData.setParameter('max_particles',int(self.CLI_dialg_num('How many particles should be simulates in the particleCloud? ', '270')))
        self.runTimeData.setParameter('particleSizeRange',(float(self.CLI_dialg_num('Set smallest Particle Size', '.00002')), float(self.CLI_dialg_num('Set biggest Particel Size', '0.00016'))))
        self.runTimeData.setParameter('cloudRadius',float(self.CLI_dialg_num('Set radius of the Cloud', '0.0018')))
        
    def CLI_dialg_choiceText(self,question,default = False,answers=["yes","no"]):
        """
        This function creates a command line interface for the user to choose between text choice.

        @return text choice answer of the user 
        """

        userAnswer = self.CLI_quest(question,answers,default)
        while userAnswer not in answers:
            print(str(userAnswer) + " unrecognised, please answer with: " + str(answers))
            userAnswer = self.CLI_quest(question,answers,default)
        return userAnswer
    
    def CLI_dialg_num(self,question,default = False):
        """
        This function creates a command line interface for the user to choose any number.

        @return number choosen by the user
        """
        userAnswer = self.CLI_quest(question,[],default)
        while userAnswer.strip('-').replace('.','',1).isdigit() ==False:
            print(str(userAnswer) + " unrecognised, this is not a number")
            userAnswer = self.CLI_quest(question,[],default) 
        return userAnswer

    def CLI_quest(self,question, answers,default):
        """
        This function defines the command line interface to set the parameters.

        @return the answer typed in the command line by the user
        """

        if default != False:
            userAnswer = input(question + " [" + str(answers) +" | default: "+ str(default)+"] :")
            if userAnswer == "":
                userAnswer = default
        else:
            userAnswer = input(question + " [" + str(answers)+ "] :")

        return userAnswer




