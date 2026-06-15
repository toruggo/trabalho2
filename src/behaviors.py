"""
Comportamentos de animação por objeto, avançados uma vez por frame.

O loop em main chama update em cada behavior depois de processar input.
Aqui ficam utilitários de sorteio e o DriftBehavior das lanternas voadoras.
"""

import random

import glm


def _random_drift_dir():
    """Vetor unitário aleatório em 3D para a direção inicial da deriva."""
    d = glm.vec3(
        random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)
    )
    return glm.normalize(d)


def random_point_in_sphere(radius):
    """Ponto aleatório uniforme dentro da esfera de raio dado, por rejeição."""
    while True:
        p = glm.vec3(
            random.uniform(-1.0, 1.0),
            random.uniform(-1.0, 1.0),
            random.uniform(-1.0, 1.0),
        )
        if glm.length(p) <= 1.0:
            return p * radius


class DriftBehavior:
    """Deriva lenta em linha reta a partir de base, refletindo na borda de uma esfera.

    O centro da esfera é base e o raio é radius. A cada frame soma speed na
    direção dir. Ao ultrapassar o raio, reflete a direção com reflect e mantém
    o offset na superfície da esfera. O offset inicial é aleatório dentro da
    esfera para várias lanternas não ficarem sincronizadas.

    Atualiza a matriz modelo de todos os SceneObject em objects, que compartilham
    o mesmo deslocamento por instância, e sincroniza light.positions zero com
    a posição mundial do ponto de luz usando light_offset do primeiro objeto.
    """

    def __init__(self, objects, light, base, radius, speed):
        self.objects = objects
        self.light = light
        self.light_offset = objects[0].light_offset
        self.base = base
        self.radius = radius
        self.speed = speed
        self.dir = _random_drift_dir()
        self.offset = random_point_in_sphere(radius)
        self._apply()

    def update(self, delta_time):
        self.offset += self.dir * self.speed * delta_time
        dist = glm.length(self.offset)
        if dist > self.radius and dist > 0.0:
            normal = self.offset / dist
            # Recoloca o ponto exatamente na casca antes de refletir. Sem isso,
            # um quase tangente pode ficar alternando fora e dentro do raio a
            # cada frame e a lanterna parece travada.
            self.offset = normal * self.radius
            self.dir = glm.reflect(self.dir, normal)
        self._apply()

    def _apply(self):
        """Aplica translação base mais offset na malha e na posição da luz pontual."""
        model = glm.translate(glm.mat4(1.0), self.base + self.offset)
        for obj in self.objects:
            obj.model = model
        self.light.positions[0] = glm.vec3(model * glm.vec4(self.light_offset, 1.0))
