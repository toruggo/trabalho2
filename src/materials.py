# Per-object material parameters (req 7 — hand-set, not read from .mtl).
# Each *_MATERIALS dict maps an OBJ material name to a spec consumed by
# scene.load_temple / scene.load_simple_object: {texture, alpha_texture,
# solid_color, Ka, Kd, Ks, shininess, alpha, Ke}.

# Only map_Kd matters for our shader; Procedural_Gold gets a solid color texture.
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

# Ka == Kd: ambient reflectance mirrors diffuse reflectance, so the ambient
# strength slider (req 4) has a visible effect across its whole 0-1 range.
DEFAULT_MATERIAL = dict(
    Ka=(0.7, 0.7, 0.7), Kd=(0.7, 0.7, 0.7), Ks=(0.1, 0.1, 0.1), shininess=8.0
)

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

GRASS_MATERIALS = {
    "Grass_Landscape": dict(
        texture="grass_texture.png",
        Ka=(0.55, 0.65, 0.45),
        Kd=(0.55, 0.65, 0.45),
        Ks=(0.02, 0.02, 0.02),
        shininess=2.0,
    ),
}

WALL_MATERIALS = {
    "Material": dict(
        texture="Image_0.jpg",
        Ka=(0.65, 0.62, 0.58),
        Kd=(0.65, 0.62, 0.58),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
    ),
}

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

HANGING_LANTERN_MATERIALS = {
    # Paper shell — translucent so the lantern reads as lit from within
    # rather than a solid block. No Ke: the whole shell glowing doesn't read
    # well (no separate small "lamp" part), so int_light_b stays an
    # invisible emitter for now.
    "TextureMaterial_54": dict(
        texture="Image_61.png",
        Ka=(0.65, 0.45, 0.25),
        Kd=(0.65, 0.45, 0.25),
        Ks=(0.10, 0.08, 0.05),
        shininess=8.0,
        alpha=0.55,
    ),
}

FLYING_LANTERN_MATERIALS = {
    # Lantern body (paper/wood) — translucent so it lets the inner glow
    # through, like light through paper.
    "default": dict(
        texture="Image_0.002.png",
        Ka=(0.65, 0.55, 0.40),
        Kd=(0.65, 0.55, 0.40),
        Ks=(0.05, 0.05, 0.05),
        shininess=4.0,
        alpha=0.55,
    ),
    # Glowing window (map_Ke in the .mtl) — the "lamp" itself. Ke makes it
    # the visible source of its own exterior light, gated off when that
    # lantern's light (key 2) is toggled off.
    ".001": dict(
        texture="Image_5.001.png",
        Ka=(0.9, 0.7, 0.4),
        Kd=(0.9, 0.7, 0.4),
        Ks=(0.0, 0.0, 0.0),
        shininess=1.0,
        # Pushed past 1.0 so it clips to a saturated, blown-out glow rather
        # than a flat tinted surface; Ke*texColor keeps the glow following
        # the texture's own bright/dark pattern.
        Ke=(2.5, 1.8, 0.8),
    ),
}
