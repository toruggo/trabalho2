"""Grama ao redor do templo/mercado."""

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
    """OBJ já no mundo (como o templo); só aplica o mesmo deslocamento do recenter."""
    pos = tuple(-c for c in ctx.temple_center)
    objects = scene.load_simple_object(
        GRASS_DIR,
        "grass_field.obj",
        pos=pos,
        materials=GRASS_MATERIALS,
        recenter=False,
    )
    return AssetResult(objects=objects)
