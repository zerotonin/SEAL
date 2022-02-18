import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from tqdm import tqdm
from mpl_toolkits.mplot3d import Axes3D


def OFvectorNormTrans(distance,stepLength):
    """
    This function calculates the angel phi measured during translational movement, 
    defined by the translational stepsize the animal took in meter and the distance 
    of the observed object from the seal agent

    @return the phi angle in rad 

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
angles = np.linspace(0.0,np.pi,bins)
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

i =45
fig = plt.figure()
ax = fig.add_subplot(1,1,1)
# Plot both positive and negative values between +/- 1.2
pos_neg_clipped = ax.imshow(result2[:,:,i], cmap='RdBu', vmin=-1, vmax=1,
                             interpolation='none')
# Add minorticks on the colorbar to make it easy to read the
# values off the colorbar.
cbar = fig.colorbar(pos_neg_clipped, ax=ax, extend='both')
cbar.minorticks_on()
ax.set_xlabel('distance, mm')
ax.set_ylabel('translational speed, mm')
ax.set_title(f' rotaional angle velocity {np.round(np.rad2deg(angles[i]),2)} deg')
plt.show()


'''

OFs = summarised optic flow
OFt = translational optic flow
OFr = rotational optic flow

d = distance to object
s = step length of viewer
phi = rotational angle of viewer


OFg = OFt+OFr              (0)
OFr = -phi                 (1)
OFt = 2(pi/2-arctan2(s/d)) (2)


OFg = 2(pi/2-arctan2(s/d))-phi (3)

if formula 3 results in zero the OF is 1:! mixture of rotation and translation

0                 = 2(pi/2-arctan2(s/d))-phi
0                 = pi-2arctan2(s/d) - phi   | +2 arctan2(s/d)
2arctan2(s/d)     = pi -phi                  | :2
arctan2(s/d)      = (pi-phi)/2               | tan
s/d               = tan((pi-phi)/2)          | *d & /tan((pi-phi)/2)
s/tan((pi-phi)/2) = d  (4)

we can now vary s and phi respectivly to determine critical d (1:1 mixture)

We than show that  our physiological feasable combinations or well below critical d


we also want to show the critical phi to prove that under a given turbidity d and a given
s of the seal critical phi is not reached as it is not performable seal.

phi = -2(pi/2-arctan2(s/d))

'''
bins =1000
stepSizes = np.linspace(0,5.36,bins) # max swim speed https://www.adfg.alaska.gov/index.cfm?adfg=harborseal.printerfriendly
distances = np.linspace(0.0001,80,bins) # max under water horizon is 80 m  Davies-Colley, R. J.; Smith, D. G. (1995). "Optically pure waters in Waikoropupu ('Pupu') Springs, Nelson, New Zealand" (PDF). New Zealand Journal of Marine and Freshwater Research. The Royal Society of New Zealand. 29 (2): 251–256. doi:10.1080/00288330.1995.9516658. Retrieved 19 October 2013.0028-8330/95/2902-0251
critical_phi = np.zeros(shape=(bins,bins))
stepC = 0
for step in tqdm(stepSizes):
    distanceC = 0
    for distance in distances:
        #print(stepC,distanceC)
        critical_phi[stepC,distanceC] =  np.rad2deg(np.abs(-3*(np.pi/2-np.arctan2(distance,step))))          
        distanceC +=1
    stepC +=1 

fig = plt.figure()
ax = fig.add_subplot(1,1,1)
# Plot both positive and negative values between +/- 1.2
           
c = ax.pcolor(distances,stepSizes,critical_phi, cmap='inferno')      
# Add minorticks on the colorbar to make it easy to read the
# values off the colorbar.
cbar = fig.colorbar(c, ax=ax)
cbar.minorticks_on()
cbar.set_label('critical rotation velocity, deg*$s^{-1}$')
ax.set_xscale("log")
ax.set_xlabel('distance, m')
ax.set_ylabel('translational speed, m*s$^{-1}$')
ax.set_title(f'1:1 translational roation OF')
plt.show()