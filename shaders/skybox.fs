// Amostra o cubemap na direção texDir vinda do vértice (vértices do cubo unitário).

varying vec3 texDir;

uniform samplerCube skybox;

void main() {
    gl_FragColor = textureCube(skybox, texDir);
}
