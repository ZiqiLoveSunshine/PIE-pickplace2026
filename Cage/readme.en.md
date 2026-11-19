# Robotics pipeline: cage

This repository contains all the code for processing the data provided by the cage and acquired by the Optitrack software.
It makes it possible to:
- Set up the operating environment for the cage;
- Calibrate the robot in the cage;
- Give movement instructions to the robot in order to grab the desired object;
- Compute the vector between two objects;
- Track objects.

## Docker

### File structure
| File | Role |
|---------|------|
| `Dockerfile` | Defines the Docker image with ROS2 and the dependencies. |
| `optitrack.yaml` | Configuration for connecting to the U2IS network. |
| `ros_entrypoint.sh` | Script run when the container starts (connects to the OptiTrack topics). |

The `Dockerfile` contains everything needed to run the tools that control the robot from
the data provided by Optitrack. The `optitrack.yaml` file contains what is needed to connect to the
U2IS network. The `ros_entrypoint.sh` file is run every time the Docker image starts. In particular, it connects to the Optitrack topics.

To avoid compatibility issues between the ROS tools and the development tools students use during their studies, everything is containerized in Docker. Here is a link to an introduction: https://docs.docker.com/get-started/.




## Running Docker

| Command | Description |
|----------|-------------|
| `make bdocker` | Builds the Docker image. *Slow (plan for some time).* |
| `make rdocker` | Starts the Docker container. **Must be connected to the U2IS network via Ethernet.** |

When starting the Docker image, you must be connected to the U2IS network via a wired connection.

**Notes (inside Docker):**
- The `--net=host` option is important so that the container has access to the lab network;
- Building the Docker image takes quite a while (enough time to go grab a coffee);

## ROS

`ROS` (Robot Operating System) is a framework of tools for operating all kinds of robots. **We use ROS2 Humble** (documentation: https://docs.ros.org/en/humble/).

In particular, it lets you listen to and publish on topics, which are channels for exchanging messages between computers and robots.

## Optitrack
Optitrack is the software that detects objects in the cage. It runs on the computer connected to the experimentation cage.

The software sees the reflective balls - markers. They must therefore be placed on the object you want to track. The marker positions are published on the `/markers` topic.

Optitrack lets you define objects, called rigid bodies, from markers detected in the cage. The objects' coordinates and their rotation quaternions are published on the `/rigidbodies` topic. A rigid body is defined by a *Name* and a *Streaming ID*, which is the object's name when it is published on the topic. At least three markers are needed to define a rigid body.

A reference: https://wiki.ros.org/mocap_optitrack.

### ROS2 topics
Here are the main topics to know:
- `/markers`: Publishes the positions of the detected *markers*.
- `/rigidbodies`: Publishes the positions and orientations (*quaternions*) of the *rigid bodies* (objects defined by ≥3 markers).
- `/instruction_cage`: Topic where the instructions for the robot are published (target coordinates in the robot frame).
- `/errors`: Publishes the error between the target object and the robot's gripper.
- `/camera_pose`: Publishes the camera's position in the cage.
- `/robot_pose`: Publishes the robot's coordinates in the robot frame. Publishing is handled by the team working on the robotic arm.

## Python scripts

Several Python scripts are used to:
- calibrate the robot;
- give instructions to the robot;
- measure the distance between the target object and the robot's gripper over time;
- track the camera's movement;

The `tools.py` file notably contains the objects' *Streaming IDs* (which must be updated if they are redefined).

---

### TLDR

---

| File | Role | Dependencies/Usage | Associated ROS2 topics |
| --- | --- | --- | --- |
| tools.py | Central configuration file: contains the Streaming IDs, topic names, and file paths (e.g. CSV_PATH). | Used by all the other scripts. | None (static configuration). |
| calibration.py | Acquires the data needed to determine the robot frame (gripper position in the robot/cage frames). | tools.py, axxb.py (for the change of basis). | /rigidbodies, TOPIC_ROBOT (defined in tools.py). |
| instruction.py | Computes the target object's coordinates in the robot frame and publishes the instructions. | tools.py, axxb.py. | /rigidbodies, /instruction_cage. |
| tacage.py | Publishes the error between the target object and the robot's gripper (distance/vector). | tools.py. | /rigidbodies, /errors. |
| camera.py | Publishes the camera's position in the cage. | tools.py. | /rigidbodies, /camera_pose. |
| axxb.py | Contains the logic for the change of basis (coordinate transformation). | Used by calibration.py and instruction.py. | None (utility functions). |

---

### Calibration

The `calibration.py` script acquires the data needed to determine the robot frame.

**Prerequisites:**
- the gripper must be tracked by a rigid body with a known ID (update the gripper ID in `tools.py` if needed);
- the gripper position must be published on the `rigid_bodies` topic (otherwise change `TOPIC_NAME` in `tools.py`);
- the robot must publish the gripper position in its own frame on a topic (the topic name is defined by `TOPIC_ROBOT` in `tools.py`).

**Usage:**
- `python3 calibration.py` inside Docker.

**Result:**
- the gripper coordinates in the robot frame and in the cage frame are written to a file named by `CSV_PATH` in `tools.py`;
- On each run, the gripper coordinates in the robot and cage frames are appended to the `CSV_PATH` file.

**Notes:**
- For a complete calibration, about twenty points with the gripper in different positions must be recorded;
- **Make sure the gripper's rotation and height are different each time.**

### Instruction

The `instruction.py` script gives the target object's coordinates in the robot frame.

**Prerequisites:**
- **It must be run only after the calibration data has been acquired;**
- The object must be captured by Optitrack and published on the topic defined by the `TOPIC_NAME` variable in `tools.py`;

**Usage:**
- `python3 instruction.py &` inside Docker (it is useful to run it in the background so you can do other things at the same time);

**Results:**
- The script computes and publishes the instructions on the `/instruction_cage` topic;
- The script prints the result of the change of basis to standard output, including the errors and the outliers (which are removed);
- The script publishes a `Transform` message on the topic.

**Notes:**
- The code needed to determine the change of basis is in the `axxb.py` file.

### Tracking

Publishes the error between the object and the arm on `/errors`.

**Prerequisites:**
- The `REF_NAME` object (in `tools.py`) must be in the cage (by default, the robot's gripper);
- The `TARGET_NAME` object (in `tools.py`) must be in the cage;

**Usage:**
- `python3 tacage.py &` inside Docker.

**Result:**
- The script computes and publishes the instructions on the `/errors` topic;
- The script publishes a `Transform` message on the topic.

### Camera tracking

Publishes the camera's position in the cage on `/errors`.

**Prerequisites:**
- The `CAMERA_NAME` object (in `tools.py`) must be in the cage.

**Usage:**
- `python3 camera.py &` inside Docker.

**Result:**
- The script computes and publishes the instructions on the `/camera_pose` topic;
- The script publishes a `Transform` message on the topic;

## TODO

Several improvements are possible:
- Move the global variables defined in `tools.py` to environment variables;
- Do some refactoring of the code (especially the code shared by the *Listener Node*);
- Integrate a tool like RViz to visualize positions in real time.
