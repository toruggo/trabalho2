attribute vec3 position;

uniform mat4 view;
uniform mat4 projection;

varying vec3 texDir;

void main() {
    texDir = position;
    vec4 pos = projection * view * vec4(position, 1.0);
    // Set z = w so the skybox always lands at depth 1.0 (behind everything).
    gl_Position = pos.xyww;
}
