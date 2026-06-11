"""Market stalls/props: each a pre-baked mesh placed at one or more instance
transforms via matrizes.place_baked_instance."""

import matrizes
import scene
from assets import AssetContext, AssetResult

FISH_TENT_MATERIALS = {
    "TextureMaterial_4": dict(
        texture="Image_9.png",
        Ka=(0.7, 0.7, 0.7),
        Kd=(0.7, 0.7, 0.7),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
    "TextureMaterial_1_4": dict(
        texture="Image_11.png",
        Ka=(0.7, 0.7, 0.7),
        Kd=(0.7, 0.7, 0.7),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}

FLAG1_MATERIALS = {
    "TextureMaterial_41": dict(
        texture="Image_52.png",
        Ka=(0.75, 0.65, 0.55),
        Kd=(0.75, 0.65, 0.55),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}

FOOD_TENT_MATERIALS = {
    "TextureMaterial_1_9": dict(
        texture="Image_44.png",
        Ka=(0.7, 0.7, 0.7),
        Kd=(0.7, 0.7, 0.7),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}

MEAT_TENT_MATERIALS = {
    "TextureMaterial_26": dict(
        texture="Image_36.png",
        Ka=(0.7, 0.7, 0.7),
        Kd=(0.7, 0.7, 0.7),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}

SPICE_TENT_MATERIALS = {
    "TextureMaterial_7": dict(
        texture="Image_16.png",
        Ka=(0.7, 0.7, 0.7),
        Kd=(0.7, 0.7, 0.7),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
    "TextureMaterial_1_7": dict(
        solid_color=(204, 204, 204),
        Ka=(0.8, 0.8, 0.8),
        Kd=(0.8, 0.8, 0.8),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}

STANDING_UMBRELLA_MATERIALS = {
    "TextureMaterial_21": dict(
        texture="Image_31.png",
        Ka=(0.75, 0.65, 0.55),
        Kd=(0.75, 0.65, 0.55),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}

TABLES_MATERIALS = {
    "TextureMaterial_34": dict(
        texture="Image_45.png",
        Ka=(0.6, 0.5, 0.4),
        Kd=(0.6, 0.5, 0.4),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}

# Each mesh was exported pre-baked to one specific scene.json instance's world
# transform ("baked": position, rotation_z_deg, scale, all in Blender world
# coordinates). `targets` lists every instance to place using that mesh;
# matrizes.place_baked_instance() compensates for any Y-rotation / uniform-
# scale difference between `baked` and each target.
MARKET_OBJECTS = [
    dict(
        dir="objects/fish_tent",
        file="fish_tent.obj",
        materials=FISH_TENT_MATERIALS,
        baked=(
            (5.467783451080322, -27.850482940673828, 1.637453317642212),
            0.0,
            0.0005368956481106579,
        ),
        targets=[
            (
                (5.467783451080322, -27.850482940673828, 1.637453317642212),
                0.0,
                0.0005368956481106579,
            ),  # fish_tent_a/b
            (
                (5.11183500289917, -38.65605926513672, 1.637453317642212),
                0.0,
                0.0005368956481106579,
            ),  # fish_tent_a/b.001
        ],
    ),
    dict(
        dir="objects/flag1",
        file="flag1.obj",
        materials=FLAG1_MATERIALS,
        baked=(
            (4.405760288238525, -31.69893455505371, 3.0643084049224854),
            90.0,
            0.0003897630958817899,
        ),
        targets=[
            (
                (4.405760288238525, -31.69893455505371, 3.0643084049224854),
                90.0,
                0.0003897630958817899,
            ),  # flag1
            (
                (-1.8033266067504883, -24.106781005859375, 3.0643084049224854),
                90.0,
                0.0003897630958817899,
            ),  # flag1.001
        ],
    ),
    dict(
        dir="objects/food_tent",
        file="food_tent.obj",
        materials=FOOD_TENT_MATERIALS,
        baked=(
            (5.220168113708496, -25.36267852783203, 1.0445088148117065),
            0.0,
            0.0004688884655479342,
        ),
        targets=[
            (
                (5.220168113708496, -25.36267852783203, 1.0445088148117065),
                0.0,
                0.0004688884655479342,
            ),  # food_tent_1
            (
                (4.814486026763916, -36.064910888671875, 1.2097200155258179),
                0.0,
                0.0004084281390532851,
            ),  # food_tent_0
        ],
    ),
    dict(
        dir="objects/meat_tent",
        file="meat_tent.obj",
        materials=MEAT_TENT_MATERIALS,
        baked=(
            (-3.5610203742980957, -32.09426498413086, 1.0506778955459595),
            0.0,
            0.00042814877815544605,
        ),
        targets=[
            (
                (-3.5610203742980957, -32.09426498413086, 1.0506778955459595),
                0.0,
                0.00042814877815544605,
            ),  # meat_tent_b
        ],
    ),
    dict(
        dir="objects/spice_tent",
        file="spice_tent.obj",
        materials=SPICE_TENT_MATERIALS,
        baked=(
            (-3.36627197265625, -26.63774299621582, 1.6107171773910522),
            -180.0,
            0.6224765777587891,
        ),
        targets=[
            (
                (-3.36627197265625, -26.63774299621582, 1.6107171773910522),
                -180.0,
                0.6224765777587891,
            ),  # spice_tent
            (
                (-3.457801580429077, -38.71965408325195, 1.6107171773910522),
                -180.0,
                0.6224765777587891,
            ),  # spice_tent.001
        ],
    ),
    dict(
        dir="objects/standing_umbrella",
        file="standing_umbrella.obj",
        materials=STANDING_UMBRELLA_MATERIALS,
        baked=(
            (9.14824104309082, -26.97772216796875, 2.304640531539917),
            0.0,
            0.00038976300857029855,
        ),
        targets=[
            (
                (9.14824104309082, -26.97772216796875, 2.304640531539917),
                0.0,
                0.00038976300857029855,
            ),  # standing_umbrella
            (
                (13.54757022857666, -23.269926071166992, 2.304640531539917),
                0.0,
                0.00038976300857029855,
            ),  # standing_umbrella.001
        ],
    ),
    dict(
        dir="objects/tables",
        file="tables.obj",
        materials=TABLES_MATERIALS,
        baked=(
            (13.589741706848145, -25.852642059326172, 0.8880937099456787),
            180.0,
            0.00047512794844806194,
        ),
        targets=[
            (
                (13.589741706848145, -25.852642059326172, 0.8880937099456787),
                180.0,
                0.00047512794844806194,
            ),  # tables.001
            (
                (9.4158296585083, -24.77208709716797, 0.8880937099456787),
                0.0,
                0.0004751279775518924,
            ),  # tables
        ],
    ),
]


def build(ctx: AssetContext) -> AssetResult:
    objects = []
    for spec in MARKET_OBJECTS:
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
