"""Grass field: the ground plane around the temple/market."""

import scene
from assets import AssetContext, AssetResult

GRASS_DIR = "objects/grass_field"

GRASS_MATERIALS = {
    "Grass_Landscape": dict(
        texture="grass_texture.png",
        Ka=(0.55, 0.65, 0.45),
        Kd=(0.55, 0.65, 0.45),
        Ks=(0.02, 0.02, 0.02),
        shininess=2.0,
    ),
}


def build(ctx: AssetContext) -> AssetResult:
    """grass_field.obj was exported pre-baked to its true world position (in
    the same axis convention as temple.obj), so it only needs to be shifted
    by the same offset that recentered the temple to the origin."""
    pos = tuple(-c for c in ctx.temple_center)
    objects = scene.load_simple_object(
        GRASS_DIR,
        "grass_field.obj",
        pos=pos,
        materials=GRASS_MATERIALS,
        recenter=False,
    )
    return AssetResult(objects=objects)
