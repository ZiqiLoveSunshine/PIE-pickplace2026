FROM ros:humble-ros-base AS base

# Install basic build tools
RUN apt-get update && apt-get install -y \
    python3-colcon-common-extensions \
    && rm -rf /var/lib/apt/lists/*

# Create workspace
WORKDIR /ros_ws
COPY ./augmented_odometry ./augmented_odometry

# Install dependencies using rosdep
# This avoids the "multiple packages" error by only scanning the current src
RUN apt-get update && \
    rosdep update && \
    rosdep install --from-paths augmented_odometry --ignore-src -y && \
    rm -rf /var/lib/apt/lists/*

# Build the workspace
RUN . /opt/ros/humble/setup.sh && \
    colcon build --symlink-install

# Automatically source the workspace for interactive shells
RUN echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
RUN echo "source /ros_ws/install/setup.bash" >> ~/.bashrc

CMD ["bash"]