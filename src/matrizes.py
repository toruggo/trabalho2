import math

import glm


def model_matrix(pos=(0.0, 0.0, 0.0), rot_deg=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
    """Build a TRS model matrix: translate * rotateZ * rotateY * rotateX * scale."""
    m = glm.mat4(1.0)
    m = glm.translate(m, glm.vec3(*pos))
    if rot_deg[2]:
        m = glm.rotate(m, math.radians(rot_deg[2]), glm.vec3(0, 0, 1))
    if rot_deg[1]:
        m = glm.rotate(m, math.radians(rot_deg[1]), glm.vec3(0, 1, 0))
    if rot_deg[0]:
        m = glm.rotate(m, math.radians(rot_deg[0]), glm.vec3(1, 0, 0))
    m = glm.scale(m, glm.vec3(*scale))
    return m


def normal_matrix(model):
    return glm.transpose(glm.inverse(glm.mat3(model)))


def light_world_pos(obj):
    """World-space position of a light-emitting SceneObject's light_offset."""
    return glm.vec3(obj.model * glm.vec4(obj.light_offset, 1.0))


def blender_to_scene_pos(x, y, z):
    """Convert a Blender (Z-up) world position to our Y-up scene coordinates.

    Equivalent to a -90 deg rotation about X: (x, y, z) -> (x, z, -y).
    A Blender Euler Z-rotation maps directly to a scene Y-rotation under
    this same conversion, so rot_deg=(0, blender_z_rotation, 0) lines up.
    """
    return (x, z, -y)


def place_baked_instance(baked_pos, baked_rot_z_deg, target_pos, target_rot_z_deg,
                          baked_scale, target_scale, temple_center):
    """Compute (pos, rot_deg, scale) for `instances=` to place a copy of a
    pre-baked mesh — exported at `baked_pos`/`baked_rot_z_deg`/`baked_scale`
    in Blender world coordinates — at `target_pos`/`target_rot_z_deg`/
    `target_scale`, relative to the recentered temple (`temple_center`).

    Handles a Blender Z-axis (-> our Y-axis) rotation difference and a
    uniform scale ratio between the baked instance and the target instance.
    Pass target == baked for the baked instance itself (identity transform).
    """
    Q  = blender_to_scene_pos(*baked_pos)
    Q0 = blender_to_scene_pos(*target_pos)
    delta_rot = target_rot_z_deg - baked_rot_z_deg
    ratio     = target_scale / baked_scale

    theta = math.radians(delta_rot)
    c, s  = math.cos(theta), math.sin(theta)
    rQ = (Q[0] * c + Q[2] * s, Q[1], -Q[0] * s + Q[2] * c)

    pos = tuple(Q0[i] - temple_center[i] - ratio * rQ[i] for i in range(3))
    return pos, (0.0, delta_rot, 0.0), (ratio, ratio, ratio)
