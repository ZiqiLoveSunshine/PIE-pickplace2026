#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rosidl_runtime_py.utilities import get_message
from geometry_msgs.msg import Transform


from tools import *


class CameraPoseNode(Node):
    def __init__(self, topic_name: str):
        super().__init__("camera_pose_node")

        self.topic_name = topic_name
        self.last_transform = None

        self.publisher = self.create_publisher(Transform, "/camera_pose", 10)

        self.get_logger().info(f'Recherche du topic "{topic_name}"...')
        self.wait_timer = self.create_timer(1.0, self.wait_for_topic)
        self.publish_timer = self.create_timer(1.0, self.publish_last_transform)

    def wait_for_topic(self):
        topics = dict(self.get_topic_names_and_types())

        if self.topic_name not in topics:
            self.get_logger().warn(
                f'Topic "{self.topic_name}" introuvable, nouvelle tentative...'
            )
            return

        topic_type_str = topics[self.topic_name][0]
        try:
            msg_type = get_message(topic_type_str)
        except Exception as e:
            self.get_logger().error(
                f"Type de message inconnu : {topic_type_str} -> {e}"
            )
            return

        self.subscription = self.create_subscription(
            msg_type,
            self.topic_name,
            self.listener_callback,
            10,
        )
        self.get_logger().info(f'Abonné à "{self.topic_name}" ({topic_type_str})')
        self.wait_timer.cancel()

    def listener_callback(self, msg):
        for rb in msg.rigidbodies:
            if rb.rigid_body_name == CAMERA_NAME:
                t = Transform()
                t.translation.x = rb.pose.position.x
                t.translation.y = rb.pose.position.y
                t.translation.z = rb.pose.position.z
                t.rotation.x = rb.pose.orientation.x
                t.rotation.y = rb.pose.orientation.y
                t.rotation.z = rb.pose.orientation.z
                t.rotation.w = rb.pose.orientation.w
                self.last_transform = t
                return

        self.get_logger().warn(f'"{CAMERA_NAME}" non trouvé dans le message.')

    def publish_last_transform(self):
        if self.last_transform is not None:
            self.publisher.publish(self.last_transform)
        else:
            self.get_logger().warn("Aucun transform disponible, publication ignorée.")


def main():
    rclpy.init()
    node = CameraPoseNode(topic_name=TOPIC_NAME)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Arrêt du noeud camera_pose.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


main()
