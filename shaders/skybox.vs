// Vertex shader do skybox: transforma um cubo unitário centrado na origem.
// A direção de cada vértice (position) vira texDir para o fragment amostrar o cubemap.
// A view vinda do Python costuma ter só rotação, sem translação, para o cubo girar com a câmera.

attribute vec3 position;

uniform mat4 view;
uniform mat4 projection;

varying vec3 texDir;

void main() {
    // Direção no espaço da câmera / mundo para textureCube no skybox.fs.
    texDir = position;
    vec4 pos = projection * view * vec4(position, 1.0);
    // Força profundidade máxima: z = w implica z/w = 1.0 após perspectiva,
    // então o cubo fica no fundo do depth buffer (atrás da geometria da cena).
    gl_Position = pos.xyww;
}
