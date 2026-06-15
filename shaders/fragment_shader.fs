// Fragment shader do Projeto 3: ambiente, difusa e especular no modelo local por pixel.
// Os varyings vêm do vertex shader já interpolados no triângulo: posição e UV no mundo,
// normal no mundo.

varying vec3 fragPos;
varying vec2 out_texture;
varying vec3 fragNormal;

uniform vec3 viewPos;
uniform sampler2D samplerTexture;

// Ka Kd Ks e shininess vêm por objeto 
uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float shininess;
uniform float alpha;

// Ke coeficiente emissivo; emissiveOn liga ou corta o termo junto ao interruptor da luz.
uniform vec3 Ke;
uniform int emissiveOn;

// Luz ambiente uniforme em toda a cena: liga ou desliga, muda a intensidade.
uniform int ambientOn;
uniform float ambientStrength;
uniform vec3 ambientColor;

// Escala global da parcela difusa e da parcela especular, teclas C V e B N.
uniform float diffuseMult;
uniform float specularMult;

// Cantos opostos em espaço mundo de uma caixa alinhada aos eixos que marca o interior do templo.
// Só com isso o shader separa luz de fora e luz de dentro sem stencil extra.
uniform vec3 interiorMin;
uniform vec3 interiorMax;

// Até NUM_LANTERNS fontes pontuais nas lanternas voadoras, só fora da caixa interior.
// Mantenha este número igual ao de instâncias configuradas no Python.
#define NUM_LANTERNS 20

uniform int lanternOn[NUM_LANTERNS];
uniform vec3 lanternPos[NUM_LANTERNS];
uniform vec3 lanternColor[NUM_LANTERNS];

// Luzes internas em duas famílias com cores diferentes, só dentro da caixa interior.
uniform int intLightAOn;
uniform vec3 intLightAPos;
uniform vec3 intLightAColor;

uniform int intLightBOn;
uniform vec3 intLightB1Pos;
uniform vec3 intLightB2Pos;
uniform vec3 intLightB3Pos;
uniform vec3 intLightBColor;

// Uma chamada por fonte pontual: difuso Lambert, especular Phong (reflexo vs. olho), atenuação com a distância.
vec3 computeLight(vec3 lightPos, vec3 lightColor, vec3 norm, vec3 viewDir, vec3 texColor) {
    vec3 toLight  = lightPos - fragPos;
    float dist    = length(toLight);
    vec3 lightDir = toLight / dist;

    // Difuso: cosseno entre normal e direção da luz, clampado em zero para a face de costas.
    float diff    = max(dot(norm, lightDir), 0.0);
    vec3 diffuse  = diffuseMult * diff * Kd * texColor * lightColor;

    // Especular: quão alinhados estão o olho e o reflexo da luz na superfície, elevado a shininess.
    vec3 reflectDir = reflect(-lightDir, norm);
    float spec      = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular   = specularMult * spec * Ks * lightColor;

    // Ganho menor longe da fonte para não saturar tudo em branco quando várias luzes somam perto.
    float attenuation = 1.0 / (1.0 + 0.045 * dist + 0.0075 * dist * dist);

    return attenuation * (diffuse + specular); // atenuação * (difuso + especular)
}

void main() {
    vec4 texSample = texture2D(samplerTexture, out_texture);
    if (texSample.a < 0.1) discard;
    vec3 texColor = texSample.rgb;

    vec3 norm    = normalize(fragNormal);
    // Corrige normais invertidas em malhas importadas olhando qual lado do triângulo está visível.
    if (!gl_FrontFacing) norm = -norm;
    vec3 viewDir = normalize(viewPos - fragPos);

    vec3 result = vec3(0.0);
    if (ambientOn == 1) {
        result += Ka * ambientStrength * ambientColor * texColor;
    }

    // interiorMin e interiorMax delimitam um bloco; dentro vale luz interna, fora vale luz das lanternas.
    bool isInterior = all(greaterThan(fragPos, interiorMin)) && all(lessThan(fragPos, interiorMax));

    // Lanternas voadoras: laço só quando o pixel está fora do bloco interior.
    if (!isInterior) {
        for (int i = 0; i < NUM_LANTERNS; i++) {
            if (lanternOn[i] == 1) {
                result += computeLight(lanternPos[i], lanternColor[i], norm, viewDir, texColor);
            }
        }
    }
    // Primeira luz interna
    if (isInterior && intLightAOn == 1) {
        result += computeLight(intLightAPos, intLightAColor, norm, viewDir, texColor);
    }
    // Segunda família interna
    if (isInterior && intLightBOn == 1) {
        result += computeLight(intLightB1Pos, intLightBColor, norm, viewDir, texColor);
        result += computeLight(intLightB2Pos, intLightBColor, norm, viewDir, texColor);
        result += computeLight(intLightB3Pos, intLightBColor, norm, viewDir, texColor);
    }

    if (emissiveOn == 1) {
        // Ke vezes a cor da textura concentra o brilho nas áreas já claras do mapa.
        result += Ke * texColor;
    }

    gl_FragColor = vec4(result, alpha * texSample.a);
}
