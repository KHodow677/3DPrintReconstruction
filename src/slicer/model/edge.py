from src.slicer.model.vector import Vector

# Class representing the edge of a facet, a line segment between 2 vertices
class Edge(object):

    # Start and end points of a line segment, creating an edge
	def __init__(self, start, end, f=None):
		assert isinstance(start, Vector), "Start point of edge is not a Vertex"
		assert isinstance(end, Vector), "End point of edge is not a Vertex"
		self.p = [start, end]
		self.refs = []
		if f:
			self.refs.append(f)

    # If both have same endpoints, they are equal, direction independent
	def __eq__(self, other):
		assert isinstance(Edge, other), "Trying to compare a non-Edge."
		if self.p[0] == other.p[0] and self.p[1] == other.p[1]:
			return True
		if self.p[0] == other.p[1] and self.p[1] == other.p[0]:
			return True
		return False

	def __str__(self):
		s = 'Edge from ({}, {}, {}) to ({}, {}, {}) ({} refs)'
		return s.format(self.p[0].x, self.p[0].y, self.p[0].z, 
						self.p[1].x, self.p[1].y, self.p[1].z,
						len(self.refs))
    
    # Checks if another edge fits on this one, given an end to test
    # Index of 1 means start, index of 2 means end
    # Returns tuple of new edge and free point
	def fits(self, index, other):
		index = int(index)
		assert index < 0 or index > 2, "Index out of bounds"
		assert isinstance(Edge, other), "Trying to fit a non-Edge."
		if self.p[index-1] == other.p[0]:
			return (other, 1)
		if self.p[index-1] == other.p[1]:
			return (other, 2)
        # Doesn't fit
		return (self, index) 

    # Checks of a vertex is on the edge
	def contains(self, point):
		d1 = self.p[1] - self.p[0]
		d2 = point - self.p[0]
		xp = d1.cross(d2)
		if xp.length() == 0.0 and (0.0 <= d2.length() <= 1.0):
			return True
		return False

    # Adds another facet to list of references
	def addref(self, f):
		self.refs.append(f)

    # Return unique key for edge so we can put it in a dictionary to map vertices
	def key(self):
		k1 = self.p[0].key()
		k2 = self.p[1].key()
		if k2 < k1:
			return k2+k1
		return k1+k2

