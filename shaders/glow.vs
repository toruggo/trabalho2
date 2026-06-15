// Vertex shader do halo: quad billboard voltado para a câmera, centrado na lanterna.
// cameraRight e cameraUp vêm do Python para o quad sempre olhar a tela.

attribute vec2 position;

uniform mat4 view;
uniform mat4 projection;
uniform vec3 center;
uniform vec3 cameraRight;
uniform vec3 cameraUp;
uniform float size;

varying vec2 localPos;

void main() {
    // Posição no mundo: centro mais deslocamento no plano do billboard.
    vec3 worldPos = center + (position.x * size) * cameraRight + (position.y * size) * cameraUp;
    gl_Position    = projection * view * vec4(worldPos, 1.0);
    // Passa UV local para o fragment fazer queda radial do brilho.
    localPos       = position;
}
