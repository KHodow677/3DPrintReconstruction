from src.slicer.model.vector import Vector, Normal
from src.slicer.model.triangle import Triangle, find_interpolated_points_at_x, find_interpolated_points_at_y, find_interpolated_points_at_z
from struct import unpack

# Class to represent 3D objects
class Model(object):

    # Initialize the object
    def __init__(self, f=None):

        if f is None:
            raise ValueError("You must provide a file.")

        self.triangles = []
        self.vertices = {}
        self.normals = {}

        self.name = ""

        self.xmin = self.xmax = None
        self.ymin = self.ymax = None
        self.zmin = self.zmax = None

        # Not the means :D
        self.mx = self.my = self.mz = 0.0

        contents = f.read()
        f.close()

        if contents.find(b"vertex", 80) == -1:
            # File is a binary STL file.
            self.process_bin(contents)
        else:
            self.process_text(contents)

    def __str__(self):
        return "3D Model: %s" % self.name

    def __len__(self):
        return len(self.triangles)

    def __iter__(self):
        for t in self.triangles:
            yield t

    # Add the specified vertices and possibly a normal vector to the obj
    def add_triangle(self, v1, v2, v3, norm):
        hash_1 = v1.hash
        if hash_1 not in self.vertices:
            self.vertices[hash_1] = v1

        hash_2 = v2.hash
        if hash_2 not in self.vertices:
            self.vertices[hash_2] = v2

        hash_3 = v3.hash
        if hash_3 not in self.vertices:
            self.vertices[hash_3] = v3

        triangle = Triangle(self.vertices[hash_1], 
                            self.vertices[hash_2], 
                            self.vertices[hash_3],
                            norm)

        if not isinstance(norm, Normal):
            norm = triangle.norm

        normal_hash = norm.hash
        if normal_hash not in self.normals:
            self.normals[normal_hash] = norm
        else:
            triangle.norm = self.normals[normal_hash]

        self.triangles.append(triangle)
        self.update_extents(triangle)

    def extents(self):
        return ((self.xmin, self.xmax),
                (self.ymin, self.ymax),
                (self.zmin, self.zmax))

    def center(self):
        return ((self.xmin+self.xmax)/2,
                (self.ymin+self.ymax)/2,
                (self.zmin+self.zmax)/2)

    def mean_point(self):
        c = 3 * len(self.triangles)
        return (self.mx/c, self.my/c, self.mz/c)

    # Update the extents of the model based on Triangle t
    def update_extents(self, triangle):
        if self.xmin == None:
            self.xmin = self.xmax = triangle.vertices[0].x
            self.ymin = self.ymax = triangle.vertices[0].y
            self.zmin = self.zmax = triangle.vertices[0].z

            self.mx = 0.0
            self.my = 0.0
            self.mz = 0.0

        self.mx += (triangle.vertices[0].x +
                    triangle.vertices[1].x +
                    triangle.vertices[2].x)
        self.my += (triangle.vertices[0].y +
                    triangle.vertices[1].y +
                    triangle.vertices[2].y)
        self.mz += (triangle.vertices[0].z +
                    triangle.vertices[1].z +
                    triangle.vertices[2].z)

        for vertex in triangle.vertices:
            if vertex.x < self.xmin:
                self.xmin = vertex.x
            elif vertex.x > self.xmax:
                self.xmax = vertex.x

            if vertex.y < self.ymin:
                self.ymin = vertex.y
            elif vertex.y > self.ymax:
                self.ymax = vertex.y

            if vertex.z < self.zmin:
                self.zmin = vertex.z
            elif vertex.z > self.zmax:
                self.zmax = vertex.z

    def stats(self):
        out = {
            'name': self.name,
            'facets': len(self.triangles),
            'vertices': len(self.vertices),
            'normals': len(self.normals),
            'extents': {
                'x': {
                    'lower': self.xmin,
                    'upper': self.xmax,
                },
                'y': {
                    'lower': self.ymin,
                    'upper': self.ymax,
                },
                'z': {
                    'lower': self.zmin,
                    'upper': self.zmax,
                }
            },
            'center': self.center(),
            'meanpoint': self.mean_point()
        }

        return out

    def process_bin(self, contents=None):
        self.name, num_facets_1 = unpack(b"=80sI", contents[:84])

        self.name = self.name.replace(b"solid", b"")
        self.name = self.name.strip(b'\x00 \t\n\r')

        if len(self.name) == 0:
            self.name = b"Unkown"

        contents = contents[84:]
        facetsz = len(contents)

        num_facets_2 = facetsz / 50

        if num_facets_1 != num_facets_2:
            raise ValueError("Incorrect number of facets.")

        items = [contents[n:n+50] for n in range(0, facetsz, 50)]

        for i in items:
            nx, ny, nz, f1x, f1y, f1z, f2x, f2y, f2z, f3x, f3y, f3z = \
                unpack(b"=ffffffffffffxx", i)
            v1 = Vector(f1x, f1y, f1z)
            v2 = Vector(f2x, f2y, f2z)
            v3 = Vector(f3x, f3y, f3z)
            try:
                norm = Normal(nx, ny, nz)
            except ValueError:
                norm = None
            
            self.add_triangle(v1, v2, v3, norm)

    # Process the contents of a text file as a generator
    def process_text(self, contents=None):
        items = contents.split()
        del contents
        items = [s.strip() for s in items]
        try:
            sn = items.index("solid")+1
            en = items.index("facet")
        except:
            raise ValueError("Not an STL file.")
        if sn == en:
            self.name = "unknown"
        else:
            self.name = ' '.join(items[sn:en])
        nf1 = items.count('facet')
        del items[0:en]
        # Items now begins with "facet"
        while items[0] == "facet":
            v1 = Vector(items[8], items[9], items[10])
            v2 = Vector(items[12], items[13], items[14])
            v3 = Vector(items[16], items[17], items[18])
            try:
                norm = Normal(items[2], items[3], items[4])
            except ValueError:
                norm = None
            
            self.add_triangle(v1, v2, v3, norm)
            del items[:21]

# Function to slice the model at a certain z coordinate
# Returns an array of tuples describing lines between points
def slice_at_z(targetz, triangles):
    output = []

    for triangle in triangles:
        points = find_interpolated_points_at_z(targetz, triangle.vertices)

        if len(points) == 2:
            output.append((points[0], points[1]))

    return output

# Function to slice the model at a certain x coordinate
# Returns an array of tuples describing lines between points
def slice_at_x(targetx, triangles):
    output = []

    for triangle in triangles:
        points = find_interpolated_points_at_x(targetx, triangle.vertices)

        if len(points) == 2:
            output.append((points[0], points[1]))

    return output

# Function to slice the model at a certain y coordinate
# Returns an array of tuples describing lines between points
def slice_at_y(targety, triangles):
    output = []

    for triangle in triangles:
        points = find_interpolated_points_at_y(targety, triangle.vertices)

        if len(points) == 2:
            output.append((points[0], points[1]))

    return output