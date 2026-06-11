"""Generic per-object animation behaviors, advanced once per frame via
update(delta_time) (see main.py's render loop)."""

import random

import glm


def _random_drift_dir():
    d = glm.vec3(
        random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)
    )
    return glm.normalize(d)


def random_point_in_sphere(radius):
    """Uniformly sample a point within a sphere of the given radius (rejection sampling)."""
    while True:
        p = glm.vec3(
            random.uniform(-1.0, 1.0),
            random.uniform(-1.0, 1.0),
            random.uniform(-1.0, 1.0),
        )
        if glm.length(p) <= 1.0:
            return p * radius


class DriftBehavior:
    """Slow wandering animation: drifts in a straight line from `base`,
    "ping-ponging" (reflecting) off the boundary of a sphere of `radius`
    around `base`. Starts at a random point within that sphere (and with a
    random direction), so multiple instances are out of phase from the start.

    Applies the resulting translation to every SceneObject in `objects`
    (they share one model matrix, e.g. the parts of one flying lantern
    instance) and keeps `light`'s first position in sync, using the first
    object's `light_offset`.
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
            # Snap back onto the boundary before reflecting. Without this, a
            # near-radial bounce can leave the object just outside the radius
            # every frame, flipping `dir` back and forth and making it appear
            # stuck in place.
            self.offset = normal * self.radius
            self.dir = glm.reflect(self.dir, normal)
        self._apply()

    def _apply(self):
        model = glm.translate(glm.mat4(1.0), self.base + self.offset)
        for obj in self.objects:
            obj.model = model
        self.light.positions[0] = glm.vec3(model * glm.vec4(self.light_offset, 1.0))
