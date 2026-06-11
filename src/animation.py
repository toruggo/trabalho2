import random

import glm

# Total number of flying-lantern point lights (4 original + 16 added around
# the temple exterior). Must match NUM_LANTERNS in fragment_shader.fs and the
# number of instances in main.py's lantern_instances.
NUM_LANTERNS = 20


# Slow wandering animation for the flying lanterns: each lantern drifts in a
# random straight line from its 'base' position, then "ping-pongs" (reflects)
# off the boundary of a sphere of 'radius' around 'base'. Each lantern starts
# at a different random point within that sphere (and with a different random
# direction), so they're out of phase with each other from the start.
# 'base'/'radius'/'speed'/'offset' are filled in by main.py once `extent` is
# known.
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


lantern_drift = [
    {
        "base": glm.vec3(0.0),
        "offset": glm.vec3(0.0),
        "dir": _random_drift_dir(),
        "speed": 0.0,
        "radius": 0.0,
    }
    for _ in range(NUM_LANTERNS)
]


def process_lantern_drift(delta_time):
    """Advance each flying lantern's slow wander: move in a straight line,
    and "ping-pong" (reflect) off the boundary of its drift radius."""
    for drift in lantern_drift:
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
