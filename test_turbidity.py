import time, turbidity

reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()   
C.moveParticles() 
start = time.time() 
C.moveParticles() 
end = time.time()
print(end-start)   
#

for po in C.partclObjList: 
   ...:     print(po.position) 
 
 
reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()  
for i in range(1000):

    C.moveParticles() 
print(len(C.partclObjList))