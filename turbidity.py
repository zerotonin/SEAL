import numpy as np
import math as m 
from sympy import *

class Particle:
   def __init__(self, position,size):
        """
        The particle class holds information about the size and position of a particle 
        inside our turbidity simulation. More information yadiyadiya

        @param size          float default: none
            size save the particle radius in µm. Particles have no form so far but if
            plotted spheres or tetrahedron might be best according to the rendering 
            algorithm.
        @param position     np.array default: none
            blah blah what that is
        """
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

   

   def sphere2cart (self): # attempt to convert spheric coordinates of our pobjects in our self.partclObjList to cartasian coordinates 
        
        #take list r = pobject.positison[0],theta = pobject.positison[1],phi = pobject.positison[2]
       x = self.position[0] * sin( self.position[1] ) * cos( self.position[2] )
       y = self.position[0] * sin( self.position[1] ) * sin( self.position[2] )
       z = self.position[0] * cos( self.position[1] )
       self.position = [x,y,z]
       return [x,y,z] # this is just giving me one set of changed Coordinates and is not changing the whole list 
   
   def cart2sphere(self):
       XsqPlusYsq = self.position[0]**2 + self.position[1]**2
       r = m.sqrt(XsqPlusYsq + self.position[2]**2)               # r
       theta = m.atan2(m.sqrt(XsqPlusYsq),self.position[2])     # theta 
       phi = m.atan2(self.position[1],self.position[0])          # phi not correct 
       self.position = [r,theta,phi]
       return [r,theta,phi]

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
        sphereCoord = self.multiplyBySphereMax(np.random.rand(3))
        return (sphereCoord,size)

    def multiplyBySphereMax(self,coordinates)

        sphereCoord[0] = coordinates[0]*self.radiusMax
        sphereCoord[1] = coordinates[1]*np.pi
        sphereCoord[2] = coordinates[2]*np.pi*2-np.pi
        return sphereCoord

    
    def resetParticles(self):
        for pobject in self.partclObjList:

            pobject.position[0] = self.radiusMax -(pobject.position[0]%self.radiusMax) #+/-10% Radius
            pobject.position[1] = (pobject.position[1]+(np.pi/2))%np.pi  #+/-10% Theta
            pobject.position[2] = ((pobject.position[2]+np.pi)%np.pi) -np.pi #+/-10% Phi    
            # random offset of 5% in each direction
            offSet = self.multiplyBySphereMax((np.random.rand(3)-0.5)/10.0)
            pobject.position = pobject.position+offSet




    def moveParticles(self):
        # for all Particles in List run randomwalk
        for pobject in self.partclObjList:
            pobject.randomWalk()
            

            if pobject.position[0] > self.radiusMax:
                self.resetParticles()
       
    def deleteParticle(self, pobject):
#        for Particle in self.partclObjList_drift
        if pobject.position[0] > self.radiusMax:
            return True
        else:
            return False 


    # r = sqrt(x*x + y*y + z*z)
    #phi = atan2(y,x)
    #theta = acos(z,r)
    
    
    def Cloudsphere2cart (self):
        for pobject in self.partclObjList:
            pobject.sphere2cart()

    def Cloudcart2sphere (self):
        for pobject in self.partclObjList:
            pobject.cart2sphere()
