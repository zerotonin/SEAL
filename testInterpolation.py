
import numpy as np 

x = np.arange(0,180,5)
y = np.sin(x)
xvals = np.arange(0,180,1)
pitchinterp = np.interp(xvals, x, y)
print(pitchinterp)
print(len(pitchinterp))