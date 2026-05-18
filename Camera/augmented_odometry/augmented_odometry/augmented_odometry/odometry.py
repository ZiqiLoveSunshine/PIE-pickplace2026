import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo
from geometry_msgs.msg import PoseStamped
from cv_bridge import CvBridge
import cv2
import numpy as np
from scipy.spatial.transform import Rotation as R

class VisualOdometryNode(Node):
    def __init__(self):
        super().__init__('visual_odometry_node')
        
        # --- Subscribers ---
        # Adjust these topic names to match your ZED ROS wrapper output
        self.image_sub = self.create_subscription(Image, '/zed/zed_node/left/image_rect_color', self.image_callback, 10)
        self.depth_sub = self.create_subscription(Image, '/zed/zed_node/depth/depth_registered', self.depth_callback, 10)
        self.info_sub = self.create_subscription(CameraInfo, '/zed/zed_node/left/camera_info', self.info_callback, 10)

        # --- Publisher ---
        self.pose_pub = self.create_publisher(PoseStamped, '/camera/visual_pose', 10)

        # --- Utilities & State ---
        self.bridge = CvBridge()
        self.orb = cv2.ORB_create(nfeatures=1000)
        self.lk_params = dict(winSize=(21, 21), maxLevel=3, 
                             criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
        
        self.camera_matrix = None
        self.intrinsics = None # (fx, fy, cx, cy)
        self.latest_depth = None
        self.prev_gray = None
        self.prev_pts = None
        self.cur_pose = np.eye(4)

    def info_callback(self, msg):
        """Extracts camera intrinsics once."""
        if self.camera_matrix is None:
            self.camera_matrix = np.array(msg.k).reshape(3, 3)
            self.intrinsics = (msg.k[0], msg.k[4], msg.k[2], msg.k[5]) # fx, fy, cx, cy
            self.get_logger().info("Camera Intrinsics Received")

    def depth_callback(self, msg):
        """Stores the latest depth map."""
        self.latest_depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='32FC1')

    def image_callback(self, msg):
        """Main processing loop triggered by incoming frames."""
        if self.camera_matrix is None or self.latest_depth is None:
            return

        # 1. Convert ROS Image to OpenCV
        frame_bgr = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        curr_gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        fx, fy, cx, cy = self.intrinsics

        if self.prev_gray is not None and self.prev_pts is not None:
            # 2. Optical Flow
            curr_pts, status, _ = cv2.calcOpticalFlowPyrLK(self.prev_gray, curr_gray, self.prev_pts, None, **self.lk_params)
            
            valid_curr = curr_pts[status == 1]
            valid_prev = self.prev_pts[status == 1]

            obj_points = []
            img_points = []

            # 3. Back-projection
            for p_prev, p_curr in zip(valid_prev, valid_curr):
                u, v = int(p_prev[0]), int(p_prev[1])
                if 0 <= v < self.latest_depth.shape[0] and 0 <= u < self.latest_depth.shape[1]:
                    z = self.latest_depth[v, u]
                    if np.isfinite(z) and z > 0.1:
                        x = (u - cx) * z / fx
                        y = (v - cy) * z / fy
                        obj_points.append([x, y, z])
                        img_points.append(p_curr)

            # 4. PnP RANSAC
            if len(obj_points) > 10:
                success, rvec, tvec, _ = cv2.solvePnPRansac(
                    np.array(obj_points, dtype=np.float32),
                    np.array(img_points, dtype=np.float32),
                    self.camera_matrix, None)

                if success:
                    R_mat, _ = cv2.Rodrigues(rvec)
                    T_rel = np.eye(4)
                    T_rel[:3, :3] = R_mat.T
                    T_rel[:3, 3] = -R_mat.T @ tvec.flatten()
                    
                    self.cur_pose = self.cur_pose @ T_rel
                    self.publish_pose(msg.header.stamp)

        # 5. Feature Refreshing
        if self.prev_pts is None or len(self.prev_pts) < 500:
            kp = self.orb.detect(curr_gray, None)
            self.prev_pts = np.array([k.pt for k in kp], dtype=np.float32).reshape(-1, 1, 2)
        else:
            self.prev_pts = curr_pts[status == 1].reshape(-1, 1, 2)

        self.prev_gray = curr_gray

    def publish_pose(self, timestamp):
        """Converts current pose matrix to PoseStamped and publishes."""
        msg = PoseStamped()
        msg.header.stamp = timestamp
        msg.header.frame_id = "odom" # or "world"

        # Position
        msg.pose.position.x = float(self.cur_pose[0, 3])
        msg.pose.position.y = float(self.cur_pose[1, 3])
        msg.pose.position.z = float(self.cur_pose[2, 3])

        # Orientation
        rot_matrix = self.cur_pose[:3, :3]
        quat = R.from_matrix(rot_matrix).as_quat()
        msg.pose.orientation.x = quat[0]
        msg.pose.orientation.y = quat[1]
        msg.pose.orientation.z = quat[2]
        msg.pose.orientation.w = quat[3]

        self.pose_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = VisualOdometryNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()