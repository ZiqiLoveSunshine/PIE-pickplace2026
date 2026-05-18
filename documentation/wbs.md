# WBS - Projet Pick-and-Place (PIE 2025-2026)

Format hierarchique en syntaxe etoilee.

```text
* Projet PIE Pick-and-Place
** 1. Gouvernance et coordination
*** 1.1 Cadrage objectifs et livrables
*** 1.2 Organisation equipe et RACI
*** 1.3 Synchronisation inter-equipes
*** 1.4 Suivi planning et jalons

** 2. Environnement technique transverse
*** 2.1 Dockerisation
**** 2.1.1 Images Docker
**** 2.1.2 Scripts et entrypoints
*** 2.2 Infrastructure ROS2
**** 2.2.1 Topics et messages
**** 2.2.2 Interfaces communes
*** 2.3 Configuration reseau laboratoire U2IS
*** 2.4 Documentation installation et usage

** 3. Developpements metier
*** 3.1 Lot Cage - Optitrack
**** 3.1.1 Prise en main Optitrack et rigid bodies
**** 3.1.2 Acquisition donnees markers rigidbodies
**** 3.1.3 Calibration cage vers base robot AX egal XB
**** 3.1.4 Publication instructions instruction_cage
**** 3.1.5 Calcul et publication erreurs
**** 3.1.6 Tracking camera dans la cage camera_pose
*** 3.2 Lot Camera - ZED Mini
**** 3.2.1 Setup materiel GPU CUDA SDK ZED
**** 3.2.2 Integration zed-ros2-wrapper
**** 3.2.3 Node data_processor changement de repere
**** 3.2.4 Publication coordonnees objets vers ROS commun
**** 3.2.5 Prototype augmented_odometry
**** 3.2.6 Preparation pistes fusion Kalman
*** 3.3 Lot Bras robotique
**** 3.3.1 Prise en main bras et securite
**** 3.3.2 Controle manuel interface RViz
**** 3.3.3 Controle par code
**** 3.3.4 Controle automatique vers cible
**** 3.3.5 Commande pince avec seuil effort

** 4. Integration et validation
*** 4.1 Integration systeme
**** 4.1.1 Couplage Cage et Bras
**** 4.1.2 Couplage Camera et Bras
**** 4.1.3 Deux modes de perception independants
**** 4.1.4 Validation des transformations de repere
*** 4.2 Validation et demonstration
**** 4.2.1 Scenarios de test en cage
**** 4.2.2 Verification preconditions execution
**** 4.2.3 Tests pick-and-place bout en bout
**** 4.2.4 Analyse ecarts et ameliorations

** 5. Livrables et capitalisation
*** 5.1 Suite logicielle complete
*** 5.2 Documentation technique utilisateur
*** 5.3 Donnees et modeles environnement
*** 5.4 Rapport final et synthese resultats
```
