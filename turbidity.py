import numpy as np
import math as m 
#from sympy import *

class Particle:
    def __init__(self, position,size, groundLevel = -70.0,samplesPerSec =10.0):
        """
        Creates a list of particles. Particles are in spherical space with defined 3 positions, 
        consisted of Radius, Theta and Phi values. The particle class holds information about the size 
        and position of a particle inside our turbidity simulation. 

        @param size          float default: none
            size save the particle radius in µm. Particles have no form so far but if
            plotted spheres or tetrahedron might be best according to the rendering 
            algorithm.
        @param position     np.array default: none
            tuple consistin of three coordinates radius,theta,phi
        @param trajectory 
            list of former position of particle
        @param groundLevel  float  default: -70.0
            the depth of an ocean in metres
        @param samplesPerSec float default: 10.0 
            The models basic frequency. How often it updates in one second.
        """
        self.size = size
        self.position       = position # tuple consistin of three coordinates radius,theta,phi
        self.trajectory     = [] # list of former positions
        self.activeMovement = True 
        self.visible        = True 
        self.OFavailable    = list()
        self.groundLevel    = -70.0 # depth in meter
        self.samplesPerSec  = samplesPerSec
        self.temperature    = float("NAN")
        self.viscosity      = float("NAN")
        


        

    def checkVisibility(self):
       """
       Function checks if coordinates of particles are inside of a sphere and visible. 
       Particle is not visible if it's above the surface level and if it's below ground level. 
       """
       if self.position[2] >= 0. or self.position[2] <= self.groundLevel-0.1:
           self.visible = False
       else: 
           self.visible = True
   
    def checkActiveMovement(self):
       """
       The checkActiveMovement function defines which particles are moving and which are stationary.
       Those particles with a self.position[2](z value) between -70m and -70.1m are stationary. 
       Those that are between 0 and -70m are moving according to the randomWalk function. 
       """
       if self.visible == True:
           if self.position[2]<= self.groundLevel:
               self.activeMovement = False
           else: 
               self.activeMovement = True
       else:
           self.activeMovement = False  
           
    def particleStateCheck(self):
       """
       The particlStateCheck function calls the information for the visibility and active movement
       state of the particle
       """
       self.checkVisibility()
       self.checkActiveMovement()

    def randomWalk(self):
        """
        Creates a random walk trajectory for particles, that move in the direction of currents in a 
        spherical space.
        
        @param current 
        is a moving vector of current, where numpy array is three values containing radius,theta,phi
        @param position
        coordinates of particle in spherical space, that are updated by random walk coordinates with 
        defined step size in the current's vectors direction.
        """
        
        stepSize = self.getBrownianMotionStepSize()
 
        self.position  = self.position+ (np.random.choice((-1,1),3)*stepSize)

    def sphere2cart (self): 
        """
        Converts spheric coordinates(r = pobject.positison[0],theta = pobject.positison[1],
        phi = pobject.positison[2]) of pobjects in self.partclObjList to cartasian coordinates
        and returns x,y,z coordinates as a list
        """
        # attempt to convert spheric coordinates of our pobjects in our self.partclObjList to cartasian coordinates 
        #take list
        x = self.position[0] * np.sin( self.position[1] ) * np.cos( self.position[2] )
        y = self.position[0] * np.sin( self.position[1] ) * np.sin( self.position[2] )
        z = self.position[0] * np.cos( self.position[1] )
        self.position = [x,y,z]
        self.particleStateCheck()
        return [x,y,z] # this is just giving me one set of changed Coordinates and is not changing the whole list 
  
    def depth2Temperature(self):
        """
        The temperature of the water environment is modelled based on f1. The data represented by
        a Gaussian function is temperature data from the Gulf of Finland (Figure 2). Fitting was
        done via plotly @ 29th May 2020

        Gaussian function: 

        A  = 3.1643818163582185
        H  = 5.289978692454068
        xo = -2.854807838826537
        w  = 13.943640614002176

        temperatue(z) = A+H*exp(-(z-xo)²/(2*w²))

        f1: Placke, Manja, et al. "Long-term mean circulation of the Baltic Sea as represented by 
        various ocean circulation models." Frontiers in Marine Science 5 (2018): 287.
        """
        self.temperature = 3.1643818163582185+5.289978692454068*np.exp(-1*(self.position[2]+2.854807838826537)**2/(2*13.943640614002176**2))
    
    def temperature2viscosity(self):
        '''
        The viscosity of saltwater was modeled based on data from https://www.engineeringtoolbox.com/sea-water-properties-d_840.html
        Where the absolute dynamic viscosity is given in (Ns/m²,Pa*s). The data was fitted with plot.ly and a quadratic fit model resulting
        in the following formula and coefficients:

        self.viscosity = A*self.temperature**2+B*x+C
        A = 6.432652442106597e-7
        B = -0.00005261247345535204
        C = 0.0018733137829911907
        '''
        self.viscosity = 6.432652442106597*10**-7*self.temperature**2+-0.00005261247345535204*self.temperature+0.0018733137829911907

    def getBrownianMotionStepSize(self):
        """
        the temperature2SteoSize function runs a temperature dependent brownian motion for each particle.

        In a three dimensional space we cand describe the velocity in each direction by the Einstein-Smoluchowski (E-S) equation
        for observation duration approaching 0 sec. As we will describe motion behaviour in high temporal resolution. We
        can use discrete formulae instead of differential equations.

        Displacement formula (E-S): |Δx2| = 2Dt       |Δy2| = 2Dt       |Δz2| = 2Dt

        v = x/t = np.sqrt(2D)/t = (2D/t)^(1/2) = np.sqrt((RT)/(3*N*pi*eta*r*t))

        R = 8.314462 | general gas constant
        T = temperature in Kelvin
        N = 6.022*10²³ | Avogadro's number
        """
        self.depth2Temperature()
        self.temperature2viscosity()

        return np.sqrt((8.314462 * self.temperature+273.15 )/ (3* (6.022*10**23))*np.pi*self.viscosity*self.size* (1/self.samplesPerSec))


    def cart2sphere(self):
       """
       Converts cartasian coordinates (x = pobject.positison[0],y = pobject.positison[1],
       z = pobject.positison[2]) of pobjects in self.partclObjList to sperical coordinates
       and returns radius, theta, phi coordinates as list of floats.
       r = sqrt(x*x + y*y + z*z)
       theta = atan2((x*x +y*y),z)
       phi = atan2(y,x)
       """
       XsqPlusYsq = self.position[0]**2 + self.position[1]**2
       r = m.sqrt(XsqPlusYsq + self.position[2]**2)               # r
       theta = m.atan2(m.sqrt(XsqPlusYsq),self.position[2])     # theta 
       phi = m.atan2(self.position[1],self.position[0])          # phi not correct 
       self.position = [r,theta,phi]
       return [r,theta,phi]

    def particleMovement(self,waterCurrent):
        #saving the old position
        self.trajectory.append(self.position)
        # checking if the particle is moving
        self.particleStateCheck()
        if self.activeMovement == True:
            # perform Brownian motion
            self.randomWalk()
            # perform current motion
            self.position += waterCurrent
        else:
            self.OFavailable.append(False)   
   
    
    def combinedMovement(self,waterCurrent,sealTrajectory):
        self.particleMovement(waterCurrent)
        self.sealMovement(sealTrajectory)




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
                maxVectorMagnitue= 10): # needs to be vector magnitute , discribing the length of a vector
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
        self.maxVectorMagnitue = maxVectorMagnitue # 6 item wide tuple with the minimum and maximum values of the
        self.sealPosition = np.zeros(shape = 3) #centre of the coordinate system of the Seal in disctance to (0,0,0) of world
        self.sealOrientation = np.zeros(shape = 3)
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

        Sizes of the particles are between 20µm and 160µm
        """  
        size = np.random.uniform(self.sizeRange[0], self.sizeRange[1], size=(1))*0.00016 + 0.00002
        initialCoord = np.random.uniform(-1,1,size = (3)) # rancom vector (x,y,z) from -1 to 1
        initialCoord = self.getRandomVectorMagnitude(initialCoord)
        return (initialCoord,size)

    #def multiplyBySphereMax(self,coordinate):
    #    """
    #    The multiplyBySphereMax function is creating the mathematic setting for the coordinats in 
    #    the spheric coordinate system (0=radius,1=theta,2=phi). defining 
    #        radius by radiusMax
    #        theta by np.pi describing a range between (0-180°)
    #        phi by np.pi*2-np.pi describing a range between ((-180°)-180°)
    #    """
    #    sphereCoord = np.empty(3)
    #    sphereCoord[0] = coordinate[0]*self.radiusMax
    #    sphereCoord[1] = coordinate[1]*np.pi
    #    sphereCoord[2] = coordinate[2]*np.pi*2-np.pi
    #    return sphereCoord

    def getRandomVectorMagnitude(self,coordinate):
        """
        Creats a vector with a random magnitute from 0 to maxVectorMagnitue(10), Thereby
        randomly choosen positions with a distance of less than 10m for each particle 
        sorrounding the center of the seals coordinate system is choosen starting at postion 
        (0,0,0) in the world coordinate system, representing a position at the ocean surface
        """
        normCoord = np.empty(3)
        normCoord = coordinate*(np.random.rand(1)*self.maxVectorMagnitue/np.linalg.norm(coordinate))
        return normCoord
        


    def resetParticles(self,relPariclePos,relPariclePosNorm):
        """
        The resetParticles function resets those particles that moved out of the sphere
        (MaxVectorMagnitute) by having them reappear on the opposite site 
        of the sphere, with a offset of 5 percent
        """
        newMagnitude = self.maxVectorMagnitue-(relPariclePosNorm%self.maxVectorMagnitue) # new magnitute of reset position for the particle
        offSet = (np.random.rand(3)-0.5)*(self.maxVectorMagnitue/10)/self.maxVectorMagnitue # offset by 5 % 
        newVector = (relPariclePos+offSet)*-1*newMagnitude/relPariclePosNorm # new vector discribing the opposite position of the particle to the seal
        return newVector

    def moveParticles(self):
        """
        this function lets all particles move activly by a browninan motion 
        and a current. Those particle who get a higher vector magnitute than the 
        MaxVectorMagnitute(10), need to reset to opposite side of the seals 
        visual sphere. Therefore relPariclePos calculates the vector between the 
        particle postion and the seals position within the world coordinate system
        The relPariclePosNorm calculates the magnitude of this vector. 
        Those particles that have a higher magnitude from the seal than the MaxVectorMagnitude
        need to set to a new postion which is defined by the resetParticle function. 
        Afterwards the sealPostionVector needs to be added again to those particles to 
        end up with the Coordinate values in the world Coordinate System 
        """    
        for pobject in self.partclObjList:
            pobject.randomWalk(self.sealPosition)             # for all Particles in List run randomwalk
            relPariclePos = pobject.position-self.sealPosition
            relPariclePosNorm = np.linalg.norm(relPariclePos)
            if  relPariclePosNorm > self.maxVectorMagnitue: # if the magnitude of the particle vector is bigger than 10, 
                newPosition = self.resetParticles(relPariclePos,relPariclePosNorm)
                pobject.position = newPosition + self.sealPosition 
       
    def deleteParticle(self, pobject):
        """NOT NEEDED ANYMORE ?"""
        if pobject.position[0] > self.radiusMax:
            return True
        else:
            return False 

    def CloudDepth2Temperature(self):
        """
        The CloudDepth2Temperature function calls all particle objects in the Cloud 
        which are between surface and seafloor and calculates the temperature for
        every particle. This information will be needed for the temperature dependent
        brownian motion of the particles.
        """
        for pobject in self.partclObjList:
            if pobject.activeMovement == True:

                pobject.depth2Temperature()
    
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
