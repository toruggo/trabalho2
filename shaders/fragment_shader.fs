varying vec3 fragPos;
varying vec2 out_texture;
varying vec3 fragNormal;

uniform vec3 viewPos;
uniform sampler2D samplerTexture;

// Per-object material (req 7).
uniform vec3 Ka;
uniform vec3 Kd;
uniform vec3 Ks;
uniform float shininess;

// Ambient (req 3 / req 4).
uniform int ambientOn;
uniform float ambientStrength;
uniform vec3 ambientColor;

// Diffuse / specular adjustment (req 5 / req 6).
uniform float diffuseMult;
uniform float specularMult;

// World-space AABB used to mask interior-only / exterior-only lights.
uniform vec3 interiorMin;
uniform vec3 interiorMax;

// Exterior lights, one per flying lantern — affect only fragments outside
// the interior box (req 1).
uniform int lantern1On;
uniform vec3 lantern1Pos;
uniform vec3 lantern1Color;

uniform int lantern2On;
uniform vec3 lantern2Pos;
uniform vec3 lantern2Color;

uniform int lantern3On;
uniform vec3 lantern3Pos;
uniform vec3 lantern3Color;

uniform int lantern4On;
uniform vec3 lantern4Pos;
uniform vec3 lantern4Color;

// Interior lights — affect only fragments inside the interior box (req 2).
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

    float diff    = max(dot(norm, lightDir), 0.0);
    vec3 diffuse  = diffuseMult * diff * Kd * texColor * lightColor;

    vec3 reflectDir = reflect(-lightDir, norm);
    float spec      = pow(max(dot(viewDir, reflectDir), 0.0), shininess);
    vec3 specular   = specularMult * spec * Ks * lightColor;

    // Distance attenuation - without it, every light contributes the same
    // intensity regardless of how close it is, so several nearby interior
    // lights stack and clip to white instead of producing a visible falloff.
    float attenuation = 1.0 / (1.0 + 0.045 * dist + 0.0075 * dist * dist);

    return attenuation * (diffuse + specular);
}

void main() {
    vec4 texSample = texture2D(samplerTexture, out_texture);
    if (texSample.a < 0.1) discard;
    vec3 texColor = texSample.rgb;

    vec3 norm    = normalize(fragNormal);
    vec3 viewDir = normalize(viewPos - fragPos);

    vec3 result = vec3(0.0);
    if (ambientOn == 1) {
        result += Ka * ambientStrength * ambientColor;
    }

    bool isInterior = all(greaterThan(fragPos, interiorMin)) && all(lessThan(fragPos, interiorMax));

    if (!isInterior) {
        if (lantern1On == 1) result += computeLight(lantern1Pos, lantern1Color, norm, viewDir, texColor);
        if (lantern2On == 1) result += computeLight(lantern2Pos, lantern2Color, norm, viewDir, texColor);
        if (lantern3On == 1) result += computeLight(lantern3Pos, lantern3Color, norm, viewDir, texColor);
        if (lantern4On == 1) result += computeLight(lantern4Pos, lantern4Color, norm, viewDir, texColor);
    }
    if (isInterior && intLightAOn == 1) {
        result += computeLight(intLightAPos, intLightAColor, norm, viewDir, texColor);
    }
    if (isInterior && intLightBOn == 1) {
        result += computeLight(intLightB1Pos, intLightBColor, norm, viewDir, texColor);
        result += computeLight(intLightB2Pos, intLightBColor, norm, viewDir, texColor);
        result += computeLight(intLightB3Pos, intLightBColor, norm, viewDir, texColor);
    }

    gl_FragColor = vec4(result, 1.0);
}
