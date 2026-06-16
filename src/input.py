"""
Sistema de Input: Eventos de Teclado e Mouse

Controles de iluminação:
  1 = ligar/desligar luz ambiente
  2 = ligar/desligar lanternas exteriores
  3 = ligar/desligar dragon candle (interior)
  4 = ligar/desligar hanging lanterns (interior)
  Z/X = diminuir/aumentar intensidade da luz ambiente
  C/V = diminuir/aumentar reflexão difusa
  B/N = diminuir/aumentar reflexão especular

Controles de Câmera:
  W/A/S/D = movimento horizontal
  ESPAÇO/SHIFT = cima/baixo
  MOUSE = rotação da câmera
  ESC = sair

Opcional:
  T = modo wireframe (arestas)
  P = imprimir posição da câmera (para placement de lanternas)
"""

import math

import glfw
import glm

import state


def _fmt(v):
    """Formata um vetor 3D para impressão no console."""
    return f"({v.x:.2f}, {v.y:.2f}, {v.z:.2f})"


def key_event(window, key, scancode, action, mods):
    """Processa eventos de teclado pressionado/liberado."""
    rig = state.lighting_rig

    if action == glfw.PRESS:
        # Registra a tecla como pressionada
        state.keys_pressed.add(key)

        # Teclas de Iluminação (Toggle)
        if key == glfw.KEY_1:
            # Ligar ou desligar luz ambiente
            rig.ambient_on = not rig.ambient_on
            print(f"[Luz] Ambiente: {'LIGADA' if rig.ambient_on else 'DESLIGADA'}")

        elif key == glfw.KEY_2:
            # Ligar ou desligar todas as 20 lanternas exteriores
            new_state = not rig.lantern_lights[0].on
            for light in rig.lantern_lights:
                light.on = new_state
            print(
                f"[Luz] Lanternas Exteriores: {'LIGADAS' if new_state else 'DESLIGADAS'}"
            )

        elif key == glfw.KEY_3:
            # Ligar ou desligar dragon candle no interior
            rig.int_light_a.on = not rig.int_light_a.on
            print(
                f"[Luz] Interior A (Dragon Candle): {'LIGADA' if rig.int_light_a.on else 'DESLIGADA'}"
            )

        elif key == glfw.KEY_4:
            # Ligar ou desligar hanging lanterns, três lanternas penduradas
            rig.int_light_b.on = not rig.int_light_b.on
            print(
                f"[Luz] Interior B (Hanging Lanterns x3): {'LIGADAS' if rig.int_light_b.on else 'DESLIGADAS'}"
            )

        elif key == glfw.KEY_P:
            # Imprime a posição atual da câmera (útil para adicionar novas lanternas)
            cam = state.camera
            print(f"[Câmera] pos={_fmt(cam['pos'])}")

        elif key == glfw.KEY_T:
            # Modo wireframe: mostra apenas arestas dos triângulos
            state.wireframe_view = not state.wireframe_view
            print(f"[Wireframe] {'ATIVADO' if state.wireframe_view else 'DESATIVADO'}")

        elif key == glfw.KEY_G:
            state.debug_glow = not state.debug_glow
            print(f"[Debug Glow] {'ATIVADO' if state.debug_glow else 'DESATIVADO'}")
    elif action == glfw.RELEASE:
        state.keys_pressed.discard(key)

        if key in (glfw.KEY_Z, glfw.KEY_X):
            print(f"[Lighting] ambient_strength = {rig.ambient_strength:.3f}")
        elif key in (glfw.KEY_C, glfw.KEY_V):
            print(f"[Lighting] diffuse_mult = {rig.diffuse_mult:.3f}")
        elif key in (glfw.KEY_B, glfw.KEY_N):
            print(f"[Lighting] specular_mult = {rig.specular_mult:.3f}")


def mouse_event(window, xpos, ypos):
    """Calcula rotação da câmera baseado no movimento do mouse."""
    cam = state.camera

    # Na primeira chamada, só registra a posição sem calcular delta
    if cam["first"]:
        cam["last_x"] = xpos
        cam["last_y"] = ypos
        cam["first"] = False
        return

    # Calcula diferença de movimento desde o último frame (sensibilidade: 0.1)
    dx = (xpos - cam["last_x"]) * 0.1
    dy = (cam["last_y"] - ypos) * 0.1
    cam["last_x"] = xpos
    cam["last_y"] = ypos

    # Atualiza ângulos de rotação (yaw = horizontal, pitch = vertical)
    cam["yaw"] += dx
    # Limita pitch entre -89 e 89 graus (impede virada de cabeça para cima/baixo)
    cam["pitch"] = max(-89.0, min(89.0, cam["pitch"] + dy))

    # Calcula vetor direção da câmera (para onde ela está olhando)
    front = glm.vec3(
        math.cos(math.radians(cam["yaw"])) * math.cos(math.radians(cam["pitch"])),
        math.sin(math.radians(cam["pitch"])),
        math.sin(math.radians(cam["yaw"])) * math.cos(math.radians(cam["pitch"])),
    )
    cam["front"] = glm.normalize(front)


def process_camera(window, speed):
    """Processa teclas WASD, ESPAÇO e SHIFT para mover a câmera."""
    cam = state.camera
    # Calcula o vetor "direita" (perpendicular ao front e up)
    right = glm.normalize(glm.cross(cam["front"], cam["up"]))

    # Movimento para frente/trás (along look direction)
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        cam["pos"] += cam["front"] * speed  # W = para frente
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        cam["pos"] -= cam["front"] * speed  # S = para trás

    # Movimento lateral (esquerda/direita)
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        cam["pos"] -= right * speed  # A = para esquerda
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        cam["pos"] += right * speed  # D = para direita

    # Movimento cima/baixo (vertical)
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        cam["pos"] += cam["up"] * speed  # ESPAÇO = para cima
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        cam["pos"] -= cam["up"] * speed  # SHIFT = para baixo

    # Restringe altura da câmera: entre chão (-10) e acima do teto (45)
    cam["pos"].y = max(state.camera_min_y, min(state.camera_max_y, cam["pos"].y))


# Velocidades de ajuste para teclas pressionadas (unidades por segundo)
AMBIENT_SPEED = 0.2  # Luz ambiente: muda 0.2 por segundo
DIFFUSE_SPEED = 0.5  # Reflexão difusa: muda 0.5 por segundo
SPECULAR_SPEED = 0.5  # Reflexão especular: muda 0.5 por segundo


def process_lighting(delta_time):
    """
    Processa ajustes contínuos de iluminação enquanto as teclas estão pressionadas.

    Z e X ajustam intensidade da luz ambiente entre 0.0 e 1.0.
    C e V ajustam o multiplicador da reflexão difusa entre 0.0 e 3.0.
    B e N ajustam o multiplicador da reflexão especular entre 0.0 e 3.0.

    Esses ajustes afetam TODOS os objetos da cena em tempo real.
    """
    rig = state.lighting_rig
    keys = state.keys_pressed

    # ── Ajuste luz ambiente ───────────────────────────────────────────────────
    if glfw.KEY_Z in keys:
        # Z = diminuir intensidade (0.0 = escuro total)
        rig.ambient_strength = max(
            0.0, rig.ambient_strength - AMBIENT_SPEED * delta_time
        )
    if glfw.KEY_X in keys:
        # X = aumentar intensidade (1.0 = máximo brilho ambiente)
        rig.ambient_strength = min(
            1.0, rig.ambient_strength + AMBIENT_SPEED * delta_time
        )

    # ── Ajuste reflexão difusa ────────────────────────────────────────────────
    # Afeta como os materiais refletem luz nos pontos iluminados
    if glfw.KEY_C in keys:
        # C = diminuir reflexão (0.0 = sem difusa, cena muito escura)
        rig.diffuse_mult = max(0.0, rig.diffuse_mult - DIFFUSE_SPEED * delta_time)
    if glfw.KEY_V in keys:
        # V = aumentar reflexão (3.0 = muito brilhante)
        rig.diffuse_mult = min(3.0, rig.diffuse_mult + DIFFUSE_SPEED * delta_time)

    # ── Ajuste reflexão especular ─────────────────────────────────────────────
    # Afeta brilho/shine de superfícies (reflex especular)
    if glfw.KEY_B in keys:
        # B = diminuir reflexão especular (0.0 = sem brilho)
        rig.specular_mult = max(0.0, rig.specular_mult - SPECULAR_SPEED * delta_time)
    if glfw.KEY_N in keys:
        # N = aumentar reflexão especular (3.0 = muito brilhante)
        rig.specular_mult = min(3.0, rig.specular_mult + SPECULAR_SPEED * delta_time)
