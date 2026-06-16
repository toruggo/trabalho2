import os
from dataclasses import dataclass, field

from OpenGL.GL import *
import glm

import geometry
import matrizes
from lighting import Light

# Material padrão quando o .obj não traz spec (Ka = Kd para o slider de ambiente)
DEFAULT_MATERIAL = dict(
    Ka=(0.7, 0.7, 0.7), Kd=(0.7, 0.7, 0.7), Ks=(0.1, 0.1, 0.1), shininess=8.0
)


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
    light: Light = None


def load_temple(temple_dir, materials, material_textures, gold_color=(204, 166, 26)):
    """Carrega temple.obj: um SceneObject por material.

    materials: nome -> Ka, Kd, Ks, shininess, alpha (no código, não no .mtl).
    material_textures: nome -> caminho da textura; sem entrada usa textura sólida gold_color.

    Retorna (objects, extent, raw_center): raw_center é o centro da bbox antes
    do recenter, referência para posicionar os outros assets.
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

        rel = material_textures.get(mat)
        if rel:
            tex = geometry.load_texture(os.path.join(temple_dir, rel))
        else:
            tex = geometry.make_solid_texture(*gold_color)

        params = materials.get(mat, DEFAULT_MATERIAL)
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
    lights=None,
):
    """Carrega um OBJ simples (grama, muro, sakura, lanternas, etc.).

    materials: nome -> textura, alpha, cor sólida, Ka/Kd/Ks/shininess; falta vira DEFAULT_MATERIAL.

    instances: lista de (pos, rot_deg, scale); malha carregada uma vez, vários SceneObjects.
    Sem lista, uma só instância em pos / rot_deg / scale.

    recenter=False: mantém coordenadas do export (malha já no mundo, ex. grama);
    pos vira só o deslocamento do recenter do templo.

    pivot='base': recenter em X/Z e ancora Y no mínimo da bbox (árvores no chão).

    lights: uma Light por instância; liga emissiveOn do Ke ao interruptor da luz.
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
        light = lights[inst_i] if lights is not None else None
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
                    light=light,
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
            1 if (obj.light is None or obj.light.on) else 0,
        )
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, obj.tex)
        glDrawArrays(GL_TRIANGLES, 0, obj.n_verts)
