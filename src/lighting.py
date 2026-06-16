"""
Sistema de Iluminação - Projeto 3

Define a estrutura de 3 tipos de fonte de luz:
  1. Ambiente (ambient): Luz global, afeta toda a cena
  2. Lanternas Exteriores (lantern_lights): 20 fontes pontuais que cercam o templo
     - Afetam APENAS objetos FORA do interior
     - Animadas com drift (movimento lento)
     - Podem ser ligadas/desligadas (tecla 2)
  3. Luzes Interiores (int_light_a + int_light_b):
     - int_light_a: Dragon candle (candela de dragão dentro do templo)
     - int_light_b: 3 hanging lanterns (lanternas penduradas em 3 posições)
     - Afetam APENAS objetos DENTRO do interior
     - Cores diferentes: dragon=alaranjada, hanging=avermelhada
     - Podem ser ligadas/desligadas (teclas 3 e 4)

Cada luz possui:
  - on (bool): estado ligado/desligado
  - color (R, G, B): cor da luz (pode ser > 1.0 para brilho)
  - positions (list): posição(ões) da luz no espaço 3D
"""

from dataclasses import dataclass, field

import glm

# Número total de lanternas voadoras
# Deve ser igual a NUM_LANTERNS em shaders/fragment_shader.fs e em assets/flying_lantern.py
NUM_LANTERNS = 20


@dataclass
class Light:
    """Uma fonte de luz pontual no espaço 3D."""

    on: bool
    color: tuple
    positions: list = field(default_factory=lambda: [glm.vec3(0.0)])


@dataclass
class LightingRig:
    """Configuração completa de iluminação para a cena."""

    # Iluminação Ambiente (afeta toda a cena)
    ambient_on: bool  # Ligado/desligado (tecla 1)
    ambient_strength: float  # Intensidade 0.0-1.0, ajustável com Z/X
    ambient_color: tuple  # Cor da luz ambiente, normalmente branco (1.0, 1.0, 1.0)

    # Multiplicadores de Material (ajustáveis em tempo real)
    diffuse_mult: float  # Multiplicador reflexão difusa (C/V), padrão 1.0
    specular_mult: float  # Multiplicador reflexão especular (B/N), padrão 1.0

    # Luzes Exteriores: Flying Lanterns
    lantern_lights: list  # 20 luzes pontuais que cercam o templo (tecla 2)

    # Luzes Interiores: Dragon Candle
    int_light_a: Light  # Candela dentro do templo (tecla 3)

    # Luzes Interiores: Hanging Lanterns
    int_light_b: Light  # 3 lanternas penduradas (tecla 4)


def make_default_rig() -> LightingRig:
    """Cria a configuração padrão de iluminação."""
    return LightingRig(
        # Luz ambiente: ligada por padrão, intensidade 0.15 (30% de brilho base)
        ambient_on=True,
        ambient_strength=0.15,
        ambient_color=(1.0, 1.0, 1.0),  # Branco puro
        # Reflexões padrão: 100% difusa, 100% especular
        diffuse_mult=1.0,
        specular_mult=1.0,
        # 20 lanternas voadoras: luz quente (alaranjada) Ke=(1.0, 0.85, 0.6)
        lantern_lights=[
            Light(on=True, color=(1.0, 0.85, 0.6)) for _ in range(NUM_LANTERNS)
        ],
        # Dragon candle: luz quente alaranjada e intensa
        int_light_a=Light(on=True, color=(2.0, 0.55, 0.2)),
        # Hanging lanterns (3 posições): luz avermelhada quente
        int_light_b=Light(
            on=True,
            color=(1.5, 0.3, 0.1),
            positions=[
                glm.vec3(0.0) for _ in range(3)
            ],  # Será preenchido em scene_builder
        ),
    )
