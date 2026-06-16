// position do cubo unitário é usada diretamente como direção no cubemap.
// A view recebe só a parte de rotação (sem translação) para o céu girar com a câmera mas não se deslocar.

attribute vec3 position;

uniform mat4 view;
uniform mat4 projection;

varying vec3 texDir;

void main() {
    texDir = position;
    vec4 pos = projection * view * vec4(position, 1.0);
    // xyww força z/w = 1.0 após perspectiva, colocando o cubo no fundo do depth buffer.
    gl_Position = pos.xyww;
}
