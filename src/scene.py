import os
from dataclasses import dataclass, field

from OpenGL.GL import *
import glm

import geometry
import matrizes
from materials import DEFAULT_MATERIAL, MATERIAL_TEXTURES, TEMPLE_MATERIALS


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
    alpha: float = 1.0
    Ke: tuple = (0.0, 0.0, 0.0)
    light_ref: object = None


def load_temple(temple_dir):
    """Load objects/temple/temple.obj as one SceneObject per material.

    Returns (objects, extent, raw_center) — raw_center is the temple's raw
    (pre-recenter) bbox center in the OBJ export's own coordinate frame, used
    as the reference origin when placing other objects relative to the temple.
    """
    raw_groups, extent, raw_center = geometry.load_obj(
        os.path.join(temple_dir, "temple.obj")
    )
    mat_map = geometry.merge_groups(raw_groups)
    print(f"Temple: extent={extent:.2f}, materials={list(mat_map.keys())}")

    model = glm.mat4(1.0)
    nmat = matrizes.normal_matrix(model)

    objects = []
    for mat, verts in mat_map.items():
        vbo = geometry.upload_vbo(verts)
        n = len(verts) // 8

        rel = MATERIAL_TEXTURES.get(mat)
        if rel:
            tex = geometry.load_texture(os.path.join(temple_dir, rel))
        else:
            # Procedural_Gold: (0.8, 0.65, 0.1) -> uint8
            tex = geometry.make_solid_texture(204, 166, 26)

        params = TEMPLE_MATERIALS.get(mat, DEFAULT_MATERIAL)
        objects.append(
            SceneObject(
                vbo=vbo,
                tex=tex,
                n_verts=n,
                model=model,
                normal_matrix=nmat,
                Ka=params["Ka"],
                Kd=params["Kd"],
                Ks=params["Ks"],
                shininess=params["shininess"],
                alpha=params.get("alpha", 1.0),
            )
        )
        print(f"  {mat}: {n} verts")

    return objects, extent, raw_center


def load_simple_object(
    obj_dir,
    obj_filename,
    pos=(0.0, 0.0, 0.0),
    rot_deg=(0.0, 0.0, 0.0),
    scale=(1.0, 1.0, 1.0),
    materials=None,
    light_offset=(0.0, 0.0, 0.0),
    instances=None,
    recenter=True,
    pivot="center",
    light_refs=None,
):
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

    `light_refs`, if given, is a list of `state.lighting` entries (dicts with
    an 'on' key), one per instance, used to gate that instance's emissive
    (Ke) parts so a lamp's glow turns off with its light (req 3).
    """
    materials = materials or {}

    raw_groups, _, _ = geometry.load_obj(
        os.path.join(obj_dir, obj_filename), recenter=recenter, pivot=pivot
    )
    mat_map = geometry.merge_groups(raw_groups)
    offset = glm.vec3(*light_offset)

    parts = []
    for mat, verts in mat_map.items():
        vbo = geometry.upload_vbo(verts)
        n = len(verts) // 8

        spec = materials.get(mat, {})
        tex_rel = spec.get("texture")
        alpha_rel = spec.get("alpha_texture")
        if tex_rel and alpha_rel:
            tex = geometry.load_texture_with_alpha(
                os.path.join(obj_dir, tex_rel), os.path.join(obj_dir, alpha_rel)
            )
        elif tex_rel:
            tex = geometry.load_texture(os.path.join(obj_dir, tex_rel))
        else:
            tex = geometry.make_solid_texture(*spec.get("solid_color", (180, 180, 180)))

        parts.append((vbo, tex, n, spec))

    transforms = instances if instances is not None else [(pos, rot_deg, scale)]

    objects = []
    for inst_i, (t_pos, t_rot, t_scale) in enumerate(transforms):
        model = matrizes.model_matrix(t_pos, t_rot, t_scale)
        nmat = matrizes.normal_matrix(model)
        light_ref = light_refs[inst_i] if light_refs is not None else None
        for vbo, tex, n, spec in parts:
            objects.append(
                SceneObject(
                    vbo=vbo,
                    tex=tex,
                    n_verts=n,
                    model=model,
                    normal_matrix=nmat,
                    Ka=spec.get("Ka", DEFAULT_MATERIAL["Ka"]),
                    Kd=spec.get("Kd", DEFAULT_MATERIAL["Kd"]),
                    Ks=spec.get("Ks", DEFAULT_MATERIAL["Ks"]),
                    shininess=spec.get("shininess", DEFAULT_MATERIAL["shininess"]),
                    light_offset=offset,
                    alpha=spec.get("alpha", 1.0),
                    Ke=spec.get("Ke", (0.0, 0.0, 0.0)),
                    light_ref=light_ref,
                )
            )

    return objects


def draw_objects(locs, objects, pos_loc, uv_loc, norm_loc):
    for obj in objects:
        geometry.bind_vbo(obj.vbo, pos_loc, uv_loc, norm_loc)
        glUniformMatrix4fv(locs["model"], 1, GL_FALSE, glm.value_ptr(obj.model))
        glUniformMatrix3fv(
            locs["normalMatrix"], 1, GL_FALSE, glm.value_ptr(obj.normal_matrix)
        )
        glUniform3f(locs["Ka"], *obj.Ka)
        glUniform3f(locs["Kd"], *obj.Kd)
        glUniform3f(locs["Ks"], *obj.Ks)
        glUniform1f(locs["shininess"], obj.shininess)
        glUniform1f(locs["alpha"], obj.alpha)
        glUniform3f(locs["Ke"], *obj.Ke)
        glUniform1i(
            locs["emissiveOn"],
            1 if (obj.light_ref is None or obj.light_ref["on"]) else 0,
        )
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, obj.tex)
        glDrawArrays(GL_TRIANGLES, 0, obj.n_verts)
