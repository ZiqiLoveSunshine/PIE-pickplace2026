# Module permettant de mesurer l'erreur entre un objet de référence et un objet cible

#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rosidl_runtime_py.utilities import get_message
from geometry_msgs.msg import Transform
import copy

from tools import *


class ErrorNode(Node):
    def __init__(self, topic_name: str):
        super().__init__("error_node")

        self.topic_name = topic_name
        self.last_error = None

        self.publisher = self.create_publisher(Transform, "/errors", 10)

        self.get_logger().info(f'Recherche du topic "{topic_name}"...')
        self.wait_timer = self.create_timer(1.0, self.wait_for_topic)
        self.publish_timer = self.create_timer(3.0, self.publish_last_error)

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
        """Reçoit les données et met à jour la dernière erreur, sans publier."""
        reference = None
        target = None

        for rb in msg.rigidbodies:
            if rb.rigid_body_name == REF_NAME:
                reference = copy.copy(rb)
            elif rb.rigid_body_name == TARGET_NAME:
                target = copy.copy(rb)

        if reference is None:
            self.get_logger().warn(
                f'"{REF_NAME}" introuvable. '
                f"Noms reçus : {[rb.rigid_body_name for rb in msg.rigidbodies]}"
            )
            return

        if target is None:
            self.get_logger().warn(
                f'"{TARGET_NAME}" introuvable. '
                f"Noms reçus : {[rb.rigid_body_name for rb in msg.rigidbodies]}"
            )
            return

        self.last_error = error_between_rigid_bodies(reference, target)

    def publish_last_error(self):
        """Publie la dernière erreur calculée toutes les x secondes."""
        if self.last_error is not None:
            self.publisher.publish(self.last_error)
        else:
            self.get_logger().warn("Aucune erreur disponible, publication ignorée.")


def main():
    rclpy.init()
    node = ErrorNode(topic_name=TOPIC_NAME)

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Arrêt du noeud erreur.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


main()
