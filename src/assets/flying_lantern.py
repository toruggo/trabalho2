"""20 lanternas voadoras ao redor do templo, cada uma com luz pontual e DriftBehavior."""

import os

import glm

import geometry
import matrizes
import scene
from assets import AssetContext, AssetResult
from behaviors import DriftBehavior

FLYING_LANTERN_DIR = "objects/flying_lantern"

FLYING_LANTERN_MATERIALS = {
    "default": dict(
        texture="Image_0.002.png",
        Ka=(0.65, 0.55, 0.40),
        Kd=(0.65, 0.55, 0.40),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
        alpha=0.55,
    ),
    # Ke > 1.0 para brilho intenso; emissiveOn apaga junto com o interruptor da luz.
    ".001": dict(
        texture="Image_5.001.png",
        Ka=(0.9, 0.7, 0.4),
        Kd=(0.9, 0.7, 0.4),
        Ks=(0.0, 0.0, 0.0),
        shininess=1.0,
        Ke=(2.5, 1.8, 0.8),
    ),
}

# 4 lanternas do Blender (Z-up); a malha foi exportada pré-assada, só posições variam.
FLYING_LANTERN_TRANSFORMS = [
    (
        -0.7945289015769958,
        -35.838497161865234,
        4.637933731079102,
    ),  # flying_lantern_solo
    (2.002218723297119, -33.08412551879883, 4.637933731079102),  # .001
    (-0.49790430068969727, -28.973752975463867, 4.637933731079102),  # .002
    (2.150531053543091, -25.541379928588867, 4.637933731079102),  # .003
]

# 16 posições extras capturadas com a tecla P (já em coordenadas da cena).
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

GLOW_COLOR = (1.0, 0.7, 0.35)
GLOW_SIZE_FACTOR = 0.08

DRIFT_RADIUS_FACTOR = 0.06
DRIFT_SPEED_FACTOR = 0.007


def build(ctx: AssetContext) -> AssetResult:
    lantern_origin = FLYING_LANTERN_TRANSFORMS[0]
    instances = []

    for bx, by, bz in FLYING_LANTERN_TRANSFORMS:
        delta = (bx - lantern_origin[0], by - lantern_origin[1], bz - lantern_origin[2])
        delta_ours = matrizes.blender_to_scene_pos(*delta)
        pos = tuple(d - c for d, c in zip(delta_ours, ctx.temple_center))
        instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    for pos in EXTRA_LANTERN_POSITIONS:
        instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    _, _, lantern_glow_offset = geometry.load_obj(
        os.path.join(FLYING_LANTERN_DIR, "flying_lantern.obj"), recenter=False
    )

    objects = scene.load_simple_object(
        FLYING_LANTERN_DIR,
        "flying_lantern.obj",
        materials=FLYING_LANTERN_MATERIALS,
        instances=instances,
        recenter=False,
        light_offset=lantern_glow_offset,
        lights=ctx.rig.lantern_lights,
    )

    n_parts = len(objects) // len(instances)

    behaviors = []
    for i, (inst_pos, _, _) in enumerate(instances):
        behaviors.append(
            DriftBehavior(
                objects=objects[i * n_parts : (i + 1) * n_parts],
                light=ctx.rig.lantern_lights[i],
                base=glm.vec3(*inst_pos),
                radius=ctx.extent * DRIFT_RADIUS_FACTOR,
                speed=ctx.extent * DRIFT_SPEED_FACTOR,
            )
        )

    return AssetResult(objects=objects, behaviors=behaviors)
