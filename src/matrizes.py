"""
Funções auxiliares de álgebra linear para OpenGL.

Montagem de matriz modelo TRS, matriz de normais, conversão de coordenadas
Blender para a convenção da cena, e posição de luz ligada a um SceneObject.
"""

import math

import glm


def model_matrix(pos=(0.0, 0.0, 0.0), rot_deg=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0)):
    """Retorna matriz 4x4 modelo: translação, rotações Z, Y, X em graus, escala."""
    m = glm.mat4(1.0)
    m = glm.translate(m, glm.vec3(*pos))
    if rot_deg[2]:
        m = glm.rotate(m, math.radians(rot_deg[2]), glm.vec3(0, 0, 1))
    if rot_deg[1]:
        m = glm.rotate(m, math.radians(rot_deg[1]), glm.vec3(0, 1, 0))
    if rot_deg[0]:
        m = glm.rotate(m, math.radians(rot_deg[0]), glm.vec3(1, 0, 0))
    m = glm.scale(m, glm.vec3(*scale))
    return m


def normal_matrix(model):
    """Matriz 3x3 para transformar normais no espaço mundo sob escala não uniforme.

    Usa transposta da inversa da parte linear da matriz modelo, padrão em
    pipeline programável para manter os produtos escalares da iluminação corretos.
    """
    return glm.transpose(glm.inverse(glm.mat3(model)))


def light_world_pos(obj):
    """Posição mundial do ponto de luz associado a um SceneObject.

    Aplica a matriz modelo do objeto ao vetor light_offset em coordenadas locais,
    típico para alinhar a luz à chama ou ao bulbo da malha exportada.
    """
    return glm.vec3(obj.model * glm.vec4(obj.light_offset, 1.0))


def blender_to_scene_pos(x, y, z):
    """Converte um ponto do mundo Blender, eixo Z para cima, para nossa cena com eixo Y para cima.

    Equivale a rotação de -90 graus em torno de X: entrada x, y, z
    vira saída x, z, menos y. Rotações Euler em Z no Blender alinham com rotação
    em Y na cena quando você usa essa conversão nas instâncias.
    """
    return (x, z, -y)


def place_baked_instance(baked_pos, baked_rot_z_deg, target_pos, target_rot_z_deg,
                          baked_scale, target_scale, temple_center):
    """Monta posição, rotação em graus e escala para instanciar malha já assada no Blender.

    A malha veio exportada com posição, rotação em Z e escala fixas no arquivo.
    Esta função calcula o tripleto pos, rot_deg, scale para colocar uma cópia
    em outro alvo no mundo Blender, depois expresso na cena recenterada pelo
    temple_center. Trata diferença de rotação em torno do eixo vertical e razão
    de escala uniforme entre instância assada e alvo. Se alvo e assado forem
    iguais, o resultado é a identidade na prática.
    """
    Q  = blender_to_scene_pos(*baked_pos)
    Q0 = blender_to_scene_pos(*target_pos)
    delta_rot = target_rot_z_deg - baked_rot_z_deg
    ratio     = target_scale / baked_scale

    theta = math.radians(delta_rot)
    c, s  = math.cos(theta), math.sin(theta)
    rQ = (Q[0] * c + Q[2] * s, Q[1], -Q[0] * s + Q[2] * c)

    pos = tuple(Q0[i] - temple_center[i] - ratio * rQ[i] for i in range(3))
    return pos, (0.0, delta_rot, 0.0), (ratio, ratio, ratio)
