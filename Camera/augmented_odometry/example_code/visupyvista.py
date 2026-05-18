import pyvista as pv
import json
import numpy as np

def visualize_with_pyvista(json_path):
    # 1. Load your clean JSON
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Extract positions for the trail
    path_points = np.array([[d['pose']['position']['x'], 
                             d['pose']['position']['y'], 
                             d['pose']['position']['z']] for d in data])

    # 2. Setup the Plotter
    plotter = pv.Plotter(title="Visual Odometry Trajectory")
    plotter.set_background("black") # Dark theme for a "tech" look

    # 3. Create the Path (Spline)
    if len(path_points) > 1:
        path = pv.MultipleLines(path_points)
        plotter.add_mesh(path, color="cyan", line_width=2, label="VO Path")

    # 4. Create a "Camera" Actor
    # We'll use a simple Cone to represent the camera's FOV
    camera_indicator = pv.Cone(radius=0.1, height=0.2, direction=(0, 0, 1))
    camera_mesh = plotter.add_mesh(camera_indicator, color="magenta")

    # 5. Animation Logic
    plotter.add_text("Manual VO Animation", font_size=12)
    
    # If running in Docker without a screen, you can use plotter.open_movie("vo.mp4")
    plotter.show(interactive_update=True)

    for i in range(len(data)):
        # Update camera position
        pos = path_points[i]
        
        # Get rotation matrix from the JSON (flattened 16-element list to 4x4)
        matrix = np.array(data[i]['raw_matrix']).reshape(4, 4)
        
        # Update the mesh transform
        camera_mesh.user_matrix = matrix
        
        plotter.update()
        plotter.render()

    plotter.show()

visualize_with_pyvista("cage_traj.json")