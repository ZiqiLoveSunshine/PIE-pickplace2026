#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rosidl_runtime_py.utilities import get_message
from geometry_msgs.msg import Vector3, Quaternion, Transform

from axxb import calibrate_from_csv, cameraPose2T, rotm_to_quaternion

import numpy as np

import copy

from tools import *


class InstructionNode(Node):
    def __init__(self, topic_name: str):
        super().__init__("instruction_node")

        self.topic_name = topic_name
        self.last_transform = None  # Stocke le dernier transform calculé

        self.publisher = self.create_publisher(Transform, "/instruction_cage", 10)

        self.get_logger()

        self.get_logger().info(f'Recherche du topic "{topic_name}"...')
        self.wait_timer = self.create_timer(1.0, self.wait_for_topic)

        # Timer de publication toutes les 3 secondes
        self.publish_timer = self.create_timer(3.0, self.publish_last_transform)

        self.get_logger().info("Calibration en cours...")
        calib = calibrate_from_csv()

        self.X_gc = calib["X_gc"]
        self.X_bc = calib["X_bc"]

        self.get_logger().info("Calibration terminée.")

    def wait_for_topic(self):
        """Attend que le topic soit disponible, puis s'y abonne."""
        topics = dict(self.get_topic_names_and_types())

        if self.topic_name not in topics:
            self.get_logger().warn(
                f'Topic "{self.topic_name}" introuvable, nouvelle tentative...'
            )
            return

        topic_type_str = topics[self.topic_name][0]
        self.get_logger().info(f"Topic trouvé ! Type : {topic_type_str}")

        try:
            msg_type = get_message(topic_type_str)
        except Exception as e:
            self.get_logger().error(
                f"Type de message inconnu : {topic_type_str} -> {e}"
            )
            return

        self.subscription = self.create_subscription(
            msg_type, self.topic_name, self.listener_callback, 10
        )

        self.get_logger().info(f'Abonné à "{self.topic_name}" ({topic_type_str})')
        self.wait_timer.cancel()

    def listener_callback(self, msg):
        """Reçoit les données et met à jour le dernier transform, sans publier."""
        target = None

        for rb in msg.rigidbodies:
            if rb.rigid_body_name == TARGET_NAME:
                target = copy.copy(rb)

        if target is None:
            self.get_logger().warn("Objet non trouvé.")
            return

        pose_cage = [
            target.pose.orientation.x,
            target.pose.orientation.y,
            target.pose.orientation.z,
            target.pose.orientation.w,
            target.pose.position.x,
            target.pose.position.y,
            target.pose.position.z,
        ]

        Tcg = cameraPose2T(pose_cage)

        Tbg = self.X_bc @ Tcg @ np.linalg.inv(self.X_gc)

        t = Transform()

        t.translation.x = float(Tbg[0, 3])
        t.translation.y = float(Tbg[1, 3])
        t.translation.z = float(Tbg[2, 3])

        q = rotm_to_quaternion(Tbg[:3, :3])

        t.rotation.x = float(q[0])
        t.rotation.y = float(q[1])
        t.rotation.z = float(q[2])
        t.rotation.w = float(q[3])

        self.last_transform = t

    def publish_last_transform(self):
        """Publie le dernier transform calculé, toutes les 3 secondes."""
        if self.last_transform is not None:
            self.publisher.publish(self.last_transform)
        else:
            self.get_logger().warn("Aucun transform disponible, publication ignorée.")


def main():
    rclpy.init()
    node = InstructionNode(topic_name=TOPIC_NAME)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Arrêt du paquet instruction.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


main()
