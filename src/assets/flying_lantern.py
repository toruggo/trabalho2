"""
Lanternas voadoras ao redor do templo

20 instâncias de lanternas que voam ao redor do templo:
- Cada lanterna é uma fonte de luz pontual (lanternOn/Pos/Color[i])
- Afetam APENAS objetos fora da caixa interior (exterior)
- Animadas com comportamento DriftBehavior (movimento lento)
- Quando a lanterna está desligada (tecla 2), sua luz e brilho (Ke) se apagam
- Ao descer para dentro do interior, deixam de iluminar

Estrutura:
- 4 lanternas do Blender (flying_lantern_solo a .003)
- 16 lanternas adicionais espalhadas ao redor do exterior do templo
- Total: 20 lanternas compartilhando a mesma malha 3D (otimização)
"""

import os

import glm

import geometry
import matrizes
import scene
from assets import AssetContext, AssetResult
from behaviors import DriftBehavior

FLYING_LANTERN_DIR = "objects/flying_lantern"

FLYING_LANTERN_MATERIALS = {
    # Parâmetros de material definidos manualmente no código, não lidos do mtl

    # Corpo da lanterna (papel/madeira) - translúcido
    # Deixa o brilho interno atravessar, como luz através do papel
    "default": dict(
        texture="Image_0.002.png",
        Ka=(0.65, 0.55, 0.40),  # Reflexão ambiente (fraca, papel matte)
        Kd=(0.65, 0.55, 0.40),  # Reflexão difusa (cor quente)
        Ks=(0.05, 0.05, 0.05),  # Reflexão especular (quase nenhuma, papel matte)
        shininess=4.0,  # Brilho baixo (matte)
        alpha=0.55,  # Transparência 55% (deixa luz passar)
    ),

    # Janela brilhante (Ke = emissão) — a própria "lâmpada"
    # Ke segue emissiveOn para apagar o brilho junto com o interruptor da luz
    ".001": dict(
        texture="Image_5.001.png",
        Ka=(0.9, 0.7, 0.4),  # Reflexão ambiente (brilhante, papel fino)
        Kd=(0.9, 0.7, 0.4),  # Reflexão difusa (brilho quente)
        Ks=(0.0, 0.0, 0.0),  # Sem especular (superfície fosca)
        shininess=1.0,
        # Ke > 1.0 deixa o brilho forte; no fragment, Ke * texColor concentra nas áreas claras.
        Ke=(2.5, 1.8, 0.8),  # Cor quente: alaranja-avermelhada
    ),
}

# Posições das 4 primeiras lanternas (do Blender, coordenadas Z-up)
# flying_lantern.obj foi exportado pré-assado (geometria + rotação + escala já aplicadas)
# As outras 3 instâncias reutilizam a mesma malha deslocadas pela posição delta
# A rotação e escala são iguais em todas (só mudam as posições)
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

# Posições das 16 lanternas adicionais espalhadas ao redor do exterior do templo
# Essas coordenadas estão no espaço final da cena (já convertidas)
# Capturadas com tecla P (camera position) para placement interativo
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

# Halo de brilho ao redor de cada lanterna (billboard aditivo, desenhado em render_passes)
GLOW_COLOR = (1.0, 0.7, 0.35)  # Cor quente (alaranjada)
GLOW_SIZE_FACTOR = 0.08  # Tamanho = 8% do tamanho total da cena

# Animação de drift com translação suave ao longo do tempo
# Cada lanterna voa dentro de um pequeno raio da sua posição base
# Segue uma linha reta que "ping-ponga" (rebate) nas bordas da esfera
DRIFT_RADIUS_FACTOR = 0.06  # Raio = 6% do tamanho total da cena
DRIFT_SPEED_FACTOR = 0.007  # Velocidade = 0.7% do tamanho da cena por segundo


def build(ctx: AssetContext) -> AssetResult:
    """Carrega e configura as 20 instâncias de lanternas voadoras."""

    # Cria lista de instâncias (posição, rotação, escala) para todas as 20 lanternas
    lantern_origin = FLYING_LANTERN_TRANSFORMS[0]
    instances = []

    # Processa as 4 lanternas originais do Blender (convertendo de Z-up para Y-up)
    for bx, by, bz in FLYING_LANTERN_TRANSFORMS:
        delta = (bx - lantern_origin[0], by - lantern_origin[1], bz - lantern_origin[2])
        delta_ours = matrizes.blender_to_scene_pos(*delta)
        pos = tuple(d - c for d, c in zip(delta_ours, ctx.temple_center))
        instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    # Adiciona as 16 lanternas extras (já em coordenadas da cena)
    for pos in EXTRA_LANTERN_POSITIONS:
        instances.append((pos, (0.0, 0.0, 0.0), (1.0, 1.0, 1.0)))

    # Verifica que temos exatamente 20 lanternas para combinar com lighting.NUM_LANTERNS
    assert len(instances) == len(ctx.rig.lantern_lights), (
        "número de instâncias de lanternas deve ser = lighting.NUM_LANTERNS"
    )

    # A posição do centro da malha (raw bbox center) aproxima-se do brilho da lanterna
    # Usamos isso como light_offset para que cada instância da lanterna rastreie sua posição de luz
    _, _, lantern_glow_offset = geometry.load_obj(
        os.path.join(FLYING_LANTERN_DIR, "flying_lantern.obj"), recenter=False
    )

    # Carrega as 20 objetos 3D, compartilhando a mesma malha de lanterna
    # Cada instância aponta para a sua Light para o emissivo acompanhar o interruptor
    objects = scene.load_simple_object(
        FLYING_LANTERN_DIR,
        "flying_lantern.obj",
        materials=FLYING_LANTERN_MATERIALS,
        instances=instances,
        recenter=False,
        light_offset=lantern_glow_offset,
        lights=ctx.rig.lantern_lights,  # Gera a relação objeto <-> luz
    )

    # A malha tem 2 partes (corpo opaco + janela brilhante)
    # n_parts = objetos por instância
    n_parts = len(objects) // len(instances)

    # Cria comportamentos de drift para cada lanterna
    behaviors = []
    for i, (inst_pos, _, _) in enumerate(instances):
        behaviors.append(
            DriftBehavior(
                objects=objects[i * n_parts : (i + 1) * n_parts],  # Partes dessa instância
                light=ctx.rig.lantern_lights[i],  # Luz associada
                base=glm.vec3(*inst_pos),  # Posição base (centro do raio de drift)
                radius=ctx.extent * DRIFT_RADIUS_FACTOR,  # Quão longe pode derivar
                speed=ctx.extent * DRIFT_SPEED_FACTOR,  # Velocidade do drift
            )
        )

    return AssetResult(objects=objects, behaviors=behaviors)
