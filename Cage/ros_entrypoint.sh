#!/bin/bash

source /opt/ros/humble/setup.bash
source /ros2_ws/install/setup.bash

ros2 launch mocap4r2_optitrack_driver optitrack2.launch.py config_file:=config/optitrack.yaml &

wait_for_node() {
    local node_name=$1
    local timeout=30
    local elapsed=0

    echo "Attente du node $node_name..."
    while [ $elapsed -lt $timeout ]; do
        if ros2 node list | grep -q "$node_name"; then
            echo "Node $node_name détecté!"
            return 0
        fi
        echo "  > Node $node_name non trouvé !"
        sleep 1
        elapsed=$((elapsed + 1))
    done

    echo "Timeout: Node $node_name non trouvé après ${timeout}s"
    return 1
}

if wait_for_node "/mocap4r2_optitrack_driver_node"; then
    sleep 1
    ros2 lifecycle set /mocap4r2_optitrack_driver_node activate
fi

# # Calibration path
# export CSV_PATH='mesures.csv'

# # Topic name
# export BODIES_TOPIC='/rigid_bodies'
# export ROBOT_TOPIC='/robot_pose'

# # Target name
# export ROBOT_NAME='1028'
# export CLAMP_NAME='1046'
# export TARGET_NAME='1034'
# export CAMERA_NAME='1051'



exec "$@"
