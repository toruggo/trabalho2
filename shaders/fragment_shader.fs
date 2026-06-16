varying vec3 fragPos;
varying vec2 out_texture;
varying vec3 fragNormal;

uniform vec3 viewPos;
uniform sampler2D samplerTexture;

uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float shininess;
uniform float alpha;

uniform vec3 Ke;
uniform int emissiveOn;

uniform int ambientOn;
uniform float ambientStrength;
uniform vec3 ambientColor;

uniform float diffuseMult;
uniform float specularMult;

// AABB do interior do templo: separa luz externa de interna sem stencil.
uniform vec3 interiorMin;
uniform vec3 interiorMax;

// Deve ser igual ao número de instâncias em flying_lantern.py e a NUM_LANTERNS em lighting.py.
#define NUM_LANTERNS 20

uniform int lanternOn[NUM_LANTERNS];
uniform vec3 lanternPos[NUM_LANTERNS];
uniform vec3 lanternColor[NUM_LANTERNS];

uniform int intLightAOn;
uniform vec3 intLightAPos;
uniform vec3 intLightAColor;

uniform int intLightBOn;
uniform vec3 intLightB1Pos;
uniform vec3 intLightB2Pos;
uniform vec3 intLightB3Pos;
uniform vec3 intLightBColor;

vec3 computeLight(vec3 lightPos, vec3 lightColor, vec3 norm, vec3 viewDir, vec3 texColor) {
    vec3 toLight  = lightPos - fragPos;
    float dist    = length(toLight);
    vec3 lightDir = toLight / dist;

    float diff   = max(dot(norm, lightDir), 0.0);
    vec3 diffuse = diffuseMult * diff * Kd * texColor * lightColor;

    vec3 reflectDir = reflect(-lightDir, norm);
    float spec      = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular   = specularMult * spec * Ks * lightColor;

    // Evita saturação quando várias fontes se somam perto da superfície.
    float attenuation = 1.0 / (1.0 + 0.045 * dist + 0.0075 * dist * dist);

    return attenuation * (diffuse + specular);
}

void main() {
    vec4 texSample = texture2D(samplerTexture, out_texture);
    if (texSample.a < 0.1) discard;

    // Descomentar para visualizar a máscara de alpha cutout (ex: folhas da sakura).
    // if (texSample.a < 0.1) { gl_FragColor = vec4(1.0, 0.0, 1.0, 1.0); return; }

    vec3 texColor = texSample.rgb;

    vec3 norm = normalize(fragNormal);
    // Malhas importadas podem ter normais invertidas; gl_FrontFacing corrige sem reprocessar o OBJ.
    if (!gl_FrontFacing) norm = -norm;
    vec3 viewDir = normalize(viewPos - fragPos);

    bool isInterior = all(greaterThan(fragPos, interiorMin)) && all(lessThan(fragPos, interiorMax));

    vec3 result = vec3(0.0);
    if (ambientOn == 1 && !isInterior) {
        result += Ka * ambientStrength * ambientColor * texColor;
    }

    if (!isInterior) {
        for (int i = 0; i < NUM_LANTERNS; i++) {
            if (lanternOn[i] == 1) {
                result += computeLight(lanternPos[i], lanternColor[i], norm, viewDir, texColor);
            }
        }
    }

    if (isInterior && intLightAOn == 1) {
        result += computeLight(intLightAPos, intLightAColor, norm, viewDir, texColor);
    }

    if (isInterior && intLightBOn == 1) {
        result += computeLight(intLightB1Pos, intLightBColor, norm, viewDir, texColor);
        result += computeLight(intLightB2Pos, intLightBColor, norm, viewDir, texColor);
        result += computeLight(intLightB3Pos, intLightBColor, norm, viewDir, texColor);
    }

    if (emissiveOn == 1) {
        // Multiplica pela textura para concentrar o brilho nas áreas já claras do mapa.
        result += Ke * texColor;
    }

    gl_FragColor = vec4(result, alpha * texSample.a);
}
