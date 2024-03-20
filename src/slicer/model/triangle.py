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
    # Find the vector between the 2 points
    def findInterpolatedPoint(self, A, B, targetz):
        # Find the vector between the two...
        V = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
        
        # Therefore the interpolated point = ('n' * V) + A
        refz = targetz - A[2]
        n = refz / V[2]
        coords = (n * V[0] + A[0], n * V[1] + A[1])
        return coords

    # Find interpolated points along the z axis at a specified z coordinate
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

    # Find interpolated points along the x axis at a specified x coordinate
    def find_interpolated_points_at_x(self, targetx):
        pair = []

        # Calculate the coordinates of one segment at x = targetx (between v[0] and v[1])
        if (self.vertices[0].x > targetx and self.vertices[1].x < targetx) or (self.vertices[0].x < targetx and self.vertices[1].x > targetx):
            A = (self.vertices[0].y, self.vertices[0].z, self.vertices[0].x)
            B = (self.vertices[1].y, self.vertices[1].z, self.vertices[1].x)
            pair.append(self.findInterpolatedPoint(A, B, targetx))

        # Calculate the coordinates of one segment at x = targetx (between v[0] and v[2])
        if (self.vertices[0].x > targetx and self.vertices[2].x < targetx) or (self.vertices[0].x < targetx and self.vertices[2].x > targetx):
            A = (self.vertices[0].y, self.vertices[0].z, self.vertices[0].x)
            B = (self.vertices[2].y, self.vertices[2].z, self.vertices[2].x)
            pair.append(self.findInterpolatedPoint(A, B, targetx))

        # Calculate the coordinates of one segment at x = targetx (between v[1] and v[2])
        if (self.vertices[1].x > targetx and self.vertices[2].x < targetx) or (self.vertices[1].x < targetx and self.vertices[2].x > targetx):
            A = (self.vertices[1].y, self.vertices[1].z, self.vertices[1].x)
            B = (self.vertices[2].y, self.vertices[2].z, self.vertices[2].x)
            pair.append(self.findInterpolatedPoint(A, B, targetx))

        if self.vertices[0].x == targetx:
            pair.append((self.vertices[0].y, self.vertices[0].z))
        elif self.vertices[1].x == targetx:
            pair.append((self.vertices[1].y, self.vertices[1].z))
        elif self.vertices[2].x == targetx:
            pair.append((self.vertices[2].y, self.vertices[2].z))

        return pair

    # Find interpolated points along the y axis at a specified y coordinate
    def find_interpolated_points_at_y(self, targety):
        pair = []

        # Calculate the coordinates of one segment at y = targety (between v[0] and v[1])
        if (self.vertices[0].y > targety and self.vertices[1].y < targety) or (self.vertices[0].y < targety and self.vertices[1].y > targety):
            A = (self.vertices[0].x, self.vertices[0].z, self.vertices[0].y)
            B = (self.vertices[1].x, self.vertices[1].z, self.vertices[1].y)
            pair.append(self.findInterpolatedPoint(A, B, targety))

        # Calculate the coordinates of one segment at y = targety (between v[0] and v[2])
        if (self.vertices[0].y > targety and self.vertices[2].y < targety) or (self.vertices[0].y < targety and self.vertices[2].y > targety):
            A = (self.vertices[0].x, self.vertices[0].z, self.vertices[0].y)
            B = (self.vertices[2].x, self.vertices[2].z, self.vertices[2].y)
            pair.append(self.findInterpolatedPoint(A, B, targety))

        # Calculate the coordinates of one segment at y = targety (between v[1] and v[2])
        if (self.vertices[1].y > targety and self.vertices[2].y < targety) or (self.vertices[1].y < targety and self.vertices[2].y > targety):
            A = (self.vertices[1].x, self.vertices[1].z, self.vertices[1].y)
            B = (self.vertices[2].x, self.vertices[2].z, self.vertices[2].y)
            pair.append(self.findInterpolatedPoint(A, B, targety))

        if self.vertices[0].y == targety:
            pair.append((self.vertices[0].x, self.vertices[0].z))
        elif self.vertices[1].y == targety:
            pair.append((self.vertices[1].x, self.vertices[1].z))
        elif self.vertices[2].y == targety:
            pair.append((self.vertices[2].x, self.vertices[2].z))

        return pair
