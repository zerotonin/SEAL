
import numpy as np
import matplotlib.patches as mpatches 
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt

def draw_self_loop(center, radius, facecolor='#2693de', edgecolor='#000000', theta1=-30, theta2=180):
    
    # Add the ring
    rwidth = 0.02
    ring = mpatches.Wedge(center, radius, theta1, theta2, width=rwidth)
    # Triangle edges
    offset = 0.02
    xcent  = center[0] - radius + (rwidth/2)
    left   = [xcent - offset, center[1]]
    right  = [xcent + offset, center[1]]
    bottom = [(left[0]+right[0])/2., center[1]-0.05]
    arrow  = plt.Polygon([left, right, bottom, left])
    p = PatchCollection(
        [ring, arrow], 
        edgecolor = edgecolor, 
        facecolor = facecolor
    )
    ax.add_collection(p)
#---------------------------------------------
# Drawing time
#---------------------------------------------
fig, ax = plt.subplots(figsize=(6,6))
draw_self_loop(center=(.5, .7), radius=.1,theta2=60)
draw_self_loop(center=(.2, .2), radius=.15, facecolor='#ffb83c', edgecolor='gray')
draw_self_loop(center=(.8, .3), radius=.15, facecolor='#39c1c8', edgecolor=None)
plt.show()