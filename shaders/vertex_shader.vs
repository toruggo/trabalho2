attribute vec3 position;
attribute vec2 texture_coord;
attribute vec3 normal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;
uniform mat3 normalMatrix;

varying vec3 fragPos;
varying vec2 out_texture;
varying vec3 fragNormal;

void main() {
    vec4 worldPos = model * vec4(position, 1.0);
    fragPos       = vec3(worldPos);
    out_texture   = texture_coord;
    fragNormal    = normalMatrix * normal;
    gl_Position   = projection * view * worldPos;
}
