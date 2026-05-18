// --- Importations ---
#import "@preview/timeliney:0.4.0"

// --- Configuration du document ---
#set page(paper :"a5",
footer: context [
  #set align(right)
  #counter(page).display()
])

#set text(size : 11pt, lang: "fr")
#set heading(numbering: "I. 1.", hanging-indent: 1.5em)
#set enum(spacing: 1.5em) // Règle l'espace entre les points

// --- Page de garde ---

#grid(
  columns: (1fr,1fr),
  align(left,image("logo_ensta.png", width : 50%)),
  align(right,image("logo_institut_polytechnique.png", width : 50%))
)

#align(center+horizon)[
  #line(length:100%,stroke: 0.5pt)
  #block(text(weight: "bold", 2em)[PIE 10 :\ Manipulation guidée par la perception – Un pipeline pour la tâche robotique \ pick-and-place])
  #text(size: 1.2em)[Rapport final]\
  #text(size: 1.2em)[MDC_4PIE2_TA]\
  #text(weight: "light",1.2em)[2026]
  #v(1em)
  #text(size : 1em)[Thiago Rosa Carvalho]\
  #text(size : 1em)[Mohamed Amine Changal]\
  #text(size : 1em)[Yasmine Dhouib]\
  #text(size : 1em)[Paul-Edouard Espanol]\
  #text(size : 1em)[Gustavo Kuratomi]\
  #text(size : 1em)[Montans Zucheram Diego Magno]\
  #text(size : 1em)[Mohamed Salah Mhiri]\
  #text(size : 1em)[Henry Royer]\
  #text(size : 1em)[Leto Van Ruymbeke]\
  #text(size : 1em)[Tianze Xia]\
  #text(size : 1em)[Thomas Zsdanszki]\
  #v(2em)
  #line(length:100%,stroke: 0.5pt)
]


// --- Table des matières ---
#pagebreak()
#show outline.entry: set block(above: 1.5em)
#outline(indent : auto)
#pagebreak()

// --- Corps du Rapport ---
= Enjeux et objectifs
\
Ce projet s’inscrit dans une démarche visant à automatiser des tâches de manipulation d’objets dans des environnements contrôlés. L’objectif est de développer un système capable de saisir, déplacer et positionner des objets de manière autonome, en s’adaptant à différents niveaux d’information environnementale.

== Objectifs
L’U2IS nous met à disposition un robot doté de quatre roues et d’un bras articulé pour:
- Développer un système de contrôle pour le robot.
- Permettre au robot de saisir un objet et de le déplacer vers une cible de manière autonome.
- Atteindre deux niveaux d’autonomie :
  - Contrôle basé sur des informations complètes dans un environnement maîtrisé (cf @Methode).
  - Contrôle basé sur des informations relatives dans un environnement contrôlé.


== Livrables
Les livrables attendus sont les suivants : 
#table(
  columns : 3,
  [*Livrable*],[*Description*],[*Date de rendu*],
  [Suite logiciel], [Logiciel complet pour le contrôle du robot (interface pour le contrôler, algorithmes pour lui faire des tâches autonomes). Cela pour les deux degrés d'automonomie décrits plus tôt.],[Mi-mai],
  [Environnement de test],[Au moins deux scénarios variés dans la cage d'expérimentation pour valider les fonctionnalités],[Mi-mai],
  [Documentation technique],[Manuel d'utilisation],[Mi-Avril],
  [Modèle 3D et données environnementales],[Représentation 3D de la cage et des objets pour la simulation],[Mi-Avril],
)

== Méthodes <Methode>
Ces objectifs impliquent de : 
  - Disposer d'une représentation 3D de l'environnement géométrique et sémantique :
    - Dans un premier temps avec la cage et les caméras de la cage;
    - Caméra stéréo ZED Mini (fournie par le laboratoire);
  - Construire des environnements de test dans le laboratoire U2IS
  - Etre capable de contrôler un bras robotique
  - Construire une pipeline permettant d'acquérir une représentation de l'environnement en vu de faire effectuer des tâches au robot de manière automatique


= Organisation de l'équipe
== Matrice RACI
#align(center)[
  #figure(
    caption: [Matrice RACI _Cage_ et _Caméra_],
    table(
      columns : 7,
      align : center + horizon,
      table.cell(colspan: 4, fill: rgb("#ef5c00c1"))[*Equipe _Cage_*],
      table.cell(colspan : 3, fill : rgb("#50f404db"))[*Aide*],
      [*Tâches*],[Thomas],[Mohamed A.],[Tianze],[Thiago],[P-E],[Ziqi],
      [Prise en main],[R,A],[R],[],[],[],[C],
      [Calibration et \ instruction robot],[R,A],[R],[],[I, C],[],[C],
      [Suivi caméra],[R,A],[],[],[],[C],[C],
      table.cell(colspan : 5, fill :rgb("#009fefbf"))[*Equipe _Camera_*],
      table.cell(colspan : 2,fill : rgb("#50f404db"))[*Aide*],
      [*Tâches*],[Henry],[Paul-Edouard],[Leto],[Mohamed S.],[Ziqi],[Thomas],
      [Prise en main],[R,A],[R,A],[I],[I],[I],[],
      [Docker & \ Setup],[C,I],[R,A],[I],[],[I],[],
      [Services ZED],[R],[R,A],[I],[],[I],[],
      [Topic ROS],[R,A],[C,I],[I],[],[I],[I],
    )
  )
]<RACI>

#pagebreak()
#align(center)[
  #figure(
    caption: [Matrice RACI _Bras_],
    table(
     columns : 7,
     align : center + horizon,
     table.cell(colspan :5,fill :rgb("#ea06ff8e"))[*Equipe _Bras_*],
     table.cell(colspan :2,fill :rgb("#50f404db"))[*Aide*],
     [*Tâches*],[Thiago],[Gustavo],[Diego],[Yasmine],[Thomas],[P-E],
     [Prise en main],[R,A],[R],[R],[R],[],[],
     [Contrôle par RViz],[R,A],[R],[R],[R],[],[],
     [Contrôle par code],[R,A],[R],[R],[I],[],[],
     [Contrôle automatique],[R,A],[R],[R],[I],[C,I],[C,I],
    )
  )
]

== Descriptif
\
Les sous-équipes n'ont pas changées de membres, mais certaines se sont retrouvées
réduites suite au départ des étudiant tunisiens au second semestre. Ces derniers
sont marqués d'une $(*)$. 
\
#align(center)[#text(weight :"bold",1.1em)[L'équipe _Caméra_]]
$bold("Responsabilité : ")$ Perception 3D et acquisition des données environnementales.\
$bold("Membres : ")$ 
  - Henry Royer;
  - Paul-Edouard Espanol;
  - Leto Van Ruymbeke;
  - Mohamed Salah Mhiri$(*)$;
$bold("Missions principales :")$
  - Intégration et calibration de la caméra stéréo ZED Mini
  - Développement des algorithmes de reconstruction 3D de l'environnement
\
#align(center)[#text(weight :"bold",1.1em)[L'équipe _Cage_]]
$bold("Responsabilité : ")$Conception et gestion des environnements de test.\
$bold("Membres :")$
  - Thomas Zsdanszki, Responsable global du projet;
  - Mohamed Amine Changal$(*)$;
  - Tianze Xia;
$bold("Missions principales :")$
  - Aménagement de la cage d'expérimentation
  - Intégration
  - Définition des scénarios de test pour valider les niveaux d'autonomie du robot
\
#align(center)[#text(weight :"bold",1.1em)[L'équipe _Bras_]]
$bold("Responsable : ")$Contrôle et automatisation des mouvements du bras.
$bold("Membres :")$
  - Montans Zucheram Diego Magno, Leader de l'équipe;
  - Gustavo Kuratomi, Responsable algorithmes;
  - Thiago Rosa Carvalho, Responsable algorithmes;
  - Yasmine Dhouib$(*)$, Responsable simulations;
$bold("Missions principales :")$
  - Développement des algorithmes de contrôle du bras robotique
  - Intégration des données environnementales pour des mouvements précis
  - Validation des tâches de saisie et déplacement d'objets en conditions réelles


= Livrables Fournis
Nos livrables sont purement *logiciels*. En effet, le robot étant fournie,
et non à concevoir par le groupe, l'objectif de ce projet consistait
à créer la suite logicielle pour contrôler ce robot. Les 3 livrables suivent 
donc la segmentation du groupe en sous-équipes que nous avons établie : 
3 images _Docker_ distinctes. 
#v(1em)
  + *Le code de fonctionnement de la cage*
    \ La *cage* est une structure contenant 6 caméras infrarouges perchées, reliées 
    à un logiciel (_Optitrack_) qui repère des billes reflechissantes dans la cage. 
    Le logiciel traite les positions, qui sont mises sur le réseau du labo. Le code
    de la cage doit acquérir ces données, de définir des objets sur lesquels
    sont posées ces boules. En listant ces objets (dont fait parti le bras, sur
    lequel on a posé ces billes, mais aussi de balles et des obstacles), on peut
    les trier et les *catégoriser*. Ceci permet une étape de *calibration*, nécessaire 
    pour établir une correspondance entre le repère de la cage et celui du robot. 
    Une fois cette correspondance obtenue, on peut définir des instructions à donner au robot 
    pour réaliser une tâche, comme attraper une balle. \
    Enfin, un dernier script permet de *valider* les mouvements de la caméra, ce 
    qui a grandement servi au code caméra en tant que référence, pour qu'une 
    utilisation indépendante, avec la caméra uniquement, soit finalement possible. 
  + *Le code de la caméra*
    \ Ce code est en deux niveaux. D'abord, il s'approprie les fonctionnalités
    fabricant de la caméra, qui a la capacité de repérer des objets en les 
    classant par *catégorie* (humain, animal, objet électronique...), et leur
    donner une position $(x,y,z)$ dans le *repère* de la caméra. \ 
    Le code acquérit 
    ces données, et les converti pour les fournir aux autres équipes. Le robot 
    est alors capable d'estimer sa distance avec telle ou telle entité de son 
    environnement, qu'il sait identifier grâce à la caméra. Cette dernière étant posée sur le bras, elle constitue en plus
    un moyen pour le robot de se *repérer* dans son environnement direct. 
  + *Le code de contrôle du bras mécanique*
    \ L'objectif de ce code est, étant données les *coordonnées* d'un objet,
    entrées par l'utilisateur, de permettre au bras de réaliser les
    déplacements (rotations des différents coudes) nécessaires pour
    atteindre cet objet. Il est aussi possible d'ordonner la fermeture 
    de la pince du bras pour saisir l'objet. La fermeture s'arrête à 
    un seuil donné du retour de force, pour éviter de casser des objets 
    fragiles. 


C'est 3 images sont conçues de sorte à fonctionner sur 3 terminaux
différents. Les 3 canaux communiquent grâce à _ROS2_, qui centralise leur 
utilisation en jouant le rôle de socle commun. De plus, la caméra et la cage fonctionnent indépendamment, en 
tant que 2 systèmes de repérage différents pour le robot, qui peut se répérer 
grâce à l'un ou grâce à l'autre. Mais elles sont utilisables surtout indépendamment
du robot, ce qui signifie qu'il est tout à fait possible de les utiliser pour 
un nouveau robot. 

#pagebreak()
= Déroulé du Projet et GANTT final
== Déroulé réel
La grande majorité du déroulé réel du projet a suivi les prévision exactes de notre 
diagramme de *GANTT* prévisonnel, à quelques légères corrections près. Voici un résumé par équipe. 
#v(1em)
  + L'équipe _Cage_
    - [_Fin Octobre - début Novembre_] : Prise en main du matériel
    - [_Novembre - fin Décembre_] : Dockerisation de ROS
    - [_Fin Décembre - mi-Janvier_] : Logiciel de visualisation
    Dès mi-janvier, la cage était fonctionnelle et la détection d'objet aussi. La partie
    _Logiciel de visualisation_ n'a finalement pas été concluante et a été *abandonnée* après discussion avec nos encadrants-chercheurs.
  + L'équipe _Caméra_
    - [_Fin Octobre_] : Prise en main du matériel
    - [_Novembre - mi-Décembre_] : *Dockerisation* & setup de l'environnement
    - [_mi-Décembre - Janvier_] : Obtention de la distance caméra-objet à partir des données fournies par le logiciel interne de la _ZED_
    - [_Début Janvier - mi-Janvier_] : Automatisation & topic _ROS_
    Dès mi-janvier, la caméra est maitrisée. Elle détecte les objets et
    on peut récupérer leur position et leur nature.
  + L'équipe _Bras_
    - [_Fin Octobre - début Novembre_] : Prise en main du matériel
    - [_Début Novembre - fin Novembre_] : Contrôle du bras par l'interface graphique fournie, sans code
    - [_Fin Novembre - fin Décembre_] : Contrôle du bras par code 
    - [_Fin Décembre - fin Janvier_] : Contrôle automatique, simplement en donnant les coordonnées du point à atteindre
    Fin décembre, le jalon final, consistant à contrôler le bras à l'aide de données au format
     fourni par la caméra et la cage, était atteint.
  + Mise en commun
    - [_Fin Janvier - fin Février_] : Association du bras et de la cage; le robot peut se réperer dans la cage et y réaliser des tâches sur commande
    - [_Fin Février - début Avril_] : Calibration de la caméra installée sur le bras, grâce à la cage.
    - [_Début Avril - Aujourd'hui_] : Indépendance de la caméra vis-à-vis de la cage : le robot peut se repérer uniquement grâce à la caméra, hors de la cage. 

$(*)$ A noter qu'à ce stade, certains précautions doivent être prises lors de l'éxécution de tests pick-and-place : mettre le robot en position _home_,
vérifier que la balle soit bien reconnue par la caméra, lancer la commande depuis le robot pour cibler les coordonnées reçues. <Precautions> 

#pagebreak()

== Arbre WBS

== GANTT final

#figure(
  timeliney.timeline(
    show-grid: true,
    {
      import timeliney:*
      // Variable mois
      let mois = ("Oct", "Nov", "Déc",
      "Jan", "Fév", "Mars", "Avr")
      // Définition de la ligne de temps
      headerline(group(([*2025-2026*],7)))
      headerline(group(..mois.map(m=>strong(m))))

      // Groupe Cage
      taskgroup(title : [*Cage*],style: (stroke :4pt + rgb("#ef5c00c1")),{
        task("Prise en main matériel", (from : 0.6, to:1.2), style :(stroke :3pt + rgb("#ef5c00")))
        task("Dockerisation ROS",(from:1.2, to:2.8), style :(stroke :3pt + rgb("#ef5c00")))
        task("Logiciel de visualisation", (from:2.8,to:3.5),style :(stroke :3pt + rgb("#ef5c00")))
      })

      // Groupe Caméra 
      taskgroup(title: [*Caméra*],style: (stroke :4pt + rgb("#009fefbf")),{
        task("Prise en main matériel",(from:0.6, to:1), style :(stroke :3pt + rgb("#009fef")))
        task("Dockerisation & setup env",(from:1,to:2.5), style :(stroke :3pt + rgb("#009fef")))
        task("Services ZED (distance, objet)", (from:2.5,to:3), style :(stroke :3pt + rgb("#009fef")))
        task("Automatisation et topic ROS",(from:3,to:3.4), style :(stroke :3pt + rgb("#009fef")))
      })

      // Groupe Bras
      taskgroup(title: [*Contrôle Bras*],style: (stroke :4pt + rgb("#ea06ff8e")),{
        task("Prise en main matériel",(from:0.6,to:1.2), style :(stroke :3pt + rgb("#ea06ffdd")))
        task("Contrôle du bras par RViz",(from:1.2,to:1.9), style :(stroke :3pt + rgb("#ea06ffdd")))
        task("Contrôle par code",(from:1.9,to:2.8), style :(stroke :3pt + rgb("#ea06ffdd")))
        task("Contrôle automatique",(from:2.8,to:3.7), style :(stroke :3pt + rgb("#ea06ffdd")))
      })

      // Milestone
      milestone(at:3.6,
      align(center)[
        #rect(
          stroke: 1pt + rgb("#1202f4dd"),
          stack(dir : ttb,
            spacing : 4pt,
            text(fill : rgb("#1202f4dd"))[Livrables fin Janvier : ],
            text(fill : rgb("#ef5c00c1"))[- Cage fonctionnelle, détection d'objets  ],
            text(fill : rgb("#009fefbf"))[- Caméra détecte objets ],
            text(fill : rgb("#ea06ff8e"))[- Bras controllable]
          )
        )  
      ],    
      style: (stroke: (paint: rgb("#1202f4dd"), thickness: 1.5pt, dash: "dashed"))
      )

      // Mise en commun
      taskgroup(title: [*Mise en commun*],style:(stroke:4pt + rgb("#f50d0da0")),{
        task("Robot + Cage",(from:3.9,to:4.9),style:(stroke:3pt + rgb("#f50d0ddd")))
        task("Robot + Cage + Caméra", (from:4.9,to:6.1),style:(stroke:3pt + rgb("#f50d0ddd")))
        task("Robot + Caméra", (from:6.1,to:6.8),style:(stroke:3pt + rgb("#f50d0ddd")))
      })
    }
  ),
  caption : [Diagramme GANTT final.],
)<GANTT>



= Organisation Alternative <Orga_alt>
Le projet s'est, dans les grandes lignes, déroulé sans échec particulier ni retard. 
L'absence de cahier des charges *précis*, donnant les attendus chiffrés (temps de réponse, efficatcité) de ce que la suite logicielle rendue
doit permettre au bras de faire, empêche de savoir dans quelle mesure ce qui a été 
réalisé est satisfaisant. Cependant, le groupe a compris ce manque de précision comme
un défi. Celui de rendre le robot *le plus capable possible*, au sens de sa faculté 
à réaliser les tâches simples demandée : prise et de dépot d'objets.

En ce sens, il paraît important de mentionner que nous n'avons pas pu faire en sorte que 
le bras soit capable d'éviter les *collision* avec son environnement et avec lui-même. Il est arrivé 
régulièrement pendant nos tests que le bras, en exécutant une requête de notre part, se positionne 
dangereusement pour lui-même ou pour les utilisateurs environnement, menant ainsi à des collisions. 
Ces-dernières pourraient mener, par manque de vigilance, à des dégats sur le matériel voire à des 
blessures.

Pour corriger en partie ce problème, il est possible d'implémenter une *disjonction de cas* selon la position 
d'une cible par rapport au bras. En effet, actuellement, que ce soit pour une balle sur le sol ou une balle surélevée 
sur une table par exemple, la pince se positionne de la même manière pour l'attraper : à l'horizontale, les deux "doigts"
de la pince dans le plan parallèle au sol. Or, il serait plus judicieux que pour ce cas particulier, la pince plonge 
vers le sol du haut vers le bas, pour attraper la balle. Se mettre à la bonne hauteur avant d'avancer jusqu'à 
la balle n'est pas optimal et dangeraux. C'est typiquement ce genre de mouvements non-optimisé qui mène à des collisions
*évitables*, avec le sol ou des obstacles environnants. 

Pour éviter les collision avec lui-même, en revanche, il faudrait plutôt se tourner vers l'implémentation d'une
zone que la pince ne doit pas franchir, correspondant exactement à l'armature du robot (tout appart la pince). De 
cette manière, la pince ne peut plus percuter le chariot ou son bras.

Or, on sait désormais que l'équipe _Cage_ a perdu un mois sur l'étape _Logiciel de visualisation_, qui a finalement
été abandonnée. Une organisation alternative pertinente aurait donc pu être de greffer l'équipe _Cage_ dès Janvier
à l'équipe _Bras_, qui travaillait sur le contrôle automatique. Ceci aurait *accéléré* les choses puisque les tests
du bras sont facilités si plus de personnes y participent (entrée de commande, surveillance des données retournées
par le robot, reflexion constante et recherche de solutions). Ainsi, l'équipe _Bras_ aurait atteint leurs objectifs 
plus rapidement et aurait pu se concentrer sur les implémentations décrites plus tôt, atteignant ainsi de nouveaux 
objectifs.  

= Conclusion
== Réalisation des objectifs
Comme précisé en début du @Orga_alt, notre PIE était limité en terme d'exigences précises à faire réaliser au bras. En revanche, 
notre groupe est fier d'avoir pu remplir les différents objectifs intermédiaires qu'il s'est donné, comme la 
dockerisation qui assure une mise en commun efficace des travaux des différentes équipes, surout en ce qui concerne les
multiples dépendances entre _ROS2_ et les outils employés. La réussite, à 
la fois de la maîtrise de la cage et de la caméra, est vue par le groupe comme une complétion d'objectifs 
qui auraient pu nécessiter une passation aux équipes des années qui suivront. En effet, le robot est désormais capable
d'agir sur son environnement absolu (cage) comme relatif (caméra), deux jalons majeurs qu'une organisation 
moins efficace aurait pu ne jamais atteindre. 

Ce jalon majeur atteint, notre groupe a pu, sur la fin de la période dédiée, se concentrer sur des améliorations du robot
moins visibles, possibles justement grâce à cette polyvalence dans le contrôle du robot. A ce titre, on compte bon nombre de 
calibrations de la caméra grâce au point de vu absolu offert par la cage, même si cette phase peut être accelérée (_voir plus bas_).  

Le bras est désormais capable d'exécuter une série d'actions demandées, qu'il soit dans un environnement totalement connu, 
comme la cage, ou un environnement dont il ne connais que ce qui se trouve dans le cadre de sa caméra. La compatibilité 
assurée des différentes composantes logicielles du projet, rende ce projet adaptée à la postérité. Les étudiants qui 
le reprendront n'auront pas à reprendre tout depuis le début : deux fichiers complets, un guidant l'utilisateur (_README_)
l'autre, plus détaillé, à destination des développeurs, ont été rédigés pour assurer une transition fluide. 
== Expérience acquise
En terme de compétence technique, ce projet a représenté une véritable mine à connaissance en terme de robotique. Grâce à 
sa réalisation, les membres de l'équipe ont tous acquis une première introduction à _ROS2_, qui constitue une norme 
en terme de _framework_, quand on parle de robotique. De plus, ce projet est un exemple de projet réel en entreprise, 
notament dans l'industrie, où la mise en commun de différents composants (caméra, bras) et de différents acteurs 
(membres du groupe) sont de mises. C'est exactement un cas d'integration : on dispose de pièces variées que l'on doit
rendre compatibles. 

Mais c'est surout en terme d'organisation, de gestion et de travail d'équipe, que nos membres ont le plus appris. 
En effet, ce PIE est peut-être le premier cas dans notre parcours de subdivision réelle de l'équipe en groupes
indépendants devant mettre les résultats de leur travail en commun. On constate donc que les connaissances acquises
au cours du projet par un membre donné dépendent de l'équipe dans laquelle il a été placé. Les équipes sont donc très 
compétentes dans leur domaine, et n'ont pas perdu de temps à acquérir des compétences dont elles n'avaient pas besoin.
En revanche, un réel effort de communication leur a été demandé lors de la mise en commun des différents travaux, pour 
obtenir le résultat final : expliquer ce qu'on a fait aux autres en langage simple. 
== La suite
Pour la suite de ce projet, plusieures ameliorations pourraient être ajoutées. En effet, bien que nous ayons 
réussis à faire fonctionner le robot lorsque des membres du groupe executent le code, son autonomie peut être améliorée. 
D'abord, sa phase de calibration est longue est laborieuse, car manuelle : on donne une série de points de l'espace
que le robot doit atteindre avec sa pince, et on observe où il arrive avec la cage. Cette étape est nécessaire avant 
toute utilisation du robot en fonctionnement caméra, pour reconstruire la base du robot, en en trouvant l'origine en
particulier. Les équipes suivantes pourraient gagner du temps en implémentant une routine de plusieurs points que le
bras exécute les uns à la suite des autres, sous l'observations des caméras de la cage, pour une calibration automatique
en quelques minutes. 

Ensuite, les scripts manquent encore d'une imbrications ergonomique, qui permettraient le 
lancement de la pipeline à l'appuie d'un seul bouton, pour accélérer l'étape mentionné #link(<Precautions>)[#underline("en IV.1")].  

En terme d'exécution de mouvement, il arrive que le bras choisisse des trajectoires non-admissibles, qui mèneraient à des collisions avec
lui-même et son environnement, si on ne l'arrêtait pas rapidement. C'est aussi quelque chose qui doit être amélioré, surtout dans l'optique d'un robot
utilitaire à la maison. On peut aussi se convaincre qu'à l'utilisation réelle (tâches ménagères ou industielles), où on attend du robot une efficacité 
supérieur ou égale à celle d'un humain, le point de vue relatif donnée par la caméra embarquée sur le robot est insuffisant. En effet, 
lors d'une utilisation du robot pour aider un humain à faire la vaisselle, ou de deux robots faisant du pick-and-place ensemble dans une usine, 
que ce passe-t-il si un tiers retire un objet de l'environnement hors du champ de vision du robot, mais que ce même objet
était le prochain objectif du robot ? Au contraire, si une caméra extérieur supplémentaire est placée de sorte à avoir tout
ce qui entoure le robot dans son champ de vision, il ne peut plus se faire surprendre. 

Enfin, on peut se donner comme objectif de personnaliser le modèle de détection de la caméra embarquée, ou de créer différents modèles, 
qui s'adaptent à différentes tâches. Pour le moment, le modèe de détection est celui de _ZED_, le constructeur de la caméra, qui n'est 
donc pas dédié aux tâches prévues pour le robot. 

et ensuite tester ceci avec de l'odometrie optique (possibiliter de filtrer avec kalman et la position du robot)
faire le modele custom pour detecter des nouveaux types d’objets
