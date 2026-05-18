from geometry_msgs.msg import Vector3, Transform
from scipy.spatial.transform import Rotation as R

# ==================
# VARIABLES GLOBALES
# ==================

ROBOT_NAME = "1028"  # Id du rigidbody permettant de distinguer la base du robot
CLAMP_NAME = (
    "1046"  # Id du rigidbody permettant de distinguer la pince au bout du bras du robot
)

REF_NAME = CLAMP_NAME # Id de l'objet à traquer.

TARGET_NAME = "1034"  # Id du rigidbody représentant l'objet à saisir
CAMERA_NAME = "1051"  # Id du rigidbody représentant la caméra

TOPIC_NAME = "/rigid_bodies"  # nom du topic où sont postés les rigidbodies
TOPIC_ROBOT = "/robot_pose"  # nom du topic où sont postés les coordonnées du bras dans la base du robot


# Fichier où sont stockés les données pour calibrer le robot avec le système de motion capture
CSV_PATH = "out.csv"

# Header du fichier CSV_PATH où sont stockés les données pour calibrer le robot avec le système de motion capture
CSV_HEADER = [
    "c_tx",
    "c_ty",
    "c_tz",
    "c_qx",
    "c_qy",
    "c_qz",
    "c_qw",
    "r_tx",
    "r_ty",
    "r_tz",
    "r_rx",
    "r_ry",
    "r_rz",
    "r_qw_null",
]


# ======================
# FONCTIONS AUXILLIAIRES
# ======================


def error_between_rigid_bodies(rb_ref, rb_target) -> Transform:
    """
    Calcule l'erreur de position et d'orientation entre l'objet de référence et l'objet cible.

    Paramètres :
        rb_ref    : RigidBody  objet de référence (bras)
        rb_target : RigidBody  objet cible

    Retourne :
        Transform  erreur de position et d'orientation entre rb_ref et rb_target (coordonnées de la cage)
    """
    translation = Vector3()
    translation.x = rb_target.pose.position.x - rb_ref.pose.position.x
    translation.y = rb_target.pose.position.y - rb_ref.pose.position.y
    translation.z = rb_target.pose.position.z - rb_ref.pose.position.z

    q_ref = rb_ref.pose.orientation
    q_target = rb_target.pose.orientation

    rotation_ref = R.from_quat([q_ref.x, q_ref.y, q_ref.z, q_ref.w])
    rotation_target = R.from_quat([q_target.x, q_target.y, q_target.z, q_target.w])

    rotation_error = rotation_target * rotation_ref.inv()

    quaternion_error = rotation_error.as_quat()

    res = Transform()
    res.translation = translation
    res.rotation = type(q_ref)(
        x=quaternion_error[0],
        y=quaternion_error[1],
        z=quaternion_error[2],
        w=quaternion_error[3],
    )

    return res
