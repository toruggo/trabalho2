import random

import glm

# Total number of flying-lantern point lights (4 original + 16 added around
# the temple exterior). Must match NUM_LANTERNS in fragment_shader.fs and the
# number of instances in main.py's lantern_instances.
NUM_LANTERNS = 20

# Camera state (first-person view). Populated by main.py once `extent` is known.
camera = {
    "pos": glm.vec3(0.0, 0.0, 0.0),
    "front": glm.vec3(0.0, 0.0, -1.0),
    "up": glm.vec3(0.0, 1.0, 0.0),
    "yaw": -90.0,
    "pitch": 0.0,
    "first": True,
    "last_x": 400.0,
    "last_y": 300.0,
}

# Vertical bounds for the camera (world-space Y), so it can't fly below the
# grass/ground or far above the temple. Filled in by main.py once the grass
# field's world-space height is known.
camera_min_y = 0.0
camera_max_y = 0.0

# Currently held-down keys (for continuous/per-frame input handling).
keys_pressed = set()

# Lighting state. Positions/colors below are placeholders, replaced by
# main.py with extent-derived (or object-derived) values once the scene is
# loaded.
#
# - 'lantern_lights' — one entry per flying lantern (req 1, exterior light),
#                 lights only fragments OUTSIDE the interior bounding box.
#                 pos = matrizes.light_world_pos(flying_lantern_obj_i).
#                 Toggled together as a group (key 2).
# - 'int_light_a' / 'int_light_b' light only fragments INSIDE the interior
#                 bounding box (req 2, two different colors). 'int_light_a'
#                 is carried by the dragon candle (single instance);
#                 'int_light_b' is carried by the 3 hanging lanterns, each
#                 emitting its own copy of the same-colored light, toggled
#                 together as a group (key 4).
lighting = {
    "ambient_on": True,
    "ambient_strength": 0.15,
    "ambient_color": (1.0, 1.0, 1.0),
    "diffuse_mult": 1.0,
    "specular_mult": 1.0,
    "lantern_lights": [
        {"on": True, "color": (1.0, 0.85, 0.6), "pos": glm.vec3(0.0)}
        for _ in range(NUM_LANTERNS)
    ],
    "int_light_a": {
        "on": True,
        "color": (2.0, 0.55, 0.2),
        "pos": glm.vec3(0.0),
    },
    "int_light_b": {
        "on": True,
        "color": (1.5, 0.3, 0.1),
        "positions": [glm.vec3(0.0) for _ in range(3)],
    },
}

# World-space AABB defining the temple's "interior" zone for light masking.
interior_min = glm.vec3(0.0)
interior_max = glm.vec3(0.0)

# Debug visualization (key M) — draws a small cube at each active light's
# position (colored by that light's color) and the interior AABB wireframe,
# to make light placement/parameters easier to tune.
debug_view = False

# Wireframe view (key T) — draws the whole scene with GL_LINE polygon mode
# instead of GL_FILL.
wireframe_view = False


# Slow wandering animation for the flying lanterns: each lantern drifts in a
# random straight line from its 'base' position, then "ping-pongs" (reflects)
# off the boundary of a sphere of 'radius' around 'base'. Each lantern starts
# at a different random point within that sphere (and with a different random
# direction), so they're out of phase with each other from the start.
# 'base'/'radius'/'speed'/'offset' are filled in by main.py once `extent` is
# known.
def _random_drift_dir():
    d = glm.vec3(
        random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)
    )
    return glm.normalize(d)


def random_point_in_sphere(radius):
    """Uniformly sample a point within a sphere of the given radius (rejection sampling)."""
    while True:
        p = glm.vec3(
            random.uniform(-1.0, 1.0),
            random.uniform(-1.0, 1.0),
            random.uniform(-1.0, 1.0),
        )
        if glm.length(p) <= 1.0:
            return p * radius


lantern_drift = [
    {
        "base": glm.vec3(0.0),
        "offset": glm.vec3(0.0),
        "dir": _random_drift_dir(),
        "speed": 0.0,
        "radius": 0.0,
    }
    for _ in range(NUM_LANTERNS)
]
