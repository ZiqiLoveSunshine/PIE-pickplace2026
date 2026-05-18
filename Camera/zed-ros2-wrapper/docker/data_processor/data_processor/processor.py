import rclpy
from rclpy.node import Node
from zed_msgs.msg import ObjectsStamped
from geometry_msgs.msg import Point
from geometry_msgs.msg import TransformStamped
from scipy.spatial.transform import Rotation as R
import numpy as np

class DataProcessorNode(Node):
    def __init__(self):
        super().__init__('data_processor')
        self.target_id = -1
        self.subscription = self.create_subscription(
            ObjectsStamped,
            '/zed/zed_node/obj_det/objects',  
            self.listener_callback,
            1),
        self.subscription_arm = self.create_subscription(
            TransformStamped,
            '/robot_pose',  
            self.get_arm_position,
            1)
        self.publisher = self.create_publisher(Point, '/object_positions', 1)


        self.T_mount_camera = np.eye(4)
        r_static = R.from_euler('xyz', [0,0,90], degrees=True).as_matrix()
        self.T_mount_camera[:3, :3] = r_static
        self.T_mount_camera[:3, 3] = [-0.15, 0, 0]
        self.A= np.eye(4)

    def listener_callback(self, msg):
        if not msg.objects:
            self.get_logger().info('No objects detected.')
            return
        if self.target_id ==-1:
            self.target_id = msg.objects[0].label_id
            self.get_logger().info(f'Set target ID to {self.target_id}')
        
        found=False
        for obj in msg.objects:
            if (obj.label_id == self.target_id) and (obj.label=="SPORT"):
                found=True
                self.get_logger().info(f'Found target object: {obj.label} with ID {obj.label_id} at position {obj.position} (camera space)')
                point_msg = Point()
                point_msg.x = float(obj.position[0])
                point_msg.y = float(obj.position[1])
                point_msg.z = float(obj.position[2])
                point_msg = self.change_coor_space(point_msg)
                self.get_logger().info(f'Sent target object: {obj.label} with ID {obj.label_id} at position {point_msg.x}, {point_msg.y}, {point_msg.z} (robot space)')
                self.publisher.publish(point_msg)
                break
        if not found:
            self.get_logger().info(f'Target object with ID {self.target_id} not found.')
            self.target_id=-1

    def get_arm_position(self, msg):
        if msg=="":
            self.get_logger().info('No arm position received.')
            return
        else:
            T=msg.transform
            self.get_logger().info("Received arm position: rotation ({T.rotation.x}, {T.rotation.y}, {T.rotation.z}, {T.rotation.w}), translation ({T.translation.x}, {T.translation.y}, {T.translation.z})")
            #r = R.from_quat([T.rotation.x, T.rotation.y, T.rotation.z, T.rotation.w])
            r = R.from_euler('xyz', [T.rotation.x+1.52, T.rotation.y, T.rotation.z], degrees=False)
            self.A[:3, :3] = r.as_matrix()
            t=np.array([T.translation.x, T.translation.y, T.translation.z])
            self.A[:3, 3] = t
            return 
        
    def change_coor_space(self, p:Point):
        p_cam = np.array([p.x, p.y, p.z, 1.0])
        T_base_camera = self.A @ self.T_mount_camera
        p_base = T_base_camera @ p_cam
        return Point(x=p_base[0], y=p_base[1], z=p_base[2])


def main(args=None):
    rclpy.init(args=args)
    data_processor_node = DataProcessorNode()
    rclpy.spin(data_processor_node)
    data_processor_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()


