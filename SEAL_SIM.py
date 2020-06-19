import turbidity, seal_agent

class SEAL_SIM:
    def __init__(self):
        self.seal = seal_agent.Seal('agent')
        self.pCloud = turbidity.Cloud('particle cloud')
