"""Lanternas pendentes: 3 instâncias da mesma malha; cada uma acopla uma posição de int_light_b."""

import os

import geometry
import matrizes
import scene
from assets import AssetContext, AssetResult

HANGING_LANTERN_DIR = "objects/hanging_lantern"

HANGING_LANTERN_MATERIALS = {
    # Papel translúcido; sem Ke (a malha inteira brilhando não lembra lâmpada pequena).
    "TextureMaterial_54": dict(
        texture="Image_61.png",
        Ka=(0.65, 0.45, 0.25),
        Kd=(0.65, 0.45, 0.25),
        Ks=(0.10, 0.08, 0.05),
        shininess=8.0,
        alpha=0.55,
    ),
}

# Posições Blender (Z up) do scene.json. OBJ assado no .001; as outras são deltas da mesma malha.
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


def build(ctx: AssetContext) -> AssetResult:
    """Alimenta int_light_b: três luzes da mesma cor, interruptor único; light_offset = centro da bbox."""
    origin = HANGING_LANTERN_TRANSFORMS[HANGING_LANTERN_ORIGIN_INDEX]
    instances = []
    for bx, by, bz in HANGING_LANTERN_TRANSFORMS:
        delta = (bx - origin[0], by - origin[1], bz - origin[2])
        delta_ours = matrizes.blender_to_scene_pos(*delta)
        pos = tuple(d - c for d, c in zip(delta_ours, ctx.temple_center))
        instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    _, _, glow_offset = geometry.load_obj(
        os.path.join(HANGING_LANTERN_DIR, "hanging_lantern.obj"), recenter=False
    )
    objects = scene.load_simple_object(
        HANGING_LANTERN_DIR,
        "hanging_lantern.obj",
        materials=HANGING_LANTERN_MATERIALS,
        instances=instances,
        recenter=False,
        light_offset=glow_offset,
        lights=[ctx.rig.int_light_b] * len(instances),
    )

    # Um objeto representativo por instância basta para atualizar a posição da luz.
    n_parts = len(objects) // len(instances)
    for i, hanging_obj in enumerate(objects[::n_parts]):
        ctx.rig.int_light_b.positions[i] = matrizes.light_world_pos(hanging_obj)

    return AssetResult(objects=objects)
