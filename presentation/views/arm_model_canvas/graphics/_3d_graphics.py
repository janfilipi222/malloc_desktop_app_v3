import math
import numpy as np
from domain.model.arm_model import Vertex

def rot_x(p, a):
    x, y, z = p
    ca, sa = math.cos(a), math.sin(a)
    return (x, y*ca - z*sa, y*sa + z*ca)

def rot_y(p, a):
    x, y, z = p
    ca, sa = math.cos(a), math.sin(a)
    return (x*ca + z*sa, y, -x*sa + z*ca)

def rot_z(p, a):
    x, y, z = p
    ca, sa = math.cos(a), math.sin(a)
    return (x*ca - y*sa, x*sa + y*ca, z)


# def camera_transform(p, yaw, pitch, r):
#     x, y, z = p
#     x, y, z = rot_y((x, y, z), yaw)
#     x, y, z = rot_x((x, y, z), pitch)
#     return (x, y, z + r)

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

def camera_transform(v, yaw, pitch, distance):

    # Převod bodu na numpy array
    v = np.array(v, dtype=float)

    # Rotace kolem X (pitch)
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(pitch), -np.sin(pitch)],
        [0, np.sin(pitch),  np.cos(pitch)]
    ])

    # Rotace kolem Y (yaw) - lokální po pitch
    Ry = np.array([
        [np.cos(yaw), 0, np.sin(yaw)],
        [0, 1, 0],
        [-np.sin(yaw), 0, np.cos(yaw)]
    ])

    # Kombinovaná rotace: nejprve yaw, potom pitch
    R = Rx @ Ry

    # Rotovaný bod
    v_rot = R @ v

    # Přidání posunu kamery (z = distance) pro perspektivu
    v_rot[2] += distance

    return v_rot


def project(p, w, h, fov=800, offset_y=170):
    x, y, z = p
    if z == 0:
        z = 0.0001
    return (
        w//2 + int(x * fov / z),
        h//2 - int(y * fov / z) + offset_y
    )



