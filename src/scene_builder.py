"""Assembles the full scene: loads the temple first (it defines the
recentering origin and overall scale), then every other asset relative to it,
collecting their objects/behaviors into one SceneData."""

from dataclasses import dataclass

from assets import AssetContext, flying_lantern, grass, hanging_lantern, market, mountain_range, sakura, temple, wall, dragon_candle
from lighting import LightingRig

# World-space AABB marking the temple interior, hand-tuned with the debug
# box tool (key M + arrows/J/L/I/K/U/O) to snugly fit the interior room
# (floor to ceiling, wall to wall) — used to mask interior-only/exterior-only
# lights (req 1 / req 2).
INTERIOR_AABB_MIN = (-3.55, -2.81, -24.33)
INTERIOR_AABB_MAX = (4.40, 1.43, 5.21)


@dataclass
class SceneData:
    objects: list
    opaque_objects: list
    translucent_objects: list
    behaviors: list
    extent: float
    temple_center: tuple
    glow_color: tuple
    glow_size: float


def build_scene(rig: LightingRig) -> SceneData:
    print("Loading temple OBJ...")
    temple_objects, extent, temple_center = temple.build()

    ctx = AssetContext(temple_center=temple_center, extent=extent, rig=rig)

    print("Loading grass field OBJ...")
    grass_result = grass.build(ctx)
    print("Loading wall OBJ...")
    wall_result = wall.build(ctx)
    print("Loading sakura tree OBJ...")
    sakura_result = sakura.build(ctx)
    print("Loading flying lantern OBJ...")
    flying_lantern_result = flying_lantern.build(ctx)
    print("Loading dragon candle OBJ...")
    dragon_candle_result = dragon_candle.build(ctx)
    print("Loading hanging lantern OBJ...")
    hanging_lantern_result = hanging_lantern.build(ctx)
    print("Loading market objects...")
    market_result = market.build(ctx)
    print("Loading mountain range OBJ...")
    mountain_range_result = mountain_range.build(ctx)

    results = [
        grass_result,
        wall_result,
        sakura_result,
        flying_lantern_result,
        dragon_candle_result,
        hanging_lantern_result,
        market_result,
        mountain_range_result,
    ]

    objects = temple_objects + [obj for r in results for obj in r.objects]
    behaviors = [b for r in results for b in r.behaviors]

    # Translucent parts (e.g. paper lantern shells) are drawn in a separate
    # pass, after everything opaque, with blending on and depth writes off.
    opaque_objects = [o for o in objects if o.alpha >= 1.0]
    translucent_objects = [o for o in objects if o.alpha < 1.0]

    return SceneData(
        objects=objects,
        opaque_objects=opaque_objects,
        translucent_objects=translucent_objects,
        behaviors=behaviors,
        extent=extent,
        temple_center=temple_center,
        glow_color=flying_lantern.GLOW_COLOR,
        glow_size=extent * flying_lantern.GLOW_SIZE_FACTOR,
    )
