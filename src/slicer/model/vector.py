from hashlib import md5
from math import fabs, sqrt

TOLERANCE = 1e-7

# Class for a 3D Catesian Point
class Vector(object):

    # Creates a 3D vector from coords
	def __init__(self, x, y, z):
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)

		key_string = '(%f, %f, %f)' % (self.x, self.y, self.z)
		key_string = key_string.encode('utf-8')
		self.hash = md5(key_string).hexdigest()

	def __add__(self, other):
		return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other):
		return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

	def __str__(self):
		return '(%f, %f, %f)' % (self.x, self.y, self.z)

	def __eq__(self, other):
		if other == None:
			return False
		if (fabs(self.x - other.x) < TOLERANCE and
			fabs(self.y - other.y) < TOLERANCE and
			fabs(self.z - other.z) < TOLERANCE):
			return True
		else:
			return False

	def __mul__(self, multi):
		return Vector(self.x * multi, self.y * multi, self.z * multi)

    # Direct distance between point and origin 
	def length(self):
		return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

    # Calculate cross product with other vector
	def cross(self, other):
		return Vector(self.y*other.z-self.z*other.y,
						self.z*other.x-self.x*other.z,
						self.x*other.y-self.y*other.x)

# Class for a 3D normal vector in catesian space
class Normal(Vector):

	def __init__(self, dx, dy, dz):
		self.dx = float(dx)
		self.dy = float(dy)
		self.dz = float(dz)

		l = sqrt(self.dx*self.dx+self.dy*self.dy+self.dz*self.dz)

		if l == 0.0:
			raise ValueError("Length of Vector is 0")

		super(Normal, self).__init__(self.dx, self.dy, self.dz)

	def __str__(self):
		return 'Normal: (%f, %f, %f)' % (self.dx, self.dy, self.dz)

