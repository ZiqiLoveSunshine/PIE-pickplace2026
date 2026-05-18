Voici la liste des fichiers dans ce dossier:

camera-in-cage.svo2 : la video (en stereo) de notre deplacemnet dans la voiliere

cage_traj.json : notre trajectoire d'apres les donnes de l'optitrack
camera_trajectory.json : notre trajectoire d'apres le flux video 

donnes_cage_camera : notre trajectoire d'apres l'optitrack : un echo > txt

cage_to_traj.py : transfomer les donnes_cage_camera en json bien formate
get_cam_pos.py : transfomer la video stereo en points dans l'espace : trajectoire
visupyvista.py : prendre un .json et l'afficher dans une fenetre

attention : il faut avoir pyvista et numpy, et avoir l'affichage graphique permis (voir readme principal)
