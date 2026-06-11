"""Distant mountain ranges surrounding the temple grounds: one pre-baked mesh
placed at multiple instance transforms via matrizes.place_baked_instance."""

import matrizes
import scene
from assets import AssetContext, AssetResult

MOUNTAIN_RANGE_MATERIALS = {
    "Material.001": dict(
        texture="Image_0.003.jpg",
        Ka=(0.6, 0.6, 0.6),
        Kd=(0.6, 0.6, 0.6),
        Ks=(0.02, 0.02, 0.02),
        shininess=2.0,
    ),
}

# mountain_range.obj was exported pre-baked to mountain_range.003's world
# transform; the other 3 instances reuse that same mesh placed via
# place_baked_instance().
MOUNTAIN_RANGE_OBJECTS = [
    dict(
        dir="objects/mountain_range",
        file="mountain_range.obj",
        materials=MOUNTAIN_RANGE_MATERIALS,
        baked=(
            (-64.46244812011719, -127.65333557128906, 5.575518608093262),
            -14.534765497192195,
            0.9375219941139221,
        ),
        targets=[
            (
                (-108.52672576904297, 0.0, 13.498826026916504),
                63.91706051714107,
                0.9375218152999878,
            ),  # mountain_range
            (
                (30.545913696289062, 94.68980407714844, 13.498826026916504),
                -33.76533727518693,
                0.9375219941139221,
            ),  # mountain_range.001
            (
                (62.837711334228516, -40.186378479003906, -0.7426433563232422),
                66.30356959427854,
                0.9375219941139221,
            ),  # mountain_range.002
            (
                (-64.46244812011719, -127.65333557128906, 5.575518608093262),
                -14.534765497192195,
                0.9375219941139221,
            ),  # mountain_range.003 (baked)
        ],
    ),
]


def build(ctx: AssetContext) -> AssetResult:
    objects = []
    for spec in MOUNTAIN_RANGE_OBJECTS:
        baked_pos, baked_rot, baked_scale = spec["baked"]
        instances = [
            matrizes.place_baked_instance(
                baked_pos, baked_rot, t_pos, t_rot, baked_scale, t_scale, ctx.temple_center
            )
            for t_pos, t_rot, t_scale in spec["targets"]
        ]
        objects += scene.load_simple_object(
            spec["dir"],
            spec["file"],
            materials=spec["materials"],
            instances=instances,
            recenter=False,
        )
    return AssetResult(objects=objects)
