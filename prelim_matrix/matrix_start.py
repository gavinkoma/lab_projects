#!usr/bin/python
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#okay so im not actually starting this right now because fuck lol but
#essentially we need to set our matrix array dimensions
#we probably will want some logic that determines how many bits this should be

#within the created array, each 'block' will have 1unit distance going in x and y
#the z dimensions will be randomly generated from a user input hip height 
#i need this to then make a lovely graph that shows the blocks rising into the air

#lets just say hip height is 15cm (this is way too high)
#np.random.normal(mean,std,(size))
array = np.random.normal(15,0,(50,8))
z = np.array(array)

#define the plot
ax = plt.axes(projection="3d")

#z = np.array([[248, 236,289,300,267,225,266,265,259,279,269,335],[246,253,241,232,276,213,198,201,222,229,193,237],[182,180,200,192,233,211,227,220,174,187,181,197],[124,102,137,130,144,168,149,164,168,156,90,156],[117,124,133,119,155,140,133,120,130,134,138,102],[155,140,137,125,146,102,129,114,119,113,132,122],[104,117,119,138,137,118,117,128,131,133,119,133],[136,115,108,105,133,104,121,135,136,127,135,112],[84,87,93,116,123,110,90,123,112,115,92,107],[118,94,100,83,132,90,111,91,98,116,100,95],[101,76,115,121,108,102,94,80,83,104,101,81],[86,86,109,105,95,75,18,87,92,99,101,128]])

#evenly spaced values given within an interval
y = np.arange(len(z))
print(y)
x = np.arange(len(z[0]))
print(x)

#use meshgrid to return a list of coordinate matrices from coordinate vectors
#we can create a nice lil thanng with this
(x ,y) = np.meshgrid(x,y)
print(x,y)

#make a 3d dataset given x & y & z of a matrix!
ax.plot_surface(x,y,z)
plt.show()