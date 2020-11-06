import turbidity, seal_agent,copy,environment,utilities,protoMov
import numpy as np

class SEAL_SIM:
    def __init__(self):
        self.sps         = 1 # samples per second
        self.environment = environment.environment(self) # velocity in meter per second will be transformed into an evironment object
        self.seal        = seal_agent.Seal(self)
        self.pCloud      = turbidity.Cloud(self)
        self.pCloud.add_particles()
        self.plot        = utilities.plotUtils()
        self.math        = utilities.mathUtils()
        self.turbidity   = turbidity
        self.protoMove   = protoMov.ProtMov(self)
        self.simParameterDict = {'diveType'          : 'vShape',
                                 'durSec'            : 240,
                                 'currentType'       : 'static',
                                 'oceanDepth'        : -70,
                                 'amountOfObstacles' : 100
                                 }
        
            
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
    #    1) decide for dive type, length etc.
    #    2) decide for environment (currents,depth,objects)
    #    3) compose trajectory
    #    4) run turbidty cloud through tra
    def simulationImplementation (self):

        self.simParameterDict['diveType']          = self.CLI_dialg_text('What dive Type schould be simulated ?', 'vShape', ['uShape','vShape'])
        self.simParameterDict['durSec']            = int(self.CLI_dialg_text('How long should the dive simulation last?', 240, ['60','120','180','240','300']))    
        self.simParameterDict['currentType']       = self.CLI_dialg_text('What kind of current should be simulates? ', 'static', ['static','interp'])
        self.simParameterDict['oceanDepth']        = int(self.CLI_dialg_text('Set a depth of the oceans', -70, ['-20','-30','-40','-50','-60','-70','-80']))
        self.simParameterDict['amountOfObstacles'] = self.CLI_dialg_text('How many obstacle should be simulates in the environment? ', 100, ['50','100','150','200'])

    def setParameters(self):
        self.protoMove.mode               = self.simParameterDict['diveType']
        self.protoMove.traDurSec          = self.simParameterDict['durSec']
        self.environment.waterCurrentMode = self.simParameterDict['currentType']
        self.environment.oceanDepth       = self.simParameterDict['oceanDepth']
        self.environment.maxObstacles     = self.simParameterDict['amountOfObstacles']
        
    def CLI_dialg_text(self,question,default = False,answers=["yes","no"]):

        userAnswer = self.CLI_quest(question,answers,default)
        while userAnswer not in answers:
            print(str(userAnswer) + " unrecognised, please answer with: " + str(answers))
            userAnswer = self.CLI_quest(question,answers,default)
        return userAnswer

    def CLI_quest(self,question, answers,default):

        if default != False:
            userAnswer = input(question + " [" + str(answers) +" | default: "+ str(default)+"] :")
            if userAnswer == "":
                userAnswer = default
        else:
            userAnswer = input(question + " [" + str(answers)+ "] :")

        return userAnswer




