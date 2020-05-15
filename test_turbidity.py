import time, turbidity

reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()   
C.moveParticles() 
start = time.time() 
C.moveParticles() 
end = time.time()
print(end-start)   

reload(turbidity)   
C = turbidity.Cloud('test')  
C.add_particles()  
for i in range(1000):

    C.moveParticles() 
print(len(C.partclObjList))