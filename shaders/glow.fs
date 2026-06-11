varying vec2 localPos;

uniform vec3 color;

void main() {
    // Soft radial falloff: bright at the center, fading to nothing at the
    // edge of the billboard. Drawn with additive blending to look like a
    // glow halo around the lamp.
    float d = length(localPos) * 2.0;
    float falloff = pow(clamp(1.0 - d, 0.0, 1.0), 2.0);
    if (falloff <= 0.0) discard;
    gl_FragColor = vec4(color * falloff, falloff);
}
