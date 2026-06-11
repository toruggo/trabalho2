"""Courtyard wall: all wall segments pre-baked into one mesh."""

import scene
from assets import AssetContext, AssetResult

WALL_DIR = "objects/wall"

WALL_MATERIALS = {
    "Material": dict(
        texture="Image_0.jpg",
        Ka=(0.65, 0.62, 0.58),
        Kd=(0.65, 0.62, 0.58),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}


def build(ctx: AssetContext) -> AssetResult:
    """wall.obj was exported the same way as grass_field.obj: every wall
    piece already sits at its true world position, so it only needs the same
    temple-recentering offset."""
    pos = tuple(-c for c in ctx.temple_center)
    objects = scene.load_simple_object(
        WALL_DIR,
        "wall.obj",
        pos=pos,
        materials=WALL_MATERIALS,
        recenter=False,
    )
    return AssetResult(objects=objects)
