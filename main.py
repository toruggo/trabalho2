"""
Computação Gráfica - Projeto 3: Iluminação com 3 fontes de luz
- Iluminação ambiente: luz global
- Iluminação exterior: 20 flying lanterns em movimento de translação
- Iluminação interior: dragon candle + hanging lanterns em três posições

Controles:
  1 = ligar/desligar luz ambiente
  2 = ligar/desligar lanterns exteriores
  3 = ligar/desligar dragon candle
  4 = ligar/desligar hanging lanterns
  Z/X = diminuir/aumentar intensidade ambiente
  C/V = diminuir/aumentar reflexão difusa
  B/N = diminuir/aumentar reflexão especular
"""

import math
import sys
import os

import glfw
from OpenGL.GL import *
import glm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import input as inp
import render_passes
import scene
import scene_builder
import state

SKYBOX_DIR = "objects/sky_78_cubemap_2k"


def main():
    # Inicializa a janela OpenGL
    if not glfw.init():
        sys.exit("GLFW init failed")

    glfw.window_hint(glfw.SAMPLES, 4)
    window = glfw.create_window(1600, 900, "Trabalho 2 - Temple", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Window creation failed")

    glfw.make_context_current(window)

    main_pass = render_passes.build_main_pass()  # Renderização principal com iluminação
    skybox_pass = render_passes.build_skybox_pass(SKYBOX_DIR)  # Céu/cubemap
    glow_pass = render_passes.build_glow_pass()  # Halos de brilho das lanternas

    # Carrega a cena: templo, árvores, lanternas, objetos de iluminação, etc
    scene_data = scene_builder.build_scene(state.lighting_rig)
    extent = scene_data.extent  # Tamanho da cena (usado para escalar câmera, animações)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Posiciona a câmera a uma distância adequada do templo, olhando para o centro
    cam_dist = extent * 0.9
    camera_pos = glm.vec3(0.0, extent * 0.1, cam_dist)
    init_front = glm.normalize(glm.vec3(0, 0, 0) - camera_pos)
    state.camera["pos"] = camera_pos
    state.camera["front"] = init_front
    state.camera["yaw"] = math.degrees(math.atan2(init_front.z, init_front.x))
    state.camera["pitch"] = math.degrees(
        math.asin(max(-1.0, min(1.0, float(init_front.y))))
    )
    speed = extent * 0.014

    # Controla a altura da câmera: entre o chão (grama) e acima do teto do templo
    # Controles: WASD = movimento horizontal, ESPAÇO/SHIFT = cima/baixo, MOUSE = rotação
    state.camera_min_y = -10.0
    state.camera_max_y = 45.0

    # Define a caixa que delimita o interior do templo
    # Fragmentos dentro dessa caixa recebem luz dos interiores (dragon candle + hanging lanterns)
    # Fragmentos fora recebem luz das flying lanterns (lanternas exteriores)
    state.interior_min = glm.vec3(*scene_builder.INTERIOR_AABB_MIN)
    state.interior_max = glm.vec3(*scene_builder.INTERIOR_AABB_MAX)

    glfw.set_cursor_pos_callback(window, inp.mouse_event)
    glfw.set_key_callback(window, inp.key_event)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    projection = glm.perspective(glm.radians(45.0), 1600.0 / 900.0, 0.1, cam_dist * 4)
    main_pass.shader.use()
    glUniformMatrix4fv(
        main_pass.locs["projection"], 1, GL_FALSE, glm.value_ptr(projection)
    )

    locs = main_pass.locs
    pos_loc, uv_loc, norm_loc = main_pass.pos_loc, main_pass.uv_loc, main_pass.norm_loc

    # Loop Principal de Renderização 
    last_frame = glfw.get_time()

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        # Calcula tempo decorrido desde o último frame (cap máximo de 0.05s para evitar grandes saltos)
        delta_time = min(current_frame - last_frame, 0.05)
        last_frame = current_frame

        # Processa eventos do teclado/mouse
        glfw.poll_events()
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            break

        # Atualiza a câmera baseado em teclas pressionadas (WASD, ESPAÇO, SHIFT, MOUSE)
        inp.process_camera(window, speed)
        # Ajusta parâmetros de iluminação (Z/X, C/V, B/N) enquanto as teclas estão pressionadas
        inp.process_lighting(delta_time)

        # Atualiza comportamentos animados (drift das flying lanterns)
        for behavior in scene_data.behaviors:
            behavior.update(delta_time)

        cam = state.camera
        # Matriz view: posiciona a câmera olhando para a cena
        view = glm.lookAt(cam["pos"], cam["pos"] + cam["front"], cam["up"])

        # Limpa o framebuffer com uma cor de fundo cinza escuro
        glClearColor(0.12, 0.12, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        scene_polygon_mode = GL_LINE if state.wireframe_view else GL_FILL
        glPolygonMode(GL_FRONT_AND_BACK, scene_polygon_mode)

        # Renderiza templo, árvores, chão e outros objetos com iluminação
        main_pass.shader.use()
        glUniformMatrix4fv(locs["view"], 1, GL_FALSE, glm.value_ptr(view))
        render_passes.set3f(locs["viewPos"], cam["pos"])
        # Luzes: ambiente, exteriores (lanternas), interiores (candela + pendentes)
        render_passes.upload_lighting_uniforms(
            locs, state.lighting_rig, state.interior_min, state.interior_max
        )
        # Desenha todos os objetos opacos com seus parâmetros de material (Ka, Kd, Ks, shininess)
        #Ka = o quanto reflete a luz ambiente
        #Kd = o quanto reflete a luz difusa
        #Ks = o quanto reflete a luz especular
        #shininess = o "tamanho" do brilho da superfície
        scene.draw_objects(locs, scene_data.opaque_objects, pos_loc, uv_loc, norm_loc)

        # Cubemap do céu, desenhado por último para ficar ao fundo
        render_passes.draw_skybox(skybox_pass, view, projection)

        # As cascas das lanternas são semi-transparentes 
        main_pass.shader.use()
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)  # Não escreve na profundidade para blending correto
        scene.draw_objects(
            locs, scene_data.translucent_objects, pos_loc, uv_loc, norm_loc
        )
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        # Billboards que adicionam um brilho aditivo onde cada lanterna está acesa
        render_passes.draw_glow_halos(
            glow_pass,
            view,
            projection,
            cam,
            state.lighting_rig.lantern_lights,
            scene_data.glow_color,
            scene_data.glow_size,
        )

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
