"""Cada módulo de asset: pasta do OBJ, materiais, posicionamento e build(ctx) -> AssetResult
usado pelo scene_builder."""

from dataclasses import dataclass, field

from lighting import LightingRig


@dataclass
class AssetContext:
    """Dados comuns ao build(): centro do templo já recenterado e rig de luzes."""

    temple_center: tuple
    extent: float
    rig: LightingRig


@dataclass
class AssetResult:
    objects: list = field(default_factory=list)
    behaviors: list = field(default_factory=list)
