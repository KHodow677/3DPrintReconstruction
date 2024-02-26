import pyrealsense2 as rs
import numpy as np
import cv2

# Function to draw vertices on the 3D print model
def draw_vertices_on_3d_model(vertices_3d, image):
    for vertex in vertices_3d:
        # Draw a small circle at each vertex position
        cv2.circle(image, (int(vertex[0]), int(vertex[1])), 3, (0, 255, 0), -1)

# Function to capture depth data from RealSense camera
def capture_depth_data():
    # Configure depth and color streams
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

    # Start streaming
    pipeline.start(config)

    # Wait for a coherent pair of frames: depth and color
    frames = pipeline.wait_for_frames()
    depth_frame = frames.get_depth_frame()

    # Stop streaming
    pipeline.stop()

    return depth_frame

# Example 3D model vertices (replace with your actual 3D model vertices)
# This is just a placeholder
model_vertices_3d = np.array([[100, 100], [200, 200], [300, 300]])

# Capture depth data
depth_frame = capture_depth_data()

# Convert depth data to numpy array
depth_image = np.asanyarray(depth_frame.get_data())

# Display depth image
cv2.imshow('Depth Image', depth_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Draw vertices on 3D model
draw_vertices_on_3d_model(model_vertices_3d, depth_image)

# Display 3D model with vertices
cv2.imshow('3D Model with Vertices', depth_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

