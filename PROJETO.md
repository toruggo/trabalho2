# Projeto 3 — Iluminação com OpenGL

Cena 3D de um templo japonês com três tipos de fonte de luz, animações e skybox, implementada em Python com OpenGL programável (sem pipeline fixo).

---

## Estrutura de arquivos

```
main.py                  ponto de entrada, loop de renderização
src/
  scene_builder.py       monta a SceneData chamando cada asset
  scene.py               SceneObject, load_temple, load_simple_object, draw_objects
  lighting.py            Light, LightingRig, make_default_rig
  render_passes.py       compilação dos shaders, passes de render, upload de uniforms
  behaviors.py           DriftBehavior — animação das lanternas voadoras
  geometry.py            load_obj, upload_vbo, bind_vbo, texturas
  matrizes.py            model_matrix, normal_matrix, blender_to_scene_pos
  shader_s.py            Shader — compila e linka vertex + fragment
  state.py               estado global: câmera, rig de luz, flags
  input.py               callbacks de teclado e mouse
  assets/
    __init__.py          AssetContext, AssetResult
    temple.py            templo principal
    grass.py / wall.py   chão e muros
    sakura.py            árvores sakura
    flying_lantern.py    20 lanternas externas animadas
    dragon_candle.py     candela de dragão (luz interna A)
    hanging_lantern.py   3 lanternas pendentes (luz interna B)
    market.py            objetos de mercado
    mountain_range.py    serras ao fundo
shaders/
  vertex_shader.vs + fragment_shader.fs   passe principal (Phong)
  skybox.vs + skybox.fs                   céu em cubemap
  glow.vs + glow.fs                       halo billboard das lanternas
```

---

## Dataclasses principais

### `SceneObject` — `scene.py`

Unidade de renderização. Cada material de cada OBJ vira um `SceneObject`.

| Campo | Tipo | O que é |
|---|---|---|
| `vbo` | `int` | handle do buffer de vértices na GPU |
| `tex` | `int` | handle da textura 2D na GPU |
| `n_verts` | `int` | quantidade de vértices |
| `model` | `glm.mat4` | transformação local → mundo |
| `normal_matrix` | `glm.mat3` | transposta da inversa de `model` |
| `Ka / Kd / Ks` | `tuple` | coeficientes ambiente, difuso e especular |
| `shininess` | `float` | expoente da parcela especular |
| `alpha` | `float` | opacidade (< 1 = translúcido) |
| `Ke` | `tuple` | coeficiente emissivo |
| `light_offset` | `glm.vec3` | posição local do ponto de luz relativo à malha |
| `light` | `Light \| None` | luz associada (controla `emissiveOn`) |

---

### `Light` e `LightingRig` — `lighting.py`

```
Light
  on: bool          liga/desliga
  color: tuple      (R, G, B) — valores > 1.0 são permitidos
  positions: list   lista de glm.vec3 (uma por instância)

LightingRig
  ambient_on / ambient_strength / ambient_color
  diffuse_mult / specular_mult      (ajustados em tempo real)
  lantern_lights: list[Light]       20 lanternas externas
  int_light_a: Light                dragon candle
  int_light_b: Light                3 lanternas pendentes
```

Um único `LightingRig` global em `state.py` é passado para `scene_builder` e para `upload_lighting_uniforms` a cada frame.

---

### `AssetContext` e `AssetResult` — `assets/__init__.py`

Cada módulo em `assets/` expõe apenas `build(ctx) -> AssetResult`.

```
AssetContext
  temple_center: tuple    centro do templo (usado para reposicionar outros assets)
  extent: float           tamanho da cena (escala câmera, velocidade, raio de órbita)
  rig: LightingRig        referência ao rig global

AssetResult
  objects: list[SceneObject]
  behaviors: list          animações que o main loop vai chamar
```

---

### `SceneData` — `scene_builder.py`

Produto final de `build_scene`. Mantido durante todo o loop.

```
SceneData
  opaque_objects      objetos com alpha == 1.0
  translucent_objects objetos com alpha < 1.0
  behaviors           lista de DriftBehavior
  extent              dimensão máxima da cena
  glow_color / glow_size  cor e tamanho dos halos
```

A separação opaco / translúcido define a ordem de renderização:
opacos primeiro → skybox → translúcidos com blend.

---

### Passes de renderização — `render_passes.py`

Cada passe tem sua dataclass com shader compilado, handles de atributo e dicionário de locations de uniform.

```
MainPass    vertex + fragment com Phong, recebe toda a geometria da cena
SkyboxPass  cubo unitário com cubemap GL_TEXTURE_CUBE_MAP
GlowPass    quad billboard com blend aditivo (GL_ONE, GL_ONE)
```

---

## Pipeline de shaders

### Passe principal — `vertex_shader.vs` + `fragment_shader.fs`

**Vertex shader**

Recebe três atributos por vértice:

| Atributo | Conteúdo |
|---|---|
| `position` | XYZ local |
| `texture_coord` | UV |
| `normal` | normal local |

Aplica `model → view → projection` e passa para o fragment:
- `fragPos` — posição no espaço mundo
- `fragNormal` — normal transformada pela `normalMatrix`
- `out_texture` — UV interpolada

**Fragment shader — modelo de Phong local por pixel**

Equação por fonte de luz pontual:

```
diffuse  = diffuseMult × max(N·L, 0) × Kd × texColor × lightColor
specular = specularMult × max(V·R, 0)^shininess × Ks × lightColor
attenuation = 1 / (1 + 0.045·d + 0.0075·d²)
resultado += attenuation × (diffuse + specular)
```

**Separação interior / exterior via AABB**

O fragment recebe `interiorMin` e `interiorMax` e decide com `all(greaterThan/lessThan)`:

- Pixels **fora** → somam as 20 lanternas voadoras (`lanternOn[i]`)
- Pixels **dentro** → somam `int_light_a` (dragon candle) e `int_light_b` (3 pendentes)

Isso elimina a necessidade de stencil buffer para separar os dois ambientes.

---

### Passe skybox — `skybox.vs` + `skybox.fs`

Cubo unitário centrado na câmera. A view é truncada para só rotação (`glm.mat3(view)`) para o céu não se deslocar com a câmera. O vertex shader força `z = w` (`pos.xyww`) para o cubo sempre ficar no fundo do depth buffer (`GL_LEQUAL`).

---

### Passe glow — `glow.vs` + `glow.fs`

Billboard: quad de dois triângulos com posição 2D local `[-0.5, 0.5]`.

O vertex shader monta a posição no mundo:
```
worldPos = center + (x × size) × cameraRight + (y × size) × cameraUp
```
`cameraRight` e `cameraUp` são vetores ortonormais da câmera enviados pelo Python.

O fragment faz queda radial suavizada:
```
d       = length(localPos) × 2.0
falloff = clamp(1 − d, 0, 1)²
cor     = vec4(color × falloff, falloff)
```
Blend `GL_ONE + GL_ONE` (aditivo) garante que halos sobrepostos se somam.

---

## Pipeline de geometria — `geometry.py`

1. **`load_obj`** — lê o OBJ linha a linha, trianguliza faces poligonais em leque, retorna grupos `(material, verts_float32)` com stride `[px py pz u v nx ny nz]`, além de `extent` e `center`.
2. **`merge_groups`** — concatena grupos com mesmo nome de material.
3. **`upload_vbo`** — `glBufferData` estático.
4. **`bind_vbo`** — `glVertexAttribPointer` para os três atributos com stride de 8 floats.
5. **`load_texture`** — PIL → flip Y → `glTexImage2D` RGBA, limite de 2048 px.
6. **`load_texture_with_alpha`** — junta RGB de um arquivo com alpha de outro (folhas de sakura).
7. **`load_cubemap`** — seis faces `px/nx/py/ny/pz/nz.png` para `GL_TEXTURE_CUBE_MAP`.
8. **`make_solid_texture`** — textura 1×1 para materiais sem arquivo.

---

## Matrizes — `matrizes.py`

| Função | O que faz |
|---|---|
| `model_matrix(pos, rot_deg, scale)` | TRS na ordem T·Rz·Ry·Rx·S |
| `normal_matrix(model)` | `transpose(inverse(mat3(model)))` |
| `blender_to_scene_pos(x, y, z)` | Blender Z-up → cena Y-up: `(x, z, -y)` |
| `light_world_pos(obj)` | `model × vec4(light_offset, 1)` |
| `place_baked_instance(...)` | posiciona instância de malha já assada no Blender |

---

## Comportamentos — `behaviors.py`

### `DriftBehavior`

Cada lanterna voadora tem uma instância. A cada `update(delta_time)`:

1. `offset += dir × speed × dt`
2. Se `|offset| > radius` → reflete `dir` em torno da normal da esfera e recoloca na casca
3. Aplica `model = translate(base + offset)` em todos os `SceneObject` da instância
4. Atualiza `light.positions[0]` para manter a luz pontual alinhada à malha

---

## Controles em tempo real

| Tecla | Efeito |
|---|---|
| `1` | liga/desliga luz ambiente |
| `2` | liga/desliga lanternas externas |
| `3` | liga/desliga dragon candle |
| `4` | liga/desliga hanging lanterns |
| `Z / X` | intensidade ambiente − / + |
| `C / V` | `diffuse_mult` − / + |
| `B / N` | `specular_mult` − / + |
| `WASD` | movimento da câmera |
| `Espaço / Shift` | sobe / desce |
| Mouse | rotação |
