import numpy as np
import math as m 
import copy 
from ai import cs
#from sympy import *

class Particle:
    """
    Class 'Particle' holds information about the size and position of a particle inside the turbidity simulation.
    This class defines trajectiries of particles movement by Brownian motion in the ocean that forms tubidity.  
    Generated particles form cloud (class 'Cloud') with a seal as a center of a particles' cloud (class 'Seal').
    The trajectories of particles' movement are influenced by water currents, water viscosity and obstacles e.g.
    corals, rocks etc. (class 'Environment')
    """

    def __init__(self,cloudObj, position,size):
        """
        This function initialises the trajectory of movement for each single particle with a x,y,z position
        inside a particle cloud in cartesian 3D space. Particles are moving by Brownian motion, where we consider viscosity
        and temperature gradient of the ocean water, so particles have different velocity of random walk movement
        (Brownian motion), depending on the depth of their position in the 3D space of ocean (z axis position).
        Trajectories of particles movement are also influenced by other environmental factors such as
        the water currents and obstacles in the ocean, and are negativly influnced by the seal trajectory.

        @param cloudObj      string default: none
           string that defines that particles move as a cloud object.
        @param size          float default: none
            size save the particle radius [µm]. Particles have no form so far but if
            plotted spheres or tetrahedron might be best according to the rendering 
            algorithm.
        @param position     np.array default: none
            tuple consisting of three random coordinates x,y,z in 3D cartesian space.
        @param trajectory    float default: none
            list of position of particle (x,y,z) before and after the sealStep, and visibility
            of the particle. The list is supplemented with these 3 datasets for each sealStep.
        @param activeMovement  bool default: True
            defines boundaries of the ocean' space, where partciles move actively. 
            Active movement of particles is true for ocean depth with the limit - 0 [m] to oceanDepth [m],
            and true when particles are not in the area of obstacle.
        @param visible         bool default: True
            particles are visible in the water for seal, and form opic flow. They are not
            visible above 0 [m] and 10cm below oceanDepth [m] or if their position is within an obstacle.
        @param temperature  float default: none
            the temperature [K] of water that changes with the depth of ocean. 
        @param viscosity    float default: none 
            viscosity of saltwater [Ns/m²,Pa*s] that depends on temperature and vary with the depth.
        @param samplesPerSec float default: 20.0 
            the model's basic frequency. It defines, how often samples are updated per one second.
        """
        # objects from other classes
        self.cloudObj       = cloudObj # particles form cloud object
        self.samplesPerSec  = self.cloudObj.simObj.runTimeData.getParameter('sps') #samples per second
        self.size           = size # radius of the particles [µm]
        self.position       = position # tuple consisting of three coordinates x,y,z
        # private objects
        self.trajectory     = [] # list of positions pre and post sealStep
        self.activeMovement = True #particles actively move by Brownian motian
        self.visible        = True #particles are in the visual field of a seal
        self.temperature    = float("NAN")
        self.viscosity      = float("NAN")
        self.absPosition    = None
        
    def randomWalk(self):
        """
        The function 'randomWalk' defines the random step size of a particle that moves via 
        Brownian motion in the space of seal's visual field.

        @ return a random array of particle's coordinates position x,y,z influenced by Brownian motion
        step size.         
        """
        stepSize = self.getBrownianMotionStepSize()
 
        return np.random.choice((-1,1),3)*stepSize
 
    def depth2Temperature(self):
        """
        The function 'depth2Temperature' creates a gradient of water's temerature in the ocean
        environment. The data is taken from the doi.org/10.3389/fmars.2018.00287. 
        The data represented by a Gaussian function is temperature data from the Gulf of Finland (Figure 2).
        Fitting was done via plot.ly @ 29th May 2020.

        Gaussian function resulting in the following formula and coefficients: 

        A (area)  = 3.1643818163582185
        H (FWHM) = 5.289978692454068
        xo (center) = -2.854807838826537
        w (width)  = 13.943640614002176
        z  = absolute coordinate position of a particle on z axis (depth of the ocean)

        The tempetature gradient (z): 
        \f$\ A+H*exp{(-(z-x_o)^2/(2*w^2))}\f$.
        """
        self.temperature = 3.1643818163582185+5.289978692454068*np.exp(-1*(self.absPosition[2]+2.854807838826537)**2/(2*13.943640614002176**2))
    
    def temperature2viscosity(self):
        """
        The function 'temperature2viscosity' calculates the viscosity of salt water gradient based on data 
        from https://www.engineeringtoolbox.com/sea-water-properties-d_840.html
        
        Where the absolute dynamic viscosity is given in [Ns/m²],[Pa*s]. 
        The data was fitted with plot.ly.

        Quadratic fit model resulting in the following formula and coefficients:

        A = 6.432652442106597e-7
        B = -0.00005261247345535204
        C = 0.0018733137829911907

        The viscosity gradient (z): 
        \f$\ A*temperature(z)^2+B*x+C\f$.
        """
        self.viscosity = 6.432652442106597*10**-7*self.temperature**2+-0.00005261247345535204*self.temperature+0.0018733137829911907

    def getBrownianMotionStepSize(self):
        """
        The function 'getBrownianMotionStepSize' runs a temperature dependent brownian motion for each particle.

        In a three dimensional space we can describe the velocity in each direction by 
        the Einstein-Smoluchowski (E-S) equation for observation duration approaching 0 sec. 
        As we will describe motion behaviour in high temporal resolution. We can use discrete formulae
        instead of differential equations.

        Displacement formula (E-S): |Δx2| = 2Dt       |Δy2| = 2Dt       |Δz2| = 2Dt

        The velosity (v) of particle:
        \f$\ x/t = sqrt{(2D)/t = (2D/t)^(1/2)} = sqrt{((RT)/(3*N*pi*eta*r*t))}\f$.

        R = 8.314462 (general gas constant)
        T = temperature [K]
        N = 6.022*10²³ (Avogadro's number)

        @return brownian motion based stepSize
        """
        self.depth2Temperature()
        self.temperature2viscosity()

        return np.sqrt((8.314462 * self.temperature+273.15 )/ (3* (6.022*10**23))*np.pi*self.viscosity*self.size* (1/self.samplesPerSec))

    def particleMovement(self,sealPosition,waterCurrent,sealStep):
        """
        the 'particleMovement' function moves all particles relative to the seal postion by brownian motion
        if the particle is visible. 
        For the statecheck the absolute position of the particles is calculated to calculate the respetive 
        depth and temperature.
        Next the active movement is checked, and those particle beeing visbile and freefloating are moved
        by the brownian motion(randomwalk), the waterCurrent and relative to the sealStep.
        Those particle on the ocean ground, that are not actively moving are just moved by the SealStep
        Those particles above water and 10cm under the seefloor or within an obstacle are not moving.

        The results of former and new position of particle are saved in self.trajectory. Status indicates
        in bool if the particle is visible or not.
        """
        # absolute position is soley needed for environment checks (soil, sky, etc)
        self.absPosition = self.position + sealPosition
        self.cloudObj.simObj.environment.particleStateCheck(self)
        
        # depending on environment checks a step is calculated
        if self.activeMovement == True and self.visible == True:
            # perform Brownian motion
            step  = self.randomWalk() + waterCurrent - sealStep[0:3]
        elif self.activeMovement == False and self.visible == True:
            step  = -1*sealStep[0:3]
        else:
            step  = np.zeros(shape = 3)
        
        # get old and new position
        oldPosition    = copy.deepcopy(self.position)
        self.position += step
        newPosition    =copy.deepcopy(self.position)
        status         = copy.deepcopy(self.visible)
    
        self.trajectory.append((oldPosition,newPosition,status))

class Cloud:
    """
    The 'Cloud' class holds information about the name and the size of the turbidity Sphere/Cloud
    as well as the number and size of particles simulated within the cloud.    
    The Cloud class holds functions to create and move particles within the cloud, which is the 
    visual field of a seal. Seal is a center of a cloud (0,0,0). When particles are outside of the visual
    fild of a seal, they are being reset, so the number of particles inside a cloud is constant.
   
            PARTICLE
             180µm  a
    |----------|-----------|
    \          |ya      be/
     \         |         /
      \        |        /
       \      b|       / c
        \      |      /
         \     |     / y = 90°
          \    |    /
           \   |   /
            \  |al/
             \ | /
               o
             SEAL

                   a
    tan(alpha) =   -
                   b
             a
    b = ----------
        tan(alpha)

    alpha  = best visual resolution of a seal 5,5' = 0.09166666° R1) 
    a =  20 -160µm R2)
                                                                                                  160
    b for the best optical performance in R1 with the maximum size particle of R2 1740 µm = ----------------
                                                                                            tan(0.091666)

    The lowest count of particles in the baltic sea is 1500 particles pro cm³ R3), the highets 35000. For a sphere of 0.022 cm³ in which 
    the seal can sea particles this renders  22-770 particles.


    R1) Michael Weiffen, Bettina Möller, Björn Mauck, Guido Dehnhardt, Effect of water turbidity 
        on the visual acuity of harbor seals (Phoca vitulina) Vision Research (2005)
    R2) Bunke, Dennis, et al. "Natural and Anthropogenic Sediment Mixing Processes in 
        the South-Western Baltic Sea." Frontiers in Marine Science (2019).
    R3) Miroslaw Jonasz (1983) Particle-size distributions in the Baltic, Tellus B:
        Chemical and Physical Meteorology, 35:5, 346-358, DOI: 10.3402/tellusb.v35i5.14624
    """

    def __init__(self, simObj): 
        """ 
        This function initialises a list of random sized particles[µm] with a random x,y,z position, limited by
        radius of the visual field of a seal (@ param maxVectorMagnitude). Particles are in cartesian 3D space 
        forming a cloud with the seal as a center (0,0,0). 

        @param simObj                   SEAL_SIM.SEAL_SIM
           shortCut to simulated object           
        @param max_particles            int default: 400
            this manual choosen number sets the number of particles being placed inside the 
            turbidity cloud, this parameter represent the density of the particle.
        @param sizeRange                tuple default: none
            tuple with the range of minimum and maximum size of the particles [µm].
        @param maxVectorMagnitute       float default: .3
            this value sets the radius of the turbidty spherical cloud. It's defined by the maximum 
            sight area resolution of the habor seal underwater.
        @param sealStep                 default: (0,0,0,0,0,0)
            the combined list of values of coordinates trajectory (x,y,z) and orientations (yaw, pitch, roll) 
            of a seal that defines the change of step position when seal moves in the ocean. 
        @param sealPosition             default: (0,0,0,0,0,0)
            the combined list of values of coordinates position (x,y,z)  
        @param partclObjList            list default: none  
            list of particle objects within the turbidity cloud. Length of the list defined by max_particles. 
        @param waterCurrent             default: np.zeros(shape=3)
            an array describing a 3D current (x,y,z) [m/s].
        """
        self.simObj            = simObj # string name
        #from simulation parameters dictionary
        self.max_particles      = self.simObj.runTimeData.getParameter('max_particles') # integer number of particles )
        self.sizeRange          = self.simObj.runTimeData.getParameter('particleSizeRange') # tuple with the min and max radius[µm]
        self.maxVectorMagnitude = self.simObj.runTimeData.getParameter('cloudRadius') # max radius of a cloud
        #from seal object of the simulation object
        self.sealStep          = self.simObj.runTimeData.getParameter('sealStep') # change of position and orientation
        self.sealPosition      = self.simObj.runTimeData.getParameter('sealPosition') # change of position and orientation
        
        self.partclObjList     = [] # list of particle objects
        self.waterCurrent      = self.simObj.runTimeData.getParameter('waterCurrent') # water current

        # this part of the cloud is not used because the particles would drive right through the seal
        self.centralFreeSpace  = 1-(0.0199/self.maxVectorMagnitude) # normalised to sphere radius 0.0199 avoid devision by zero 
        self.gridParticles = False
    
    def add_particles(self):
        """
        The 'add_particle' function initializes and adds random sized particles in random position from
        'randomInit' function within the Cloud. this forms the partclObjList.
        These positions are described with x,y,z coordinates with the seal being the center of the system.
        """
        if self.gridParticles == False:
            while len(self.partclObjList)<self.max_particles:
                posSize = self.randomInit() # get random size and position
                self.partclObjList.append(Particle(self,posSize[0],posSize[1])) # initialise particle and add to list
        else:
            self.spawnMeshGridParticles()
            for i in range(len(self.particlePositions)):
                self.partclObjList.append(Particle(self,self.particlePositions[i],0.001))

    def randomInit(self):
        """
        The 'randomInit' function returns a list of random sized particles[µm] within a size range 
        of 20µm and 160µm.
        And it returns 'initialCoord' as a random vector (x,y,z) with a range from -1 to 1.
        This is limited by a set maxVectorMagnitute within the getRandomVectorMagnitute
        function.
        @return particle coordinates (x,y,z) and its size [µm]
        """  
        size = np.random.uniform(self.sizeRange[0], self.sizeRange[1], size=(1))
        initialCoord = np.random.uniform(-1,1,size = (3)) # random vector (x,y,z) from -1 to 1
        initialCoord = self.getRandomVectorMagnitude(initialCoord)
        return (initialCoord,size)
    def getRandomVectorMagnitude(self,coordinate):
        """
        The function 'getRandomVectorMagnitude' calculates the magnitude of the random vector,
        limited by the size of 'maxVectorMagnitude', which is the radius of particles' cloud.
        @return a positional vector of the particle within the particle Cloud
        """
        normCoord = np.empty(3)
        normCoord = coordinate*(np.random.uniform(low=self.centralFreeSpace, high= 1.0,size=(1,))*self.maxVectorMagnitude/np.linalg.norm(coordinate))
        return normCoord
     
    def spawnMeshGridParticles(self):
        
        radius, theta, phi = np.meshgrid(np.linspace(self.centralFreeSpace*self.maxVectorMagnitude,self.maxVectorMagnitude,         num=1), #outer 2cm of the sphere radius
                                         np.linspace(-0.4166666*np.pi,           0.4166666*np.pi, num= 20),    #theta ranging from -0.5pi to 0.5 pi
                                         np.linspace(-np.pi,               np.pi,     num = 40))            #phi ranging from -pi to pi 

        x,y,z = cs.sp2cart(r=radius, theta=theta, phi=phi)
        self.particlePositions = np.stack((x.ravel(), y.ravel(),z.ravel()),axis=1)

        return self.particlePositions

        
    def resetParticles(self,lastInitialPosition):
        """
        The 'resetParticles' function resets those particles that moved out of the sphere
        (MaxVectorMagnitute) by having them reappear on the opposite site of the sphere.

        @return new vector discribing the opposite position of the particle to the seal.
        """
        randomCoord = np.random.uniform(-1,1,size = (3)) # random vector (x,y,z) from -1 to 1
        initialCoord = self.getRandomVectorMagnitude(randomCoord)
        # To respawn the particle in the opposing quandrant of its last intial position we invert those
        # axis
        for i in range(3):
            if lastInitialPosition[i] <0:
                if initialCoord[i] < 0:
                    initialCoord[i] = initialCoord[i]*-1
            else:
                if initialCoord[i] >0:
                    initialCoord[i] = initialCoord[i]*-1

        return initialCoord

    def moveParticles(self):
        """
        This function lets all particles move activly by a browninan motion and a current and passively 
        by a SealStep. 
        The relPariclePosNorm calculates the magnitude of the particle Vectors.
        Those particle that have a higher vector magnitute than the MaxVectorMagnitute(.3), are
        reseted to the opposite side of the seals visual sphere by 'resetParticles'.
        """    
        #update water current
        self.waterCurrent = self.simObj.environment.getWaterCurrent()
        self.sealPosition = self.simObj.runTimeData.getParameter('sealPosition')
        self.sealStep     = self.simObj.runTimeData.getParameter('sealStep')
        for pObject in self.partclObjList:
            # transform from meter per second to meter per sample
            presentSealStep    = self.simObj.meterPerSecond2meterPerSample(self.sealStep)
            presentCurrentStep = self.simObj.meterPerSecond2meterPerSample(self.waterCurrent)
            # we move particles relative to seal and save vector in p-object trajectory
            pObject.particleMovement(self.sealPosition,presentCurrentStep,presentSealStep)# for all Particles in List run randomwalk
            # checking if particle norm is still in range
            relParticlePosNorm = np.linalg.norm(pObject.position)
            if  relParticlePosNorm > self.maxVectorMagnitude: # if the magnitude of the particle vector is bigger than 0.3, 
                #respawing particles that drifted away
                pObject.position = self.resetParticles(pObject.trajectory[-1][0])

       