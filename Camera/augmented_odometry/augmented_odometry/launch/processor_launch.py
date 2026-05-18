from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='augmented_odometry',
            executable='augmented_odometry',
            name='augmented_odometry',
            output='screen',
            parameters=[{'processing_rate': 3}]
        )
    ])
