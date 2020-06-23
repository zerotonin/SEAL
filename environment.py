import numpy as np 

class Environment:
    def __init__(self):
        
        self.oceanSurface = 0
        self.oceanDepth = -70
        self.activeMovement = True 
        self.visible        = True 

    def waterCurrent(self):
        """
        should be defined as moving vector (x.y.z) which should change dependent on position in 3D world ? 
        dependen on all 3 dimensions ? 
        look for waterCurrent values in paper ??
        """
        self.waterCurrent = np.array([0.0,2.0,0.0]) # just a simple example will be changed later 

    
    def checkVisibility(self,oceanSurface,oceanDepth):
       """
       Function checks if coordinates of particles are inside of a sphere and visible. 
       Particle is not visible if it's above the surface level and if it's below ground level. 
       """
       if self.absPosition[2] >= self.oceanSurface or self.absPosition[2] <= self.oceanDepth-0.1: # how to get self.absoultePosition from turbidity.particles ? or does it go the other way ? 
           self.visible = False
       else: 
           self.visible = True

    def creatObstacles(self):

        #obstacle = [[0:1],[0:1],[self.oceanSurface:self.oceanDepth]] # creat an obstacle going from 0-1m in x and 0-1 m in y dimension 

    def checkActiveMovement(self):
       """
       The checkActiveMovement function defines which particles are moving and which are stationary.
       Those particles with a self.position[2](z value) between -70m and -70.1m are stationary. 
       Those that are between 0 and -70m are moving according to the randomWalk function. 
       """

       if self.visible == True:
           if self.absPosition[2]<= self.oceanDepth or Obstacle.left <= self.absPosition[0] <= Obstacle.right and Obstacle.top <= self.absPosition[1] <= Obstacle.bottom:
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

    def SealStateCheck(self):

class Obstacle:

    """
    A rectangle identified by two points.
    The rectangle stores left, top, right, and bottom values.
    Coordinates are based on screen coordinates.
    origin                               top
     +-----> x increases                |
     |                           left  -+-  right
     v                                  |
    y increases                         bottom
    set_points  -- reset rectangle coordinates
    """

    def __init__(self, pt1, pt2):
        """Initialize a rectangle from two points."""
        self.set_points(pt1, pt2)

    def set_points(self, pt1, pt2):
        """Reset the rectangle coordinates."""
        (x1, y1) = pt1.as_tuple()
        (x2, y2) = pt2.as_tuple()
        self.left = min(x1, x2)
        self.top = min(y1, y2)
        self.right = max(x1, x2)
        self.bottom = max(y1, y2)
    # somehow create a list of specific obstacles  ? 
    