#!/bin/bash
set -e

# setup ros2 environment
source "/opt/ros/$ROS_DISTRO/setup.bash" --
source "/root/ros2_ws/install/local_setup.bash" --

export ROS_DOMAIN_ID=0

# Welcome information
echo "ZED ROS2 Docker Image"
echo "---------------------"
echo 'ROS distro: ' $ROS_DISTRO
echo 'DDS middleware: ' $RMW_IMPLEMENTATION
echo 'ROS 2 Workspaces:' $COLCON_PREFIX_PATH
echo 'ROS 2 Domain ID:' $ROS_DOMAIN_ID
echo ' * Note: Host and Docker image Domain ID must match to allow communication'
echo 'Local IPs:' $(hostname -I)
echo "---"  
echo 'Available ZED packages:'
ros2 pkg list | grep zed
echo "---------------------"
echo 'To start a ZED camera node:'
echo "---------------------"
source 'install/setup.bash'
ros2  'launch' 'zed_wrapper' 'zed_camera.launch.py' 'camera_model:=zedm' & 
ros2 'launch' 'data_processor' 'processor_launch.py' &
# ros2 'launch' 'augmented_odometry' 'processor_launch.py' &
exec "bash"