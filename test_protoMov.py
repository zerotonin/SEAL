from importlib import reload 
import SEAL_SIM,protoMov
import numpy as np 

reload(protoMov)
simObj = SEAL_SIM.SEAL_SIM()
P = protoMov.ProtMov(simObj)
P.vShapeDive()