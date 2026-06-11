"""Dragon candle: single pre-baked mesh ("o dragon_candles.002") that carries
the interior `intLightA` light (req 2)."""

import os

import geometry
import matrizes
import scene
from assets import AssetContext, AssetResult

DRAGON_CANDLE_DIR = "objects/dragon_candle"

DRAGON_CANDLE_MATERIALS = {
    # No Ke: unlike the flying lantern, the whole candle mesh would glow
    # (there's no separate small "flame" part), which doesn't read well.
    # int_light_a stays an invisible emitter for now.
    "TextureMaterial_55": dict(
        texture="Image_62.png",
        Ka=(0.55, 0.45, 0.30),
        Kd=(0.55, 0.45, 0.30),
        Ks=(0.35, 0.30, 0.20),
        shininess=24.0,
    ),
}


def build(ctx: AssetContext) -> AssetResult:
    """int_light_a (req 2) is carried by this object — light_offset is the
    mesh's own raw bbox center, i.e. roughly the candle flame."""
    pos = tuple(-c for c in ctx.temple_center)
    _, _, glow_offset = geometry.load_obj(
        os.path.join(DRAGON_CANDLE_DIR, "dragon_candle.obj"), recenter=False
    )
    objects = scene.load_simple_object(
        DRAGON_CANDLE_DIR,
        "dragon_candle.obj",
        pos=pos,
        materials=DRAGON_CANDLE_MATERIALS,
        recenter=False,
        light_offset=glow_offset,
        lights=[ctx.rig.int_light_a],
    )
    ctx.rig.int_light_a.positions[0] = matrizes.light_world_pos(objects[0])
    return AssetResult(objects=objects)
