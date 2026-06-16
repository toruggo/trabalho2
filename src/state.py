"""
Estado global compartilhado entre main, input e renderização.

Aqui ficam a câmera, teclas mantidas pressionadas, o rig de iluminação,
os limites da caixa interior usada no fragment shader e flags de modo
visual. O main.py atualiza parte desses valores depois de carregar a cena.
"""

import glm

from lighting import make_default_rig

# Câmera estilo primeira pessoa: posição, direção frontal, vetor cima,
# ângulos yaw e pitch em graus, e estado do mouse para o primeiro frame.
camera = {
    "pos": glm.vec3(0.0, 0.0, 0.0),
    "front": glm.vec3(0.0, 0.0, -1.0),
    "up": glm.vec3(0.0, 1.0, 0.0),
    "yaw": -90.0,
    "pitch": 0.0,
    "first": True,
    "last_x": 400.0,
    "last_y": 300.0,
}

# Limites verticais da câmera em espaço mundo, eixo Y, para não atravessar
# o chão nem subir infinito. O main.py define valores coerentes com a cena.
camera_min_y = 0.0
camera_max_y = 0.0

# Conjunto de teclas GLFW atualmente pressionadas. Serve para ajuste contínuo
# de luz ambiente ou difusa enquanto Z, X, C, V, B ou N ficam seguradas.
keys_pressed = set()

# Rig completo de iluminação: ambiente, multiplicadores difuso e especular,
# lista de luzes das lanternas voadoras, int_light_a e int_light_b.
# Detalhes dos campos em lighting.LightingRig. Posições das luzes pontuais
# são preenchidas pelos build dos assets ao montar a cena.
lighting_rig = make_default_rig()

# Cantos mínimo e máximo em espaço mundo do paralelepípedo que representa
# o interior do templo para o fragment shader decidir quais luzes somar.
# O main.py copia de scene_builder.INTERIOR_AABB_MIN e MAX na inicialização.
interior_min = glm.vec3(0.0)
interior_max = glm.vec3(0.0)

# Tecla T: desenha a cena em modo arame, GL_LINE em vez de preenchimento GL_FILL.
wireframe_view = False

# Tecla G: mostra os quads billboard do glow em wireframe com cor sólida.
debug_glow = False
