import numpy as np
import math
from domain.model.arm_model import Joint

def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s,  c]
    ])

def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([
        [ c, 0, s],
        [ 0, 1, 0],
        [-s, 0, c]
    ])

def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ])



def calculate_FK(joints: list[Joint]):
    points = []

    pos = np.array([0.0, 0.0, 0.0])
    R = np.eye(3)

    points.append(tuple(pos))

    for i, j in enumerate(joints):
        angle = j.angle

        if j.axis == "x":
            R = R @ rot_x(angle)
        elif j.axis == "y":
            R = R @ rot_y(angle)
        elif j.axis == "z":
            R = R @ rot_z(angle)

        local_dir = np.array([0.0, 1.0, 0.0])
        world_dir = R @ local_dir

        pos = pos + world_dir * j.length

        points.append(tuple(pos))

    points = (float(p) for p in points[-1])
    return points, R


def rotation_to_euler(R):
    yaw = math.atan2(R[1, 0], R[0, 0])
    pitch = math.atan2(-R[2, 0], math.sqrt(R[2, 1]**2 + R[2, 2]**2))
    roll = math.atan2(R[2, 1], R[2, 2])
    return roll, pitch, yaw


def get_pitch_in_4DOF(joints: list[Joint]):

    pitch = joints[1].angle + joints[2].angle + joints[4].angle
    return float(pitch - math.pi / 2)



def rotation_to_euler_xyz(R: np.ndarray):
    """
    R: 3x3 rotační matice
    návrat: (rx, ry, rz) v radiánech
    """

    ry = math.atan2(
        -R[2, 0],
        math.sqrt(R[2, 1]**2 + R[2, 2]**2)
    )

    rx = math.atan2(
        R[2, 1],
        R[2, 2]
    )

    rz = math.atan2(
        R[1, 0],
        R[0, 0]
    )

    return rx, ry, rz
