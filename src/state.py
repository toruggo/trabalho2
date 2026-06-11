import glm

from lighting import make_default_rig

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

# Lighting state (req 1-6): ambient/diffuse/specular sliders, plus the
# exterior (lantern) and interior (int_light_a/int_light_b) lights.
# See lighting.LightingRig. Object positions are filled in by each asset's
# build() once the scene is loaded (see scene_builder.build_scene).
lighting_rig = make_default_rig()

# World-space AABB defining the temple's "interior" zone for light masking.
# Filled in by main.py from scene_builder.INTERIOR_AABB_MIN/MAX.
interior_min = glm.vec3(0.0)
interior_max = glm.vec3(0.0)

# Debug visualization (key M) — draws the interior AABB wireframe, to make
# light placement/parameters easier to tune.
debug_view = False

# Wireframe view (key T) — draws the whole scene with GL_LINE polygon mode
# instead of GL_FILL.
wireframe_view = False
