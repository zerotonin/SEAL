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
        self.size = size
        self.position = position # tuple consistin of three coordinates radius,theta,phi
        self.trajectory = [] # list of former positions
  
   def randomWalk(self,
                  stepSize = 1,
                  current = np.array([1,1,1])): # moving vector 
       # current should be an numpy array of three values containing radius,theta,phi
        self.trajectory.append(self.position)
        self.position  = self.position+ np.random.uniform(-1*stepSize,stepSize,3)
        self.position  = self.position+ current
    
    def temperatureFromZ(self,z):
        return 3.1643818163582185+5.289978692454068* np.exp(-(z--2.854807838826537)**2/(2*13.943640614002176**2))

   

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
    """
    The Cloud class holds information about the name and the size of the turbidity Sphere/Cloud
    as well as the amount and size of particles simulated within the cloud.
    
    The Cloud class holds functions to create and move particles within the cloud, and 
    converts their coordinates from spheric coordinate system to cartasian coordinate system
    and back. This allows to run all active movements of the partcile and the passive movement
    by the seal agend in a cartasian coordinate system. 
    """

    def __init__(self,
                name,
                max_particles = 400,
                sizeRange = (0.001,1.0),
                radiusMax= 10):
        """ 
        @param name            float default: none
            a individual name should be given to each new version of the turbidity sphere
            (different particle density, particle sizes)
        @param max_particles     float default: none
            this manual choosen number sets the number of particles being placed inside the 
            turbidity sphere, this parameter represent the density of the particles
        @param sizeRange       tuple default=none
            tuple with the minimum and maximum size of the particles.(min,max)
        @param radiusMax       float default= none
            this value sets the Radius of the turbidty sphere, this value should be taken from
            the maximum sight of the habor seal underwater
        @param partclObjList    list default=none  
            list of particle objects within the turbidity cloud. length of the list defined by 
            max_particles 
        """
        
        self.name = name # string name
        self.max_particles = max_particles # integer number of particles of the same size and position range
        self.partclObjList = [] # list of particle objects
        self.sizeRange = sizeRange # tuple with the minim and maximum size / radius of our tetrahedron
        self.radiusMax = radiusMax # 6 item wide tuple with the minimum and maximum values of the
       # positions in order: xmin xmax ymin ymax zmin zmax
 
    def add_particles(self):
        """
        The add_particle function initializes and adds random sized particles in random position 
        within the Cloud. This forms the partclObjList.These positions are descriebed with
        radius, theta and phi.
        """
        while len(self.partclObjList)<self.max_particles:

            posSize = self.randomInit() # get random size and position
            self.partclObjList.append(Particle(posSize[0],posSize[1])) # initialise particle and add to list
          
    def randomInit(self):
        """
        the randomInit function creates random numbers for each coordinate (radius, theta, phi)
        within their ranges.
        """  
        size = np.random.uniform(self.sizeRange[0], self.sizeRange[1], size=(1))
        sphereCoord = self.multiplyBySphereMax(np.random.rand(3))
        return (sphereCoord,size)

    def multiplyBySphereMax(self,coordinate):
        """
        The multiplyBySphereMax function is creating the mathematic setting for the coordinats in 
        the spheric coordinate system (0=radius,1=theta,2=phi). defining 
            radius by radiusMax
            theta by np.pi describing a range between (0-180°)
            phi by np.pi*2-np.pi describing a range between ((-180°)-180°)
        """
        sphereCoord = np.empty(3)
        sphereCoord[0] = coordinate[0]*self.radiusMax
        sphereCoord[1] = coordinate[1]*np.pi
        sphereCoord[2] = coordinate[2]*np.pi*2-np.pi
        return sphereCoord

    
    def resetParticles(self):
        """
        The resetParticles function resets those particles that moved out of the sphere
        (radius higher than the radiusMax) by having them reappear on the opposite site 
        of the sphere. 
        """
        
        for pobject in self.partclObjList:

            pobject.position[0] = self.radiusMax -(pobject.position[0]%self.radiusMax) #+/-10% Radius
            pobject.position[1] = (pobject.position[1]+(np.pi/2))%np.pi  #+/-10% Theta
            pobject.position[2] = ((pobject.position[2]+np.pi)%np.pi) -np.pi #+/-10% Phi    
            # random offset of 5% in each direction
            offSet = self.multiplyBySphereMax((np.random.rand(3)-0.5)/10.0)
            pobject.position = pobject.position+offSet




    def moveParticles(self):
        """
        The moveParticles makes all particle object in the cloud move by a random walk 
        for each particle and an universal current acting on all particles. 
        Thos partiles that leave the sphere by this function are detected and the
        resetParticle function makes them reappear on th opposite site of the sphere
        """    
        for pobject in self.partclObjList:
            pobject.randomWalk()             # for all Particles in List run randomwalk
            
            if pobject.position[0] > self.radiusMax:
                self.resetParticles()
       
    def deleteParticle(self, pobject):
        """NOT NEEDED ANYMORE ?"""
        if pobject.position[0] > self.radiusMax:
            return True
        else:
            return False 


    # r = sqrt(x*x + y*y + z*z)
    #phi = atan2(y,x)
    #theta = acos(z,r)
    
    
    def Cloudsphere2cart (self):
        """
        The Cloudsphere2cart function converts the postions of each particle from 
        spheric coordinates (radius,theta,phi) to cartasian coordinates (x,y,z)
        """
        for pobject in self.partclObjList:
            pobject.sphere2cart()

    def Cloudcart2sphere (self):
        """
        The Cloudcart2sphere function converts the postion of each particle from 
        cartasian coordinates (x,y,z) to spheric coordinates (radius,theta,phi)
        """
        for pobject in self.partclObjList:
            pobject.cart2sphere()
