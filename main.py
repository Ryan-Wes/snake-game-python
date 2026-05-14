import pygame
import sys
import random
import json
import os
import asyncio

pygame.init()
pygame.mixer.init()

som_comer = pygame.mixer.Sound("assets/sounds/eat.ogg")
som_game_over = pygame.mixer.Sound("assets/sounds/game_over.ogg")
musica_atual = None

def tocar_musica(caminho):
    global musica_atual
    if musica_atual != caminho:
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        musica_atual = caminho

# ── Configurações ────────────────────────────────────
LARGURA = 800
ALTURA = 600
TAMANHO_BLOCO = 20
FPS = 60
ALTURA_HUD = 70

HIGHSCORE_FILE = "highscore.json"

# Cores cyberpunk
FUNDO        = (10,  8,  20)
FUNDO_HUD    = (18, 14,  36)
TEXTO        = (235, 235, 245)
ROXO_PRINCIPAL = (196, 11, 255)
ROXO_CLARO   = (220, 120, 255)
ROXO_ESCURO  = (110,  20, 150)
AZUL_NEON    = (0,  246, 249)
AZUL_CLARO   = (120, 250, 255)
GRID         = (40,  26,  60)
PRETO        = (0,   0,   0)

# Power-up cores
COR_POWERUP_VELOCIDADE = (255, 220,  50)   # amarelo
COR_POWERUP_PONTOS     = (50,  255, 120)   # verde neon
COR_POWERUP_ESCUDO     = (50,  180, 255)   # azul claro

# Obstáculo
COR_OBSTACULO = (200,  40,  40)

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

fonte_titulo = pygame.font.SysFont("arial", 48, bold=True)
fonte_texto  = pygame.font.SysFont("arial", 28)
fonte_score  = pygame.font.SysFont("arial", 22)
fonte_mini   = pygame.font.SysFont("arial", 16)

MENU      = "menu"
JOGANDO   = "jogando"
GAME_OVER = "game_over"
PAUSADO   = "pausado"

estado_jogo = MENU

# ── High score persistido ────────────────────────────
def carregar_highscore():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            with open(HIGHSCORE_FILE, "r") as f:
                data = json.load(f)
                return data.get("high_score", 0)
        except Exception:
            pass
    return 0

def salvar_highscore(valor):
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump({"high_score": valor}, f)
    except Exception:
        pass

high_score = carregar_highscore()

# ── Power-up ─────────────────────────────────────────
class PowerUp:
    VELOCIDADE = "velocidade"
    PONTOS     = "pontos"
    ESCUDO     = "escudo"
    TIPOS      = [VELOCIDADE, PONTOS, ESCUDO]

    def __init__(self, cobra, obstaculos):
        self.tipo = random.choice(self.TIPOS)
        self.posicao = self._gerar_posicao(cobra, obstaculos)
        self.tempo_restante = 300   # frames até sumir
        self.ativo = True

    def _gerar_posicao(self, cobra, obstaculos):
        ocupados = set(map(tuple, cobra)) | set(map(tuple, obstaculos))
        while True:
            x = random.randrange(0, LARGURA, TAMANHO_BLOCO)
            y = random.randrange(ALTURA_HUD, ALTURA, TAMANHO_BLOCO)
            if (x, y) not in ocupados:
                return [x, y]

    def cor(self):
        if self.tipo == self.VELOCIDADE: return COR_POWERUP_VELOCIDADE
        if self.tipo == self.PONTOS:     return COR_POWERUP_PONTOS
        return COR_POWERUP_ESCUDO

    def icone(self):
        if self.tipo == self.VELOCIDADE: return "⚡"
        if self.tipo == self.PONTOS:     return "★"
        return "🛡"

    def desenhar(self):
        if not self.ativo:
            return
        cx = self.posicao[0] + TAMANHO_BLOCO // 2
        cy = self.posicao[1] + TAMANHO_BLOCO // 2
        raio = TAMANHO_BLOCO // 2 - 1
        pulsacao = abs(pygame.math.Vector2(raio, 0).rotate(pygame.time.get_ticks() * 0.2).x)
        raio_atual = raio + int(pulsacao * 0.3)

        pygame.draw.circle(tela, self.cor(), (cx, cy), raio_atual)
        pygame.draw.circle(tela, PRETO, (cx, cy), raio_atual // 2)

        # barra de duração
        proporcao = self.tempo_restante / 300
        barra_w = int(TAMANHO_BLOCO * proporcao)
        pygame.draw.rect(tela, self.cor(), (self.posicao[0], self.posicao[1] + TAMANHO_BLOCO + 2, barra_w, 2))

    def atualizar(self):
        self.tempo_restante -= 1
        if self.tempo_restante <= 0:
            self.ativo = False

# ── Obstáculos ───────────────────────────────────────
def gerar_obstaculos(cobra, comida, quantidade):
    ocupados = set(map(tuple, cobra)) | {tuple(comida)}
    obstaculos = []
    tentativas = 0
    while len(obstaculos) < quantidade and tentativas < 500:
        tentativas += 1
        x = random.randrange(TAMANHO_BLOCO, LARGURA - TAMANHO_BLOCO, TAMANHO_BLOCO)
        y = random.randrange(ALTURA_HUD + TAMANHO_BLOCO * 2, ALTURA - TAMANHO_BLOCO, TAMANHO_BLOCO)
        pos = (x, y)
        if pos not in ocupados:
            ocupados.add(pos)
            obstaculos.append([x, y])
    return obstaculos

def desenhar_obstaculos(obstaculos):
    for ob in obstaculos:
        rect = pygame.Rect(ob[0] + 2, ob[1] + 2, TAMANHO_BLOCO - 4, TAMANHO_BLOCO - 4)
        pygame.draw.rect(tela, COR_OBSTACULO, rect, border_radius=3)
        pygame.draw.rect(tela, (240, 80, 80), rect, width=1, border_radius=3)

# ── Helpers ──────────────────────────────────────────
def desenhar_texto(texto, fonte, cor, x, y, centralizar=True):
    sup = fonte.render(texto, True, cor)
    rect = sup.get_rect()
    if centralizar:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    tela.blit(sup, rect)

def gerar_comida(cobra, obstaculos):
    ocupados = set(map(tuple, cobra)) | set(map(tuple, obstaculos))
    while True:
        x = random.randrange(0, LARGURA, TAMANHO_BLOCO)
        y = random.randrange(ALTURA_HUD, ALTURA, TAMANHO_BLOCO)
        if (x, y) not in ocupados:
            return [x, y]

def reiniciar_jogo():
    pos_y = ALTURA_HUD + 100
    cobra = [
        [LARGURA // 2, pos_y],
        [LARGURA // 2 - TAMANHO_BLOCO, pos_y],
        [LARGURA // 2 - TAMANHO_BLOCO * 2, pos_y],
    ]
    direcao = "RIGHT"
    proxima_direcao = "RIGHT"
    comida = gerar_comida(cobra, [])

    nivel = 1
    obstaculos = gerar_obstaculos(cobra, comida, quantidade_obstaculos(nivel))

    return cobra, direcao, proxima_direcao, comida, 0, nivel, obstaculos, None, False, 0

def quantidade_obstaculos(nivel):
    return min(2 + (nivel - 1) * 2, 20)

def velocidade_base(nivel):
    return 10 + (nivel - 1) * 3

# ── Desenho da cobra ─────────────────────────────────
def desenhar_cobra(cobra, direcao, com_escudo):
    cor_cabeca = AZUL_NEON if com_escudo else ROXO_CLARO
    cor_corpo  = (0, 200, 220) if com_escudo else ROXO_PRINCIPAL

    for i, seg in enumerate(cobra):
        x, y = seg
        if i == 0:
            pygame.draw.rect(tela, cor_cabeca, (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO), border_radius=4)

            if direcao == "RIGHT":
                olho1, olho2 = (x+13, y+6), (x+13, y+14)
                lingua_i, lingua_f = (x+TAMANHO_BLOCO, y+TAMANHO_BLOCO//2), (x+TAMANHO_BLOCO+10, y+TAMANHO_BLOCO//2)
            elif direcao == "LEFT":
                olho1, olho2 = (x+7, y+6), (x+7, y+14)
                lingua_i, lingua_f = (x, y+TAMANHO_BLOCO//2), (x-10, y+TAMANHO_BLOCO//2)
            elif direcao == "UP":
                olho1, olho2 = (x+6, y+7), (x+14, y+7)
                lingua_i, lingua_f = (x+TAMANHO_BLOCO//2, y), (x+TAMANHO_BLOCO//2, y-10)
            else:
                olho1, olho2 = (x+6, y+13), (x+14, y+13)
                lingua_i, lingua_f = (x+TAMANHO_BLOCO//2, y+TAMANHO_BLOCO), (x+TAMANHO_BLOCO//2, y+TAMANHO_BLOCO+10)

            pygame.draw.circle(tela, PRETO, olho1, 2)
            pygame.draw.circle(tela, PRETO, olho2, 2)

            tempo = pygame.time.get_ticks() // 120
            if tempo % 2 == 0:
                pygame.draw.line(tela, AZUL_NEON, lingua_i, lingua_f, 2)
                if direcao in ["RIGHT", "LEFT"]:
                    pygame.draw.line(tela, AZUL_NEON, lingua_f, (lingua_f[0], lingua_f[1]-4), 2)
                    pygame.draw.line(tela, AZUL_NEON, lingua_f, (lingua_f[0], lingua_f[1]+4), 2)
                else:
                    pygame.draw.line(tela, AZUL_NEON, lingua_f, (lingua_f[0]-4, lingua_f[1]), 2)
                    pygame.draw.line(tela, AZUL_NEON, lingua_f, (lingua_f[0]+4, lingua_f[1]), 2)

            if com_escudo:
                pygame.draw.rect(tela, AZUL_NEON, (x-2, y-2, TAMANHO_BLOCO+4, TAMANHO_BLOCO+4), width=1, border_radius=5)
        else:
            pygame.draw.rect(tela, cor_corpo, (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO), border_radius=4)

def desenhar_comida(comida):
    cx = comida[0] + TAMANHO_BLOCO // 2
    cy = comida[1] + TAMANHO_BLOCO // 2
    raio = TAMANHO_BLOCO // 2 - 2
    pygame.draw.circle(tela, AZUL_NEON, (cx, cy), raio)
    pygame.draw.circle(tela, AZUL_CLARO, (cx, cy), raio // 2)

def desenhar_hud(score, nivel, com_escudo, escudo_ticks):
    pygame.draw.rect(tela, FUNDO_HUD, (0, 0, LARGURA, ALTURA_HUD))
    pygame.draw.line(tela, ROXO_PRINCIPAL, (0, ALTURA_HUD), (LARGURA, ALTURA_HUD), 2)

    desenhar_texto(f"Score: {score}", fonte_score, AZUL_NEON, 20, 18, centralizar=False)
    desenhar_texto(f"Recorde: {high_score}", fonte_score, ROXO_CLARO, 20, 42, centralizar=False)
    desenhar_texto(f"Nível {nivel}", fonte_score, TEXTO, LARGURA // 2, 30)

    if com_escudo and escudo_ticks > 0:
        barra_max = 180
        barra_w = int((escudo_ticks / barra_max) * 100)
        pygame.draw.rect(tela, (30, 100, 180), (LARGURA-120, 20, 100, 10), border_radius=5)
        pygame.draw.rect(tela, AZUL_NEON, (LARGURA-120, 20, barra_w, 10), border_radius=5)
        desenhar_texto("[ ESCUDO ]", fonte_mini, AZUL_NEON, LARGURA-70, 40, centralizar=True)

def desenhar_grid():
    for x in range(0, LARGURA, TAMANHO_BLOCO):
        pygame.draw.line(tela, GRID, (x, ALTURA_HUD), (x, ALTURA))
    for y in range(ALTURA_HUD, ALTURA, TAMANHO_BLOCO):
        pygame.draw.line(tela, GRID, (0, y), (LARGURA, y))

# ── Legenda ──────────────────────────────────────────
def desenhar_legenda(y_inicio):
    itens = [
        (COR_POWERUP_VELOCIDADE, "Velocidade (+nivel)", "circle"),
        (COR_POWERUP_PONTOS,     "+5 Pontos",           "circle"),
        (COR_POWERUP_ESCUDO,     "Escudo (1 batida)",   "circle"),
        (COR_OBSTACULO,          "Obstaculo",           "rect"),
    ]

    total = len(itens)
    espacamento = LARGURA // (total + 1)

    for i, (cor, label, forma) in enumerate(itens):
        cx = espacamento * (i + 1)
        cy = y_inicio

        if forma == "circle":
            raio = TAMANHO_BLOCO // 2 - 1
            pygame.draw.circle(tela, cor, (cx, cy), raio)
            pygame.draw.circle(tela, PRETO, (cx, cy), raio // 2)
        else:
            r = pygame.Rect(cx - TAMANHO_BLOCO//2 + 2, cy - TAMANHO_BLOCO//2 + 2,
                            TAMANHO_BLOCO - 4, TAMANHO_BLOCO - 4)
            pygame.draw.rect(tela, cor, r, border_radius=3)
            pygame.draw.rect(tela, (240, 80, 80), r, width=1, border_radius=3)

        desenhar_texto(label, fonte_mini, cor, cx, cy + 20)

# ── Telas ────────────────────────────────────────────
def tela_menu():
    tela.fill(FUNDO)
    desenhar_texto("SNAKE GAME", fonte_titulo, ROXO_PRINCIPAL, LARGURA//2, 80)
    desenhar_texto("Um jogo criado por WRyan", fonte_texto, AZUL_NEON, LARGURA//2, 140)
    desenhar_texto(f"Recorde: {high_score}", fonte_texto, ROXO_CLARO, LARGURA//2, 190)

    desenhar_texto("CONTROLES", fonte_texto, ROXO_CLARO, LARGURA//2, 255)
    desenhar_texto("Enter - Jogar   |   P - Pausar   |   ESC - Sair", fonte_mini, TEXTO, LARGURA//2, 288)

    desenhar_texto("ITENS DO JOGO", fonte_texto, ROXO_CLARO, LARGURA//2, 350)
    desenhar_legenda(390)

    desenhar_texto("Enter para jogar", fonte_texto, TEXTO, LARGURA//2, 490)
    pygame.display.flip()

def tela_pausa():
    tela.fill(FUNDO)
    desenhar_texto("PAUSADO", fonte_titulo, ROXO_PRINCIPAL, LARGURA//2, 140)
    desenhar_texto("P - Continuar", fonte_texto, AZUL_NEON, LARGURA//2, 220)
    desenhar_texto("ESC - Menu", fonte_texto, TEXTO, LARGURA//2, 262)

    desenhar_texto("ITENS DO JOGO", fonte_texto, ROXO_CLARO, LARGURA//2, 340)
    desenhar_legenda(380)

    pygame.display.flip()

def tela_game_over_func(score):
    tela.fill(FUNDO)
    desenhar_texto("GAME OVER", fonte_titulo, ROXO_PRINCIPAL, LARGURA//2, 140)
    desenhar_texto(f"Pontuação: {score}", fonte_texto, AZUL_NEON, LARGURA//2, 225)
    desenhar_texto(f"Recorde: {high_score}", fonte_texto, ROXO_CLARO, LARGURA//2, 270)
    desenhar_texto("R - Reiniciar", fonte_texto, TEXTO, LARGURA//2, 340)
    desenhar_texto("M - Menu", fonte_texto, TEXTO, LARGURA//2, 385)
    pygame.display.flip()

# ── Loop principal ───────────────────────────────────
async def main():
    global high_score, estado_jogo

    cobra, direcao, proxima_direcao, comida, score, nivel, obstaculos, powerup, com_escudo, escudo_ticks = reiniciar_jogo()
    tempo_movimento = 0

    while True:
        dt = clock.tick(FPS)

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                salvar_highscore(high_score)
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN:
                if estado_jogo == MENU:
                    if evento.key == pygame.K_RETURN:
                        cobra, direcao, proxima_direcao, comida, score, nivel, obstaculos, powerup, com_escudo, escudo_ticks = reiniciar_jogo()
                        estado_jogo = JOGANDO
                    elif evento.key == pygame.K_ESCAPE:
                        salvar_highscore(high_score)
                        pygame.quit()
                        sys.exit()

                elif estado_jogo == JOGANDO:
                    if evento.key == pygame.K_UP    and direcao != "DOWN":  proxima_direcao = "UP"
                    elif evento.key == pygame.K_DOWN  and direcao != "UP":   proxima_direcao = "DOWN"
                    elif evento.key == pygame.K_LEFT  and direcao != "RIGHT": proxima_direcao = "LEFT"
                    elif evento.key == pygame.K_RIGHT and direcao != "LEFT":  proxima_direcao = "RIGHT"
                    elif evento.key == pygame.K_p: estado_jogo = PAUSADO
                    elif evento.key == pygame.K_ESCAPE: estado_jogo = MENU

                elif estado_jogo == PAUSADO:
                    if evento.key == pygame.K_p: estado_jogo = JOGANDO
                    elif evento.key == pygame.K_ESCAPE: estado_jogo = MENU

                elif estado_jogo == GAME_OVER:
                    if evento.key == pygame.K_r:
                        cobra, direcao, proxima_direcao, comida, score, nivel, obstaculos, powerup, com_escudo, escudo_ticks = reiniciar_jogo()
                        estado_jogo = JOGANDO
                    elif evento.key == pygame.K_m: estado_jogo = MENU
                    elif evento.key == pygame.K_ESCAPE:
                        salvar_highscore(high_score)
                        pygame.quit()
                        sys.exit()

        # ── Lógica de jogo ───────────────────────────────
        if estado_jogo == JOGANDO:
            tocar_musica("assets/sounds/game_song.ogg")

            if com_escudo:
                escudo_ticks -= 1
                if escudo_ticks <= 0:
                    com_escudo = False
                    escudo_ticks = 0

            if powerup is None or not powerup.ativo:
                if random.random() < 0.003:
                    powerup = PowerUp(cobra, obstaculos)
                else:
                    powerup = None

            if powerup:
                powerup.atualizar()

            velocidade = velocidade_base(nivel) + (score // 5)
            tempo_movimento += dt

            if tempo_movimento >= 1000 // velocidade:
                tempo_movimento = 0
                direcao = proxima_direcao

                cx, cy = cobra[0]
                if direcao == "UP":    cy -= TAMANHO_BLOCO
                elif direcao == "DOWN":  cy += TAMANHO_BLOCO
                elif direcao == "LEFT":  cx -= TAMANHO_BLOCO
                elif direcao == "RIGHT": cx += TAMANHO_BLOCO

                nova_cabeca = [cx, cy]
                cobra.insert(0, nova_cabeca)

                if powerup and powerup.ativo and nova_cabeca == powerup.posicao:
                    if powerup.tipo == PowerUp.VELOCIDADE:
                        nivel = min(nivel + 1, 10)
                    elif powerup.tipo == PowerUp.PONTOS:
                        score += 5
                    elif powerup.tipo == PowerUp.ESCUDO:
                        com_escudo = True
                        escudo_ticks = 180
                    powerup.ativo = False

                if nova_cabeca == comida:
                    score += 1
                    som_comer.play()
                    comida = gerar_comida(cobra, obstaculos)

                    novo_nivel = 1 + score // 5
                    if novo_nivel != nivel:
                        nivel = novo_nivel
                        obstaculos = gerar_obstaculos(cobra, comida, quantidade_obstaculos(nivel))
                else:
                    cobra.pop()

                cabeca = cobra[0]
                bateu_parede = cabeca[0] < 0 or cabeca[0] >= LARGURA or cabeca[1] < ALTURA_HUD or cabeca[1] >= ALTURA
                bateu_si = cabeca in cobra[1:]
                obs_set = set(map(tuple, obstaculos))
                bateu_obstaculo = tuple(cabeca) in obs_set

                if bateu_parede or bateu_si or (bateu_obstaculo and not com_escudo):
                    if bateu_obstaculo and com_escudo:
                        com_escudo = False
                        escudo_ticks = 0
                    else:
                        if score > high_score:
                            high_score = score
                            salvar_highscore(high_score)
                        som_game_over.play()
                        estado_jogo = GAME_OVER

            tela.fill(FUNDO)
            desenhar_grid()
            desenhar_obstaculos(obstaculos)
            desenhar_cobra(cobra, direcao, com_escudo)
            desenhar_comida(comida)
            if powerup and powerup.ativo:
                powerup.desenhar()
            desenhar_hud(score, nivel, com_escudo, escudo_ticks)
            pygame.display.flip()

        elif estado_jogo == MENU:
            tocar_musica("assets/sounds/menu_song.ogg")
            tela_menu()

        elif estado_jogo == GAME_OVER:
            tocar_musica("assets/sounds/menu_song.ogg")
            tela_game_over_func(score)

        elif estado_jogo == PAUSADO:
            tela_pausa()

        await asyncio.sleep(0)


asyncio.run(main())
