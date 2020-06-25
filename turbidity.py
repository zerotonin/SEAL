import numpy as np
import math as m 
import copy 
#from sympy import *

class Particle:
    '''
    Class 'Particle' holds information about the size and position of a particle inside the turbidity simulation. 
    Generated particles form cloud (class 'Cloud') with a seal as a center of a particles' cloud (class 'Seal').
    The trajectories of particles' movement are influanced by water currents, water viscosity and obstacles e.g.
    corals, rocks etc. (class 'Enviroment')
    '''

    def __init__(self,cloudObj, position,size, groundLevel = -70.0,samplesPerSec =10.0):
        '''
        This function initialises a list of random sized particles[µm] with a random x,y,z position, limited by
        radius of the visual field of a seal (@ param maxVectorMagnitue in the 'Seal' class). Particles are in 
        cartesian 3D space with the seal as a center postion (0,0,0). Particles are moving by Brownian motion, 
        where we consider viscosity of the ocean' water, so particles have different velocity of random walk 
        movement (Brownian motion) depending on the depth of their position in the 3D space of ocean (z axis 
        position).Trajectories of particles movement are also influenced by the water currents.

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
            the list of particles that are visible and move actively (????)
        @param groundLevel  float  default: -70.0
            the depth of an ocean [m] that is limited by the value of -70 [m].
        @param temperature  float default: none (????)
            the temperature [K] of water that changes with the depth of ocean. 
        @param viscosity    float default: none (????)
            viscosity of saltwater [Ns/m²,Pa*s] that depends on temerature and vary with the depth.
        @param samplesPerSec float default: 10.0 
            the model's basic frequency. How often it updates in one second.
        '''
        self.cloudObj       = cloudObj # particles form cloud object
        self.size           = size # radius of the particles [µm]
        self.position       = position # tuple consisting of three coordinates x,y,z
        self.trajectory     = [] # list of former positions x,y,z
        self.activeMovement = True #particles actively move by Brownian motian
        self.visible        = True #particles are in the visual field of a seal
        self.OFavailable    = list() #list of available particles
        self.groundLevel    = self.cloudObj.simObj.environment.oceanDepth # depth of ocean [m]
        self.temperature    = float("NAN")
        self.viscosity      = float("NAN")
        self.samplesPerSec  = self.cloudObj.simObj.sps #samples per second
        

    def randomWalk(self):
        """
        The function 'randomWalk' define the random step size of a particle that moves via 
        Brownian motion in the space of seal's visual field.

        @ return a random array of particle's coordinates position x,y,z, influenced by Brownian motion
        step size         
        """
        
        stepSize = self.getBrownianMotionStepSize()
 
        return np.random.choice((-1,1),3)*stepSize

    
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
        self.temperature = 3.1643818163582185+5.289978692454068*np.exp(-1*(self.absPosition[2]+2.854807838826537)**2/(2*13.943640614002176**2))
    
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
        the temperature2StepSize function runs a temperature dependent brownian motion for each particle.

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




    def particleMovement(self,sealPosition,waterCurrent,sealStep):
        """
        the particleMovement function moves all particles relative to the seal postion and activly by 
        brownian motion. 
        For the statecheck the absolute position of the particles is calculated to calculate the respetive 
        depth and temperature.
        Next the active movement is checked, and those particle beeing visbile and freefloating are moved
        by the brownian motion(randomwalk), the waterCurrent and the sealStep
        Those particle on the seafloor that are not activly moving are just moved by the SealStep
        Those particles above water and 10cm under the seefloor are not moving.
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
    The Cloud class holds information about the name and the size of the turbidity Sphere/Cloud
    as well as the amount and size of particles simulated within the cloud.
    
    The Cloud class holds functions to create and move particles within the cloud, and 
    converts their coordinates from spheric coordinate system to cartasian coordinate system
    and back. This allows to run all active movements of the partcile and the passive movement
    by the seal agend in a cartasian coordinate system. 
    """

    def __init__(self,
                simObj,
                max_particles = 400,
                sizeRange = (0.001,1.0),
                maxVectorMagnitue= 10):
                #super()__init__(self) # needs to be vector magnitute , discribing the length of a vector
        """ 
        @param name            float default: none
            a individual name should be given to each new version of the turbidity sphere
            (different particle density, particle sizes)
        @param max_particles     float default: none
            this manual choosen number sets the number of particles being placed inside the 
            turbidity sphere, this parameter represent the density of the particles
        @param sizeRange       tuple default=none
            tuple with the minimum and maximum size of the particles.(min,max)
        @param maxVectorMagnitute       float default= none
            this value sets the Radius of the turbidty sphere, this value should be taken from
            the maximum sight of the habor seal underwater
        @param partclObjList    list default=none  
            list of particle objects within the turbidity cloud. length of the list defined by 
            max_particles 
        @param sealPosition 
            center of the coordinate system of the seal in distance to the (o,0,0) point in the world
        @param sealOrientation 
            Orientation as yaw, pitch, roll
        @param sealStep
            change of position and orientation (x,y,z,yaw,pitch,roll)
        @param sealTrajectory 
            list of seal movement vectors ? 
        @param waterCurrent
            force of the water current 
        """
        self.simObj = simObj # string name
        self.max_particles = max_particles # integer number of particles of the same size and position range
        self.partclObjList = [] # list of particle objects
        self.sizeRange = sizeRange # tuple with the minim and maximum size / radius of our tetrahedron
        self.maxVectorMagnitue = maxVectorMagnitue # 6 item wide tuple with the minimum and maximum values of the
        self.sealPosition    = self.simObj.seal.sealPosition #centre of the coordinate system of the Seal in disctance to (0,0,0) of world
        self.sealOrientation = self.simObj.seal.sealOrientation  # orientation as yaw pitch roll
        self.sealStep        = self.simObj.seal.sealStep # change of position and orientation
        self.waterCurrent    = np.zeros(shape=3) # force of the water current 
    
    def add_particles(self):
        """
        The add_particle function initializes and adds random sized particles in random position 
        within the Cloud. This forms the partclObjList.These positions are descriebed with
        x,y,z with the seal being the center of the coordinate system
        """
        while len(self.partclObjList)<self.max_particles:

            posSize = self.randomInit() # get random size and position
            self.partclObjList.append(Particle(self,posSize[0],posSize[1])) # initialise particle and add to list
          
    def randomInit(self):
        """
        the randomInit function creates random numbers for each coordinate (x,y,z).
        This is limited by a set maxVectorMagnitute within the getRandomVectorMagnitute
        function

        Sizes of the particles are between 20µm and 160µm
        """  
        size = np.random.uniform(self.sizeRange[0], self.sizeRange[1], size=(1))*0.00016 + 0.00002
        initialCoord = np.random.uniform(-1,1,size = (3)) # rancom vector (x,y,z) from -1 to 1
        initialCoord = self.getRandomVectorMagnitude(initialCoord)
        return (initialCoord,size)

    def getRandomVectorMagnitude(self,coordinate):
        """
        Creats a vector with a random magnitute from 0 to maxVectorMagnitue(10), Thereby
        randomly choosen positions with a distance of less than 10m for each particle 
        sorrounding the center of the seals coordinate system is choosen starting at position 
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
        and a current and passivly by a SealStep. 
        ############################################################################
        We need to safe the start and end postion of all particles before and after
        the movement. This is safed as oldPosition and newPosition (see particle Movement)
        ############################################################################
        Those particle who get a higher vector magnitute than the MaxVectorMagnitute(10),
        need to reset to opposite side of the seals visual sphere.The relPariclePosNorm 
        calculates the magnitude of the particle Vectors.Those particles that have a 
        higher magnitude from the seal than the MaxVectorMagnitude need to reset to a 
        new postion which is defined by the resetParticle function.
        """    
        #update water current
        self.waterCurrent = self.simObj.environment.getWaterCurrent()
        for pObject in self.partclObjList:
            # we move particles relative to seal and save vector in p-object trajectory
            pObject.particleMovement(self.sealPosition,self.waterCurrent,self.simObj.seal.sealStep)             # for all Particles in List run randomwalk
            # checking if particle norm is still in range
            relParticlePosNorm = np.linalg.norm(pObject.position)
            if  relParticlePosNorm > self.maxVectorMagnitue: # if the magnitude of the particle vector is bigger than 10, 
                #respawing particles that drifted away
                pObject.position = self.resetParticles(pObject.position,relParticlePosNorm)
               
       