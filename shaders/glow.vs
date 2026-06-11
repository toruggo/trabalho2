attribute vec2 position;

uniform mat4 view;
uniform mat4 projection;
uniform vec3 center;
uniform vec3 cameraRight;
uniform vec3 cameraUp;
uniform float size;

varying vec2 localPos;

void main() {
    vec3 worldPos = center + (position.x * size) * cameraRight + (position.y * size) * cameraUp;
    gl_Position    = projection * view * vec4(worldPos, 1.0);
    localPos       = position;
}
