
bdocker: Dockerfile instruction.py optitrack.yaml ros_entrypoint.sh tools.py tracage.py calibration.py
	sudo docker build . -t ros2_optitrack

rdocker: bdocker
	sudo docker run -it --net=host ros2_optitrack:latest