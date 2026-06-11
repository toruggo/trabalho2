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
    debug_pass = render_passes.build_debug_pass(skybox_pass.vbo)
    glow_pass = render_passes.build_glow_pass()

    scene_data = scene_builder.build_scene(state.lighting_rig)
    extent = scene_data.extent

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # ── Camera ────────────────────────────────────────────────────────────────
    cam_dist = extent * 0.9
    camera_pos = glm.vec3(0.0, extent * 0.1, cam_dist)
    init_front = glm.normalize(glm.vec3(0, 0, 0) - camera_pos)
    state.camera["pos"] = camera_pos
    state.camera["front"] = init_front
    state.camera["yaw"] = math.degrees(math.atan2(init_front.z, init_front.x))
    state.camera["pitch"] = math.degrees(
        math.asin(max(-1.0, min(1.0, float(init_front.y))))
    )
    speed = extent * 0.02

    # Keep the camera between the grass and a height that's enough to fly
    # over the temple roof, but not much further. Grass world-space Y sits
    # around -11 (raw grass bbox shifted by -temple_center.y).
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

    # ── Render loop ───────────────────────────────────────────────────────────
    last_frame = glfw.get_time()

    while not glfw.window_should_close(window):
        current_frame = glfw.get_time()
        # Cap so a stutter/hitch doesn't make a single frame's worth of
        # animation (e.g. lantern drift) jump by a large amount.
        delta_time = min(current_frame - last_frame, 0.05)
        last_frame = current_frame

        glfw.poll_events()
        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            break

        inp.process_camera(window, speed)
        inp.process_lighting(delta_time)
        inp.process_debug_box(delta_time)

        for behavior in scene_data.behaviors:
            behavior.update(delta_time)

        cam = state.camera
        view = glm.lookAt(cam["pos"], cam["pos"] + cam["front"], cam["up"])

        glClearColor(0.12, 0.12, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Wireframe view (key T): draw the whole scene with GL_LINE polygon
        # mode instead of GL_FILL.
        scene_polygon_mode = GL_LINE if state.wireframe_view else GL_FILL
        glPolygonMode(GL_FRONT_AND_BACK, scene_polygon_mode)

        # ── Temple/scene ──────────────────────────────────────────────────────
        main_pass.shader.use()
        glUniformMatrix4fv(locs["view"], 1, GL_FALSE, glm.value_ptr(view))
        render_passes.set3f(locs["viewPos"], cam["pos"])
        render_passes.upload_lighting_uniforms(
            locs, state.lighting_rig, state.interior_min, state.interior_max
        )
        scene.draw_objects(locs, scene_data.opaque_objects, pos_loc, uv_loc, norm_loc)

        # ── Debug view (key M): interior AABB wireframe ───────────────────────
        # Light markers were dropped now that the lamp geometry itself glows
        # (Ke/emissiveOn) and acts as the visible light source.
        if state.debug_view:
            aabb_center = (state.interior_min + state.interior_max) * 0.5
            aabb_half = (state.interior_max - state.interior_min) * 0.5
            render_passes.draw_debug_aabb(
                debug_pass,
                view,
                projection,
                aabb_center,
                aabb_half,
                (1.0, 1.0, 0.0),
                restore_mode=scene_polygon_mode,
            )

        # ── Skybox (drawn last; xyww trick keeps it at depth 1.0) ─────────────
        render_passes.draw_skybox(skybox_pass, view, projection)

        # Translucent lantern shells: drawn after the skybox so they blend
        # over it correctly (depth writes off, depth test on).
        main_pass.shader.use()
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)
        scene.draw_objects(
            locs, scene_data.translucent_objects, pos_loc, uv_loc, norm_loc
        )
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        # ── Glow halos: additive billboards over each lit flying lantern ─────
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
