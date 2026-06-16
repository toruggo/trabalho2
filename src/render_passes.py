"""
Montagem dos passes de renderização e funções auxiliares por frame.

Centraliza compilação dos shaders, localização de uniforms, VBOs compartilhados
e desenho ou upload para: cena principal com Phong, skybox em cubemap e halos
aditivos das lanternas voadoras.
"""

import ctypes
from dataclasses import dataclass

from OpenGL.GL import *
import numpy as np
import glm

from shader_s import Shader
import geometry
from lighting import NUM_LANTERNS, LightingRig

# Cubo unitário com 36 vértices em triângulos. Malha do skybox em cubemap.
CUBE_VERTS = np.array(
    [
        -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1, -1,
        -1, -1, 1, -1, -1, -1, -1, 1, -1, -1, 1, -1, -1, 1, 1, -1, -1, 1,
        1, -1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, -1, -1,
        -1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, 1, -1, -1, 1,
        -1, 1, -1, 1, 1, -1, 1, 1, 1, 1, 1, 1, -1, 1, 1, -1, 1, -1,
        -1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, -1, -1, -1, 1, 1, -1, 1,
    ],
    dtype=np.float32,
)

# Quad local entre menos meio e mais meio, usado como billboard para o halo.
# O glow.vs usa cameraRight e cameraUp para orientar o quad na tela.
GLOW_QUAD_VERTS = np.array(
    [-0.5, -0.5, 0.5, -0.5, 0.5, 0.5, -0.5, -0.5, 0.5, 0.5, -0.5, 0.5],
    dtype=np.float32,
)


def set3f(loc, v):
    """Atalho para glUniform3f com glm.vec3."""
    glUniform3f(loc, v.x, v.y, v.z)


@dataclass
class MainPass:
    """Shader principal da cena, atributos posição UV normal e dicionário de locs."""

    shader: Shader
    program: int
    pos_loc: int
    uv_loc: int
    norm_loc: int
    locs: dict


@dataclass
class SkyboxPass:
    """Cubemap de céu, VBO do cubo e textura GL_TEXTURE_CUBE_MAP."""

    shader: Shader
    program: int
    pos_loc: int
    vbo: int
    cubemap_tex: int
    locs: dict


@dataclass
class GlowPass:
    """Billboard em triângulos para brilho aditivo ao redor de cada lanterna ligada."""

    shader: Shader
    program: int
    pos_loc: int
    vbo: int
    locs: dict


def build_main_pass() -> MainPass:
    """Compila vertex e fragment da cena, habilita atributos e cacheia todos os uniforms."""
    shader = Shader("shaders/vertex_shader.vs", "shaders/fragment_shader.fs")
    shader.use()
    prog = shader.getProgram()

    pos_loc = glGetAttribLocation(prog, "position")
    uv_loc = glGetAttribLocation(prog, "texture_coord")
    norm_loc = glGetAttribLocation(prog, "normal")
    glEnableVertexAttribArray(pos_loc)
    glEnableVertexAttribArray(uv_loc)
    glEnableVertexAttribArray(norm_loc)

    glActiveTexture(GL_TEXTURE0)
    glUniform1i(glGetUniformLocation(prog, "samplerTexture"), 0)

    locs = {
        "model": glGetUniformLocation(prog, "model"),
        "view": glGetUniformLocation(prog, "view"),
        "projection": glGetUniformLocation(prog, "projection"),
        "normalMatrix": glGetUniformLocation(prog, "normalMatrix"),
        "viewPos": glGetUniformLocation(prog, "viewPos"),
        "Ka": glGetUniformLocation(prog, "Ka"),
        "Kd": glGetUniformLocation(prog, "Kd"),
        "Ks": glGetUniformLocation(prog, "Ks"),
        "shininess": glGetUniformLocation(prog, "shininess"),
        "alpha": glGetUniformLocation(prog, "alpha"),
        "Ke": glGetUniformLocation(prog, "Ke"),
        "emissiveOn": glGetUniformLocation(prog, "emissiveOn"),
        "ambientOn": glGetUniformLocation(prog, "ambientOn"),
        "ambientStrength": glGetUniformLocation(prog, "ambientStrength"),
        "ambientColor": glGetUniformLocation(prog, "ambientColor"),
        "diffuseMult": glGetUniformLocation(prog, "diffuseMult"),
        "specularMult": glGetUniformLocation(prog, "specularMult"),
        "interiorMin": glGetUniformLocation(prog, "interiorMin"),
        "interiorMax": glGetUniformLocation(prog, "interiorMax"),
        "lanternOn": [
            glGetUniformLocation(prog, f"lanternOn[{i}]") for i in range(NUM_LANTERNS)
        ],
        "lanternPos": [
            glGetUniformLocation(prog, f"lanternPos[{i}]") for i in range(NUM_LANTERNS)
        ],
        "lanternColor": [
            glGetUniformLocation(prog, f"lanternColor[{i}]") for i in range(NUM_LANTERNS)
        ],
        "intLightAOn": glGetUniformLocation(prog, "intLightAOn"),
        "intLightAPos": glGetUniformLocation(prog, "intLightAPos"),
        "intLightAColor": glGetUniformLocation(prog, "intLightAColor"),
        "intLightBOn": glGetUniformLocation(prog, "intLightBOn"),
        "intLightBPos": [
            glGetUniformLocation(prog, f"intLightB{i + 1}Pos") for i in range(3)
        ],
        "intLightBColor": glGetUniformLocation(prog, "intLightBColor"),
    }

    return MainPass(shader, prog, pos_loc, uv_loc, norm_loc, locs)


def build_skybox_pass(skybox_dir) -> SkyboxPass:
    """Cubo em VBO, cubemap carregado da pasta, sampler na unidade zero."""
    shader = Shader("shaders/skybox.vs", "shaders/skybox.fs")
    prog = shader.getProgram()
    shader.use()
    glUniform1i(glGetUniformLocation(prog, "skybox"), 0)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, CUBE_VERTS.nbytes, CUBE_VERTS, GL_STATIC_DRAW)
    pos_loc = glGetAttribLocation(prog, "position")
    glEnableVertexAttribArray(pos_loc)

    cubemap_tex = geometry.load_cubemap(skybox_dir)

    locs = {
        "view": glGetUniformLocation(prog, "view"),
        "projection": glGetUniformLocation(prog, "projection"),
    }

    return SkyboxPass(shader, prog, pos_loc, vbo, cubemap_tex, locs)


def build_glow_pass() -> GlowPass:
    """Quad em VBO e uniforms para billboard e cor do halo."""
    shader = Shader("shaders/glow.vs", "shaders/glow.fs")
    prog = shader.getProgram()
    pos_loc = glGetAttribLocation(prog, "position")
    glEnableVertexAttribArray(pos_loc)

    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, GLOW_QUAD_VERTS.nbytes, GLOW_QUAD_VERTS, GL_STATIC_DRAW)

    locs = {
        "view": glGetUniformLocation(prog, "view"),
        "projection": glGetUniformLocation(prog, "projection"),
        "center": glGetUniformLocation(prog, "center"),
        "cameraRight": glGetUniformLocation(prog, "cameraRight"),
        "cameraUp": glGetUniformLocation(prog, "cameraUp"),
        "size": glGetUniformLocation(prog, "size"),
        "color": glGetUniformLocation(prog, "color"),
        "debugGlow": glGetUniformLocation(prog, "debugGlow"),
    }

    return GlowPass(shader, prog, pos_loc, vbo, locs)


def upload_lighting_uniforms(locs, rig: LightingRig, interior_min, interior_max):
    """Envia ao shader principal todo o estado de luz do frame atual.

    Inclui ambiente, multiplicadores difuso e especular, caixa interior,
    array de lanternas e luzes internas A e B com as três posições de B.
    """
    glUniform1i(locs["ambientOn"], int(rig.ambient_on))
    glUniform1f(locs["ambientStrength"], rig.ambient_strength)
    glUniform3f(locs["ambientColor"], *rig.ambient_color)
    glUniform1f(locs["diffuseMult"], rig.diffuse_mult)
    glUniform1f(locs["specularMult"], rig.specular_mult)
    set3f(locs["interiorMin"], interior_min)
    set3f(locs["interiorMax"], interior_max)

    for i, lantern in enumerate(rig.lantern_lights):
        glUniform1i(locs["lanternOn"][i], int(lantern.on))
        set3f(locs["lanternPos"][i], lantern.positions[0])
        glUniform3f(locs["lanternColor"][i], *lantern.color)

    ia = rig.int_light_a
    glUniform1i(locs["intLightAOn"], int(ia.on))
    set3f(locs["intLightAPos"], ia.positions[0])
    glUniform3f(locs["intLightAColor"], *ia.color)

    ib = rig.int_light_b
    glUniform1i(locs["intLightBOn"], int(ib.on))
    for i, pos in enumerate(ib.positions):
        set3f(locs["intLightBPos"][i], pos)
    glUniform3f(locs["intLightBColor"], *ib.color)


def draw_skybox(pass_: SkyboxPass, view, projection):
    """Desenha o cubemap atrás da geometria usando view só com rotação e teste GL_LEQUAL.

    O vertex shader usa xyww para fixar profundidade máxima e o cubo envolve a câmera.
    """
    glDepthFunc(GL_LEQUAL)
    pass_.shader.use()
    sky_view = glm.mat4(glm.mat3(view))  # só rotação: cubo gira com a cabeça, sem translação
    glUniformMatrix4fv(pass_.locs["view"], 1, GL_FALSE, glm.value_ptr(sky_view))
    glUniformMatrix4fv(pass_.locs["projection"], 1, GL_FALSE, glm.value_ptr(projection))
    glBindBuffer(GL_ARRAY_BUFFER, pass_.vbo)
    glVertexAttribPointer(pass_.pos_loc, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0))
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_CUBE_MAP, pass_.cubemap_tex)
    glDrawArrays(GL_TRIANGLES, 0, 36)
    glDepthFunc(GL_LESS)


def draw_glow_halos(pass_: GlowPass, view, projection, cam, lantern_lights, color, size, debug=False):
    pass_.shader.use()
    glUniformMatrix4fv(pass_.locs["view"], 1, GL_FALSE, glm.value_ptr(view))
    glUniformMatrix4fv(pass_.locs["projection"], 1, GL_FALSE, glm.value_ptr(projection))

    cam_right = glm.normalize(glm.cross(cam["front"], cam["up"]))
    cam_up = glm.cross(cam_right, cam["front"])
    set3f(pass_.locs["cameraRight"], cam_right)
    set3f(pass_.locs["cameraUp"], cam_up)
    glUniform3f(pass_.locs["color"], *color)
    glUniform1f(pass_.locs["size"], size)
    glUniform1i(pass_.locs["debugGlow"], int(debug))
    glBindBuffer(GL_ARRAY_BUFFER, pass_.vbo)
    glVertexAttribPointer(pass_.pos_loc, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0))

    glDepthMask(GL_FALSE)
    if debug:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
    for lantern in lantern_lights:
        if lantern.on:
            set3f(pass_.locs["center"], lantern.positions[0])
            glDrawArrays(GL_TRIANGLES, 0, 6)
    glDepthMask(GL_TRUE)
    if debug:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)
