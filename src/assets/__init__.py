"""Per-asset modules: each bundles one object family's OBJ path, material
spec, placement data, and a build(ctx) -> AssetResult function used by
scene_builder to assemble the full scene."""

from dataclasses import dataclass, field

from lighting import LightingRig


@dataclass
class AssetContext:
    """Shared inputs every asset's build() needs to place itself relative to
    the (already-loaded, recentered) temple and to wire up its lights."""

    temple_center: tuple
    extent: float
    rig: LightingRig


@dataclass
class AssetResult:
    objects: list = field(default_factory=list)
    behaviors: list = field(default_factory=list)
