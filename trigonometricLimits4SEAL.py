import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from tqdm import tqdm
from mpl_toolkits.mplot3d import Axes3D


def StepSizeTrans(rotAngleRad,distanceM):
    """ This fuction calculates the optic flow vector length for a translation.
    Einschränkung: Die Rotationswinkel die wir betrachten liegen <= pi
    Gegeben für jeden Fall ist:

    phi = rotationswinkel des Tiers
    a   = Distanz Tier <-> Objekt
    a   = höhe des Dreiecks

    of vector länge
    |------|
    object
    ________    _
    \      /    |
     \    /     |  a
      \  /      |
       \/       |
       phi      -
    
    animal
    
    Schritt 1: Ich fälle die Höhe des Dreiecks 
               damit wird es als rechtwinkeliges 
               Dreieick betrachten können.

    beta = phi/2
    gamma = pi/2
    alpha = pi/2 - beta

    gegenkatete = a
    ankatete = OF-Vektorlänge/2

                Gegenkatete
    tan(alpha) = -------------                          (1)
                    Ankatete
                    
                Gegenkatete  
    Ankatete   = ---------------
                    tan(alpha)
                    
                        Gegenkatete
    OF Vektorlänge = 2* -------------                   (2)
                        tan(alpha)
                        
                        
                            Distanz zum Objekt
    OF Vektorlänge = 2* -----------------------------   (3)
                        tan(pi/2 - (Drehwinkel/2))
                                            ´
                                           
    @param rotAngleRad:      float default: ?
        float that defines the rotational Angle in rad (Drehwinkel)
    @param distanceM:        float default: ?    
        float that defines the distance between the seal agent and the 
        observed object in meter.
    
    @return the length of the optic flow vector projected on the seal retina?
    
    """
    return 2*distanceM/np.tan(np.pi/2 - rotAngleRad/2)


# 
    """
        given a certain step size (b), and a distance (a) how large is the phi angle
        |------|
            b   
        ________    _
        \      /    |
        \    /     |  a
        \  /      |
        \/       |
        phi      -

        
                        Gegenkatete
        alpha = arctan  -------------                          (1)
                        Ankatete
        
        beta = 90° -alpha
        phi  = 2 * beta
    """

def OFvectorNormTrans(distance,stepLength):
    """
    This function calculates the angel phi measured during translational movement, 
    defined by the translational stepsize the animal took in meter and the distance 
    of the observed object from the seal agent

    @return the phi angle in rad 
    """
    return 2*(np.pi/2 - np.arctan2(distance,stepLength))


def OFvectorNormRot(angleRad):
    """
    This function returns the Optic Flow vector norm during a rotational movement.

    @param angleRad:             float default: ?
        a float describing the rotational angle in rad (0<x<pi)
    """
    return np.abs(angleRad)

"""
Calculating and plotting the translational OF vector norm in correlation 
to the stepsize of the seal agend and the distance of the observed objects

@param bins:             int default: 1000
    an int setting the number of tested stepSizes and distances
@param stepsize:             float
    a float of evenly spaced numbers over a specified interval defining
    the stepsize in meter
@param distances:            float
    a float of evenly spaced numbers over a specified interval defining
    the distance between the sealagent and the object in meter 
@param results:              array of float
    a new array of given shape (defined by stepsizes and distances) 
    and type, filled with zeros as placeholder. 
       
"""
bins =1000
stepSizes = np.linspace(0.001,20,bins)
distances = np.linspace(0.001,20,bins)

result = np.zeros(shape=(bins,bins))

# calculating the translational optic flow vector norm 
# for each stepsize/distance combination
stepC = 0
for step in tqdm(stepSizes):
    distanceC = 0
    for distance in distances:
        #print(stepC,distanceC)
        result[stepC,distanceC] = OFvectorNormTrans(distance,step)
        distanceC +=1
    stepC +=1 

fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

# Make data.
X, Y = np.meshgrid(distances, stepSizes)

# Plot the surface.
surf = ax.plot_surface(X, Y, result,
                       linewidth=0, antialiased=False)
ax.set_xlabel('distance, m')
ax.set_ylabel('stepSize, m')
ax.set_zlabel('OF vectorLength, rad')
xx,yy = np.meshgrid([0,20],[0,20])
ax.plot_surface(xx, yy,np.array([[0,0],[np.pi,np.pi]]),alpha=.5)
plt.show()

"""
adding an additional dimension with the rotational angle to visualize
the impact of rotational movement in regard to the shift on the retina 
caused by passing by objects in relation to the stepsize of the animal 
and the distance of the passing objects
"""
bins =100
angles = np.linspace(0.001,np.pi,bins)
stepSizes = np.linspace(0.001,20,bins)
distances = np.linspace(0.001,2,bins)
result2 = np.zeros(shape=(bins,bins,bins))
stepC = 0
for step in tqdm(stepSizes):
    distanceC = 0
    for distance in distances:
        angleC = 0
        for angle in angles:
            #print(stepC,distanceC)
            transNorm = OFvectorNormTrans(distance,step)
            rotNorm = OFvectorNormRot(angle)
            result2[stepC,distanceC,angleC] = (transNorm-rotNorm)/(transNorm+rotNorm)
            angleC += 1        
        distanceC +=1
    stepC +=1 

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
# Plot both positive and negative values between +/- 1.2
pos_neg_clipped = ax.imshow(result2[:,:,20], cmap='RdBu', vmin=-1, vmax=1,
                             interpolation='none')
# Add minorticks on the colorbar to make it easy to read the
# values off the colorbar.
cbar = fig.colorbar(pos_neg_clipped, ax=ax, extend='both')
cbar.minorticks_on()
plt.show()
