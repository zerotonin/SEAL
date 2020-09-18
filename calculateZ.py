import numpy as np 
uShapeDive = np.genfromtxt ('uShapeDiveDepthPitch.csv',usecols=(1), delimiter=",") #0-10
uShapeDiveLift = uShapeDive[1:]- uShapeDive[:-1]
print(uShapeDiveLift)

uShapeDiveSurface = np.genfromtxt ('uShapeDiveDepthPitch.csv', skip_footer=68,usecols=(1), delimiter=",") #0-10
uShapeDiveSurfaceLift = uShapeDiveSurface[:-1]/uShapeDiveSurface[1:]
uShapeDiveDown = np.genfromtxt ('uShapeDiveDepthPitch.csv', skip_header=10,skip_footer=64,usecols=(1), delimiter=",") #11-14
uShapeDiveDownLift = uShapeDiveDown[:-1]/uShapeDiveDown[1:]
uShapeDiveStraight = np.genfromtxt ('uShapeDiveDepthPitch.csv', skip_header=14,skip_footer=13,usecols=(1), delimiter=",") #15.66
uShapeDiveStraightLift = uShapeDiveStraight[:-1]/uShapeDiveStraight[1:]
uShapeDiveUp = np.genfromtxt ('uShapeDiveDepthPitch.csv', skip_header=65,usecols=(1), delimiter=",") #67-87
uShapeDiveUpLift = uShapeDiveUp[:-1]/uShapeDiveUp[1:]

vShapeDiveSurface = np.genfromtxt ('vShapeDiveDepthPitch.csv', skip_header=1,skip_footer=26,usecols=(1), delimiter=",") #0-12
uShapeDiveSurfaceLift = uShapeDiveSurface[:-1]/uShapeDiveSurface[1:]
vShapeDiveDown = np.genfromtxt ('vShapeDiveDepthPitch.csv', skip_header=12,skip_footer=12,usecols=(1), delimiter=",") #13-26
uShapeDiveDownLift = uShapeDiveDown[:-1]/uShapeDiveDown[1:]
vShapeDiveUp = np.genfromtxt ('vShapeDiveDepthPitch.csv', skip_header=26,usecols=(1), delimiter=",") #27-38
uShapeDiveUpLift = uShapeDiveUp[:-1]/uShapeDiveUp[1:]

