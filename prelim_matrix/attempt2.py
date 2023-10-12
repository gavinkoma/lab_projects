import math
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as ss
from scipy.stats import norm 

#theres the dist
mean = 15
std = 5
size = 200
values = np.random.normal(mean,std,size)
new = []
for val in values:
	val = int(val)
	new.append(val)
values = np.array(new)

#here is the hist
#plt.figure()
#plt.hist(values,20,edgecolor='black')
#plt.axvline(values.mean(),color='k',linestyle='dashed',linewidth=2)
#plt.show()

plt.figure()
labels, counts = np.unique(values, return_counts=True)
plt.bar(labels, counts, align='center')
plt.gca().set_xticks(labels)
plt.show()

#lets add a line plot on top of it
# mean and standard deviation 
mu, std = norm.fit(values)  
xmin, xmax = plt.xlim() 
x = np.linspace(xmin, xmax, 100) 
p = norm.pdf(x, mu, std) 
  
plt.plot(x, p, 'k', linewidth=2) 
title = "Fit Values: {:.2f} and {:.2f}".format(mu, std) 
plt.title(title) 
  
plt.show() 




#im not entirely sure how to go about this
def normal_dist():
	return

def histogram_generation():

	return

def surface_plot():

	return

def colorize():

	return

def stl_output():

	return

#done

def main():
	normal_dist()
	return

main()

