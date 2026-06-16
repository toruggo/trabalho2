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
    if not glfw.init():
        sys.exit("GLFW init failed")

    glfw.window_hint(glfw.SAMPLES, 4)
    window = glfw.create_window(1600, 900, "Trabalho 2 - Temple", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Window creation failed")

    glfw.make_context_current(window)

    main_pass = render_passes.build_main_pass()
    skybox_pass = render_passes.build_skybox_pass(SKYBOX_DIR)
    glow_pass = render_passes.build_glow_pass()

    scene_data = scene_builder.build_scene(state.lighting_rig)
    extent = scene_data.extent

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

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

    state.camera_min_y = -10.0
    state.camera_max_y = 45.0

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

    last_frame = glfw.get_time()

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        delta_time = min(current_frame - last_frame, 0.05)
        last_frame = current_frame

        glfw.poll_events()
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            break

        inp.process_camera(window, speed)
        inp.process_lighting(delta_time)

        for behavior in scene_data.behaviors:
            behavior.update(delta_time)

        cam = state.camera
        view = glm.lookAt(cam["pos"], cam["pos"] + cam["front"], cam["up"])

        glClearColor(0.12, 0.12, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        scene_polygon_mode = GL_LINE if state.wireframe_view else GL_FILL
        glPolygonMode(GL_FRONT_AND_BACK, scene_polygon_mode)

        main_pass.shader.use()
        glUniformMatrix4fv(locs["view"], 1, GL_FALSE, glm.value_ptr(view))
        render_passes.set3f(locs["viewPos"], cam["pos"])
        render_passes.upload_lighting_uniforms(
            locs, state.lighting_rig, state.interior_min, state.interior_max
        )
        scene.draw_objects(locs, scene_data.opaque_objects, pos_loc, uv_loc, norm_loc)

        render_passes.draw_skybox(skybox_pass, view, projection)

        main_pass.shader.use()
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)  # evita artefatos de profundidade entre faces translúcidas
        scene.draw_objects(
            locs, scene_data.translucent_objects, pos_loc, uv_loc, norm_loc
        )
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        render_passes.draw_glow_halos(
            glow_pass,
            view,
            projection,
            cam,
            state.lighting_rig.lantern_lights,
            scene_data.glow_color,
            scene_data.glow_size,
            debug=state.debug_glow,
        )

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
