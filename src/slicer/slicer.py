import sys, os, time
sys.path.append(os.getcwd())

from src.slicer.model.model import STLModel
from src.slicer.model.vector import Vector, Normal
from PIL import Image, ImageDraw
from sklearn.neighbors import KDTree
import numpy as np

# Determine how much space a pixel takes up physically
def calculateMultiplier(pixels, mm):
	return pixels/mm

def mmToinch(num):
	return num/25.4

def inchTomm(num):
	return num*25.4

def convertToPixels(vSet, width_multiplier, height_multiplier, object_center, center_image):
	mmSet = inchTomm(np.asarray(vSet))
    # Convert to pixels
	mmSet[:,0]*=width_multiplier
	mmSet[:,1]*=height_multiplier

	# Center the object
	mmSet[:,0]+=(center_image[0])
	mmSet[:,0]-=(inchTomm(object_center[0])*width_multiplier)
	mmSet[:,1]+=(center_image[1])
	mmSet[:,1]-=(inchTomm(object_center[1])*height_multiplier)

	m = list(mmSet)
	for i in range(len(mmSet)):
		m[i]= tuple(m[i])
	return m

def slice_file(resolution, f=None, scale_model=None, width_px=None, height_px=None, width_printer=None, height_printer=None):
    print("Status: Loading File.")

    # Converstion from mm to pixels
    width_multiplier = calculateMultiplier(width_px, width_printer) 
    height_multiplier = calculateMultiplier(height_px, height_printer)

    model = STLModel(f)
    stats = model.stats()

    # Note these are in inches not mm
    sub_vertex = Vector(stats['extents']['x']['lower'], stats['extents']['y']['lower'], stats['extents']['z']['lower'])

    # Switch to pixels
    center_image = [int(width_px / 2), int(height_px / 2)]

    model.xmin = model.xmax = None
    model.ymin = model.ymax = None
    model.zmin = model.zmax = None

    print("Status: Scaling Triangles.")

    for triangle in model.triangles:
        triangle.vertices[0] -= sub_vertex
        triangle.vertices[1] -= sub_vertex
        triangle.vertices[2] -= sub_vertex

        # The lines above have no effect on the normal.

        triangle.vertices[0] = (triangle.vertices[0] * scale_model)  # in inches
        triangle.vertices[1] = (triangle.vertices[1] * scale_model)  # in inches
        triangle.vertices[2] = (triangle.vertices[2] * scale_model)  # in inches

        # Recalculate the triangle normal

        u = model.triangles[0].vertices[1] - model.triangles[0].vertices[0]
        v = model.triangles[0].vertices[2] - model.triangles[0].vertices[0]

        triangle.n = Normal((u.y * v.z) - (u.z * v.y), (u.z * v.x) - (u.x * v.z), (u.x * v.y) - (u.y * v.x))
        model.update_extents(triangle)

    print("Status: Calculating Slices")

    stats = model.stats()

    # This is after scaling the object
    sub_vertex = Vector(stats['extents']['x']['lower'], stats['extents']['y']['lower'],
                        stats['extents']['z']['lower'])
    sup_vertex = Vector(stats['extents']['x']['upper'], stats['extents']['y']['upper'],
                        stats['extents']['z']['upper'])
    obj_center_xyz = [(sup_vertex.x + sub_vertex.x) / 2, (sup_vertex.y + sub_vertex.y) / 2,
                      (sup_vertex.z + sub_vertex.z) / 2]  # in inches

    slices = np.linspace(0.001, stats['extents']['z']['upper'] - 0.001,
                          int(stats['extents']['z']['upper'] / (mmToinch(resolution))) + 1)

    final_image = Image.new('RGB', (height_px, width_px), color='black')  # Create a blank canvas

    tic = time.time()

    for slice_idx, slice_val in enumerate(slices):
        pairs = model.slice_at_z(slice_val)

        # Now process vertices
        a = np.asarray(pairs)
        b = a.flatten()

        # Hacky Fix: This is now twice as long and just not four wide, it is now too wide
        vert_array = b.reshape(int(b.shape[0] / 2), 2)  
        tree = KDTree(vert_array, leaf_size=3)
        current_index = 1
        vertices = []
        vertice_sets = []
        visited_vertices = [current_index]
        vertices.append(tuple(vert_array[current_index]))
        for i in range(int(vert_array.shape[0] / 2)):
            to_query = np.reshape(vert_array[current_index], (1, 2))
            _, ind = tree.query(to_query, k=2)
            for id in list(ind[0]):  # there should only be two
                if id != current_index:
                    # If loop is found,
                    if id in visited_vertices:
                        vertices.append(tuple(vert_array[id]))
                        vertice_sets.append(vertices)
                        vertices = []
                        for next_vert in range(vert_array.shape[0]):
                            if next_vert not in visited_vertices:
                                current_index = next_vert
                    # Now that it found the match, find the corresponding vertex,
                    # Remember that they are in pairs of two
                    elif id % 2 == 1:
                        current_index = id - 1
                        break
                    else:
                        current_index = id + 1
                        break
            visited_vertices.append(id)
            vertices.append(tuple(vert_array[current_index]))
            visited_vertices.append(current_index)

        # Draw the percentage done
        sys.stdout.write("\r%d%%" % int(slice_idx / len(slices) * 100))
        sys.stdout.flush()

        # Save the last one to the vertice set
        vertice_sets.append(vertices)
        draw = ImageDraw.Draw(final_image)
        for i in range(len(vertice_sets)):
            if len(vertice_sets[i]) > 2:
                set = convertToPixels(vertice_sets[i], width_multiplier, height_multiplier, obj_center_xyz,
                                      center_image)
                draw.polygon(set, fill=(255, 255, 255))

    final_image.save('res/models/outputs/model.png', 'PNG')

    print("\nStatus: Finished Outputting Slices")
    print('Time: ', time.time() - tic)

if (__name__ == '__main__'):
    slice_file(1.0, open('res/models/3DBenchyTest.STL', 'rb'), 0.05, 2048, 2048, 200, 200)


