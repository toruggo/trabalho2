import ctypes
import math
import sys
import os

import glfw
from OpenGL.GL import *
import numpy as np
import glm

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from shader_s import Shader
import geometry
import scene
import state
import input as inp
import matrizes

TEMPLE_DIR = "objects/temple"
SKYBOX_DIR = "objects/sky_78_cubemap_2k"
GRASS_DIR = "objects/grass_field"
WALL_DIR = "objects/wall"
SAKURA_DIR = "objects/sakura_tree"
FLYING_LANTERN_DIR = "objects/flying_lantern"
DRAGON_CANDLE_DIR = "objects/dragon_candle"
HANGING_LANTERN_DIR = "objects/hanging_lantern"

# (x, y, z, rotation_z_deg) in Blender (Z-up) world coordinates, from
# object_transforms.md. Position is converted via matrizes.blender_to_scene_pos
# and rotation_z maps directly onto a scene Y-rotation.
SAKURA_TRANSFORMS = [
    (-12.923817, -21.774605, 0.428387, -74.919853),
    (-12.792014, -28.013264, 0.428387, -74.919853),
    (8.428210, -35.833553, 0.428387, -74.919853),
    (10.273447, -19.885433, 0.428387, -74.919853),
    (6.934447, -41.676804, 0.428387, -243.459088),
    (-8.442527, -31.440132, 0.428387, -129.741438),
    (-11.023709, -34.164055, 0.428387, -243.459088),
    (-7.797180, -39.225277, 0.428387, -299.590866),
    (-13.301259, -39.351807, 0.428387, -351.736711),
    (7.681329, -54.128819, 0.428387, -302.282671),
    (-8.354659, -54.769199, 0.428387, -394.693601),
    (-9.980225, -42.994835, 0.428387, -408.512248),
    (-7.168436, -45.367279, 0.428387, -437.373568),
    (-14.153975, -45.455151, 0.428387, -471.710076),
    (10.668856, -39.655830, 0.428387, -383.674866),
    (13.451356, -36.543823, 0.428387, -434.551935),
    (14.622935, -40.754185, 0.428387, -435.724186),
    (6.669085, -47.096527, 0.428387, -334.651648),
    (8.047447, -58.522240, 0.428387, -358.947041),
    (10.976396, -61.231518, 0.428387, -437.560551),
    (12.074751, -55.263786, 0.428387, -437.560551),
    (15.918995, -52.920628, 0.428387, -383.636344),
    (15.150146, -59.181255, 0.428387, -383.636344),
    (-13.992884, -58.210712, 0.428387, -394.693601),
    (-9.562850, -59.418903, 0.428387, -325.652027),
    (-3.778178, -62.311241, 0.428387, -312.761465),
]
SAKURA_SCALE = 8.482910

# (x, y, z) in Blender (Z-up) world coordinates, from scene.json, for the
# flying_lantern_solo / .001 / .002 / .003 objects. flying_lantern.obj was
# exported pre-baked (geometry + rotation + scale of flying_lantern_solo
# already applied), so the other instances reuse that same mesh shifted by
# the position delta to flying_lantern_solo (rotation/scale match across all 4).
FLYING_LANTERN_TRANSFORMS = [
    (
        -0.7945289015769958,
        -35.838497161865234,
        4.637933731079102,
    ),  # flying_lantern_solo
    (
        2.002218723297119,
        -33.08412551879883,
        4.637933731079102,
    ),  # flying_lantern_solo.001
    (
        -0.49790430068969727,
        -28.973752975463867,
        4.637933731079102,
    ),  # flying_lantern_solo.002
    (
        2.150531053543091,
        -25.541379928588867,
        4.637933731079102,
    ),  # flying_lantern_solo.003
]

# Additional flying-lantern positions, scattered around the temple exterior.
# Unlike FLYING_LANTERN_TRANSFORMS above, these are already in our final
# scene-space coordinates (captured live via the temporary camera-position
# printout, key P in input.py) — no Blender->scene conversion needed.
EXTRA_LANTERN_POSITIONS = [
    (-1.44, -2.75, 68.06),
    (-1.88, 0.10, 63.23),
    (3.08, -3.24, 56.96),
    (-0.86, 1.05, 52.77),
    (13.32, -7.76, 56.76),
    (8.36, -7.54, 59.23),
    (1.80, -6.61, 68.67),
    (-17.64, 5.51, 11.88),
    (-32.84, 16.44, 4.38),
    (-27.67, 11.94, -17.54),
    (28.88, 10.30, -5.92),
    (30.50, 25.84, -19.14),
    (28.80, 2.53, -1.47),
    (13.65, 1.31, 17.34),
    (-20.20, 2.13, 18.46),
    (-38.76, 14.10, 9.81),
]

# (x, y, z) in Blender (Z-up) world coordinates, from scene.json, for the
# hanging_lantern / .001 / .002 objects. hanging_lantern.obj was exported
# pre-baked as "o hanging_lantern.001" (geometry + rotation + scale already
# applied), so the other instances reuse that same mesh shifted by the
# position delta to hanging_lantern.001 (rotation/scale match across all 3).
HANGING_LANTERN_TRANSFORMS = [
    (-0.020896494388580322, 8.019309997558594, 11.573162078857422),  # hanging_lantern
    (
        1.5413868427276611,
        11.697153091430664,
        11.573162078857422,
    ),  # hanging_lantern.001 (baked)
    (1.18292236328125, 16.908143997192383, 11.573162078857422),  # hanging_lantern.002
]
HANGING_LANTERN_ORIGIN_INDEX = 1

# World-space AABB marking the temple interior, hand-tuned with the debug
# box tool (key M + arrows/J/L/I/K/U/O) to snugly fit the interior room
# (floor to ceiling, wall to wall) — used to mask interior-only/exterior-only
# lights (req 1 / req 2).
INTERIOR_AABB_MIN = (-3.55, -2.81, -24.33)
INTERIOR_AABB_MAX = (4.40, 1.43, 5.21)

# Market stalls/props. Each mesh was exported pre-baked to one specific
# scene.json instance's world transform ("baked": position, rotation_z_deg,
# scale, all in Blender world coordinates). `targets` lists every instance
# to place using that mesh; matrizes.place_baked_instance() compensates for
# any Y-rotation / uniform-scale difference between `baked` and each target.
MARKET_OBJECTS = [
    dict(
        dir="objects/fish_tent",
        file="fish_tent.obj",
        materials=scene.FISH_TENT_MATERIALS,
        baked=(
            (5.467783451080322, -27.850482940673828, 1.637453317642212),
            0.0,
            0.0005368956481106579,
        ),
        targets=[
            (
                (5.467783451080322, -27.850482940673828, 1.637453317642212),
                0.0,
                0.0005368956481106579,
            ),  # fish_tent_a/b
            (
                (5.11183500289917, -38.65605926513672, 1.637453317642212),
                0.0,
                0.0005368956481106579,
            ),  # fish_tent_a/b.001
        ],
    ),
    dict(
        dir="objects/flag1",
        file="flag1.obj",
        materials=scene.FLAG1_MATERIALS,
        baked=(
            (4.405760288238525, -31.69893455505371, 3.0643084049224854),
            90.0,
            0.0003897630958817899,
        ),
        targets=[
            (
                (4.405760288238525, -31.69893455505371, 3.0643084049224854),
                90.0,
                0.0003897630958817899,
            ),  # flag1
            (
                (-1.8033266067504883, -24.106781005859375, 3.0643084049224854),
                90.0,
                0.0003897630958817899,
            ),  # flag1.001
        ],
    ),
    dict(
        dir="objects/food_tent",
        file="food_tent.obj",
        materials=scene.FOOD_TENT_MATERIALS,
        baked=(
            (5.220168113708496, -25.36267852783203, 1.0445088148117065),
            0.0,
            0.0004688884655479342,
        ),
        targets=[
            (
                (5.220168113708496, -25.36267852783203, 1.0445088148117065),
                0.0,
                0.0004688884655479342,
            ),  # food_tent_1
            (
                (4.814486026763916, -36.064910888671875, 1.2097200155258179),
                0.0,
                0.0004084281390532851,
            ),  # food_tent_0
        ],
    ),
    dict(
        dir="objects/meat_tent",
        file="meat_tent.obj",
        materials=scene.MEAT_TENT_MATERIALS,
        baked=(
            (-3.5610203742980957, -32.09426498413086, 1.0506778955459595),
            0.0,
            0.00042814877815544605,
        ),
        targets=[
            (
                (-3.5610203742980957, -32.09426498413086, 1.0506778955459595),
                0.0,
                0.00042814877815544605,
            ),  # meat_tent_b
        ],
    ),
    dict(
        dir="objects/spice_tent",
        file="spice_tent.obj",
        materials=scene.SPICE_TENT_MATERIALS,
        baked=(
            (-3.36627197265625, -26.63774299621582, 1.6107171773910522),
            -180.0,
            0.6224765777587891,
        ),
        targets=[
            (
                (-3.36627197265625, -26.63774299621582, 1.6107171773910522),
                -180.0,
                0.6224765777587891,
            ),  # spice_tent
            (
                (-3.457801580429077, -38.71965408325195, 1.6107171773910522),
                -180.0,
                0.6224765777587891,
            ),  # spice_tent.001
        ],
    ),
    dict(
        dir="objects/standing_umbrella",
        file="standing_umbrella.obj",
        materials=scene.STANDING_UMBRELLA_MATERIALS,
        baked=(
            (9.14824104309082, -26.97772216796875, 2.304640531539917),
            0.0,
            0.00038976300857029855,
        ),
        targets=[
            (
                (9.14824104309082, -26.97772216796875, 2.304640531539917),
                0.0,
                0.00038976300857029855,
            ),  # standing_umbrella
            (
                (13.54757022857666, -23.269926071166992, 2.304640531539917),
                0.0,
                0.00038976300857029855,
            ),  # standing_umbrella.001
        ],
    ),
    dict(
        dir="objects/tables",
        file="tables.obj",
        materials=scene.TABLES_MATERIALS,
        baked=(
            (13.589741706848145, -25.852642059326172, 0.8880937099456787),
            180.0,
            0.00047512794844806194,
        ),
        targets=[
            (
                (13.589741706848145, -25.852642059326172, 0.8880937099456787),
                180.0,
                0.00047512794844806194,
            ),  # tables.001
            (
                (9.4158296585083, -24.77208709716797, 0.8880937099456787),
                0.0,
                0.0004751279775518924,
            ),  # tables
        ],
    ),
]

# Unit cube — 36 positions that serve as cubemap direction vectors.
SKYBOX_VERTS = np.array(
    [
        -1,
        1,
        -1,
        -1,
        -1,
        -1,
        1,
        -1,
        -1,
        1,
        -1,
        -1,
        1,
        1,
        -1,
        -1,
        1,
        -1,
        -1,
        -1,
        1,
        -1,
        -1,
        -1,
        -1,
        1,
        -1,
        -1,
        1,
        -1,
        -1,
        1,
        1,
        -1,
        -1,
        1,
        1,
        -1,
        -1,
        1,
        -1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        -1,
        1,
        -1,
        -1,
        -1,
        -1,
        1,
        -1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        -1,
        1,
        -1,
        -1,
        1,
        -1,
        1,
        -1,
        1,
        1,
        -1,
        1,
        1,
        1,
        1,
        1,
        1,
        -1,
        1,
        1,
        -1,
        1,
        -1,
        -1,
        -1,
        -1,
        -1,
        -1,
        1,
        1,
        -1,
        -1,
        1,
        -1,
        -1,
        -1,
        -1,
        1,
        1,
        -1,
        1,
    ],
    dtype=np.float32,
)

# Camera-facing quad (in [-0.5, 0.5] local space) used to draw glow halos
# around lamp light sources. Billboarded in glow.vs via cameraRight/cameraUp.
GLOW_QUAD_VERTS = np.array(
    [
        -0.5,
        -0.5,
        0.5,
        -0.5,
        0.5,
        0.5,
        -0.5,
        -0.5,
        0.5,
        0.5,
        -0.5,
        0.5,
    ],
    dtype=np.float32,
)

# Glow halo appearance for the flying lanterns' bulbs (req-1 exterior lights).
LANTERN_GLOW_COLOR = (1.0, 0.7, 0.35)
LANTERN_GLOW_SIZE_FACTOR = 0.08  # fraction of `extent`

# Slow wandering animation for the flying lanterns (see state.lantern_drift).
LANTERN_DRIFT_RADIUS_FACTOR = 0.06  # fraction of `extent`
LANTERN_DRIFT_SPEED_FACTOR = 0.007  # (fraction of `extent`) per second


def set3f(loc, v):
    glUniform3f(loc, v.x, v.y, v.z)


def main():
    if not glfw.init():
        sys.exit("GLFW init failed")

    glfw.window_hint(glfw.SAMPLES, 4)
    window = glfw.create_window(1600, 900, "Trabalho 2 - Temple", None, None)
    if not window:
        glfw.terminate()
        sys.exit("Window creation failed")

    glfw.make_context_current(window)

    shader = Shader("shaders/vertex_shader.vs", "shaders/fragment_shader.fs")
    shader.use()
    prog = shader.getProgram()

    # ── Skybox shader ─────────────────────────────────────────────────────────
    sky_shader = Shader("shaders/skybox.vs", "shaders/skybox.fs")
    sky_prog = sky_shader.getProgram()
    sky_shader.use()
    glUniform1i(glGetUniformLocation(sky_prog, "skybox"), 0)

    sky_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, sky_vbo)
    glBufferData(GL_ARRAY_BUFFER, SKYBOX_VERTS.nbytes, SKYBOX_VERTS, GL_STATIC_DRAW)
    sky_pos_loc = glGetAttribLocation(sky_prog, "position")
    glEnableVertexAttribArray(sky_pos_loc)

    cubemap_tex = geometry.load_cubemap(SKYBOX_DIR)

    # ── Debug shader (light markers + interior AABB wireframe, key M) ────────
    debug_shader = Shader("shaders/debug.vs", "shaders/debug.fs")
    debug_prog = debug_shader.getProgram()
    debug_pos_loc = glGetAttribLocation(debug_prog, "position")
    glEnableVertexAttribArray(debug_pos_loc)
    debug_locs = {
        "model": glGetUniformLocation(debug_prog, "model"),
        "view": glGetUniformLocation(debug_prog, "view"),
        "projection": glGetUniformLocation(debug_prog, "projection"),
        "color": glGetUniformLocation(debug_prog, "color"),
    }

    # ── Glow shader (additive halo billboards around lamp light sources) ────
    glow_shader = Shader("shaders/glow.vs", "shaders/glow.fs")
    glow_prog = glow_shader.getProgram()
    glow_pos_loc = glGetAttribLocation(glow_prog, "position")
    glEnableVertexAttribArray(glow_pos_loc)
    glow_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, glow_vbo)
    glBufferData(
        GL_ARRAY_BUFFER, GLOW_QUAD_VERTS.nbytes, GLOW_QUAD_VERTS, GL_STATIC_DRAW
    )
    glow_locs = {
        "view": glGetUniformLocation(glow_prog, "view"),
        "projection": glGetUniformLocation(glow_prog, "projection"),
        "center": glGetUniformLocation(glow_prog, "center"),
        "cameraRight": glGetUniformLocation(glow_prog, "cameraRight"),
        "cameraUp": glGetUniformLocation(glow_prog, "cameraUp"),
        "size": glGetUniformLocation(glow_prog, "size"),
        "color": glGetUniformLocation(glow_prog, "color"),
    }

    # ── Main shader attributes ────────────────────────────────────────────────
    shader.use()
    pos_loc = glGetAttribLocation(prog, "position")
    uv_loc = glGetAttribLocation(prog, "texture_coord")
    norm_loc = glGetAttribLocation(prog, "normal")
    glEnableVertexAttribArray(pos_loc)
    glEnableVertexAttribArray(uv_loc)
    glEnableVertexAttribArray(norm_loc)

    glActiveTexture(GL_TEXTURE0)
    glUniform1i(glGetUniformLocation(prog, "samplerTexture"), 0)

    # ── Load temple ───────────────────────────────────────────────────────────
    print("Loading temple OBJ...")
    temple_objects, extent, temple_center = scene.load_temple(TEMPLE_DIR)

    # ── Load grass field (ground plane around temple/market) ────────────────
    # grass_field.obj was exported pre-baked to its true world position (in the
    # same axis convention as temple.obj), so it only needs to be shifted by
    # the same offset that recentered the temple to the origin.
    print("Loading grass field OBJ...")
    grass_pos = tuple(-c for c in temple_center)
    grass_objects = scene.load_simple_object(
        GRASS_DIR,
        "grass_field.obj",
        pos=grass_pos,
        materials=scene.GRASS_MATERIALS,
        recenter=False,
    )

    # ── Load courtyard wall (all wall segments pre-baked into one mesh) ─────
    # wall.obj was exported the same way as grass_field.obj: every wall piece
    # already sits at its true world position, so it only needs the same
    # temple-recentering offset.
    print("Loading wall OBJ...")
    wall_pos = tuple(-c for c in temple_center)
    wall_objects = scene.load_simple_object(
        WALL_DIR,
        "wall.obj",
        pos=wall_pos,
        materials=scene.WALL_MATERIALS,
        recenter=False,
    )

    # ── Load sakura trees (26 instances sharing one mesh/texture set) ───────
    # sakura_tree.obj is a small object-space asset; each instance's Blender
    # world position is converted to scene coords relative to the temple's
    # Blender-world position (so it lines up with the recentered temple).
    print("Loading sakura tree OBJ...")
    temple_center_blender = (temple_center[0], -temple_center[2], temple_center[1])
    sakura_instances = []
    for bx, by, bz, rot_z in SAKURA_TRANSFORMS:
        rel = (
            bx - temple_center_blender[0],
            by - temple_center_blender[1],
            bz - temple_center_blender[2],
        )
        pos = matrizes.blender_to_scene_pos(*rel)
        sakura_instances.append((pos, (0.0, rot_z, 0.0), (SAKURA_SCALE,) * 3))
    sakura_objects = scene.load_simple_object(
        SAKURA_DIR,
        "sakura_tree.obj",
        materials=scene.SAKURA_MATERIALS,
        instances=sakura_instances,
        pivot="base",
    )

    # ── Load flying lanterns (4 instances sharing one pre-baked mesh) ───────
    print("Loading flying lantern OBJ...")
    lantern_origin = FLYING_LANTERN_TRANSFORMS[0]
    lantern_instances = []
    for bx, by, bz in FLYING_LANTERN_TRANSFORMS:
        delta = (bx - lantern_origin[0], by - lantern_origin[1], bz - lantern_origin[2])
        delta_ours = matrizes.blender_to_scene_pos(*delta)
        pos = tuple(d - c for d, c in zip(delta_ours, temple_center))
        lantern_instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))
    for pos in EXTRA_LANTERN_POSITIONS:
        lantern_instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    assert len(lantern_instances) == len(state.lighting["lantern_lights"]) == len(state.lantern_drift), (
        "lantern_instances count must match state.NUM_LANTERNS"
    )

    # The mesh's own raw bbox center sits roughly at the lantern's glow —
    # used as light_offset so each instance's light tracks its own copy.
    _, _, lantern_glow_offset = geometry.load_obj(
        os.path.join(FLYING_LANTERN_DIR, "flying_lantern.obj"), recenter=False
    )
    flying_lantern_objects = scene.load_simple_object(
        FLYING_LANTERN_DIR,
        "flying_lantern.obj",
        materials=scene.FLYING_LANTERN_MATERIALS,
        instances=lantern_instances,
        recenter=False,
        light_offset=lantern_glow_offset,
        light_refs=state.lighting["lantern_lights"],
    )

    # One SceneObject per instance is enough to compute that instance's
    # light position (model + light_offset are shared across its parts).
    flying_lantern_n_parts = len(flying_lantern_objects) // len(lantern_instances)
    for i, lantern_obj in enumerate(flying_lantern_objects[::flying_lantern_n_parts]):
        state.lighting["lantern_lights"][i]["pos"] = matrizes.light_world_pos(
            lantern_obj
        )

    # Wandering animation: each lantern drifts within a small radius of its
    # placed position, in a straight line that "ping-pongs" off the boundary.
    # Each starts at a different random point within that radius (instead of
    # all starting at the center), so they're out of phase from the start.
    for i, (inst_pos, _, _) in enumerate(lantern_instances):
        drift = state.lantern_drift[i]
        drift["base"] = glm.vec3(*inst_pos)
        drift["radius"] = extent * LANTERN_DRIFT_RADIUS_FACTOR
        drift["speed"] = extent * LANTERN_DRIFT_SPEED_FACTOR
        drift["offset"] = state.random_point_in_sphere(drift["radius"])

    # ── Load dragon candle (single pre-baked mesh, "o dragon_candles.002") ──
    # int_light_a (req 2) is carried by this object — light_offset is the
    # mesh's own raw bbox center, i.e. roughly the candle flame.
    print("Loading dragon candle OBJ...")
    dragon_candle_pos = tuple(-c for c in temple_center)
    _, _, dragon_candle_glow_offset = geometry.load_obj(
        os.path.join(DRAGON_CANDLE_DIR, "dragon_candle.obj"), recenter=False
    )
    dragon_candle_objects = scene.load_simple_object(
        DRAGON_CANDLE_DIR,
        "dragon_candle.obj",
        pos=dragon_candle_pos,
        materials=scene.DRAGON_CANDLE_MATERIALS,
        recenter=False,
        light_offset=dragon_candle_glow_offset,
        light_refs=[state.lighting["int_light_a"]],
    )
    state.lighting["int_light_a"]["pos"] = matrizes.light_world_pos(
        dragon_candle_objects[0]
    )

    # ── Load hanging lanterns (3 instances sharing one pre-baked mesh) ──────
    # int_light_b (req 2) is carried by these objects — each of the 3
    # instances emits its own copy of the same-colored light (toggled
    # together), light_offset is the mesh's own raw bbox center.
    print("Loading hanging lantern OBJ...")
    hanging_origin = HANGING_LANTERN_TRANSFORMS[HANGING_LANTERN_ORIGIN_INDEX]
    hanging_instances = []
    for bx, by, bz in HANGING_LANTERN_TRANSFORMS:
        delta = (bx - hanging_origin[0], by - hanging_origin[1], bz - hanging_origin[2])
        delta_ours = matrizes.blender_to_scene_pos(*delta)
        pos = tuple(d - c for d, c in zip(delta_ours, temple_center))
        hanging_instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))
    _, _, hanging_lantern_glow_offset = geometry.load_obj(
        os.path.join(HANGING_LANTERN_DIR, "hanging_lantern.obj"), recenter=False
    )
    hanging_lantern_objects = scene.load_simple_object(
        HANGING_LANTERN_DIR,
        "hanging_lantern.obj",
        materials=scene.HANGING_LANTERN_MATERIALS,
        instances=hanging_instances,
        recenter=False,
        light_offset=hanging_lantern_glow_offset,
        light_refs=[state.lighting["int_light_b"]] * len(hanging_instances),
    )

    # One SceneObject per instance is enough to compute that instance's
    # light position (model + light_offset are shared across its parts).
    n_parts = len(hanging_lantern_objects) // len(hanging_instances)
    for i, hanging_obj in enumerate(hanging_lantern_objects[::n_parts]):
        state.lighting["int_light_b"]["positions"][i] = matrizes.light_world_pos(
            hanging_obj
        )

    # ── Load market stalls/props (each a pre-baked mesh, 1-2 instances) ─────
    print("Loading market objects...")
    market_objects = []
    for spec in MARKET_OBJECTS:
        baked_pos, baked_rot, baked_scale = spec["baked"]
        instances = [
            matrizes.place_baked_instance(
                baked_pos, baked_rot, t_pos, t_rot, baked_scale, t_scale, temple_center
            )
            for t_pos, t_rot, t_scale in spec["targets"]
        ]
        market_objects += scene.load_simple_object(
            spec["dir"],
            spec["file"],
            materials=spec["materials"],
            instances=instances,
            recenter=False,
        )

    scene_objects = (
        temple_objects
        + grass_objects
        + wall_objects
        + sakura_objects
        + flying_lantern_objects
        + dragon_candle_objects
        + hanging_lantern_objects
        + market_objects
    )

    # Translucent parts (e.g. paper lantern shells) are drawn in a separate
    # pass, after everything opaque, with blending on and depth writes off.
    opaque_objects = [o for o in scene_objects if o.alpha >= 1.0]
    translucent_objects = [o for o in scene_objects if o.alpha < 1.0]

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

    # ── Lighting setup ────────────────────────────────────────────────────────
    # Exterior lights (req 1) — one per flying lantern, positions already set
    # above via matrizes.light_world_pos(lantern_obj).

    # Interior lights (req 2) — positions already set above via
    # matrizes.light_world_pos(dragon_candle_objects[0] / hanging_obj_i).

    state.interior_min = glm.vec3(*INTERIOR_AABB_MIN)
    state.interior_max = glm.vec3(*INTERIOR_AABB_MAX)

    glfw.set_cursor_pos_callback(window, inp.mouse_event)
    glfw.set_key_callback(window, inp.key_event)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # ── Cache uniform locations ──────────────────────────────────────────────
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
            glGetUniformLocation(prog, f"lanternOn[{i}]") for i in range(state.NUM_LANTERNS)
        ],
        "lanternPos": [
            glGetUniformLocation(prog, f"lanternPos[{i}]") for i in range(state.NUM_LANTERNS)
        ],
        "lanternColor": [
            glGetUniformLocation(prog, f"lanternColor[{i}]") for i in range(state.NUM_LANTERNS)
        ],
        "intLightAOn": glGetUniformLocation(prog, "intLightAOn"),
        "intLightAPos": glGetUniformLocation(prog, "intLightAPos"),
        "intLightAColor": glGetUniformLocation(prog, "intLightAColor"),
        "intLightBOn": glGetUniformLocation(prog, "intLightBOn"),
        "intLightBPos": [
            glGetUniformLocation(prog, f"intLightB{i+1}Pos") for i in range(3)
        ],
        "intLightBColor": glGetUniformLocation(prog, "intLightBColor"),
    }

    projection = glm.perspective(glm.radians(45.0), 1600.0 / 900.0, 0.1, cam_dist * 4)
    glUniformMatrix4fv(locs["projection"], 1, GL_FALSE, glm.value_ptr(projection))

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
        inp.process_lantern_drift(delta_time)

        # Apply each lantern's current drift offset to its instance's model
        # matrix (pure translation, so the normal matrix stays unchanged) and
        # keep its light/glow position in sync.
        for i in range(len(lantern_instances)):
            drift = state.lantern_drift[i]
            model = glm.translate(glm.mat4(1.0), drift["base"] + drift["offset"])
            for obj in flying_lantern_objects[
                i * flying_lantern_n_parts : (i + 1) * flying_lantern_n_parts
            ]:
                obj.model = model
            state.lighting["lantern_lights"][i]["pos"] = matrizes.light_world_pos(
                flying_lantern_objects[i * flying_lantern_n_parts]
            )

        cam = state.camera
        view = glm.lookAt(cam["pos"], cam["pos"] + cam["front"], cam["up"])

        glClearColor(0.12, 0.12, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Wireframe view (key T): draw the whole scene with GL_LINE polygon
        # mode instead of GL_FILL.
        scene_polygon_mode = GL_LINE if state.wireframe_view else GL_FILL
        glPolygonMode(GL_FRONT_AND_BACK, scene_polygon_mode)

        # ── Temple ────────────────────────────────────────────────────────────
        shader.use()
        glUniformMatrix4fv(locs["view"], 1, GL_FALSE, glm.value_ptr(view))
        set3f(locs["viewPos"], cam["pos"])

        lighting = state.lighting
        glUniform1i(locs["ambientOn"], int(lighting["ambient_on"]))
        glUniform1f(locs["ambientStrength"], lighting["ambient_strength"])
        glUniform3f(locs["ambientColor"], *lighting["ambient_color"])
        glUniform1f(locs["diffuseMult"], lighting["diffuse_mult"])
        glUniform1f(locs["specularMult"], lighting["specular_mult"])
        set3f(locs["interiorMin"], state.interior_min)
        set3f(locs["interiorMax"], state.interior_max)

        for i, lantern in enumerate(lighting["lantern_lights"]):
            glUniform1i(locs["lanternOn"][i], int(lantern["on"]))
            set3f(locs["lanternPos"][i], lantern["pos"])
            glUniform3f(locs["lanternColor"][i], *lantern["color"])

        ia = lighting["int_light_a"]
        glUniform1i(locs["intLightAOn"], int(ia["on"]))
        set3f(locs["intLightAPos"], ia["pos"])
        glUniform3f(locs["intLightAColor"], *ia["color"])

        ib = lighting["int_light_b"]
        glUniform1i(locs["intLightBOn"], int(ib["on"]))
        for i, pos in enumerate(ib["positions"]):
            set3f(locs["intLightBPos"][i], pos)
        glUniform3f(locs["intLightBColor"], *ib["color"])

        scene.draw_objects(locs, opaque_objects, pos_loc, uv_loc, norm_loc)

        # ── Debug view (key M): interior AABB wireframe ───────────────────────
        # Light markers were dropped now that the lamp geometry itself glows
        # (Ke/emissiveOn) and acts as the visible light source.
        if state.debug_view:
            debug_shader.use()
            glUniformMatrix4fv(debug_locs["view"], 1, GL_FALSE, glm.value_ptr(view))
            glUniformMatrix4fv(
                debug_locs["projection"], 1, GL_FALSE, glm.value_ptr(projection)
            )
            glBindBuffer(GL_ARRAY_BUFFER, sky_vbo)
            glVertexAttribPointer(
                debug_pos_loc, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0)
            )

            def draw_debug_cube(center, half_extent, color):
                m = glm.translate(glm.mat4(1.0), center)
                m = glm.scale(
                    m,
                    (
                        half_extent
                        if isinstance(half_extent, glm.vec3)
                        else glm.vec3(half_extent)
                    ),
                )
                glUniformMatrix4fv(debug_locs["model"], 1, GL_FALSE, glm.value_ptr(m))
                glUniform3f(debug_locs["color"], *color)
                glDrawArrays(GL_TRIANGLES, 0, 36)

            # Interior AABB wireframe.
            aabb_center = (state.interior_min + state.interior_max) * 0.5
            aabb_half = (state.interior_max - state.interior_min) * 0.5
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            draw_debug_cube(aabb_center, aabb_half, (1.0, 1.0, 0.0))
            glPolygonMode(GL_FRONT_AND_BACK, scene_polygon_mode)

        # ── Skybox (drawn last; xyww trick keeps it at depth 1.0) ─────────────
        glDepthFunc(GL_LEQUAL)
        sky_shader.use()
        sky_view = glm.mat4(glm.mat3(view))  # strip translation
        glUniformMatrix4fv(
            glGetUniformLocation(sky_prog, "view"), 1, GL_FALSE, glm.value_ptr(sky_view)
        )
        glUniformMatrix4fv(
            glGetUniformLocation(sky_prog, "projection"),
            1,
            GL_FALSE,
            glm.value_ptr(projection),
        )
        glBindBuffer(GL_ARRAY_BUFFER, sky_vbo)
        glVertexAttribPointer(
            sky_pos_loc, 3, GL_FLOAT, GL_FALSE, 12, ctypes.c_void_p(0)
        )
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_CUBE_MAP, cubemap_tex)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glDepthFunc(GL_LESS)

        # Translucent lantern shells: drawn after the skybox so they blend
        # over it correctly (depth writes off, depth test on).
        shader.use()
        glEnable(GL_BLEND)
        glDepthMask(GL_FALSE)
        scene.draw_objects(locs, translucent_objects, pos_loc, uv_loc, norm_loc)
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

        # ── Glow halos: additive billboards over each lit flying lantern ─────
        glow_shader.use()
        glUniformMatrix4fv(glow_locs["view"], 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(
            glow_locs["projection"], 1, GL_FALSE, glm.value_ptr(projection)
        )
        cam_right = glm.normalize(glm.cross(cam["front"], cam["up"]))
        cam_up = glm.cross(cam_right, cam["front"])
        set3f(glow_locs["cameraRight"], cam_right)
        set3f(glow_locs["cameraUp"], cam_up)
        glUniform3f(glow_locs["color"], *LANTERN_GLOW_COLOR)
        glUniform1f(glow_locs["size"], extent * LANTERN_GLOW_SIZE_FACTOR)
        glBindBuffer(GL_ARRAY_BUFFER, glow_vbo)
        glVertexAttribPointer(
            glow_pos_loc, 2, GL_FLOAT, GL_FALSE, 8, ctypes.c_void_p(0)
        )

        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
        glDepthMask(GL_FALSE)
        for lantern in lighting["lantern_lights"]:
            if lantern["on"]:
                set3f(glow_locs["center"], lantern["pos"])
                glDrawArrays(GL_TRIANGLES, 0, 6)
        glDepthMask(GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_BLEND)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
