import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as ss
import matplotlib.cm as cm
from scipy.stats import norm 
from scipy import stats
from matplotlib.colors import Normalize

# N = 300
# # x = np.random.randn(N)
# x = stats.norm.rvs(7,size=N)
# num_bins = 10
# plt.hist(x, bins=num_bins, facecolor='blue', alpha=0.5,edgecolor='black')
# plt.show()

#now i want to make this a surface plot
#lets start by generating some test data dn then we'll use our generated data
x = np.random.randn(500)
y = np.random.randn(500)

x = np.random.normal(15,20,500)
y = np.random.normal(15,20,500)

XY = np.stack((x,y),axis=-1)
intergersx = []
intergersy = []
for val,oth in XY:
	new = int(val)
	new1 = int(oth)
	intergersx.append(new)
	intergersy.append(new1)
intergersx = np.array(intergersx)
intergersy = np.array(intergersy)
XY = np.stack((intergersx,intergersx),axis=-1)

XY_select = XY

xAmplitudes = np.array(XY_select)[:,0]
yAmplitudes = np.array(XY_select)[:,1]

fig = plt.figure() #canvas
ax = fig.add_subplot(111, projection='3d')

hist, xedges, yedges = np.histogram2d(x, y, bins=(5,5), range = [[0,+30],[0,+30]]) #you can change your bins, and the range on which to take data
#hist is a 5x5 matrix, with the populations for each of the subspace parts.
xpos, ypos = np.meshgrid(xedges[:-1]+xedges[1:], yedges[:-1]+yedges[1:]) -(xedges[1]-xedges[0])

xpos = xpos.flatten()*1./2
ypos = ypos.flatten()*1./2
zpos = np.zeros_like (xpos)

dx = xedges [1] - xedges [0]
dy = yedges [1] - yedges [0]
dz = hist.flatten()

cmap = cm.get_cmap('plasma') 

max_height = np.max(dz)  
min_height = np.min(dz)

#scale each z to [0,1], and get their rgb values
ynorm = (ypos-np.min(ypos))/(np.max(ypos)-np.min(ypos))
rgba = [cmap(k) for k in ynorm] 

ax.bar3d(xpos, ypos, zpos, dx, dy, dz, color=rgba, zsort='average')
plt.title("Block Height")
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z (height cm)')
plt.show()

