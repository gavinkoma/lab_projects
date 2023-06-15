class Person(object):
	def __init__(self,age,name):
		self.age = age
		self.name = name


	def __str__(self):
		return "<" + self.name + ",'" + str(self.age) + ">"

p1 = Person(24, "john")