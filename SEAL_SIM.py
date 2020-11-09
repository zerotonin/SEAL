import turbidity, seal_agent,copy,environment,utilities,protoMov
from tqdm import tqdm
import numpy as np

class SEAL_SIM:
    def __init__(self):
        self.sps         = 20 # samples per second
        self.environment = environment.environment(self) # velocity in meter per second will be transformed into an evironment object
        self.seal        = seal_agent.Seal(self)
        self.pCloud      = turbidity.Cloud(self)
        self.pCloud.add_particles()
        self.plot        = utilities.plotUtils()
        self.math        = utilities.mathUtils()
        self.turbidity   = turbidity
        self.protoMove   = protoMov.ProtMov(self)
        self.simParameterDict = {'diveType'          : 'vShape', # description and unit if av
                                 'durSec'            : 240, # duration of the simulation in seconds
                                 'currentType'       : 'static',
                                 'currentStaticVel'  : (0.0,2.0,0.0),
                                 'oceanDepth'        : -70,
                                 'amountOfObstacles' : 100,
                                 'max_particles'     : 270,
                                 'particleSizeRange' : (.00002,0.00016),
                                 'cloudRadius'       : 0.0018,
                                 }
        self.sealTra = list()
        
            
    def meterPerSecond2meterPerSample(self,velocity):
        # THis function should be inherited
        return copy.deepcopy(velocity/self.sps)
    
    def simulate_sample(self):
        # create a step
        self.seal.createSealStep('45down')
        print(self.seal.sealStep)
        # move da particles
        self.pCloud.moveParticles()
        for po in self.pCloud.partclObjList:  
            print(po.position)
        # move da seal
        self.seal.MoveSeal()

    #- SIM Objm
    #- implementation:
    #    1) done decide for dive type, length etc.
    #    2) done decide for environment (currents,depth,objects)
    #    3) compose trajectory
    #    4) run turbidty cloud through tra

    def runSimulation(self):
        #set environment and particle cloud
        self.setParameters()
        self.environment.creatObstacles() #create obstacle if maxObsticales >0

        #get trajectory
        self.protoMove.generator2(self.simParameterDict['durSec'])
        self.sealVelTra = self.protoMove.velTra

        #run trajectory through particle cloud
        for step in tqdm(self.sealVelTra,'running simulation'):
            self.seal.sealStep = np.hstack((step,0.0))/self.sps
            self.seal.MoveSeal()
            self.pCloud.moveParticles()
        
        # save results


    def userDefParametersCLI(self):

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
        self.simParameterDict['cloudRadius']       = float(self.CLI_dialg_num('Set radius of the Cloud', '-70'))
     

        print(self.simParameterDict)
        self.setParameters()

    def setParameters(self):
        self.protoMove.mode               = self.simParameterDict['diveType']
        self.protoMove.traDurSec          = self.simParameterDict['durSec']
        self.environment.waterCurrentMode = self.simParameterDict['currentType']
        if self.simParameterDict['currentType'] == 'static':
            self.environment.waterCurrent     = self.simParameterDict['currentStaticVel']
        self.environment.oceanDepth       = self.simParameterDict['oceanDepth']
        self.environment.maxObstacles     = self.simParameterDict['amountOfObstacles']
        self.pCloud.max_particles         = self.simParameterDict['max_particles']
        self.pCloud.sizeRange             = self.simParameterDict['particleSizeRange']
        self.pCloud.maxVectorMagnitue     = self.simParameterDict['cloudRadius']
        
    def CLI_dialg_choiceText(self,question,default = False,answers=["yes","no"]):

        userAnswer = self.CLI_quest(question,answers,default)
        while userAnswer not in answers:
            print(str(userAnswer) + " unrecognised, please answer with: " + str(answers))
            userAnswer = self.CLI_quest(question,answers,default)
        return userAnswer
    
    def CLI_dialg_num(self,question,default = False):
        userAnswer = self.CLI_quest(question,[],default)
        while userAnswer.strip('-').replace('.','',1).isdigit() ==False:
            print(str(userAnswer) + " unrecognised, this is not a number")
            userAnswer = self.CLI_quest(question,[],default) 
        return userAnswer


    def CLI_quest(self,question, answers,default):

        if default != False:
            userAnswer = input(question + " [" + str(answers) +" | default: "+ str(default)+"] :")
            if userAnswer == "":
                userAnswer = default
        else:
            userAnswer = input(question + " [" + str(answers)+ "] :")

        return userAnswer




