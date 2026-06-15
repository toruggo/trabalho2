varying vec2 localPos;

uniform vec3 color;
// sensação de “glow” ao redor da posição da lanterna, além da malha e do Ke no shader principal.
void main() {
    // Distância ao centro do quad no plano local, escalada para a borda valer cerca de 1.
    float d = length(localPos) * 2.0;
    // Mais claro no centro, zero na borda, curva ao quadrado para transição suave.
    float falloff = pow(clamp(1.0 - d, 0.0, 1.0), 2.0);
    if (falloff <= 0.0) discard;
    // RGB e alpha modulados pelo falloff, o blend aditivo usa isso como intensidade do halo.
    gl_FragColor = vec4(color * falloff, falloff);
}
