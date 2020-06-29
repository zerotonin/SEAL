import numpy as np
import math as m 
import copy 
#from sympy import *

class Particle:
    '''
    Class 'Particle' holds information about the size and position of a particle inside the turbidity simulation.
    This class defines trajectiries of particles movement by Brownian motion in the ocean that forms tubidity.  
    Generated particles form cloud (class 'Cloud') with a seal as a center of a particles' cloud (class 'Seal').
    The trajectories of particles' movement are influanced by water currents, water viscosity and obstacles e.g.
    corals, rocks etc. (class 'Enviroment')
    '''

    def __init__(self,cloudObj, position,size):
        '''
        This function initialises the trajectory of movement for each single particle particle with a x,y,z position
        inside a cloud in cartesian 3D space. Particles are moving by Brownian motion, where we consider viscosity
        and temperature gradient of the ocean' water, so particles have different velocity of random walk' movement
        (Brownian motion), depending on the depth of their position in the 3D space of ocean (z axis position).
        Trajectories of particles movement are also influenced by the water currents and obstacles in the ocean.

        @param cloudObj      string default: none
           string that defines that particles move as a cloud object.
        @param size          float default: none
            size save the particle radius [µm]. Particles have no form so far but if
            plotted spheres or tetrahedron might be best according to the rendering 
            algorithm.
        @param position     np.array default: none
            tuple consisting of three random coordinates x,y,z in 3D cartesian space.
        @param trajectory    float default: none
            list of former position of particle x,y,z. List is supplemented with updated
            former positions when particles move.
        @param activeMovement  bool default: True
            defines boundaries of the ocean' space, where partciles move actively. 
            Active movement of particles is true for ocean depth with the limit - 0 [m] to -70 [m],
            and true when particles are not in the area of obstacle.
        @param visible         bool default: True
            particles are visible in the water for seal, and form opic flow. They are not
            visible above 0 [m] and below -70,1 [m] and if their position is same as a position of obstacle.
        @param OFavailable     int default: none
            the list of particles that are visible and move actively.
        @param temperature  float default: none
            the temperature [K] of water that changes with the depth of ocean. 
        @param viscosity    float default: none 
            viscosity of saltwater [Ns/m²,Pa*s] that depends on temerature and vary with the depth.
        @param samplesPerSec float default: 10.0 
            the model's basic frequency. It defines, how often samples are updated per one second.
        '''
        self.cloudObj       = cloudObj # particles form cloud object
        self.size           = size # radius of the particles [µm]
        self.position       = position # tuple consisting of three coordinates x,y,z
        self.trajectory     = [] # list of former positions x,y,z
        self.activeMovement = True #particles actively move by Brownian motian
        self.visible        = True #particles are in the visual field of a seal
        self.temperature    = float("NAN")
        self.viscosity      = float("NAN")
        self.samplesPerSec  = self.cloudObj.simObj.sps #samples per second
        

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
        '''
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

        '''
        self.temperature = 3.1643818163582185+5.289978692454068*np.exp(-1*(self.absPosition[2]+2.854807838826537)**2/(2*13.943640614002176**2))
    
    def temperature2viscosity(self):
        '''
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
       
        '''
        self.viscosity = 6.432652442106597*10**-7*self.temperature**2+-0.00005261247345535204*self.temperature+0.0018733137829911907

    def getBrownianMotionStepSize(self):
        '''
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
        '''
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
        Those particles above water and 10cm under the seefloor are not moving.

        The results of former and new position of particle are saved in self.trajectory. Status indicates
        in bool if the particle is visible or not.

        """
        
        self.absPosition = self.position + sealPosition
        self.cloudObj.simObj.environment.particleStateCheck(self)
        
        if self.activeMovement == True and self.visible == True:
            # perform Brownian motion
            step  = self.randomWalk() + waterCurrent - sealStep[0:3]
        elif self.activeMovement == False and self.visible == True:
            step  = -1*sealStep[0:3]
        else:
            step  = np.zeros(shape = 3)
        
        oldPosition = copy.deepcopy(self.position)
        self.position += step
        newPosition =copy.deepcopy(self.position)
        status = copy.deepcopy(self.visible)
        #print(step,oldPosition,newPosition,status)
        #print("=======================================================")

        self.trajectory.append((oldPosition,newPosition,status))

   
    




class Cloud:
    """
    The 'Cloud' class holds information about the name and the size of the turbidity Sphere/Cloud
    as well as the number and size of particles simulated within the cloud.    
    The Cloud class holds functions to create and move particles within the cloud, which is the 
    visual field of a seal. Seal is a center of a cloud (0,0,0). When particles are outside of the visual
    fild of a seal, they are being reset, so the number of particles inside a cloud is constant.
    """

    def __init__(self,
                simObj,
                max_particles = 400,
                sizeRange = (0.001,1.0),
                maxVectorMagnitue= .3):
                #super()__init__(self) # needs to be vector magnitute , discribing the length of a vector
        """ 
        This function initialises a list of random sized particles[µm] with a random x,y,z position, limited by
        radius of the visual field of a seal (@ param maxVectorMagnitue). Particles are in cartesian 3D space 
        form a cloud with the seal as a center (0,0,0). 

        @param simObj      string default: none
           string that gives a name: simulation object.           
        @param max_particles     int default: 400
            this manual choosen number sets the number of particles being placed inside the 
            turbidity cloud, this parameter represent the density of the particle.
        @param sizeRange      tuple default: none
            tuple with the range of minimum and maximum size of the particles [µm].
        @param maxVectorMagnitute       float default: .3
            this value sets the Radius of the turbidty spherical cloud. It defined by the maximum 
            sight area resolution of the habor seal underwater.
        @param partclObjList     list default: none  
            list of particle objects within the turbidity cloud. Length of the list defined by max_particles. 
        @param sealPosition    default: (0,0,0)
            seal position as a center of the cloud of particles.
        @param sealOrientation    default: (0,0,0)
            orientation of a seal in the ocean as yaw, pitch, roll in radians.
        @param sealStep    default: (0,0,0,0,0,0)
            the combined list of values of coordinates pasitions (x,y,z) and orientations (yaw, pitch, roll) 
            of a seal that defines the change of step position when seal moves in the ocean. 
        @param waterCurrent   default: np.zeros(shape=3)
            the list of water current vectors in the ocean space.
        """
        self.simObj = simObj # string name
        self.max_particles = max_particles # integer number of particles 
        self.partclObjList = [] # list of particle objects
        self.sizeRange = sizeRange # tuple with the min and max radius[µm]
        self.maxVectorMagnitue = maxVectorMagnitue # max radius of a cloud
        self.sealPosition    = self.simObj.seal.sealPosition #centre of the coordinate system of a Seal
        self.sealOrientation = self.simObj.seal.sealOrientation  # orientation as yaw pitch roll
        self.sealStep        = self.simObj.seal.sealStep # change of position and orientation
        self.waterCurrent    = np.zeros(shape=3) # water current 
    
    def add_particles(self):
        """
        The 'add_particle' function initializes and adds random sized particles in random position from
        'randomInit' function within the Cloud. This forms the partclObjList.
        These positions are described with x,y,z coordinates with the seal being the center of the system.
        """
        while len(self.partclObjList)<self.max_particles:

            posSize = self.randomInit() # get random size and position
            self.partclObjList.append(Particle(self,posSize[0],posSize[1])) # initialise particle and add to list
          
    def randomInit(self):
        """
        The 'randomInit' function returns a list of random sized particles[µm] within a size range 
        of 20µm and 160µm.
        And in returns 'initialCoord' as a random vector (x,y,z) with a range from -1 to 1.
        This is limited by a set maxVectorMagnitute within the getRandomVectorMagnitute
        function.
        """  
        size = np.random.uniform(self.sizeRange[0], self.sizeRange[1], size=(1))*0.00016 + 0.00002
        initialCoord = np.random.uniform(-1,1,size = (3)) # random vector (x,y,z) from -1 to 1
        initialCoord = self.getRandomVectorMagnitude(initialCoord)
        return (initialCoord,size)

    def getRandomVectorMagnitude(self,coordinate):
        """
        The function 'getRandomVectorMagnitude' returns the madnitude of the random vector,
        limited by the size of 'maxVectorMagnitue', which is radius of particles' cloud.
        """
        normCoord = np.empty(3)
        normCoord = coordinate*(np.random.rand(1)*self.maxVectorMagnitue/np.linalg.norm(coordinate))
        return normCoord
        


    def resetParticles(self,relPariclePos,relPariclePosNorm):
        """
        The 'resetParticles' function resets those particles that moved out of the sphere
        (MaxVectorMagnitute) by having them reappear on the opposite site of the sphere,
         with a offset of 5 percent.
         @return new vector discribing the opposite position of the particle to the seal.
        """
        newMagnitude = self.maxVectorMagnitue-(relPariclePosNorm%self.maxVectorMagnitue) # new magnitute of reset position for the particle
        offSet = (np.random.rand(3)-0.5)*(self.maxVectorMagnitue/10)/self.maxVectorMagnitue # offset by 5 % 
        newVector = (relPariclePos+offSet)*-1*newMagnitude/relPariclePosNorm 
        return newVector

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
        for pObject in self.partclObjList:
            # we move particles relative to seal and save vector in p-object trajectory
            pObject.particleMovement(self.sealPosition,self.waterCurrent,self.simObj.seal.sealStep)# for all Particles in List run randomwalk
            # checking if particle norm is still in range
            relParticlePosNorm = np.linalg.norm(pObject.position)
            if  relParticlePosNorm > self.maxVectorMagnitue: # if the magnitude of the particle vector is bigger than 0.3, 
                #respawing particles that drifted away
                pObject.position = self.resetParticles(pObject.position,relParticlePosNorm)

   # We need to safe the start and end postion of all particles before and after
   #the movement. This is safed as oldPosition and newPosition (see particle Movement)
               
       