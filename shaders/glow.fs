varying vec2 localPos;

uniform vec3 color;
uniform int debugGlow;

void main() {
    if (debugGlow == 1) {
        gl_FragColor = vec4(1.0, 1.0, 0.0, 1.0);
        return;
    }
    float d = length(localPos) * 2.0;
    float falloff = pow(clamp(1.0 - d, 0.0, 1.0), 2.0);
    if (falloff <= 0.0) discard;
    gl_FragColor = vec4(color * falloff, falloff);
}
