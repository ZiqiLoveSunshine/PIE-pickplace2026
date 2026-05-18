# Pipeline robotique: cage

Ce dépôt contient tous les codes pour traiter les données fournies par la cage et acquises par le logiciel optitrack.
Il permet:
- Mettre en place l'environnement d'exploitation pour la cage;
- Faire la calibration du robot dans la cage;
- Donner les instructions de mouvement au robot dans le but de d'attraper l'objet désiré;
- Calculer le vecteur entre deux objets;
- Traquer des objets.

## Docker

### Structure des fichiers
| Fichier | Rôle |
|---------|------|
| `Dockerfile` | Définit l'image Docker avec ROS2 et les dépendances. |
| `optitrack.yaml` | Configuration pour se connecter au réseau U2IS. |
| `ros_entrypoint.sh` | Script exécuté au lancement du conteneur (connexion aux topics OptiTrack). |

Le fichier docker `Dockerfile` contient le nécessaire pour executer les outils permettant de contrôler le robot à 
partir des données fournies par optitrack. Le fichier `optitrack.yaml` contient le nécessaire pour se connecter au 
réseau de l'U2IS. Le fichier `ros_entrypoint.sh` est executé à chaque lancement de l'image docker. Notamment, il se connecte aux topics de l'optitrack.

Pour éviter les problèmes de compatibilité entre les outils ROS et les outils de développement que les élèves utilisent dans leur scolarité, tout est conteneurisé dans Docker. Voici un lien pour une introduction: https://docs.docker.com/get-started/. 




## Lancement du docker

| Commande | Description |
|----------|-------------|
| `make bdocker` | Construit l'image Docker. *Long (prévoyez du temps).* |
| `make rdocker` | Lance le conteneur Docker. **Doit être connecté au réseau U2IS en filaire.** |

Lors du lancement de l'image docker, il est necessaire d'être connecter au réseau de l'U2IS en filaire.

**Remarques (dans le docker):**
- L'option `--net=host` est importante pour que le docker est accès au réseau du laboratoire;
- La construction de l'image docker est assez longue (le temps d'aller se faire un café);

## ROS

`ROS` (Robot Operating System) est un framework d'outils permettant de manipuler des robots de toutes sortes. **On utilise ROS2 Humble** (la documentation https://docs.ros.org/en/humble/).

Il permet notamment d'écouter et poster sur des topics qui sont des caneaux permettant d'échanger des messages entre les ordinateurs et les robots. 

## Optitrack
Optitrack est le logiciel permettant de détecter les objets dans la cage. Le logiciel tourne sur l'ordinateur relié à la cage d'experimentation.

Le logiciel voit les billes réfléchissantes - des markers. Ils faut donc les positionnées sur l'objet que l'on veut traquer. Les positions des billes sont postées sut le topic `/markers`.

Optitrack permet de définir des objets, appelé des rigidbodies, à partir de markers qui sont détectés dans la cage. Les coordonnées des objets et leurs quatrenions pour la rotation sont postés sur le topic `/rigidbodies`. Un rigidbodies est défini par un *Names* et un *Streaming ID* qui est le nom de l'objet lorsqu'il est posté sur le topic.  Il faut au minimum trois markers pour définir un rigidbodies. 

Une référence: https://wiki.ros.org/mocap_optitrack.

### Topics ROS2
Voici les principaux topics à connaitre:
- `/markers` : Publie les positions des *markers* détectés.
- `/rigidbodies` : Publie les positions et orientations (*quaternions*) des *rigid bodies* (objets définis par ≥3 markers).
- `/instruction_cage` : Topic où sont publiées les instructions pour le robot (coordonnées de la cible dans le repère du robot).
- `/errors` : Publie l'erreur entre l'objet cible et la pince du robot.
- `/camera_pose` : Publie la position de la caméra dans la cage.
- `/robot_pose`: Publie les coordonnées du robot dans la base du robot. La publication est gérée par l'équipe qui gère le bras robotique.

## Scripts python

Plusieurs scriptes python servant à:
- calibrer le robot;
- donner les instruction au robot;
- mesurer la distance entre l'objet cible et la pince du robot en fonction du temps;
- traquer le mouvement de la caméra;

Le fichier `tools.py` contient notamment les *Streaming Id* des objets (qu'il faut modifié s'ils sont redéfinis).

---

### TLDR

---

| Fichier | Rôle | Dépendances/Utilisations | Topics ROS2 associés |
| --- | --- | --- | --- |
| tools.py | Fichier de configuration central : contient les Streaming IDs, noms des topics, et chemins de fichiers (ex: CSV_PATH). | Utilisé par tous les autres scripts. | Aucun (configuration statique). |
| calibration.py | Acquiert les données pour déterminer la base du robot (position de la pince dans les repères robot/cage). | tools.py, axxb.py (pour le changement de base). | /rigidbodies, TOPIC_ROBOT (défini dans tools.py). |
| instruction.py | Calcule les coordonnées de l'objet cible dans le repère du robot et publie les instructions. | tools.py, axxb.py. | /rigidbodies, /instruction_cage. |
| tacage.py | Publie l'erreur entre l'objet cible et la pince du robot (distance/vecteur). | tools.py. | /rigidbodies, /errors. |
| camera.py | Publie la position de la caméra dans la cage. | tools.py. | /rigidbodies, /camera_pose. |
| axxb.py | Contient la logique pour le changement de base (transformation de coordonnées). | Utilisé par calibration.py et instruction.py. | Aucun (fonctions utilitaires). |

---

### Calibration

Le script `calibration.py` permet d'acquerir les données nécessaires à la détermination de la base du robot.

**Prérequis:**
- la pince doit être repérée par un rigidbody d'identifiant connu (éventuellement modifier l'id de la pince dans `tools.py`);
- la position de la pince doit être publier sur le topic `rigid_bodies` (sinon changer `TOPIC_NAME` dans `tools.py`);
- le robot doit publier sur un topic la position de la pince dans son repère (le nom du topic est définie dans `TOPIC_ROBOT` dans `tools.py`).

**Usage:**
- `python3 calibration.py` dans le docker. 

**Résultat:**
- les coordonnées de la pince dans la base du robot et dans la base de la cage sont écrites dans un fichiers de nom `CSV_PATH` dans `tools.py`;
- A chaque lancement les coordonnées de la pince dans la base du robot et de la cage sont ajouter au fichier `CSV_PATH`.

**Remarques:**
- Pour faire une calibration complète, une vingtaine de points de la pince dans des positions différentes doivent être pris; 
- **Il faut faire attention à la rotation de la pince et la hauteur de la pince soient différentes à chaque fois.**

### Instruction

Le script `instruction.py` donne les coordonnées de l'objet cible dans les coordonnées de la base du robot. 

**Prérequis:**
- **Il est a executé impérativement après l'acquisition des données nécessaires à la calibration;**
- L'objet doit être capté par l'optitrack et publié sur le topic défini dans la variable `TOPIC_NAME` dans  `tools.py`;

**Usage:**
- `python3 instruction.py &` dans le Docker (il est interressant de le lancer en arrière plan pour pouvoir faire autre chose en même temps); 

**Résultats:**
- Le script calcule et publie les instructions sur le topic `/instruction_cage`;
- Le script affiche sur la sortie standard le résultat du changement de base avec notamment: les erreurs, les données aberrantes (et donc enlevées); 
- Le script publie sur le topic un message de type `Transform`.

**Remarques:**
- Le code necessaire pour déterminer le changement de base se trouve dans le fichier `axxb.py`.

### Traçage

Publie l'erreur entre l'objet et la bras sur `/errors`.

**Prérequis:**
- L'objet `REF_NAME` (dans `tools.py`) doit être dans la cage (par défaut c'est la pince du robot);
- L'objet `TARGET_NAME` (dans `tools.py`) doit être dans la cage;

**Usage:**
- `python3 tacage.py &` dans le Docker.

**Résultat:**
- Le script calcule et publie les instructions sur le topic `/errors`;
- Le script publie sur le topic un message de type `Transform`.

### Traquage de la caméra

Publie la position de la caméra dans la cage `/errors`.

**Prérequis:**
- L'objet `CAMERA_NAME` (dans `tools.py`) doit être dans la cage.

**Usage:**
- `python3 camera.py &` dans le Docker.

**Résultat:**
- Le script calcule et publie les instructions sur le topic `/camera_pose`;
- Le script publie sur le topic un message de type `Transform`;

## TODO

Plusieurs axes d'amélioration sont possibles:
-  Passer les variables globales définies dans `tools.py` en variable d'environnement;
- Faire un peu de refactoring du code (notamment le code comment au *Listener Node*);
- Intégrer un outil comme RViz pour visualiser les positions en temps réel.