varying vec3 texDir;

uniform samplerCube skybox;

void main() {
    gl_FragColor = textureCube(skybox, texDir);
}
