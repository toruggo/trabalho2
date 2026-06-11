import ctypes

from OpenGL.GL import *
import numpy as np
from PIL import Image

MAX_TEX_SIZE = 2048


def load_obj(path, recenter=True, pivot='center'):
    """Parse OBJ with multi-material support via usemtl.
    Returns ([(mat_name, vertices_float32), ...], longest_extent, raw_bbox_center).
    Positions are centered at origin unless recenter=False, in which case the
    raw (exported) coordinates are kept and raw_bbox_center is the offset that
    would otherwise have been subtracted.

    `pivot` controls where that offset sits relative to the bbox:
    - 'center' (default): offset = bbox center on all axes.
    - 'base': offset = bbox center on X/Z but bbox *minimum* on Y, so the
      object's local origin lands at ground level (matches Blender objects
      whose pivot is at the base, e.g. trees/props standing on the floor).
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
            for i in range(1, len(face) - 1):
                for vi in [face[0], face[i], face[i + 1]]:
                    verts.extend(pos_arr[vi[0]])
                    verts.extend(uvs[vi[1]])
                    verts.extend(normals[vi[2]])
        result.append((mat_name, np.array(verts, dtype=np.float32)))

    return result, extent, tuple(center.tolist())


def merge_groups(groups):
    """Concatenate vertex arrays that share the same material name."""
    merged = {}
    for mat, verts in groups:
        if mat in merged:
            merged[mat] = np.concatenate([merged[mat], verts])
        else:
            merged[mat] = verts
    return merged


def upload_vbo(vertices):
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    return vbo


def bind_vbo(vbo, pos_loc, uv_loc, norm_loc):
    F      = 4
    stride = 8 * F
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glVertexAttribPointer(pos_loc,  3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glVertexAttribPointer(uv_loc,   2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * F))
    glVertexAttribPointer(norm_loc, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(5 * F))


def load_texture(path):
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
    """Load an RGB color texture and merge in a separate grayscale alpha mask
    (e.g. Sakura.png + Sakura_Opacity.png) for cutout transparency.
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
    """Upload a 1x1 RGBA texture for materials with no image (e.g. Procedural_Gold)."""
    data = np.array([[[r, g, b, 255]]], dtype=np.uint8)
    tex  = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 1, 1, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    return tex
