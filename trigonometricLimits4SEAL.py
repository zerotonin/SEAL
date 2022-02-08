import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from tqdm import tqdm

def OFvectorNorm(rotAngleRad,distanceM):
    """ This fuction calculates the optic flow vector length
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
    
    Schritt 1: Ich fälle die Höhe des Dreiecks  damit wird es rechtwinkeliges Dreieick.

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
                                           

    :param rotAngleRad: [description]
    :type rotAngleRad: [type]
    :param distanceM: [description]
    :type distanceM: [type]
    :return: [description]
    :rtype: [type]
    """
    return 2*distanceM/np.tan(np.pi/2 - rotAngleRad/2)


bins =1000
angles = np.linspace(0.001,np.pi-0.0001,bins)
distances = np.linspace(0.001,0.1,bins)

result = np.zeros(shape=(bins,bins))

angleC = 0
for angle in tqdm(angles):
    distanceC = 0
    for distance in distances:
        #print(angleC,distanceC)
        result[angleC,distanceC] = OFvectorNorm(angle,distance)
        distanceC +=1
    angleC +=1 


fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

# Make data.
X, Y = np.meshgrid(distances, angles)

# Plot the surface.
surf = ax.plot_surface(X, Y, np.log(result),
                       linewidth=0, antialiased=False)
ax.set_xlabel('distance, m')
ax.set_ylabel('rotation angle, rad')
ax.set_zlabel('log OF vectorLength, m')
plt.show()