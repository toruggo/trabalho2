"""Carrega arquivos .vs e .fs do disco, compila, linka em um programa e expõe use()/getProgram()."""

from OpenGL.GL import *


class Shader:
    def __init__(self, vertex_path, fragment_path):
        with open(vertex_path, encoding="utf-8") as f:
            vertex_src = f.read()
        with open(fragment_path, encoding="utf-8") as f:
            fragment_src = f.read()

        vert = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vert, vertex_src)
        glCompileShader(vert)
        if not glGetShaderiv(vert, GL_COMPILE_STATUS):
            raise RuntimeError(f"Vertex shader error:\n{glGetShaderInfoLog(vert).decode()}")

        frag = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(frag, fragment_src)
        glCompileShader(frag)
        if not glGetShaderiv(frag, GL_COMPILE_STATUS):
            raise RuntimeError(f"Fragment shader error:\n{glGetShaderInfoLog(frag).decode()}")

        self._program = glCreateProgram()
        glAttachShader(self._program, vert)
        glAttachShader(self._program, frag)
        glLinkProgram(self._program)
        if not glGetProgramiv(self._program, GL_LINK_STATUS):
            raise RuntimeError(f"Shader link error:\n{glGetProgramInfoLog(self._program).decode()}")

        glDeleteShader(vert)
        glDeleteShader(frag)

    def use(self):
        glUseProgram(self._program)

    def getProgram(self):
        return self._program
