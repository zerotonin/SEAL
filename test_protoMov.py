from importlib import reload 
import SEAL_SIM,protoMov
import numpy as np 

reload(protoMov)

P = protoMov.ProtMov('Test')
P.vShapeDive()