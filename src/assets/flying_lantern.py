"""Flying lanterns: 20 instances sharing one pre-baked mesh, each carrying one
of the exterior `lanternOn/Pos/Color[20]` lights (req 1) and a slow drift
animation (req 6)."""

import os

import glm

import geometry
import matrizes
import scene
from assets import AssetContext, AssetResult
from behaviors import DriftBehavior

FLYING_LANTERN_DIR = "objects/flying_lantern"

FLYING_LANTERN_MATERIALS = {
    # Lantern body (paper/wood) — translucent so it lets the inner glow
    # through, like light through paper.
    "default": dict(
        texture="Image_0.002.png",
        Ka=(0.65, 0.55, 0.40),
        Kd=(0.65, 0.55, 0.40),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
        alpha=0.55,
    ),
    # Glowing window (map_Ke in the .mtl) — the "lamp" itself. Ke makes it
    # the visible source of its own exterior light, gated off when that
    # lantern's light (key 2) is toggled off.
    ".001": dict(
        texture="Image_5.001.png",
        Ka=(0.9, 0.7, 0.4),
        Kd=(0.9, 0.7, 0.4),
        Ks=(0.0, 0.0, 0.0),
        shininess=1.0,
        # Pushed past 1.0 so it clips to a saturated, blown-out glow rather
        # than a flat tinted surface; Ke*texColor keeps the glow following
        # the texture's own bright/dark pattern.
        Ke=(2.5, 1.8, 0.8),
    ),
}

# (x, y, z) in Blender (Z-up) world coordinates, from scene.json, for the
# flying_lantern_solo / .001 / .002 / .003 objects. flying_lantern.obj was
# exported pre-baked (geometry + rotation + scale of flying_lantern_solo
# already applied), so the other instances reuse that same mesh shifted by
# the position delta to flying_lantern_solo (rotation/scale match across all 4).
FLYING_LANTERN_TRANSFORMS = [
    (
        -0.7945289015769958,
        -35.838497161865234,
        4.637933731079102,
    ),  # flying_lantern_solo
    (
        2.002218723297119,
        -33.08412551879883,
        4.637933731079102,
    ),  # flying_lantern_solo.001
    (
        -0.49790430068969727,
        -28.973752975463867,
        4.637933731079102,
    ),  # flying_lantern_solo.002
    (
        2.150531053543091,
        -25.541379928588867,
        4.637933731079102,
    ),  # flying_lantern_solo.003
]

# Additional flying-lantern positions, scattered around the temple exterior.
# Unlike FLYING_LANTERN_TRANSFORMS above, these are already in our final
# scene-space coordinates (captured live via the temporary camera-position
# printout, key P in input.py) — no Blender->scene conversion needed.
EXTRA_LANTERN_POSITIONS = [
    (-1.44, -2.75, 68.06),
    (-1.88, 0.10, 63.23),
    (3.08, -3.24, 56.96),
    (-0.86, 1.05, 52.77),
    (13.32, -7.76, 56.76),
    (8.36, -7.54, 59.23),
    (1.80, -6.61, 68.67),
    (-17.64, 5.51, 11.88),
    (-32.84, 16.44, 4.38),
    (-27.67, 11.94, -17.54),
    (28.88, 10.30, -5.92),
    (30.50, 25.84, -19.14),
    (28.80, 2.53, -1.47),
    (13.65, 1.31, 17.34),
    (-20.20, 2.13, 18.46),
    (-38.76, 14.10, 9.81),
]

# Lantern glow halo (additive billboard, drawn by render_passes.draw_glow_halos).
GLOW_COLOR = (1.0, 0.7, 0.35)
GLOW_SIZE_FACTOR = 0.08  # fraction of `extent`

# Wandering animation: each lantern drifts within a small radius of its placed
# position, in a straight line that "ping-pongs" off the boundary.
DRIFT_RADIUS_FACTOR = 0.06  # fraction of `extent`
DRIFT_SPEED_FACTOR = 0.007  # (fraction of `extent`) per second


def build(ctx: AssetContext) -> AssetResult:
    lantern_origin = FLYING_LANTERN_TRANSFORMS[0]
    instances = []
    for bx, by, bz in FLYING_LANTERN_TRANSFORMS:
        delta = (bx - lantern_origin[0], by - lantern_origin[1], bz - lantern_origin[2])
        delta_ours = matrizes.blender_to_scene_pos(*delta)
        pos = tuple(d - c for d, c in zip(delta_ours, ctx.temple_center))
        instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))
    for pos in EXTRA_LANTERN_POSITIONS:
        instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    assert len(instances) == len(ctx.rig.lantern_lights), (
        "lantern instance count must match lighting.NUM_LANTERNS"
    )

    # The mesh's own raw bbox center sits roughly at the lantern's glow —
    # used as light_offset so each instance's light tracks its own copy.
    _, _, lantern_glow_offset = geometry.load_obj(
        os.path.join(FLYING_LANTERN_DIR, "flying_lantern.obj"), recenter=False
    )
    objects = scene.load_simple_object(
        FLYING_LANTERN_DIR,
        "flying_lantern.obj",
        materials=FLYING_LANTERN_MATERIALS,
        instances=instances,
        recenter=False,
        light_offset=lantern_glow_offset,
        lights=ctx.rig.lantern_lights,
    )

    # One SceneObject per instance is enough to compute that instance's
    # light position (model + light_offset are shared across its parts).
    n_parts = len(objects) // len(instances)

    behaviors = []
    for i, (inst_pos, _, _) in enumerate(instances):
        behaviors.append(
            DriftBehavior(
                objects=objects[i * n_parts : (i + 1) * n_parts],
                light=ctx.rig.lantern_lights[i],
                base=glm.vec3(*inst_pos),
                radius=ctx.extent * DRIFT_RADIUS_FACTOR,
                speed=ctx.extent * DRIFT_SPEED_FACTOR,
            )
        )

    return AssetResult(objects=objects, behaviors=behaviors)
