import yaml
import json
import numpy as np
from scipy.spatial.transform import Rotation as R

def transform_data(input_file, output_file):
    frames = []
    
    with open(input_file, 'r') as f:
        raw_documents = yaml.safe_load_all(f)
        
        for i, doc in enumerate(raw_documents):
            if not doc: continue
            
            # 1. Extract Translation
            tx = doc['translation']['x']
            ty = doc['translation']['y']
            tz = doc['translation']['z']
            
            # 2. Extract Rotation and convert to a 3x3 Matrix
            # Note: Scipy expects [x, y, z, w] order for quaternions
            quat = [
                doc['rotation']['x'],
                doc['rotation']['y'],
                doc['rotation']['z'],
                doc['rotation']['w']
            ]
            rot_matrix_3x3 = R.from_quat(quat).as_matrix()
            
            # 3. Build the 4x4 Raw Matrix
            # Start with an identity matrix
            mat4x4 = np.identity(4)
            # Insert the 3x3 rotation
            mat4x4[:3, :3] = rot_matrix_3x3
            # Insert the translation column
            mat4x4[:3, 3] = [tx, ty, tz]
            
            # 4. Construct JSON object
            frame = {
                "frame_id": i,
                "timestamp_ms": 1775829904324 + (i * 33), # Dummy increment
                "pose": {
                    "position": {"x": tx, "y": ty, "z": tz},
                    "orientation_quat": {
                        "x": quat[0], "y": quat[1], "z": quat[2], "w": quat[3]
                    }
                },
                "raw_matrix": mat4x4.flatten().tolist() # Flatten for JSON
            }
            frames.append(frame)

    with open(output_file, 'w') as f:
        json.dump(frames, f, indent=4)

    print(f"Successfully converted {len(frames)} frames with raw_matrix.")

transform_data('donnes_cage_camera', 'cage_traj.json')