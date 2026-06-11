"""Sakura trees: 26 instances sharing one mesh/texture set, scattered around
the temple grounds."""

import matrizes
import scene
from assets import AssetContext, AssetResult

SAKURA_DIR = "objects/sakura_tree"

SAKURA_MATERIALS = {
    "Bark001_2K_JPG_Mat": dict(
        texture="Bark001_2K_JPG.png",
        Ka=(0.55, 0.45, 0.35),
        Kd=(0.55, 0.45, 0.35),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
    "Sakura_Mat": dict(
        texture="Sakura.png",
        alpha_texture="Sakura_Opacity.png",
        Ka=(0.85, 0.70, 0.78),
        Kd=(0.85, 0.70, 0.78),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}

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


def build(ctx: AssetContext) -> AssetResult:
    """sakura_tree.obj is a small object-space asset; each instance's Blender
    world position is converted to scene coords relative to the temple's
    Blender-world position (so it lines up with the recentered temple)."""
    temple_center_blender = (
        ctx.temple_center[0],
        -ctx.temple_center[2],
        ctx.temple_center[1],
    )
    instances = []
    for bx, by, bz, rot_z in SAKURA_TRANSFORMS:
        rel = (
            bx - temple_center_blender[0],
            by - temple_center_blender[1],
            bz - temple_center_blender[2],
        )
        pos = matrizes.blender_to_scene_pos(*rel)
        instances.append((pos, (0.0, rot_z, 0.0), (SAKURA_SCALE,) * 3))
    objects = scene.load_simple_object(
        SAKURA_DIR,
        "sakura_tree.obj",
        materials=SAKURA_MATERIALS,
        instances=instances,
        pivot="base",
    )
    return AssetResult(objects=objects)
