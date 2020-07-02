from importlib import reload 
import SEAL_SIM
import numpy as np 

reload(SEAL_SIM)
simObj = SEAL_SIM.SEAL_SIM()




# This test can be later used to find resolutable particles
# for the optic flow calculation
#         a                         / a \
#    b = ----------  alpha = arctan|  - |
#        tan(alpha)                 \ b/
for particle in simObj.pCloud.partclObjList:
    print
    vecNorm = np.linalg.norm(particle.position) 
    
    angleSize = np.rad2deg(np.arctan(particle.size/vecNorm)) 
    print(angleSize> 0.86,vecNorm,angleSize)
