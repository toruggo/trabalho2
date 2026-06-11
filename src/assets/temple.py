"""Temple structure: the main building, loaded as one SceneObject per
material, with hand-set lighting params (req 7) instead of the .mtl's."""

import scene

TEMPLE_DIR = "objects/temple"

# Only map_Kd matters for our shader; Procedural_Gold gets a solid color
# texture (see scene.load_temple's gold_color).
MATERIAL_TEXTURES = {
    "Black_tiles": "textures/tiles07_basecolor_diffuse.jpg",
    "Black_wood": "textures/wood03_diffuse.jpg",
    "Cement": "textures/Metal_basecolor.jpg",
    "Cement.001": "textures/Metal_basecolor.jpg",
    "Maldivian_Cement_Brick_Wall": "textures/maldives_Brick_wall_diffuseOriginal.jpg",
    "Red_wood": "textures/wood04_diffuse.jpg",
    "Simple_red_wood": "textures/wood30_diffuse.jpg",
    "Wood.117": "textures/wood-47-dark_diffuse.jpg",
}

TEMPLE_MATERIALS = {
    "Black_tiles": dict(
        Ka=(0.70, 0.70, 0.70),
        Kd=(0.70, 0.70, 0.70),
        Ks=(0.15, 0.15, 0.15),
        shininess=12.0,
    ),
    "Black_wood": dict(
        Ka=(0.60, 0.55, 0.50),
        Kd=(0.60, 0.55, 0.50),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
    "Cement": dict(
        Ka=(0.65, 0.65, 0.65),
        Kd=(0.65, 0.65, 0.65),
        Ks=(0.10, 0.10, 0.10),
        shininess=8.0,
    ),
    "Cement.001": dict(
        Ka=(0.65, 0.65, 0.65),
        Kd=(0.65, 0.65, 0.65),
        Ks=(0.10, 0.10, 0.10),
        shininess=8.0,
    ),
    "Maldivian_Cement_Brick_Wall": dict(
        Ka=(0.70, 0.65, 0.60),
        Kd=(0.70, 0.65, 0.60),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
    "Red_wood": dict(
        Ka=(0.65, 0.35, 0.25),
        Kd=(0.65, 0.35, 0.25),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
    "Simple_red_wood": dict(
        Ka=(0.65, 0.35, 0.25),
        Kd=(0.65, 0.35, 0.25),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
    "Wood.117": dict(
        Ka=(0.65, 0.35, 0.25),
        Kd=(0.65, 0.35, 0.25),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
    "Procedural_Gold": dict(
        Ka=(0.85, 0.70, 0.15),
        Kd=(0.85, 0.70, 0.15),
        Ks=(0.90, 0.80, 0.40),
        shininess=64.0,
    ),
}


def build():
    """Load the temple. Returns (objects, extent, raw_center) — raw_center is
    the temple's raw (pre-recenter) bbox center, used as the reference origin
    for placing every other object (see assets.AssetContext.temple_center)."""
    return scene.load_temple(TEMPLE_DIR, TEMPLE_MATERIALS, MATERIAL_TEXTURES)
