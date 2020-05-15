import numpy as np
class Particle:
<<<<<<< HEAD
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
=======
    def __init__(self, position,size):
        self.size = size # number
        self.position = position # tuple consistin of three coordinates radius,theta,phi
        self.trajectory = [] # list of former positions
    
    def randomWalk(self,stepSize,current):
        # current should be an numpy array of three values containing radius,theta,phi
        self.trajectory.append(self.position)
        self.position + np.random.uniform(-1*stepSize,stepSize,3)
        self.position + current


class Cloud:
    def __init__(self, 
                 name, 
                 max_particles = 400,
                 sizeRange = (0.001,1.0),
                 radiusMax= 10):
>>>>>>> 0c94a9ed14e42a09c792df7744d610fd82238875
        self.name = name # string name
        self.max_particles = max_particles # integer number of particles of the same size and position range
        self.partclObjList = [] # list of particle objects
        self.sizeRange = sizeRange # tuple with the minim and maximum size / radius of our tetrahedron
        self.radiusMax = radiusMax # 6 item wide tuple with the minimum and maximum values of the
<<<<<<< HEAD
       # positions in order: xmin xmax ymin ymax zmin zmax
 
    def add_particles(self):
        while len(self.partclObjList)<self.max_particles:

            posSize = self.randomInit() # get random size and position
            self.partclObjList.append(Particle(posSize[0],posSize[1])) # initialise particle and add to list
          
=======
        # positions in order: xmin xmax ymin ymax zmin zmax

    def add_particles(self):
        while len(self.partclObjList)<self.max_particles:
            posSize = self.randomInit() # get random size and position
            self.partclObjList.append(Particle(posSize[0],posSize[1])) # initialise particle and add to list
            
>>>>>>> 0c94a9ed14e42a09c792df7744d610fd82238875
    def randomInit(self):
        size = np.random.uniform(self.sizeRange[0], self.sizeRange[1], size=(1))
        sphereCoord = np.random.rand(3)
        sphereCoord[0] = sphereCoord[0]*self.radiusMax
        sphereCoord[1] = sphereCoord[1]*np.pi
        sphereCoord[0] = sphereCoord[0]*np.pi*2
        return (sphereCoord,size)

<<<<<<< HEAD

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

     
=======
    def moveParticles(self):
        # all particles should be moved by the same current 
        # all particles should make random steps in the same stepsize range
        # you might need new object variables for current and stepsize
        # if a particle exceeds the radius it should be deleted 
       
       
>>>>>>> 0c94a9ed14e42a09c792df7744d610fd82238875
