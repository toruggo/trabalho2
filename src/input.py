import math

import glfw
import glm

import state


def _fmt(v):
    return f"({v.x:.2f}, {v.y:.2f}, {v.z:.2f})"


def _dump_lights():
    print("[Debug] Light positions/colors:")
    for i, lantern in enumerate(state.lighting["lantern_lights"]):
        print(
            f"  lantern{i+1}: on={lantern['on']} pos={_fmt(lantern['pos'])} color={lantern['color']}"
        )
    ia = state.lighting["int_light_a"]
    print(
        f"  int_light_a (dragon candle): on={ia['on']} pos={_fmt(ia['pos'])} color={ia['color']}"
    )
    ib = state.lighting["int_light_b"]
    for i, pos in enumerate(ib["positions"]):
        print(
            f"  int_light_b[{i}] (hanging lantern): on={ib['on']} pos={_fmt(pos)} color={ib['color']}"
        )
    print(
        f"  interior AABB: min={_fmt(state.interior_min)} max={_fmt(state.interior_max)}"
    )


def key_event(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        state.keys_pressed.add(key)

        if key == glfw.KEY_1:
            state.lighting["ambient_on"] = not state.lighting["ambient_on"]
            print(f"[Light] Ambient: {'ON' if state.lighting['ambient_on'] else 'OFF'}")
        elif key == glfw.KEY_2:
            lanterns = state.lighting["lantern_lights"]
            new_state = not lanterns[0]["on"]
            for light in lanterns:
                light["on"] = new_state
            print(f"[Light] Exterior lanterns (1-4): {'ON' if new_state else 'OFF'}")
        elif key == glfw.KEY_3:
            light = state.lighting["int_light_a"]
            light["on"] = not light["on"]
            print(
                f"[Light] Interior A (dragon candle): {'ON' if light['on'] else 'OFF'}"
            )
        elif key == glfw.KEY_4:
            light = state.lighting["int_light_b"]
            light["on"] = not light["on"]
            print(
                f"[Light] Interior B (hanging lanterns x3): {'ON' if light['on'] else 'OFF'}"
            )
        elif key == glfw.KEY_P:
            # TEMPORARY: print the camera position so it can be used as a
            # placement point for new lanterns.
            cam = state.camera
            print(f"[Camera] pos={_fmt(cam['pos'])}")
        elif key == glfw.KEY_M:
            state.debug_view = not state.debug_view
            print(
                f"[Debug] Light markers + interior AABB: {'ON' if state.debug_view else 'OFF'}"
            )
            if state.debug_view:
                _dump_lights()
        elif key == glfw.KEY_T:
            state.wireframe_view = not state.wireframe_view
            print(f"[Debug] Wireframe view: {'ON' if state.wireframe_view else 'OFF'}")
    elif action == glfw.RELEASE:
        state.keys_pressed.discard(key)

        if key in (glfw.KEY_Z, glfw.KEY_X):
            print(
                f"[Lighting] ambient_strength = {state.lighting['ambient_strength']:.3f}"
            )
        elif key in (glfw.KEY_C, glfw.KEY_V):
            print(f"[Lighting] diffuse_mult = {state.lighting['diffuse_mult']:.3f}")
        elif key in (glfw.KEY_B, glfw.KEY_N):
            print(f"[Lighting] specular_mult = {state.lighting['specular_mult']:.3f}")
        elif key in _BOX_KEYS:
            print(
                f"[Debug] interior AABB: min={_fmt(state.interior_min)} max={_fmt(state.interior_max)}"
            )


def mouse_event(window, xpos, ypos):
    cam = state.camera
    if cam["first"]:
        cam["last_x"] = xpos
        cam["last_y"] = ypos
        cam["first"] = False
        return

    dx = (xpos - cam["last_x"]) * 0.1
    dy = (cam["last_y"] - ypos) * 0.1
    cam["last_x"] = xpos
    cam["last_y"] = ypos

    cam["yaw"] += dx
    cam["pitch"] = max(-89.0, min(89.0, cam["pitch"] + dy))

    front = glm.vec3(
        math.cos(math.radians(cam["yaw"])) * math.cos(math.radians(cam["pitch"])),
        math.sin(math.radians(cam["pitch"])),
        math.sin(math.radians(cam["yaw"])) * math.cos(math.radians(cam["pitch"])),
    )
    cam["front"] = glm.normalize(front)


def process_camera(window, speed):
    cam = state.camera
    right = glm.normalize(glm.cross(cam["front"], cam["up"]))

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        cam["pos"] += cam["front"] * speed
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        cam["pos"] -= cam["front"] * speed
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        cam["pos"] -= right * speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        cam["pos"] += right * speed
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        cam["pos"] += cam["up"] * speed
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        cam["pos"] -= cam["up"] * speed


# Held-key adjustment speeds (units per second).
AMBIENT_SPEED = 0.2
DIFFUSE_SPEED = 0.5
SPECULAR_SPEED = 0.5


def process_lighting(delta_time):
    """Continuous ambient/diffuse/specular adjustment while keys are held.

    Z/X -> ambient strength -/+
    C/V -> diffuse multiplier -/+
    B/N -> specular multiplier -/+
    """
    lighting = state.lighting
    keys = state.keys_pressed

    if glfw.KEY_Z in keys:
        lighting["ambient_strength"] = max(
            0.0, lighting["ambient_strength"] - AMBIENT_SPEED * delta_time
        )
    if glfw.KEY_X in keys:
        lighting["ambient_strength"] = min(
            1.0, lighting["ambient_strength"] + AMBIENT_SPEED * delta_time
        )

    if glfw.KEY_C in keys:
        lighting["diffuse_mult"] = max(
            0.0, lighting["diffuse_mult"] - DIFFUSE_SPEED * delta_time
        )
    if glfw.KEY_V in keys:
        lighting["diffuse_mult"] = min(
            3.0, lighting["diffuse_mult"] + DIFFUSE_SPEED * delta_time
        )

    if glfw.KEY_B in keys:
        lighting["specular_mult"] = max(
            0.0, lighting["specular_mult"] - SPECULAR_SPEED * delta_time
        )
    if glfw.KEY_N in keys:
        lighting["specular_mult"] = min(
            3.0, lighting["specular_mult"] + SPECULAR_SPEED * delta_time
        )


# TEMPORARY: interior AABB tuning controls (active while debug view, key M,
# is on). Move/resize the box live, then read the printed min/max (on key
# release) and hardcode them, replacing INTERIOR_CUBE_TRANSFORM/margin.
#
# Arrows / Page Up / Page Down -> move the box (X / Z / Y).
# J/L -> shrink/grow X size, I/K -> grow/shrink Y size, U/O -> shrink/grow Z size.
# (resizing keeps the box centered in place)
BOX_MOVE_SPEED  = 2.0
BOX_SCALE_SPEED = 2.0
BOX_MIN_SIZE    = 0.2

_BOX_KEYS = {
    glfw.KEY_LEFT, glfw.KEY_RIGHT, glfw.KEY_UP, glfw.KEY_DOWN,
    glfw.KEY_PAGE_UP, glfw.KEY_PAGE_DOWN,
    glfw.KEY_J, glfw.KEY_L, glfw.KEY_I, glfw.KEY_K, glfw.KEY_U, glfw.KEY_O,
}


def process_lantern_drift(delta_time):
    """Advance each flying lantern's slow wander: move in a straight line,
    and "ping-pong" (reflect) off the boundary of its drift radius."""
    for drift in state.lantern_drift:
        drift['offset'] += drift['dir'] * drift['speed'] * delta_time
        dist = glm.length(drift['offset'])
        if dist > drift['radius'] and dist > 0.0:
            normal = drift['offset'] / dist
            # Snap back onto the boundary before reflecting. Without this,
            # a near-radial bounce can leave the lantern just outside the
            # radius every frame, flipping 'dir' back and forth and making
            # it appear stuck in place.
            drift['offset'] = normal * drift['radius']
            drift['dir'] = glm.reflect(drift['dir'], normal)


def process_debug_box(delta_time):
    if not state.debug_view:
        return

    keys = state.keys_pressed
    move  = BOX_MOVE_SPEED * delta_time
    scale = BOX_SCALE_SPEED * delta_time

    delta = glm.vec3(0.0)
    if glfw.KEY_RIGHT in keys:
        delta.x += move
    if glfw.KEY_LEFT in keys:
        delta.x -= move
    if glfw.KEY_DOWN in keys:
        delta.z += move
    if glfw.KEY_UP in keys:
        delta.z -= move
    if glfw.KEY_PAGE_UP in keys:
        delta.y += move
    if glfw.KEY_PAGE_DOWN in keys:
        delta.y -= move
    state.interior_min += delta
    state.interior_max += delta

    def resize(axis, amount):
        size = state.interior_max[axis] - state.interior_min[axis]
        amount = max(amount, BOX_MIN_SIZE - size)  # don't shrink past BOX_MIN_SIZE
        state.interior_min[axis] -= amount / 2.0
        state.interior_max[axis] += amount / 2.0

    if glfw.KEY_L in keys:
        resize(0, scale)
    if glfw.KEY_J in keys:
        resize(0, -scale)
    if glfw.KEY_I in keys:
        resize(1, scale)
    if glfw.KEY_K in keys:
        resize(1, -scale)
    if glfw.KEY_O in keys:
        resize(2, scale)
    if glfw.KEY_U in keys:
        resize(2, -scale)
