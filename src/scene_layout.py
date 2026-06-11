"""Scene layout data: object placements, the interior bounding box, and
market-stall instance lists. Pure data — no OpenGL/loading logic (see
scene.py for that)."""

from materials import (
    FISH_TENT_MATERIALS,
    FLAG1_MATERIALS,
    FOOD_TENT_MATERIALS,
    MEAT_TENT_MATERIALS,
    SPICE_TENT_MATERIALS,
    STANDING_UMBRELLA_MATERIALS,
    TABLES_MATERIALS,
)

# (x, y, z, rotation_z_deg) in Blender (Z-up) world coordinates, from
# object_transforms.md. Position is converted via matrizes.blender_to_scene_pos
# and rotation_z maps directly onto a scene Y-rotation.
SAKURA_TRANSFORMS = [
    (-12.923817, -21.774605, 0.428387, -74.919853),
    (-12.792014, -28.013264, 0.428387, -74.919853),
    (8.428210, -35.833553, 0.428387, -74.919853),
    (10.273447, -19.885433, 0.428387, -74.919853),
    (6.934447, -41.676804, 0.428387, -243.459088),
    (-8.442527, -31.440132, 0.428387, -129.741438),
    (-11.023709, -34.164055, 0.428387, -243.459088),
    (-7.797180, -39.225277, 0.428387, -299.590866),
    (-13.301259, -39.351807, 0.428387, -351.736711),
    (7.681329, -54.128819, 0.428387, -302.282671),
    (-8.354659, -54.769199, 0.428387, -394.693601),
    (-9.980225, -42.994835, 0.428387, -408.512248),
    (-7.168436, -45.367279, 0.428387, -437.373568),
    (-14.153975, -45.455151, 0.428387, -471.710076),
    (10.668856, -39.655830, 0.428387, -383.674866),
    (13.451356, -36.543823, 0.428387, -434.551935),
    (14.622935, -40.754185, 0.428387, -435.724186),
    (6.669085, -47.096527, 0.428387, -334.651648),
    (8.047447, -58.522240, 0.428387, -358.947041),
    (10.976396, -61.231518, 0.428387, -437.560551),
    (12.074751, -55.263786, 0.428387, -437.560551),
    (15.918995, -52.920628, 0.428387, -383.636344),
    (15.150146, -59.181255, 0.428387, -383.636344),
    (-13.992884, -58.210712, 0.428387, -394.693601),
    (-9.562850, -59.418903, 0.428387, -325.652027),
    (-3.778178, -62.311241, 0.428387, -312.761465),
]
SAKURA_SCALE = 8.482910

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

# World-space AABB marking the temple interior, hand-tuned with the debug
# box tool (key M + arrows/J/L/I/K/U/O) to snugly fit the interior room
# (floor to ceiling, wall to wall) — used to mask interior-only/exterior-only
# lights (req 1 / req 2).
INTERIOR_AABB_MIN = (-3.55, -2.81, -24.33)
INTERIOR_AABB_MAX = (4.40, 1.43, 5.21)

# Market stalls/props. Each mesh was exported pre-baked to one specific
# scene.json instance's world transform ("baked": position, rotation_z_deg,
# scale, all in Blender world coordinates). `targets` lists every instance
# to place using that mesh; matrizes.place_baked_instance() compensates for
# any Y-rotation / uniform-scale difference between `baked` and each target.
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
