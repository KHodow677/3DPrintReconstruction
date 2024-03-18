from src.slicer.model.vector import Vector, Normal
from src.slicer.model.edge import Edge

# Class to represent a triangle in 3D Space
class Triangle(object):

	def __init__(self, p1, p2, p3, norm):

		assert isinstance(p1, Vector), "p1 is not a Vector3"
		assert isinstance(p2, Vector), "p2 is not a Vector3"
		assert isinstance(p3, Vector), "p3 is not a Vector3"

		if p1 == p2 or p1 == p3:
			raise ValueError("Degenerate Facet; Coincident Points")

		edge = Edge(p1, p2)
		if edge.contains(p3):
			raise ValueError("Degenerate Facet; Colinear Points")

		del edge

		self.vertices = [p1, p2, p3]

		if isinstance(norm, Normal):
			self.norm = norm
		else:
			d1 = p2 - p1
			d2 = p3 - p2
			xp = d1.cross(d2)
			self.norm = Normal(xp.x, xp.y, xp.z)

	def __str__(self):
		return 'Triangle: %s, %s, %s' % (self.vertices[0], self.vertices[1], self.vertices[2])

    # Find the vector between the 2 points
	def findInterpolatedPoint(self, A, B, targetz):
		# Find the vector between the two...

		V = (B[0]-A[0], B[1]-A[1], B[2]-A[2])
        
		# Therefore the interpolated point = ('n' * V)+A

		# ( x )   
		# ( y ) = n*V + A 
		# (240)

		refz = targetz - A[2]

		# ( x  )
		# ( y  ) = nV
		# (refz)

		n = refz/V[2]

		coords = (n * V[0] + A[0], n * V[1] + A[1])

		return (coords)

	def find_interpolated_points_at_z(self, targetz):
		pair = []
        
        
		# Calculate the coordinates of one segment at z = targetz (between v[0] and v[1])
		if (self.vertices[0].z > targetz and self.vertices[1].z < targetz) or (self.vertices[0].z < targetz and self.vertices[1].z > targetz):
			A = (self.vertices[0].x, self.vertices[0].y, self.vertices[0].z)
			B = (self.vertices[1].x, self.vertices[1].y, self.vertices[1].z)
			pair.append(self.findInterpolatedPoint(A, B, targetz))

		# Calculate the coordinates of one segment at z = targetz (between v[0] and v[2])
		if (self.vertices[0].z > targetz and self.vertices[2].z < targetz) or (self.vertices[0].z < targetz and self.vertices[2].z > targetz):
			A = (self.vertices[0].x, self.vertices[0].y, self.vertices[0].z)
			B = (self.vertices[2].x, self.vertices[2].y, self.vertices[2].z)
			pair.append(self.findInterpolatedPoint(A, B, targetz))

		# Calculate the coordinates of one segment at z = targetz (between v[1] and v[2])
		if (self.vertices[1].z > targetz and self.vertices[2].z < targetz) or (self.vertices[1].z < targetz and self.vertices[2].z > targetz):
			A = (self.vertices[1].x, self.vertices[1].y, self.vertices[1].z)
			B = (self.vertices[2].x, self.vertices[2].y, self.vertices[2].z)
			pair.append(self.findInterpolatedPoint(A, B, targetz))

		if self.vertices[0].z == targetz:
			pair.append((self.vertices[0].x, self.vertices[0].y))
		elif self.vertices[1].z == targetz:
			pair.append((self.vertices[1].x, self.vertices[1].y))
		elif self.vertices[2].z == targetz:
			pair.append((self.vertices[2].x, self.vertices[2].y))

		return pair

