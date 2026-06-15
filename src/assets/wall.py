"""Muro do pátio: um único OBJ com todos os trechos já posicionados."""

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
    """Mesmo esquema da grama: peças já no mundo; só compensa o recenter do templo."""
    pos = tuple(-c for c in ctx.temple_center)
    objects = scene.load_simple_object(
        WALL_DIR,
        "wall.obj",
        pos=pos,
        materials=WALL_MATERIALS,
        recenter=False,
    )
    return AssetResult(objects=objects)
