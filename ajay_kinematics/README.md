09.15.23
alright so all we have to do now in update the dataframe for ajay's kinematics and then we need to output via knn


---

06.12.23
.ignore included to ignore ajay file data
lets do a bit of exploring of the data 
need to chat with siya about how we want to work through the data

---

06.15.2023
we want to calculate:
	1. additional features
	2. height --> min, max, average?
	3. segment angles (diff from joint angles)
	4. markers/joints (is there a difference?) 

we will probably want to calculate some variable and compare with qda (we can try lda but qda is normally better with nonlinear data) and then toss it into a random forest model! wooooo 

we will definitely want to perform some version of a clustering algo. 

i am also uploading another pyscript "ajay_2d_featureeng.py" which is a tidied up summary of what was covered earlier today. things are in functions now to facilitate calling them later... might be easier for later use.... 

-----

06.20.23
chatted with siya today, a for-loop with an average function that will pull for each video would be great; most likely will need to implement some sort of .groupby per video name in vidz_list to function 

definitely do not want to have to include 500+ lines to calcualte for each individual video!~









-----

