import glm

# Camera state (first-person view). Populated by main.py once `extent` is known.
camera = {
    'pos':    glm.vec3(0.0, 0.0, 0.0),
    'front':  glm.vec3(0.0, 0.0, -1.0),
    'up':     glm.vec3(0.0, 1.0, 0.0),
    'yaw':    -90.0,
    'pitch':  0.0,
    'first':  True,
    'last_x': 400.0,
    'last_y': 300.0,
}

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
    'ambient_on':       True,
    'ambient_strength': 0.05,
    'ambient_color':    (1.0, 1.0, 1.0),

    'diffuse_mult':  1.0,
    'specular_mult': 1.0,

    'lantern_lights': [
        {'on': True, 'color': (1.0, 0.85, 0.6), 'pos': glm.vec3(0.0)}
        for _ in range(4)
    ],
    'int_light_a': {
        'on':    True,
        'color': (1.0, 0.55, 0.2),
        'pos':   glm.vec3(0.0),
    },
    'int_light_b': {
        'on':    True,
        'color': (0.4, 0.7, 1.0),
        'positions': [glm.vec3(0.0) for _ in range(3)],
    },
}

# World-space AABB defining the temple's "interior" zone for light masking.
interior_min = glm.vec3(0.0)
interior_max = glm.vec3(0.0)

# Debug visualization (key M) — draws a small cube at each active light's
# position (colored by that light's color) and the interior AABB wireframe,
# to make light placement/parameters easier to tune.
debug_view = True
