import numpy as np
import pandas as pd
from scipy.optimize import minimize
from tools import *


def calibrate_from_csv():
    """
    Calcule A et X du problème AX = XB avec:
    - A: la matrice de transformation de la base du robot vers la base de la cage
    - X: la transformation entre la base de la cage et la base du robot.

    Retourne :
        dictionnaire avec les information suivantes:
        - 'X_gc': np.ndarray de dimension 4x4 qui est la matrice de transformation caméra vers pince
        - 'X_bc': np.ndarray de dimension 4x4 qui est la matrice de transformation base_robot vers base_cage
        - 'pos_errors': np.ndarray contenant les erreurs de positions de la matrice de passage estimée
        - 'rot_errors': np.ndarray contenant les erreurs de rotation de la matrice de passage estimée
        - 'inliers': np.ndarray indices des poses conservées après la détections des outliers
        - 'outliers': np.ndarray indices des poses rejeté (ie. données aberrantes)
    """
    # Chargement des données
    df = pd.read_csv(CSV_PATH)
    print(f"\n=== DONNÉES CHARGÉES ===")
    print(f"Nombre de poses : {len(df)}")

    # Construction des poses
    cage_poses = df[["c_qx", "c_qy", "c_qz", "c_qw", "c_tx", "c_ty", "c_tz"]].values
    robot_poses = df[["r_rz", "r_ry", "r_rx", "r_tx", "r_ty", "r_tz"]].values
    N = len(df)

    Tbg = np.zeros((N, 4, 4))  # base_robot -> pince
    Tcg = np.zeros((N, 4, 4))  # base_cage -> pince

    for i in range(N):
        Tbg[i] = robotPose2T(robot_poses[i])
        Tcg[i] = cameraPose2T(cage_poses[i])

    print("\n=== EXEMPLES DE POSES ===")
    print("Pose robot 0 (Tbg[0]):")
    print(Tbg[0])
    print("\nPose caméra 0 (Tcg[0]):")
    print(Tcg[0])

    # Optimisation initiale
    p0 = 0.1 * np.random.randn(12)
    print("\n=== OPTIMISATION INITIALE ===")
    print(f"p0 (initialisation aléatoire) : {p0}")

    res = minimize(
        calibrationCost,
        p0,
        args=(Tbg, Tcg),
        method="Nelder-Mead",
        options={"maxiter": 200000, "xatol": 1e-10, "fatol": 1e-10},
    )

    p = res.x
    print(f"\nRésultat de l'optimisation initiale :")
    print(f"p = {p}")
    print(f"Nombre d'itérations : {res.nit}")
    print(f"Valeur de la fonction de coût : {res.fun}")

    # Extraction des matrices X_gc et X_bc
    X_gc = vec2T(p[:6])
    X_bc = vec2T(p[6:])

    print("\n=== MATRICES ESTIMÉES (AVANT AFFINAGE) ===")
    print("X_gc (caméra -> gripper):")
    print(X_gc)
    print("\nX_bc (base_robot -> base_cage):")
    print(X_bc)

    # Calcul des erreurs initiales
    pos_errors, rot_errors, score = computeErrors(Tbg, Tcg, X_gc, X_bc)

    print("\n=== ERREURS AVANT SUPPRESSION DES OUTLIERS ===")
    print(f"Erreur moyenne de position : {np.mean(pos_errors):.6f} m")
    print(f"Erreur maximale de position : {np.max(pos_errors):.6f} m")
    print(f"Erreur moyenne de rotation : {np.mean(rot_errors):.6f}°")
    print(f"Erreur maximale de rotation : {np.max(rot_errors):.6f}°")

    # Affichage des erreurs par pose
    for i in range(N):
        print(
            f"Pose {i}: pos={pos_errors[i]:.6f} m | rot={rot_errors[i]:.3f}° | score={score[i]:.3f}"
        )

    # Détection des inliers/outliers
    idx_keep = findInliersMAD(score, 3.5)
    idx_out = np.setdiff1d(np.arange(N), idx_keep)

    print("\n=== DÉTECTION DES OUTLIERS ===")
    print(f"Nombre d'inliers : {len(idx_keep)}")
    print(f"Indices des inliers : {idx_keep}")
    print(f"Nombre d'outliers : {len(idx_out)}")
    print(f"Indices des outliers : {idx_out}")

    # Recalibrage sans outliers
    Tbg_in = Tbg[idx_keep]
    Tcg_in = Tcg[idx_keep]

    print("\n=== RECALIBRAGE SANS OUTLIERS ===")
    print(f"Nombre de poses utilisées pour l'affinage : {len(idx_keep)}")

    res_refined = minimize(
        calibrationCost,
        p,
        args=(Tbg_in, Tcg_in),
        method="Nelder-Mead",
        options={"maxiter": 200000, "xatol": 1e-10, "fatol": 1e-10},
    )

    p_refined = res_refined.x
    print(f"\nRésultat de l'optimisation affinée :")
    print(f"p_refined = {p_refined}")
    print(f"Nombre d'itérations : {res_refined.nit}")
    print(f"Valeur de la fonction de coût : {res_refined.fun}")

    # Matrices affinées
    X_gc_refined = vec2T(p_refined[:6])
    X_bc_refined = vec2T(p_refined[6:])

    print("\n=== MATRICES AFFINÉES ===")
    print("X_gc_refined (caméra -> gripper):")
    print(X_gc_refined)
    print("\nX_bc_refined (base_robot -> base_cage):")
    print(X_bc_refined)

    # Calcul des erreurs après affinage
    pos_errors_refined, rot_errors_refined, score_refined = computeErrors(
        Tbg_in, Tcg_in, X_gc_refined, X_bc_refined
    )

    print("\n=== ERREURS APRÈS AFFINAGE (SUR INLIERS) ===")
    print(f"Erreur moyenne de position : {np.mean(pos_errors_refined):.6f} m")
    print(f"Erreur maximale de position : {np.max(pos_errors_refined):.6f} m")
    print(f"Erreur moyenne de rotation : {np.mean(rot_errors_refined):.6f} deg")
    print(f"Erreur maximale de rotation : {np.max(rot_errors_refined):.6f} deg")

    # Validation sur toutes les poses
    pos_errors_all, rot_errors_all, _ = computeErrors(
        Tbg, Tcg, X_gc_refined, X_bc_refined
    )

    print("\n=== ERREURS FINALES (SUR TOUTES LES POSES) ===")
    print(f"Erreur moyenne de position : {np.mean(pos_errors_all):.6f} m")
    print(f"Erreur maximale de position : {np.max(pos_errors_all):.6f} m")
    print(f"Erreur moyenne de rotation : {np.mean(rot_errors_all):.6f}°")
    print(f"Erreur maximale de rotation : {np.max(rot_errors_all):.6f}°")

    return {
        "X_gc": X_gc_refined,
        "X_bc": X_bc_refined,
        "pos_errors": pos_errors_all,
        "rot_errors": rot_errors_all,
        "inliers": idx_keep,
        "outliers": idx_out,
    }


# =========================
# COST FUNCTION
# =========================


def calibrationCost(p, Tbg, Tcg):
    """
    Calcule la fonction de coût pour la calibration entre un robot et une caméra.

    Paramètres:
        p   : Vecteur de 12 paramètres, les 6 premiers pour X_gc, les 6 suivants pour X_bc.
        Tbg : Tableau de N matrices 4x4 représentant les poses base_robot vers la pince.
        Tcg : Tableau de N matrices 4x4 représentant les poses base_cage vers gripper.

    Retourne:
         Valeur de la fonction de coût J, somme des erreurs de rotation
         et de translation pour toutes les poses. Plus J est proche de 0, meilleure est la calibration.
    """
    X_gc = vec2T(p[:6])
    X_bc = vec2T(p[6:])

    J = 0
    N = len(Tbg)

    for i in range(N):
        E = Tbg[i] @ X_gc - X_bc @ Tcg[i]

        Er = E[:3, :3]
        Et = E[:3, 3]

        J += (
            np.linalg.norm(Er, "fro") ** 2 + 10 * np.linalg.norm(Et) ** 2
        )  # calcule la norme de forbenius

    return J


# =========================
# TRANSFORM UTILS
# =========================


def vec2T(v):
    """
    Convertit un vecteur de 6 paramètres en une matrice de transformation homogène 4x4.

    Paramètres:
        v: np.ndarray (6,) `[r_x, r_y, r_z, t_x, t_y, t_z]`,
            où r est un vecteur de rotation (Rodrigues) et t est un vecteur de translation.

    Retourne:
        numpy.ndarray (4, 4) : Matrice de transformation homogène `T` de la forme :
        [ R   t ]
        [ 0   1 ]
    """
    r = v[:3]
    t = v[3:]

    R = rodriguesToRotm(r)

    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t
    return T


def rodriguesToRotm(r):
    """
    Cette fonction implémente la formule de Rodrigues, qui permet de convertir un vecteur
    de rotation r (représentant un axe de rotation et un angle) en une matrice de rotation 3x3.
    Cette matrice peut ensuite être utilisée pour décrire une rotation rigide en 3D.

    Paramètres:
        r   : numpy.ndarray (3,) Vecteur de rotation de Rodrigues : `[r_x, r_y, r_z]`.

    Retourne:
        numpy.ndarray (3, 3) : Matrice de rotation 3x3 correspondant au vecteur r de la forme suivante:
            [  0  -k_z  k_y ]
            [ k_z   0  -k_x ]
            [ -k_y k_x   0  ]
    """
    theta = np.linalg.norm(r)

    if theta < 1e-12:
        return np.eye(3)

    k = r / theta
    K = skew3(k)

    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)


def skew3(v):
    return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


# =========================
# POSE CONVERSIONS
# =========================


def robotPose2T(pose):
    """
    Convertit une pose robotique (angles d'Euler + translation) en une matrice de transformation homogène 4x4.

    Paramètres:
        pose    : numpy.ndarray (6,) ou liste/tuple Vecteur de pose sous la forme [tz, ty, tx, x, y, z]

    Retourne:
        numpy.ndarray (4, 4) : Matrice de transformation homogène T de la forme :
        [ R   t ]
        [ 0   1 ]
    """
    tz, ty, tx, x, y, z = pose

    Rz = np.array(
        [[np.cos(tz), -np.sin(tz), 0], [np.sin(tz), np.cos(tz), 0], [0, 0, 1]]
    )

    Ry = np.array(
        [[np.cos(ty), 0, np.sin(ty)], [0, 1, 0], [-np.sin(ty), 0, np.cos(ty)]]
    )

    Rx = np.array(
        [[1, 0, 0], [0, np.cos(tx), -np.sin(tx)], [0, np.sin(tx), np.cos(tx)]]
    )

    R = Rz @ Ry @ Rx

    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = [x, y, z]
    return T


def cameraPose2T(pose):
    """
    Convertit une pose de caméra (quaternion + translation) en une matrice de transformation homogène 4x4.

    Paramètres:
        pose    : np.ndarray (7,) ou liste/tuple Vecteur de pose sous la forme [qx, qy, qz, qw, x, y, z] où:
                    qx, qy, qz, qw : Composantes du quaternion (rotation).
                    x, y, z : Coordonnées de translation (en mètres ou unités arbitraires).

    """
    qx, qy, qz, qw, x, y, z = pose

    q = np.array([qw, qx, qy, qz])
    q = q / np.linalg.norm(q)

    qw, qx, qy, qz = q

    R = np.array(
        [
            [
                1 - 2 * (qy**2 + qz**2),
                2 * (qx * qy - qz * qw),
                2 * (qx * qz + qy * qw),
            ],
            [
                2 * (qx * qy + qz * qw),
                1 - 2 * (qx**2 + qz**2),
                2 * (qy * qz - qx * qw),
            ],
            [
                2 * (qx * qz - qy * qw),
                2 * (qy * qz + qx * qw),
                1 - 2 * (qx**2 + qy**2),
            ],
        ]
    )

    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = [x, y, z]
    return T


def rotm_to_quaternion(R):
    """
    Cette fonction prend en entrée une matrice de rotation 3×3 (R) et retourne un quaternion (représenté par un vecteur de 4 composantes [qx, qy, qz, qw]).
    Les quaternions sont une représentation alternative des rotations en 3D, souvent préférée aux angles d'Euler pour éviter les singularités et les problèmes de gimbal lock.

    Paramètres:
        R   : numpy.ndarray (3, 3) Matrice de rotation 3x3.

    Retourne:
        numpy.ndarray (4,) : Quaternion sous la forme [qx, qy, qz, qw].
    """
    q = np.zeros(4)
    trace = np.trace(R)

    if trace > 0:
        s = 0.5 / np.sqrt(trace + 1.0)
        q[3] = 0.25 / s
        q[0] = (R[2, 1] - R[1, 2]) * s
        q[1] = (R[0, 2] - R[2, 0]) * s
        q[2] = (R[1, 0] - R[0, 1]) * s
    else:
        i = np.argmax([R[0, 0], R[1, 1], R[2, 2]])

        if i == 0:
            s = 2.0 * np.sqrt(1 + R[0, 0] - R[1, 1] - R[2, 2])
            q[3] = (R[2, 1] - R[1, 2]) / s
            q[0] = 0.25 * s
            q[1] = (R[0, 1] + R[1, 0]) / s
            q[2] = (R[0, 2] + R[2, 0]) / s
        elif i == 1:
            s = 2.0 * np.sqrt(1 + R[1, 1] - R[0, 0] - R[2, 2])
            q[3] = (R[0, 2] - R[2, 0]) / s
            q[0] = (R[0, 1] + R[1, 0]) / s
            q[1] = 0.25 * s
            q[2] = (R[1, 2] + R[2, 1]) / s
        else:
            s = 2.0 * np.sqrt(1 + R[2, 2] - R[0, 0] - R[1, 1])
            q[3] = (R[1, 0] - R[0, 1]) / s
            q[0] = (R[0, 2] + R[2, 0]) / s
            q[1] = (R[1, 2] + R[2, 1]) / s
            q[2] = 0.25 * s

    return q


# =========================
# ERROR METRICS
# =========================


def computeErrors(Tbg, Tcg, X_gc, X_bc):
    """
    Calcule les erreurs de position et de rotation entre les poses estimées et réelles du robot.

    Paramètres:
        Tbg : numpy.ndarray (N, 4, 4) Tableau de N matrices de transformation base_robot vers pince (poses réelles du robot).
        Tcg : numpy.ndarray (N, 4, 4) Tableau de N matrices de transformation base_cage → gripper (poses mesurées par la caméra).
        X_gc : numpy.ndarray (4, 4) Matrice de transformation caméra vers gripper (résultat de la calibration).
        X_bc : numpy.ndarray (4, 4) Matrice de transformation base_robot vers base_cage (résultat de la calibration).

    Retourne:
        pos_errors numpy.ndarray (N,)
        rot_errors numpy.ndarray (N,)
        score numpy.ndarray (N,)
    """
    N = len(Tbg)

    pos_errors = np.zeros(N)
    rot_errors = np.zeros(N)

    for i in range(N):
        T_est = X_bc @ Tcg[i] @ np.linalg.inv(X_gc)
        T_real = Tbg[i]

        dp = T_real[:3, 3] - T_est[:3, 3]
        pos_errors[i] = np.linalg.norm(dp)

        R_err = T_real[:3, :3] @ T_est[:3, :3].T
        val = (np.trace(R_err) - 1) / 2
        val = np.clip(val, -1, 1)

        rot_errors[i] = np.degrees(np.arccos(val))

    score = pos_errors / 0.01 + rot_errors
    return pos_errors, rot_errors, score


# =========================
# OUTLIERS
# =========================


def findInliersMAD(score, thr):
    """
    Identifie les inliers dans un ensemble de scores en utilisant la méthode MAD (Median Absolute Deviation).

    Paramètres:
        score   : numpy.ndarray (N,) Tableau de N scores (par exemple, les scores calculés par computeErrors).
        thr     : float Seuil pour la détection des inliers. Les scores dont la valeur normalisée `

    Retourne:
        numpy.ndarray : Tableau des indices des inliers (poses valides) dans le tableau score.
    """
    med = np.median(score)
    mad = np.median(np.abs(score - med))

    if mad < 1e-12:
        return np.arange(len(score))

    z = 0.6745 * (score - med) / mad
    return np.where(np.abs(z) <= thr)[0]


if __name__ == "__main__":
    calibrate_from_csv()
