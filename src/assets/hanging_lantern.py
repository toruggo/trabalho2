"""Hanging lanterns: 3 instances sharing one pre-baked mesh, each emitting its
own copy of the shared `intLightB` light (req 2)."""

import os

import geometry
import matrizes
import scene
from assets import AssetContext, AssetResult

HANGING_LANTERN_DIR = "objects/hanging_lantern"

HANGING_LANTERN_MATERIALS = {
    # Paper shell — translucent so the lantern reads as lit from within
    # rather than a solid block. No Ke: the whole shell glowing doesn't read
    # well (no separate small "lamp" part), so int_light_b stays an
    # invisible emitter for now.
    "TextureMaterial_54": dict(
        texture="Image_61.png",
        Ka=(0.65, 0.45, 0.25),
        Kd=(0.65, 0.45, 0.25),
        Ks=(0.10, 0.08, 0.05),
        shininess=8.0,
        alpha=0.55,
    ),
}

# (x, y, z) in Blender (Z-up) world coordinates, from scene.json, for the
# hanging_lantern / .001 / .002 objects. hanging_lantern.obj was exported
# pre-baked as "o hanging_lantern.001" (geometry + rotation + scale already
# applied), so the other instances reuse that same mesh shifted by the
# position delta to hanging_lantern.001 (rotation/scale match across all 3).
HANGING_LANTERN_TRANSFORMS = [
    (-0.020896494388580322, 8.019309997558594, 11.573162078857422),  # hanging_lantern
    (
        1.5413868427276611,
        11.697153091430664,
        11.573162078857422,
    ),  # hanging_lantern.001 (baked)
    (1.18292236328125, 16.908143997192383, 11.573162078857422),  # hanging_lantern.002
]
HANGING_LANTERN_ORIGIN_INDEX = 1


def build(ctx: AssetContext) -> AssetResult:
    """int_light_b (req 2) is carried by these objects — each of the 3
    instances emits its own copy of the same-colored light (toggled
    together), light_offset is the mesh's own raw bbox center."""
    origin = HANGING_LANTERN_TRANSFORMS[HANGING_LANTERN_ORIGIN_INDEX]
    instances = []
    for bx, by, bz in HANGING_LANTERN_TRANSFORMS:
        delta = (bx - origin[0], by - origin[1], bz - origin[2])
        delta_ours = matrizes.blender_to_scene_pos(*delta)
        pos = tuple(d - c for d, c in zip(delta_ours, ctx.temple_center))
        instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    _, _, glow_offset = geometry.load_obj(
        os.path.join(HANGING_LANTERN_DIR, "hanging_lantern.obj"), recenter=False
    )
    objects = scene.load_simple_object(
        HANGING_LANTERN_DIR,
        "hanging_lantern.obj",
        materials=HANGING_LANTERN_MATERIALS,
        instances=instances,
        recenter=False,
        light_offset=glow_offset,
        lights=[ctx.rig.int_light_b] * len(instances),
    )

    # One SceneObject per instance is enough to compute that instance's
    # light position (model + light_offset are shared across its parts).
    n_parts = len(objects) // len(instances)
    for i, hanging_obj in enumerate(objects[::n_parts]):
        ctx.rig.int_light_b.positions[i] = matrizes.light_world_pos(hanging_obj)

    return AssetResult(objects=objects)
