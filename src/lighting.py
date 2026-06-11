"""Lighting model: typed Light entries plus the full LightingRig, mirroring
the 3 light "shapes" wired into shaders/fragment_shader.fs:
  - lantern_lights: NUM_LANTERNS independent lights (lanternOn/Pos/Color[i]),
    each with one position — exterior lights (req 1).
  - int_light_a: one light, one position — interior light (req 2).
  - int_light_b: one on/color shared across 3 positions (one per hanging
    lantern instance) — interior light (req 2).
"""

from dataclasses import dataclass, field

import glm

# Total number of flying-lantern point lights (4 original + 16 added around
# the temple exterior). Must match NUM_LANTERNS in fragment_shader.fs and the
# number of flying lantern instances in assets/flying_lantern.py.
NUM_LANTERNS = 20


@dataclass
class Light:
    on: bool
    color: tuple
    positions: list = field(default_factory=lambda: [glm.vec3(0.0)])


@dataclass
class LightingRig:
    ambient_on: bool
    ambient_strength: float
    ambient_color: tuple
    diffuse_mult: float
    specular_mult: float
    lantern_lights: list
    int_light_a: Light
    int_light_b: Light


def make_default_rig() -> LightingRig:
    return LightingRig(
        ambient_on=True,
        ambient_strength=0.15,
        ambient_color=(1.0, 1.0, 1.0),
        diffuse_mult=1.0,
        specular_mult=1.0,
        lantern_lights=[
            Light(on=True, color=(1.0, 0.85, 0.6)) for _ in range(NUM_LANTERNS)
        ],
        int_light_a=Light(on=True, color=(2.0, 0.55, 0.2)),
        int_light_b=Light(
            on=True,
            color=(1.5, 0.3, 0.1),
            positions=[glm.vec3(0.0) for _ in range(3)],
        ),
    )
