import numpy as np
import math as m 
from sympy import *

class Particle:
   def __init__(self, position,size):
       self.size = size # number
       self.position = position # tuple consistin of three coordinates radius,theta,phi
       self.trajectory = [] # list of former positions
  
   def randomWalk(self,
                  stepSize = 1,
                  current = np.array([1,1,1])): # moving vector 
       # current should be an numpy array of three values containing radius,theta,phi
       self.trajectory.append(self.position)
       self.position  = self.position+ np.random.uniform(-1*stepSize,stepSize,3)
       self.position  = self.position+ current
 
 
class Cloud:

    def __init__(self,
                name,
                max_particles = 400,
                sizeRange = (0.001,1.0),
                radiusMax= 10):
        self.name = name # string name
        self.max_particles = max_particles # integer number of particles of the same size and position range
        self.partclObjList = [] # list of particle objects
        self.sizeRange = sizeRange # tuple with the minim and maximum size / radius of our tetrahedron
        self.radiusMax = radiusMax # 6 item wide tuple with the minimum and maximum values of the
       # positions in order: xmin xmax ymin ymax zmin zmax
 
    def add_particles(self):
        while len(self.partclObjList)<self.max_particles:

            posSize = self.randomInit() # get random size and position
            self.partclObjList.append(Particle(posSize[0],posSize[1])) # initialise particle and add to list
          
    def randomInit(self):
        size = np.random.uniform(self.sizeRange[0], self.sizeRange[1], size=(1))
        sphereCoord = np.random.rand(3)
        sphereCoord[0] = sphereCoord[0]*self.radiusMax
        sphereCoord[1] = sphereCoord[1]*np.pi
        sphereCoord[2] = sphereCoord[2]*np.pi*2
        return (sphereCoord,size)



    def moveParticles(self):
        # for all Particles in List run randomwalk
        for pobject in self.partclObjList:
            pobject.randomWalk()
            

            if pobject.position[0] >= self.radiusMax:
                self.partclObjList.remove(pobject)
                self.add_particles()
       
    def deleteParticle(self, pobject):
#        for Particle in self.partclObjList_drift
        if pobject.position[0] >= self.radiusMax:
            return True
        else:
            return False 


    # r = sqrt(x*x + y*y + z*z)
    #phi = atan2(y,x)
    #theta = acos(z,r)
    
    def sphere2cart (self): # attempt to convert spheric coordinates of our pobjects in our self.partclObjList to cartasian coordinates 
        for pobject in self.partclObjList:
        #take list r = pobject.positison[0],theta = pobject.positison[1],phi = pobject.positison[2]
            x = pobject.position[0] * sin( pobject.position[1] ) * cos( pobject.position[2] )
            y = pobject.position[0] * sin( pobject.position[1] ) * sin( pobject.position[2] )
            z = pobject.position[0] * cos( pobject.position[1] )
            return [x,y,z] # this is just giving me one set of changed Coordinates and is not changing the whole list 
