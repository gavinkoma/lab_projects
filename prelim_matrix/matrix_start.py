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
array = np.random.normal(15,1,(20,20))
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


#this one works but i think there can be better
###
#recall: np.random.normal(mean,std,array)
mu,sigma = 15,2 #let the hip height be at 7cm for now
s = np.random.normal(mu,sigma,100)
new = []
for val in s:
	val = int(val)
	#new = array(val)
	new.append(val)
s = np.array(new)

#plot histogram in addition to the other values
count,bins,ignored = plt.hist(s,8,density=True,edgecolor='black')

#plot itself
plt.plot(bins, 
	1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ),
	linewidth=2, 
	color='r'
	#edgecolor='black'
	)

plt.ylabel("count per block")
plt.xlabel("height in cm")

plt.show()


#i am desperate for this to work 
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

N = 200
x = stats.norm.rvs(loc=7,scale=1,size=N) #pull samples from standard dist
num_bins = 9 #define how many different blocks
new = []
for val in x:
	val = int(val)
	new.append(val)
x = np.array(new)
plt.hist(x, bins=num_bins, facecolor='blue', alpha=0.5,edgecolor='black')
plt.show()

#y = np.linspace(4, 9, 1000)
#bin_width = (x.max() - x.min()) / num_bins
#plt.plot(y, stats.norm.pdf(y) * N * bin_width)




plt.ylabel("# of blocks")
plt.xlabel("height in cm")
plt.show()



