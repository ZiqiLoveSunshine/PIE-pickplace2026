from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='data_processor',
            executable='data_processor',
            name='data_processor',
            output='screen',
            parameters=[{'processing_rate': 1}]
        )
    ])
