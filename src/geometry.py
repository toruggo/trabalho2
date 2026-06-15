"""
Leitura de malhas OBJ, buffers na GPU e texturas.

Sem usar pipeline fixo: só VBO, textura 2D, cubemap e atributos compatíveis
com o vertex shader da cena principal.
"""

import ctypes

from OpenGL.GL import *
import numpy as np
from PIL import Image

# Limite de lado da textura para não estourar memória em assets muito grandes.
MAX_TEX_SIZE = 2048


def load_obj(path, recenter=True, pivot='center'):
    """Lê um arquivo OBJ com vários materiais via usemtl.

    Retorna uma lista de pares nome do material e vértices em float32 no layout
    intercalado posição três floats, UV dois floats, normal três floats por vértice,
    triangulado a partir de faces poligonais. Retorna também a maior extensão da
    caixa limitadora e o centro usado no recenter.

    Se recenter for True, subtrai o centro calculado das posições. Se for False,
    mantém coordenadas brutas do export e center indica o que teria sido subtraído.

    pivot center usa o centro da caixa nos três eixos. pivot base usa centro em X
    e Z mas mínimo em Y para ancorar o objeto no chão, útil para árvores e props.
    """
    positions     = []
    uvs           = []
    normals       = []
    groups        = []
    current_mat   = '__default__'
    current_faces = []

    with open(path, encoding='utf-8') as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            if parts[0] == 'v':
                positions.append([float(x) for x in parts[1:4]])
            elif parts[0] == 'vt':
                uvs.append([float(x) for x in parts[1:3]])
            elif parts[0] == 'vn':
                normals.append([float(x) for x in parts[1:4]])
            elif parts[0] == 'usemtl':
                if current_faces:
                    groups.append((current_mat, current_faces))
                current_mat   = parts[1]
                current_faces = []
            elif parts[0] == 'f':
                face = []
                for token in parts[1:]:
                    idx    = token.split('/')
                    pos_i  = int(idx[0]) - 1
                    uv_i   = int(idx[1]) - 1 if len(idx) > 1 and idx[1] else 0
                    norm_i = int(idx[2]) - 1 if len(idx) > 2 and idx[2] else 0
                    face.append((pos_i, uv_i, norm_i))
                current_faces.append(face)

    if current_faces:
        groups.append((current_mat, current_faces))

    pos_arr  = np.array(positions, dtype=np.float32)
    bbox_min = pos_arr.min(axis=0)
    bbox_max = pos_arr.max(axis=0)
    extent   = float((bbox_max - bbox_min).max())
    center   = (bbox_min + bbox_max) / 2.0
    if pivot == 'base':
        center = np.array([center[0], bbox_min[1], center[2]], dtype=center.dtype)
    if recenter:
        pos_arr -= center

    result = []
    for mat_name, faces in groups:
        verts = []
        for face in faces:
            # Triangulação em leque: primeiro vértice fixo, varre o polígono
            for i in range(1, len(face) - 1):
                for vi in [face[0], face[i], face[i + 1]]:
                    verts.extend(pos_arr[vi[0]])
                    verts.extend(uvs[vi[1]])
                    verts.extend(normals[vi[2]])
        result.append((mat_name, np.array(verts, dtype=np.float32)))

    return result, extent, tuple(center.tolist())


def merge_groups(groups):
    """Junta em um único array todos os grupos que compartilham o mesmo nome de material."""
    merged = {}
    for mat, verts in groups:
        if mat in merged:
            merged[mat] = np.concatenate([merged[mat], verts])
        else:
            merged[mat] = verts
    return merged


def upload_vbo(vertices):
    """Cria um VBO GL_ARRAY_BUFFER e copia o array numpy de vértices estático."""
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    return vbo


def bind_vbo(vbo, pos_loc, uv_loc, norm_loc):
    """Liga o VBO aos três atributos do shader principal: posição, UV, normal.

    Stride oito floats de trinta e dois bits: três pos, dois UV, três normal.
    """
    F      = 4
    stride = 8 * F
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glVertexAttribPointer(pos_loc,  3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glVertexAttribPointer(uv_loc,   2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * F))
    glVertexAttribPointer(norm_loc, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(5 * F))


def load_texture(path):
    """Carrega imagem RGBA do disco, limita tamanho, inverte eixo Y e envia para textura 2D."""
    Image.MAX_IMAGE_PIXELS = None
    img = Image.open(path).convert("RGBA")
    if img.width > MAX_TEX_SIZE or img.height > MAX_TEX_SIZE:
        img = img.resize((MAX_TEX_SIZE, MAX_TEX_SIZE), Image.LANCZOS)
    img  = img.transpose(Image.FLIP_TOP_BOTTOM)
    data = np.array(img, dtype=np.uint8)
    tex  = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,     GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,     GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tex


def load_texture_with_alpha(color_path, alpha_path):
    """Mescla textura RGB com máscara alpha em escala de cinza em um único RGBA.

    Útil para folhas ou sakura com arquivo de opacidade separado.
    """
    Image.MAX_IMAGE_PIXELS = None
    img   = Image.open(color_path).convert("RGB")
    alpha = Image.open(alpha_path).convert("L")
    if alpha.size != img.size:
        alpha = alpha.resize(img.size)
    img = Image.merge("RGBA", (*img.split(), alpha))

    if img.width > MAX_TEX_SIZE or img.height > MAX_TEX_SIZE:
        img = img.resize((MAX_TEX_SIZE, MAX_TEX_SIZE), Image.LANCZOS)
    img  = img.transpose(Image.FLIP_TOP_BOTTOM)
    data = np.array(img, dtype=np.uint8)
    tex  = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S,     GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T,     GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return tex


def load_cubemap(directory):
    """Carrega seis faces PNG em um GL_TEXTURE_CUBE_MAP para o skybox."""
    import os
    faces = [
        (GL_TEXTURE_CUBE_MAP_POSITIVE_X, 'px.png'),
        (GL_TEXTURE_CUBE_MAP_NEGATIVE_X, 'nx.png'),
        (GL_TEXTURE_CUBE_MAP_POSITIVE_Y, 'py.png'),
        (GL_TEXTURE_CUBE_MAP_NEGATIVE_Y, 'ny.png'),
        (GL_TEXTURE_CUBE_MAP_POSITIVE_Z, 'pz.png'),
        (GL_TEXTURE_CUBE_MAP_NEGATIVE_Z, 'nz.png'),
    ]
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_CUBE_MAP, tex)
    for target, fname in faces:
        img  = Image.open(os.path.join(directory, fname)).convert('RGB')
        data = np.array(img, dtype=np.uint8)
        glTexImage2D(target, 0, GL_RGB, img.width, img.height,
                     0, GL_RGB, GL_UNSIGNED_BYTE, data)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP_TO_EDGE)
    return tex


def make_solid_texture(r, g, b):
    """Textura 2D 1x1 em RGBA com cor sólida, para materiais sem arquivo de imagem."""
    data = np.array([[[r, g, b, 255]]], dtype=np.uint8)
    tex  = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return tex
