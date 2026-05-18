#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rosidl_runtime_py.utilities import get_message
from geometry_msgs.msg import Transform
import copy
import os
import csv

from tools import *


class CalibrationLoggerNode(Node):
    """
    Node écoutant les topics `/rigid_bodies` et `/robot_pose` et écrivant les coordonnées dans un fichier csv
    """

    def __init__(self):
        super().__init__("calibration_logger_node")

        self._got_clamp = False
        self._got_pos_bras = False
        self._got_written = False

        self._c_tf = None
        self._r_tf = None

        self._subscribed_topics = set()

        # Initialisation CSV
        write_header = not os.path.exists(CSV_PATH)
        self._csv_file = open(CSV_PATH, "a", newline="")
        self._csv_writer = csv.writer(self._csv_file)
        if write_header:
            self._csv_writer.writerow(CSV_HEADER)
            self._csv_file.flush()

        self.get_logger().info(f"Attente des topics {TOPIC_NAME} et {TOPIC_ROBOT}...")
        self.wait_timer = self.create_timer(1.0, self.wait_for_topics)

    def wait_for_topics(self):
        available = dict(self.get_topic_names_and_types())

        if TOPIC_NAME not in self._subscribed_topics and TOPIC_NAME in available:
            self._subscribe(TOPIC_NAME, available, self.rigid_bodies_callback)

        if TOPIC_ROBOT not in self._subscribed_topics and TOPIC_ROBOT in available:
            self._subscribe(TOPIC_ROBOT, available, self.pos_bras_callback)

        if self._subscribed_topics == {TOPIC_NAME, TOPIC_ROBOT}:
            self.wait_timer.cancel()

    def _subscribe(self, topic, available, callback):
        type_str = available[topic][0]
        try:
            msg_type = get_message(type_str)
            self.create_subscription(msg_type, topic, callback, 10)
            self._subscribed_topics.add(topic)
            self.get_logger().info(f"Abonné à {topic} ({type_str})")
        except Exception as e:
            self.get_logger().error(f"Impossible de s'abonner à {topic} : {e}")

    def rigid_bodies_callback(self, msg):
        if self._got_clamp:
            return

        for rb in msg.rigidbodies:
            if rb.rigid_body_name == CLAMP_NAME:
                t = Transform()
                t.translation.x = rb.pose.position.x
                t.translation.y = rb.pose.position.y
                t.translation.z = rb.pose.position.z
                t.rotation.x = rb.pose.orientation.x
                t.rotation.y = rb.pose.orientation.y
                t.rotation.z = rb.pose.orientation.z
                t.rotation.w = rb.pose.orientation.w
                self._c_tf = t
                self._got_clamp = True
                self.get_logger().info(f"[{TOPIC_NAME}] {CLAMP_NAME} enregistré.")
                self._check_done()
                return

        self.get_logger().warn(f'"{CLAMP_NAME}" non trouvé dans ce message.')

    def pos_bras_callback(self, msg):
        if self._got_pos_bras:
            return

        t = msg.transform if hasattr(msg, "transform") else msg
        self._r_tf = copy.copy(t)

        self._got_pos_bras = True
        self.get_logger().info(f"[{TOPIC_ROBOT}] Transform enregistré.")
        self._check_done()

    def _write_row(self):
        self._csv_writer.writerow(
            [
                self._c_tf.translation.x,
                self._c_tf.translation.y,
                self._c_tf.translation.z,
                self._c_tf.rotation.x,
                self._c_tf.rotation.y,
                self._c_tf.rotation.z,
                self._c_tf.rotation.w,
                self._r_tf.translation.x,
                self._r_tf.translation.y,
                self._r_tf.translation.z,
                self._r_tf.rotation.x,
                self._r_tf.rotation.y,
                self._r_tf.rotation.z,
                self._r_tf.rotation.w,
            ]
        )
        self._csv_file.flush()

    def _check_done(self):
        if self._got_clamp and self._got_pos_bras and not self._got_written:
            self._write_row()
            self._got_written = True
            self.get_logger().info(f"Ligne écrite dans {CSV_PATH}. Arrêt.")
            raise SystemExit

    def destroy_node(self):
        self._csv_file.close()
        super().destroy_node()


def main():
    rclpy.init()
    node = CalibrationLoggerNode()
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, SystemExit):
        node.get_logger().info("Arrêt du noeud.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


main()
