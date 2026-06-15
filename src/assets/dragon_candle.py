"""Vela dragão: malha única pré-assada com int_light_a."""

import os

import geometry
import matrizes
import scene
from assets import AssetContext, AssetResult

DRAGON_CANDLE_DIR = "objects/dragon_candle"

DRAGON_CANDLE_MATERIALS = {
    # Sem Ke: a malha toda brilhando não parece chama; a luz fica só no rig.
    "TextureMaterial_55": dict(
        texture="Image_62.png",
        Ka=(0.55, 0.45, 0.30),
        Kd=(0.55, 0.45, 0.30),
        Ks=(0.35, 0.30, 0.20),
        shininess=24.0,
    ),
}


def build(ctx: AssetContext) -> AssetResult:
    """Liga int_light_a; light_offset ≈ centro da bbox (chama)."""
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
