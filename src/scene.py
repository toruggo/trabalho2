import os
from dataclasses import dataclass, field

from OpenGL.GL import *
import glm

import geometry
import matrizes

# Only map_Kd matters for our shader; Procedural_Gold gets a solid color texture.
MATERIAL_TEXTURES = {
    "Black_tiles":                  "textures/tiles07_basecolor_diffuse.jpg",
    "Black_wood":                   "textures/wood03_diffuse.jpg",
    "Cement":                       "textures/Metal_basecolor.jpg",
    "Cement.001":                   "textures/Metal_basecolor.jpg",
    "Maldivian_Cement_Brick_Wall":  "textures/maldives_Brick_wall_diffuseOriginal.jpg",
    "Red_wood":                     "textures/wood04_diffuse.jpg",
    "Simple_red_wood":              "textures/wood30_diffuse.jpg",
    "Wood.117":                     "textures/wood-47-dark_diffuse.jpg",
}

# Per-material Phong parameters (req 7 — hand-set, not read from .mtl).
DEFAULT_MATERIAL = dict(Ka=(0.05, 0.05, 0.05), Kd=(0.7, 0.7, 0.7), Ks=(0.1, 0.1, 0.1), shininess=8.0)

TEMPLE_MATERIALS = {
    "Black_tiles":                 dict(Ka=(0.05, 0.05, 0.05), Kd=(0.70, 0.70, 0.70), Ks=(0.15, 0.15, 0.15), shininess=12.0),
    "Black_wood":                  dict(Ka=(0.04, 0.03, 0.03), Kd=(0.60, 0.55, 0.50), Ks=(0.05, 0.05, 0.05), shininess=4.0),
    "Cement":                      dict(Ka=(0.05, 0.05, 0.05), Kd=(0.65, 0.65, 0.65), Ks=(0.10, 0.10, 0.10), shininess=8.0),
    "Cement.001":                  dict(Ka=(0.05, 0.05, 0.05), Kd=(0.65, 0.65, 0.65), Ks=(0.10, 0.10, 0.10), shininess=8.0),
    "Maldivian_Cement_Brick_Wall": dict(Ka=(0.05, 0.05, 0.05), Kd=(0.70, 0.65, 0.60), Ks=(0.05, 0.05, 0.05), shininess=4.0),
    "Red_wood":                    dict(Ka=(0.05, 0.03, 0.02), Kd=(0.65, 0.35, 0.25), Ks=(0.05, 0.05, 0.05), shininess=4.0),
    "Simple_red_wood":             dict(Ka=(0.05, 0.03, 0.02), Kd=(0.65, 0.35, 0.25), Ks=(0.05, 0.05, 0.05), shininess=4.0),
    "Wood.117":                    dict(Ka=(0.05, 0.03, 0.02), Kd=(0.65, 0.35, 0.25), Ks=(0.05, 0.05, 0.05), shininess=4.0),
    "Procedural_Gold":             dict(Ka=(0.15, 0.12, 0.03), Kd=(0.85, 0.70, 0.15), Ks=(0.90, 0.80, 0.40), shininess=64.0),
}

GRASS_MATERIALS = {
    "Grass_Landscape": dict(
        texture="grass_texture.png",
        Ka=(0.05, 0.08, 0.04), Kd=(0.55, 0.65, 0.45), Ks=(0.02, 0.02, 0.02), shininess=2.0,
    ),
}

WALL_MATERIALS = {
    "Material": dict(
        texture="Image_0.jpg",
        Ka=(0.05, 0.05, 0.05), Kd=(0.65, 0.62, 0.58), Ks=(0.05, 0.05, 0.05), shininess=4.0,
    ),
}

SAKURA_MATERIALS = {
    "Bark001_2K_JPG_Mat": dict(
        texture="Bark001_2K_JPG.png",
        Ka=(0.05, 0.04, 0.03), Kd=(0.55, 0.45, 0.35), Ks=(0.05, 0.05, 0.05), shininess=4.0,
    ),
    "Sakura_Mat": dict(
        texture="Sakura.png", alpha_texture="Sakura_Opacity.png",
        Ka=(0.06, 0.04, 0.05), Kd=(0.85, 0.70, 0.78), Ks=(0.05, 0.05, 0.05), shininess=4.0,
    ),
}

FISH_TENT_MATERIALS = {
    "TextureMaterial_4":   dict(texture="Image_9.png",  Ka=(0.05, 0.05, 0.05), Kd=(0.7, 0.7, 0.7), Ks=(0.05, 0.05, 0.05), shininess=4.0),
    "TextureMaterial_1_4": dict(texture="Image_11.png", Ka=(0.05, 0.05, 0.05), Kd=(0.7, 0.7, 0.7), Ks=(0.05, 0.05, 0.05), shininess=4.0),
}

FLAG1_MATERIALS = {
    "TextureMaterial_41": dict(texture="Image_52.png", Ka=(0.06, 0.05, 0.04), Kd=(0.75, 0.65, 0.55), Ks=(0.05, 0.05, 0.05), shininess=4.0),
}

FOOD_TENT_MATERIALS = {
    "TextureMaterial_1_9": dict(texture="Image_44.png", Ka=(0.05, 0.05, 0.05), Kd=(0.7, 0.7, 0.7), Ks=(0.05, 0.05, 0.05), shininess=4.0),
}

MEAT_TENT_MATERIALS = {
    "TextureMaterial_26": dict(texture="Image_36.png", Ka=(0.05, 0.05, 0.05), Kd=(0.7, 0.7, 0.7), Ks=(0.05, 0.05, 0.05), shininess=4.0),
}

SPICE_TENT_MATERIALS = {
    "TextureMaterial_7":   dict(texture="Image_16.png", Ka=(0.05, 0.05, 0.05), Kd=(0.7, 0.7, 0.7), Ks=(0.05, 0.05, 0.05), shininess=4.0),
    "TextureMaterial_1_7": dict(solid_color=(204, 204, 204), Ka=(0.05, 0.05, 0.05), Kd=(0.8, 0.8, 0.8), Ks=(0.05, 0.05, 0.05), shininess=4.0),
}

STANDING_UMBRELLA_MATERIALS = {
    "TextureMaterial_21": dict(texture="Image_31.png", Ka=(0.06, 0.05, 0.04), Kd=(0.75, 0.65, 0.55), Ks=(0.05, 0.05, 0.05), shininess=4.0),
}

TABLES_MATERIALS = {
    "TextureMaterial_34": dict(texture="Image_45.png", Ka=(0.05, 0.04, 0.03), Kd=(0.6, 0.5, 0.4), Ks=(0.05, 0.05, 0.05), shininess=4.0),
}

DRAGON_CANDLE_MATERIALS = {
    "TextureMaterial_55": dict(
        texture="Image_62.png",
        Ka=(0.06, 0.05, 0.03), Kd=(0.55, 0.45, 0.30), Ks=(0.35, 0.30, 0.20), shininess=24.0,
    ),
}

HANGING_LANTERN_MATERIALS = {
    "TextureMaterial_54": dict(
        texture="Image_61.png",
        Ka=(0.06, 0.05, 0.03), Kd=(0.65, 0.45, 0.25), Ks=(0.10, 0.08, 0.05), shininess=8.0,
    ),
}

FLYING_LANTERN_MATERIALS = {
    # Lantern body (paper/wood).
    "default": dict(
        texture="Image_0.002.png",
        Ka=(0.05, 0.04, 0.03), Kd=(0.65, 0.55, 0.40), Ks=(0.05, 0.05, 0.05), shininess=4.0,
    ),
    # Glowing window (map_Ke in the .mtl) — high Ka approximates self-illumination
    # since the shader has no emissive term.
    ".001": dict(
        texture="Image_5.001.png",
        Ka=(0.9, 0.7, 0.4), Kd=(0.9, 0.7, 0.4), Ks=(0.0, 0.0, 0.0), shininess=1.0,
    ),
}


@dataclass
class SceneObject:
    vbo: int
    tex: int
    n_verts: int
    model: glm.mat4
    normal_matrix: glm.mat3
    Ka: tuple
    Kd: tuple
    Ks: tuple
    shininess: float
    light_offset: glm.vec3 = field(default_factory=lambda: glm.vec3(0.0, 0.0, 0.0))


def load_temple(temple_dir):
    """Load objects/temple/temple.obj as one SceneObject per material.

    Returns (objects, extent, raw_center) — raw_center is the temple's raw
    (pre-recenter) bbox center in the OBJ export's own coordinate frame, used
    as the reference origin when placing other objects relative to the temple.
    """
    raw_groups, extent, raw_center = geometry.load_obj(os.path.join(temple_dir, "temple.obj"))
    mat_map = geometry.merge_groups(raw_groups)
    print(f"Temple: extent={extent:.2f}, materials={list(mat_map.keys())}")

    model = glm.mat4(1.0)
    nmat  = matrizes.normal_matrix(model)

    objects = []
    for mat, verts in mat_map.items():
        vbo = geometry.upload_vbo(verts)
        n   = len(verts) // 8

        rel = MATERIAL_TEXTURES.get(mat)
        if rel:
            tex = geometry.load_texture(os.path.join(temple_dir, rel))
        else:
            # Procedural_Gold: (0.8, 0.65, 0.1) -> uint8
            tex = geometry.make_solid_texture(204, 166, 26)

        params = TEMPLE_MATERIALS.get(mat, DEFAULT_MATERIAL)
        objects.append(SceneObject(
            vbo=vbo, tex=tex, n_verts=n,
            model=model, normal_matrix=nmat,
            Ka=params['Ka'], Kd=params['Kd'], Ks=params['Ks'], shininess=params['shininess'],
        ))
        print(f"  {mat}: {n} verts")

    return objects, extent, raw_center


def load_simple_object(obj_dir, obj_filename, pos=(0.0, 0.0, 0.0), rot_deg=(0.0, 0.0, 0.0),
                        scale=(1.0, 1.0, 1.0), materials=None, light_offset=(0.0, 0.0, 0.0),
                        instances=None, recenter=True, pivot='center'):
    """Generic loader for a single-object OBJ folder (dragon_pillar, jade_cube,
    sakura_tree, grass_field, and future light-emitting objects like
    flying_lantern).

    `materials` maps material name -> {texture, alpha_texture, solid_color,
    Ka, Kd, Ks, shininess}. Missing entries/keys fall back to DEFAULT_MATERIAL
    and a flat gray solid-color texture.

    `instances`, if given, is a list of (pos, rot_deg, scale) tuples; the OBJ
    geometry/textures are loaded once and shared across one SceneObject set
    per instance (e.g. the 26 sakura trees). Otherwise a single instance at
    `pos`/`rot_deg`/`scale` is created.

    `recenter=False` keeps the OBJ's raw exported coordinates (no
    auto-centering to the mesh's own bbox) — use this for objects whose
    geometry was exported already baked to world position (e.g. grass_field),
    so `pos` becomes a pure offset relative to another object's raw frame.

    `pivot='base'` centers X/Z but anchors Y at the mesh's bbox minimum, so
    the local origin sits at ground level — use this for props (e.g. trees)
    whose Blender pivot is at their base, so `pos`/`instances` translations
    line up with object_transforms.md positions without sinking into the floor.
    """
    materials = materials or {}

    raw_groups, _, _ = geometry.load_obj(os.path.join(obj_dir, obj_filename),
                                          recenter=recenter, pivot=pivot)
    mat_map = geometry.merge_groups(raw_groups)
    offset  = glm.vec3(*light_offset)

    parts = []
    for mat, verts in mat_map.items():
        vbo = geometry.upload_vbo(verts)
        n   = len(verts) // 8

        spec      = materials.get(mat, {})
        tex_rel   = spec.get('texture')
        alpha_rel = spec.get('alpha_texture')
        if tex_rel and alpha_rel:
            tex = geometry.load_texture_with_alpha(os.path.join(obj_dir, tex_rel),
                                                     os.path.join(obj_dir, alpha_rel))
        elif tex_rel:
            tex = geometry.load_texture(os.path.join(obj_dir, tex_rel))
        else:
            tex = geometry.make_solid_texture(*spec.get('solid_color', (180, 180, 180)))

        parts.append((vbo, tex, n, spec))

    transforms = instances if instances is not None else [(pos, rot_deg, scale)]

    objects = []
    for t_pos, t_rot, t_scale in transforms:
        model = matrizes.model_matrix(t_pos, t_rot, t_scale)
        nmat  = matrizes.normal_matrix(model)
        for vbo, tex, n, spec in parts:
            objects.append(SceneObject(
                vbo=vbo, tex=tex, n_verts=n,
                model=model, normal_matrix=nmat,
                Ka=spec.get('Ka', DEFAULT_MATERIAL['Ka']),
                Kd=spec.get('Kd', DEFAULT_MATERIAL['Kd']),
                Ks=spec.get('Ks', DEFAULT_MATERIAL['Ks']),
                shininess=spec.get('shininess', DEFAULT_MATERIAL['shininess']),
                light_offset=offset,
            ))

    return objects


def draw_objects(locs, objects, pos_loc, uv_loc, norm_loc):
    for obj in objects:
        geometry.bind_vbo(obj.vbo, pos_loc, uv_loc, norm_loc)
        glUniformMatrix4fv(locs['model'], 1, GL_FALSE, glm.value_ptr(obj.model))
        glUniformMatrix3fv(locs['normalMatrix'], 1, GL_FALSE, glm.value_ptr(obj.normal_matrix))
        glUniform3f(locs['Ka'], *obj.Ka)
        glUniform3f(locs['Kd'], *obj.Kd)
        glUniform3f(locs['Ks'], *obj.Ks)
        glUniform1f(locs['shininess'], obj.shininess)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, obj.tex)
        glDrawArrays(GL_TRIANGLES, 0, obj.n_verts)
