import pyzed.sl as sl
import cv2
import numpy as np
import json
from scipy.spatial.transform import Rotation as R

def save_clean_trajectory(trajectory_list, filename="custom_trajectory.json"):
    clean_data = []
    
    for i, entry in enumerate(trajectory_list):
        matrix = np.array(entry['matrix'])
        
        # 1. Extract Translation
        pos = matrix[:3, 3]
        
        # 2. Extract Rotation and convert to Quaternion for easy 3D math later
        # We use scipy to ensure the conversion is numerically stable
        rot_matrix = matrix[:3, :3]
        quat = R.from_matrix(rot_matrix).as_quat() # [x, y, z, w]
        
        # 3. Create a structured dictionary
        frame_entry = {
            "frame_id": i,
            "timestamp_ms": entry.get('timestamp', 0),
            "pose": {
                "position": {
                    "x": float(pos[0]),
                    "y": float(pos[1]),
                    "z": float(pos[2])
                },
                "orientation_quat": {
                    "x": float(quat[0]),
                    "y": float(quat[1]),
                    "z": float(quat[2]),
                    "w": float(quat[3])
                }
            },
            # Keeping the raw matrix as a flattened list just in case
            "raw_matrix": matrix.flatten().tolist()
        }
        clean_data.append(frame_entry)

    with open(filename, 'w') as f:
        # 'indent=4' makes the JSON look like a clean document, not a wall of text
        json.dump(clean_data, f, indent=4)
    
    print(f"Clean trajectory saved to {filename}")

# Usage inside your loop:
# trajectory_list.append({
#    "matrix": cur_pose.copy(), 
#    "timestamp": zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds()
# })

def get_manual_camera_pose(svo_path, output_json="custom_trajectory.json"):
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.set_from_svo_file(svo_path)
    init_params.depth_mode = sl.DEPTH_MODE.ULTRA 
    
    if zed.open(init_params) != sl.ERROR_CODE.SUCCESS:
        return

    # Get Intrinsics (focal length and optical center)
    calib = zed.get_camera_information().camera_configuration.calibration_parameters.left_cam
    fx, fy = calib.fx, calib.fy
    cx, cy = calib.cx, calib.cy
    camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float32)

    # ORB & LK Tracker params
    orb = cv2.ORB_create(nfeatures=1000)
    lk_params = dict(winSize=(21, 21), maxLevel=3, 
                     criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))

    # Containers
    img_sl = sl.Mat()
    depth_sl = sl.Mat()
    prev_gray = None
    prev_pts = None 
    
    # Global Pose (Identity matrix to start)
    cur_pose = np.eye(4)
    trajectory = []

    while True:
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(img_sl, sl.VIEW.LEFT)
            zed.retrieve_measure(depth_sl, sl.MEASURE.DEPTH)
            
            frame_bgr = img_sl.get_data()
            curr_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGRA2GRAY)
            depth_map = depth_sl.get_data()

            if prev_gray is not None and prev_pts is not None:
                # 1. Track points temporally (Optical Flow)
                curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, prev_pts, None, **lk_params)
                
                valid_curr = curr_pts[status == 1]
                valid_prev = prev_pts[status == 1]

                # 2. Back-project valid PREVIOUS points to 3D using Depth
                obj_points = [] # 3D
                img_points = [] # 2D (current frame)

                height, width = depth_map.shape

                for i, (p_prev, p_curr) in enumerate(zip(valid_prev, valid_curr)):
                    # Convert to integers for indexing
                    u, v = int(p_prev[0]), int(p_prev[1])

                    # 1. Clamp coordinates to valid range [0, dimension - 1]
                    u = max(0, min(u, width - 1))
                    v = max(0, min(v, height - 1))

                    z = depth_map[v, u]

                    # Filter out invalid depth (NaN, Inf, or too far)
                    if np.isfinite(z) and z > 0.1:
                        # 2D to 3D conversion
                        x = (u - cx) * z / fx
                        y = (v - cy) * z / fy
                        obj_points.append([x, y, z])
                        img_points.append(p_curr)

                if len(obj_points) > 10:
                    # 3. Solve PnP RANSAC to get relative motion
                    _, rvec, tvec, inliers = cv2.solvePnPRansac(
                        np.array(obj_points, dtype=np.float32),
                        np.array(img_points, dtype=np.float32),
                        camera_matrix, None)

                    # 4. Convert to Matrix and update Global Pose
                    R_mat, _ = cv2.Rodrigues(rvec)
                    # Relative transform matrix
                    T_rel = np.eye(4)
                    T_rel[:3, :3] = R_mat.T
                    T_rel[:3, 3] = -R_mat.T @ tvec.flatten()
                    
                    cur_pose = cur_pose @ T_rel

                # Log trajectory
                trajectory.append({
                    "matrix": cur_pose.copy(),
                    "timestamp": zed.get_timestamp(sl.TIME_REFERENCE.IMAGE).get_milliseconds()
                })

            # Refresh points if needed
            if prev_pts is None or len(prev_pts) < 500:
                kp = orb.detect(curr_gray, None)
                prev_pts = np.array([k.pt for k in kp], dtype=np.float32).reshape(-1, 1, 2)
            else:
                prev_pts = curr_pts[status == 1].reshape(-1, 1, 2)

            prev_gray = curr_gray.copy()
            cv2.imshow("Custom VO", frame_bgr)
            if cv2.waitKey(1) == ord('q'): break
        elif zed.grab() == sl.ERROR_CODE.END_OF_SVOFILE_REACHED: break

    save_clean_trajectory(trajectory, output_json)
    zed.close()

if __name__ == "__main__":
    get_manual_camera_pose("camera-in-cage.svo2")