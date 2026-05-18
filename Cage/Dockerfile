FROM osrf/ros:humble-desktop-full
# FROM mathworks/matlab:latest

# ENV DEBIAN_FRONTEND=noninteractive

# dépendances système + ros
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    build-essential \
    cmake \
    python3-pip \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-vcstool \
    python3-numpy \
    libopencv-dev \
    python3-opencv \
    libboost-all-dev \
    libeigen3-dev \
    ros-humble-rclcpp \
    ros-humble-rclpy \
    ros-humble-std-msgs \
    ros-humble-geometry-msgs \
    ros-humble-nav-msgs \
    ros-humble-sensor-msgs \
    ros-humble-visualization-msgs \
    ros-humble-tf2 \
    ros-humble-tf2-ros \
    ros-humble-tf2-geometry-msgs \
    ros-humble-rviz2 \
    ros-humble-rviz-common \
    ros-humble-rviz-default-plugins \
    ros-humble-rviz-visual-tools \
    ros-humble-lifecycle \
    ros-humble-lifecycle-msgs \
    iproute2 \
    net-tools \
    iputils-ping \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# workspace ROS2
WORKDIR /ros2_ws
RUN mkdir -p /ros2_ws/src

# packages mocap4ros2
RUN cd /ros2_ws/src && \
    git clone -b humble https://github.com/MOCAP4ROS2-Project/mocap4ros2_msgs.git || \
    git clone https://github.com/MOCAP4ROS2-Project/mocap4ros2_msgs.git

RUN cd /ros2_ws/src && \
    git clone -b humble https://github.com/MOCAP4ROS2-Project/mocap4ros2_optitrack.git || \
    git clone https://github.com/MOCAP4ROS2-Project/mocap4ros2_optitrack.git

#  installer les dépendances
RUN apt-get update && \
    rosdep update && \
    rosdep install --from-paths src --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

# Compiler le workspace
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    cd /ros2_ws && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release"

# Vérifier l'installation
RUN /bin/bash -c "source /opt/ros/humble/setup.bash && \
    source /ros2_ws/install/setup.bash"

# pandas
RUN apt-get update && \ 
apt-get install -y --no-install-recommends python3-pandas && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

# Configuration de l'environnement
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc && \
    echo "source /ros2_ws/install/setup.bash" >> ~/.bashrc

# Créer les dossiers de configuration
RUN mkdir -p /ros2_ws/config /ros2_ws/launch

# fichiers de configuration
COPY optitrack.yaml config/optitrack.yaml
COPY ros_entrypoint.sh /ros_entrypoint.sh
RUN chmod +x /ros_entrypoint.sh

# script.py
COPY tools.py /ros2_ws/tools.py

COPY instruction.py /ros2_ws/instruction.py
RUN chmod +x /ros2_ws/instruction.py

COPY calibration.py /ros2_ws/calibration.py
RUN chmod +x /ros2_ws/calibration.py

COPY axxb.py /ros2_ws/axxb.py
RUN chmod +x /ros2_ws/axxb.py

COPY camera.py /ros2_ws/camera.py
RUN chmod +x /ros2_ws/camera.py

# DEBUG

# COPY out3.csv /ros2_ws/out.csv

# ports nécessaires
EXPOSE 1511/udp

ENTRYPOINT ["/ros_entrypoint.sh"]

CMD ["bash"]

