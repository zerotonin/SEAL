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
        self.simParameterDict = {'diveType': 'vShape',
                                 'durSec'  : 240,
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
        self.simParameterDict = dict()
        diveType = input ('What type of dive should be simulated? (uShape/vShape)')
        if diveType == 'uShape':
            self.protoMove.mode = 'uShape'
        elif diveType == 'vShape':
            self.protoMove.mode = 'vShape'   
        else:
            print('Unkown  diveType: ' + diveType)
        
        diveDuration = input ('How long should the dive last in seconds?')
        self.protoMove.traLenSec = diveDuration

        currentType = input ('What type of current should be simulated? (currentType(static/interpolated)')
        if currentType == 'static':
            self.environment.waterCurrentMode = 'static'
        elif currentType == 'interpolated':
            self.environment.waterCurrentMode = 'interp'
        else:
            print('unknown currentType: '+ currentType)

        oceanDepth = input ('How deep should the simulated ocean be?')
        self.simParameterDict['oceanDepth'] = oceanDepth
        
        self.environment.oceanDepth = oceanDepth

        amountOfObstacle = input ('How many obstacle should be simulated?')
        self.environment.maxObstacles = amountOfObstacle

    def setParameters(self):
        self.protoMove.traLenSec = self.simParameterDict['durSec']

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




