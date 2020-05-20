import numpy as np
import time, turbidity
from importlib import reload 
from sympy import *


reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()   
C.moveParticles() 
start = time.time() 
C.moveParticles() 
end = time.time()
print(end-start)   
# thingi

for po in C.partclObjList: 
   ...:     print(po.position) 
 

reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()  
for i in range(1000):

    C.moveParticles() 
print(len(C.partclObjList))

for po in C.partclObjList: 
   ...:     print(po.position) 


# for testing sphere2cart function 

import numpy as np
import time, turbidity
from importlib import reload 
from sympy import *

reload(turbidity)
C = turbidity.Cloud('test')  
C.add_particles() 
C.sphere2cart()


print(C.partclObjList[0].position)                                                                                                 
C.Cloudsphere2cart()                                                                                                               
print(C.partclObjList[0].position)                                                                                                 
C.Cloudcart2sphere()                                                                                                               
print(C.partclObjList[0].position) 