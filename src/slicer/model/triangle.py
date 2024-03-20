from src.slicer.model.vector import Vector, Normal
from src.slicer.model.edge import Edge
from numba import njit

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
@njit(fastmath=True)
def findInterpolatedPoint(A, B, targetz):
    # Find the vector between the two...
    V = (B[0] - A[0], B[1] - A[1], B[2] - A[2])
    
    # Therefore the interpolated point = ('n' * V) + A
    refz = targetz - A[2]
    n = refz / V[2]
    coords = (n * V[0] + A[0], n * V[1] + A[1])
    return coords

# Find interpolated points along the z axis at a specified z coordinate
def find_interpolated_points_at_z(targetz, vertices):
    pair = []

    # Calculate the coordinates of one segment at z = targetz (between v[0] and v[1])
    if (vertices[0].z > targetz and vertices[1].z < targetz) or (vertices[0].z < targetz and vertices[1].z > targetz):
        A = (vertices[0].x, vertices[0].y, vertices[0].z)
        B = (vertices[1].x, vertices[1].y, vertices[1].z)
        pair.append(findInterpolatedPoint(A, B, targetz))

    # Calculate the coordinates of one segment at z = targetz (between v[0] and v[2])
    if (vertices[0].z > targetz and vertices[2].z < targetz) or (vertices[0].z < targetz and vertices[2].z > targetz):
        A = (vertices[0].x, vertices[0].y, vertices[0].z)
        B = (vertices[2].x, vertices[2].y, vertices[2].z)
        pair.append(findInterpolatedPoint(A, B, targetz))

    # Calculate the coordinates of one segment at z = targetz (between v[1] and v[2])
    if (vertices[1].z > targetz and vertices[2].z < targetz) or (vertices[1].z < targetz and vertices[2].z > targetz):
        A = (vertices[1].x, vertices[1].y, vertices[1].z)
        B = (vertices[2].x, vertices[2].y, vertices[2].z)
        pair.append(findInterpolatedPoint(A, B, targetz))

    if vertices[0].z == targetz:
        pair.append((vertices[0].x, vertices[0].y))
    elif vertices[1].z == targetz:
        pair.append((vertices[1].x, vertices[1].y))
    elif vertices[2].z == targetz:
        pair.append((vertices[2].x, vertices[2].y))

    return pair

# Find interpolated points along the x axis at a specified x coordinate
def find_interpolated_points_at_x(targetx, vertices):
    pair = []

    # Calculate the coordinates of one segment at x = targetx (between v[0] and v[1])
    if (vertices[0].x > targetx and vertices[1].x < targetx) or (vertices[0].x < targetx and vertices[1].x > targetx):
        A = (vertices[0].y, vertices[0].z, vertices[0].x)
        B = (vertices[1].y, vertices[1].z, vertices[1].x)
        pair.append(findInterpolatedPoint(A, B, targetx))

    # Calculate the coordinates of one segment at x = targetx (between v[0] and v[2])
    if (vertices[0].x > targetx and vertices[2].x < targetx) or (vertices[0].x < targetx and vertices[2].x > targetx):
        A = (vertices[0].y, vertices[0].z, vertices[0].x)
        B = (vertices[2].y, vertices[2].z, vertices[2].x)
        pair.append(findInterpolatedPoint(A, B, targetx))

    # Calculate the coordinates of one segment at x = targetx (between v[1] and v[2])
    if (vertices[1].x > targetx and vertices[2].x < targetx) or (vertices[1].x < targetx and vertices[2].x > targetx):
        A = (vertices[1].y, vertices[1].z, vertices[1].x)
        B = (vertices[2].y, vertices[2].z, vertices[2].x)
        pair.append(findInterpolatedPoint(A, B, targetx))

    if vertices[0].x == targetx:
        pair.append((vertices[0].y, vertices[0].z))
    elif vertices[1].x == targetx:
        pair.append((vertices[1].y, vertices[1].z))
    elif vertices[2].x == targetx:
        pair.append((vertices[2].y, vertices[2].z))

    return pair

# Find interpolated points along the y axis at a specified y coordinate
def find_interpolated_points_at_y(targety, vertices):
    pair = []

    # Calculate the coordinates of one segment at y = targety (between v[0] and v[1])
    if (vertices[0].y > targety and vertices[1].y < targety) or (vertices[0].y < targety and vertices[1].y > targety):
        A = (vertices[0].x, vertices[0].z, vertices[0].y)
        B = (vertices[1].x, vertices[1].z, vertices[1].y)
        pair.append(findInterpolatedPoint(A, B, targety))

    # Calculate the coordinates of one segment at y = targety (between v[0] and v[2])
    if (vertices[0].y > targety and vertices[2].y < targety) or (vertices[0].y < targety and vertices[2].y > targety):
        A = (vertices[0].x, vertices[0].z, vertices[0].y)
        B = (vertices[2].x, vertices[2].z, vertices[2].y)
        pair.append(findInterpolatedPoint(A, B, targety))

    # Calculate the coordinates of one segment at y = targety (between v[1] and v[2])
    if (vertices[1].y > targety and vertices[2].y < targety) or (vertices[1].y < targety and vertices[2].y > targety):
        A = (vertices[1].x, vertices[1].z, vertices[1].y)
        B = (vertices[2].x, vertices[2].z, vertices[2].y)
        pair.append(findInterpolatedPoint(A, B, targety))

    if vertices[0].y == targety:
        pair.append((vertices[0].x, vertices[0].z))
    elif vertices[1].y == targety:
        pair.append((vertices[1].x, vertices[1].z))
    elif vertices[2].y == targety:
        pair.append((vertices[2].x, vertices[2].z))

    return pair
