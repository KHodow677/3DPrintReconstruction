import sys, os, time
from typing import final
sys.path.append(os.getcwd())

from src.slicer.model.model import Model, slice_at_x, slice_at_y, slice_at_z
from src.slicer.model.vector import Vector, Normal
from PIL import Image, ImageDraw, ImageOps
from sklearn.neighbors import KDTree
from shapely.geometry import Polygon, Point
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

def parse_file(f=None, scale_model=None):
    print("Status: Loading File.")

    model = Model(f)
    stats = model.stats()

    # Note these are in inches not mm
    sub_vertex = Vector(stats['extents']['x']['lower'], stats['extents']['y']['lower'], stats['extents']['z']['lower'])

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

    return model

def slice_file(resolution, model, direction='z', width_px=None, height_px=None, width_printer=None, height_printer=None, slice_reverse = False, output= ""):

    # Converstion from mm to pixels
    width_multiplier = calculateMultiplier(width_px, width_printer) 
    height_multiplier = calculateMultiplier(height_px, height_printer)

    # Switch to pixels
    center_image = [int(width_px / 2), int(height_px / 2)]

    print("Status: Calculating Slices")

    stats = model.stats()

    # This is after scaling the object
    sub_vertex = Vector(stats['extents']['x']['lower'], stats['extents']['y']['lower'],
                        stats['extents']['z']['lower'])
    sup_vertex = Vector(stats['extents']['x']['upper'], stats['extents']['y']['upper'],
                        stats['extents']['z']['upper'])
    obj_center_xyz = [(sup_vertex.x + sub_vertex.x) / 2, (sup_vertex.y + sub_vertex.y) / 2,
                      (sup_vertex.z + sub_vertex.z) / 2]  # in inches

    if direction == 'x':
        slices = np.linspace(0.001, stats['extents']['x']['upper'] - 0.001,
                              int(stats['extents']['x']['upper'] / (mmToinch(resolution))) + 1)
    elif direction == 'y':
        slices = np.linspace(0.001, stats['extents']['y']['upper'] - 0.001,
                              int(stats['extents']['y']['upper'] / (mmToinch(resolution))) + 1)
    elif direction == 'z':
        slices = np.linspace(0.001, stats['extents']['z']['upper'] - 0.001,
                              int(stats['extents']['z']['upper'] / (mmToinch(resolution))) + 1)

    imgs = []
    grayIncrement = float(255 / len(slices))
    color = (0, 0, 0, 255)

    tic = time.time()
    
    if (slice_reverse):
        slices = np.flip(slices)

    for slice_idx, slice_val in enumerate(slices):
        if direction == 'x':
            pairs = slice_at_x(slice_val, model.triangles)
        elif direction == 'y':
            pairs = slice_at_y(slice_val, model.triangles)
        elif direction == 'z':
            pairs = slice_at_z(slice_val, model.triangles)

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
        img = Image.new('RGBA', (height_px, width_px))
        imgDraw = ImageDraw.Draw(img)
        holes = []
        colorVal = int(color[0] + grayIncrement)
        color = (colorVal, colorVal, colorVal, 255)

        # Inside the for loop where polygons are drawn
        for i in range(len(vertice_sets)):
            if len(vertice_sets[i]) > 2:
                set = convertToPixels(vertice_sets[i], width_multiplier, height_multiplier, obj_center_xyz, center_image)
                
                # Check if any other vertex is inside the polygon
                # Check if any vertex of the current polygon is inside any other polygon
                is_hole = False
                for j in range(len(vertice_sets)):
                    if j != i and len(vertice_sets[j]) > 2:
                        other_set = convertToPixels(vertice_sets[j], width_multiplier, height_multiplier, obj_center_xyz, center_image)
                        other_poly = Polygon(other_set)
                        for vertex in set:
                            if other_poly.contains(Point(vertex)):
                                is_hole = True
                                break
                        if is_hole:
                            break
                
                # Fill the polygon based on whether it's a hole or not
                if is_hole:
                    holes.append(set)
                imgDraw.polygon(set, fill=color)

        for set in holes:
            imgDraw.polygon(set, fill=(0, 0, 0, 255))

        data = img.getdata()

        newData = []
        for item in data:
            if item[0] == 0 and item[1] == 0 and item[2] == 0:
                newData.append((0, 0, 0, 0))
            else:
                newData.append(item)
        
        img.putdata(newData)
        imgs.append(img)

    final_image = Image.new('RGBA', (height_px, width_px), color=(0, 0, 0, 255))  
    for img in imgs:
        final_image.paste(img, (0, 0), img)  # Paste the current image onto the final image, using itself as the mask
    if (slice_reverse):
        final_image = ImageOps.mirror(final_image)
    final_image = ImageOps.flip(final_image)
    final_image.save(output, 'PNG')

    print("\nStatus: Finished Outputting Slices")
    print('Time: ', time.time() - tic)

if (__name__ == '__main__'):
    model = parse_file( 
        f=open('res/models/3DBenchyTest.STL', 'rb'), 
        scale_model=0.05)
    slice_file(
        resolution=1.0, model=model, direction='x', 
        width_px=512, height_px=512, 
        width_printer=200, height_printer=200,
        slice_reverse=False, output='res/models/outputs/x1.png')
    
    slice_file(
        resolution=1.0, model=model, direction='y', 
        width_px=512, height_px=512, 
        width_printer=200, height_printer=200,
        slice_reverse=False, output='res/models/outputs/y1.png')
    
    slice_file(
        resolution=1.0, model=model, direction='x', 
        width_px=512, height_px=512, 
        width_printer=200, height_printer=200,
        slice_reverse=True, output='res/models/outputs/x2.png')
    
    slice_file(
        resolution=1.0, model=model, direction='y', 
        width_px=512, height_px=512, 
        width_printer=200, height_printer=200,
        slice_reverse=True, output='res/models/outputs/y2.png')
