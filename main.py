import pygame
import sys
import random

pygame.init()

pygame.mixer.init()

som_comer = pygame.mixer.Sound("assets/sounds/eat.wav")
som_game_over = pygame.mixer.Sound("assets/sounds/game_over.wav")

musica_atual = None

def tocar_musica(caminho):
    global musica_atual

    if musica_atual != caminho:
        pygame.mixer.music.load(caminho)
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
        musica_atual = caminho

# =========================
# CONFIGURAÇÕES GERAIS
# =========================
LARGURA = 800
ALTURA = 600
TAMANHO_BLOCO = 20
FPS = 10

# Área da HUD
ALTURA_HUD = 70

# Cores - tema cyberpunk
FUNDO = (10, 8, 20)
FUNDO_HUD = (18, 14, 36)
TEXTO = (235, 235, 245)

ROXO_PRINCIPAL = (196, 11, 255)      # #c40bff
ROXO_CLARO = (220, 120, 255)
ROXO_ESCURO = (110, 20, 150)

AZUL_NEON = (0, 246, 249)            # #00f6f9
AZUL_CLARO = (120, 250, 255)
AZUL_ESCURO = (0, 120, 140)

GRID = (40, 26, 60)
PRETO = (0, 0, 0)

# Tela
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Snake Game")

# Relógio
clock = pygame.time.Clock()

# Fontes
fonte_titulo = pygame.font.SysFont("arial", 48, bold=True)
fonte_texto = pygame.font.SysFont("arial", 28)
fonte_score = pygame.font.SysFont("arial", 24)

# Estados do jogo
MENU = "menu"
JOGANDO = "jogando"
GAME_OVER = "game_over"
PAUSADO = "pausado"

estado_jogo = MENU
high_score = 0

def desenhar_texto(texto, fonte, cor, x, y, centralizar=True):
    superficie = fonte.render(texto, True, cor)
    rect = superficie.get_rect()

    if centralizar:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    tela.blit(superficie, rect)


def tela_menu():
    tela.fill(FUNDO)

    desenhar_texto("SNAKE GAME", fonte_titulo, ROXO_PRINCIPAL, LARGURA // 2, 100)
    desenhar_texto("Um jogo criado por WRyan", fonte_texto, AZUL_NEON, LARGURA // 2, 170)
    desenhar_texto("CONTROLES", fonte_texto, ROXO_CLARO, LARGURA // 2, 250)
    desenhar_texto("Enter - Jogar", fonte_texto, TEXTO, LARGURA // 2, 300)
    desenhar_texto("Setas - Mover", fonte_texto, TEXTO, LARGURA // 2, 340)
    desenhar_texto("P - Pausar", fonte_texto, TEXTO, LARGURA // 2, 380)
    desenhar_texto("ESC - Sair", fonte_texto, TEXTO, LARGURA // 2, 420)

    pygame.display.flip()


def gerar_comida(cobra):
    while True:
        x = random.randrange(0, LARGURA, TAMANHO_BLOCO)
        y = random.randrange(ALTURA_HUD, ALTURA, TAMANHO_BLOCO)

        if [x, y] not in cobra:
            return [x, y]


def reiniciar_jogo():
    posicao_inicial_y = ALTURA_HUD + 100

    cobra = [
        [LARGURA // 2, posicao_inicial_y],
        [LARGURA // 2 - TAMANHO_BLOCO, posicao_inicial_y],
        [LARGURA // 2 - (TAMANHO_BLOCO * 2), posicao_inicial_y]
    ]

    direcao = "RIGHT"
    proxima_direcao = "RIGHT"
    comida = gerar_comida(cobra)
    score = 0

    return cobra, direcao, proxima_direcao, comida, score




def desenhar_comida(comida):
    centro_x = comida[0] + TAMANHO_BLOCO // 2
    centro_y = comida[1] + TAMANHO_BLOCO // 2
    raio = TAMANHO_BLOCO // 2 - 2

    pygame.draw.circle(tela, AZUL_NEON, (centro_x, centro_y), raio)
    pygame.draw.circle(tela, AZUL_CLARO, (centro_x, centro_y), raio // 2)


def desenhar_score(score):
    pygame.draw.rect(tela, FUNDO_HUD, (0, 0, LARGURA, ALTURA_HUD))
    pygame.draw.line(tela, ROXO_PRINCIPAL, (0, ALTURA_HUD), (LARGURA, ALTURA_HUD), 2)

    texto_score = fonte_score.render(f"Score: {score}", True, AZUL_NEON)
    texto_recorde = fonte_score.render(f"Recorde: {high_score}", True, ROXO_CLARO)

    tela.blit(texto_score, (20, 15))
    tela.blit(texto_recorde, (20, 40))


def atualizar_cobra(cobra, direcao, comida, score):
    cabeca_x = cobra[0][0]
    cabeca_y = cobra[0][1]

    if direcao == "UP":
        cabeca_y -= TAMANHO_BLOCO
    elif direcao == "DOWN":
        cabeca_y += TAMANHO_BLOCO
    elif direcao == "LEFT":
        cabeca_x -= TAMANHO_BLOCO
    elif direcao == "RIGHT":
        cabeca_x += TAMANHO_BLOCO

    nova_cabeca = [cabeca_x, cabeca_y]
    cobra.insert(0, nova_cabeca)

    if nova_cabeca == comida:
        score += 1
        comida = gerar_comida(cobra)
        som_comer.play()
    else:
        cobra.pop()

    return cobra, comida, score


def verificar_colisao(cobra):
    cabeca = cobra[0]

    if cabeca[0] < 0 or cabeca[0] >= LARGURA:
        return True

    if cabeca[1] < ALTURA_HUD or cabeca[1] >= ALTURA:
        return True

    if cabeca in cobra[1:]:
        return True

    return False


def desenhar_grid():
    for x in range(0, LARGURA, TAMANHO_BLOCO):
        pygame.draw.line(tela, GRID, (x, ALTURA_HUD), (x, ALTURA))

    for y in range(ALTURA_HUD, ALTURA, TAMANHO_BLOCO):
        pygame.draw.line(tela, GRID, (0, y), (LARGURA, y))


def tela_jogo(cobra, comida, score, direcao):
    tela.fill(FUNDO)
    desenhar_grid()
    desenhar_cobra(cobra, direcao)
    desenhar_comida(comida)
    desenhar_score(score)
    pygame.display.flip()

def tela_game_over(score):
    tela.fill(FUNDO)

    desenhar_texto("GAME OVER", fonte_titulo, ROXO_PRINCIPAL, LARGURA // 2, 160)
    desenhar_texto(f"Pontuação: {score}", fonte_texto, AZUL_NEON, LARGURA // 2, 240)
    desenhar_texto(f"Recorde: {high_score}", fonte_texto, ROXO_CLARO, LARGURA // 2, 285)
    desenhar_texto("R - Reiniciar", fonte_texto, TEXTO, LARGURA // 2, 350)
    desenhar_texto("M - Voltar ao menu", fonte_texto, TEXTO, LARGURA // 2, 395)
    desenhar_texto("ESC - Sair", fonte_texto, TEXTO, LARGURA // 2, 440)

    pygame.display.flip()

def tela_pausa():
    tela.fill(FUNDO)

    desenhar_texto("PAUSADO", fonte_titulo, ROXO_PRINCIPAL, LARGURA // 2, 200)
    desenhar_texto("Pressione P para continuar", fonte_texto, AZUL_NEON, LARGURA // 2, 300)
    desenhar_texto("ESC - Menu", fonte_texto, TEXTO, LARGURA // 2, 350)

    pygame.display.flip()

def desenhar_cobra(cobra, direcao):
    for i, segmento in enumerate(cobra):
        x, y = segmento

        if i == 0:
            pygame.draw.rect(
                tela,
                ROXO_CLARO,
                (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO),
                border_radius=4
            )

            # olhos apontando para a direção
            if direcao == "RIGHT":
                olho1 = (x + 13, y + 6)
                olho2 = (x + 13, y + 14)
                lingua_inicio = (x + TAMANHO_BLOCO, y + TAMANHO_BLOCO // 2)
                lingua_fim = (x + TAMANHO_BLOCO + 10, y + TAMANHO_BLOCO // 2)

            elif direcao == "LEFT":
                olho1 = (x + 7, y + 6)
                olho2 = (x + 7, y + 14)
                lingua_inicio = (x, y + TAMANHO_BLOCO // 2)
                lingua_fim = (x - 10, y + TAMANHO_BLOCO // 2)

            elif direcao == "UP":
                olho1 = (x + 6, y + 7)
                olho2 = (x + 14, y + 7)
                lingua_inicio = (x + TAMANHO_BLOCO // 2, y)
                lingua_fim = (x + TAMANHO_BLOCO // 2, y - 10)

            else:  # DOWN
                olho1 = (x + 6, y + 13)
                olho2 = (x + 14, y + 13)
                lingua_inicio = (x + TAMANHO_BLOCO // 2, y + TAMANHO_BLOCO)
                lingua_fim = (x + TAMANHO_BLOCO // 2, y + TAMANHO_BLOCO + 10)

            pygame.draw.circle(tela, PRETO, olho1, 2)
            pygame.draw.circle(tela, PRETO, olho2, 2)

            # linguinha "mexendo"
            tempo = pygame.time.get_ticks() // 120
            if tempo % 2 == 0:
                pygame.draw.line(tela, AZUL_NEON, lingua_inicio, lingua_fim, 2)

                if direcao in ["RIGHT", "LEFT"]:
                    pygame.draw.line(
                        tela,
                        AZUL_NEON,
                        lingua_fim,
                        (lingua_fim[0], lingua_fim[1] - 4),
                        2
                    )
                    pygame.draw.line(
                        tela,
                        AZUL_NEON,
                        lingua_fim,
                        (lingua_fim[0], lingua_fim[1] + 4),
                        2
                    )
                else:
                    pygame.draw.line(
                        tela,
                        AZUL_NEON,
                        lingua_fim,
                        (lingua_fim[0] - 4, lingua_fim[1]),
                        2
                    )
                    pygame.draw.line(
                        tela,
                        AZUL_NEON,
                        lingua_fim,
                        (lingua_fim[0] + 4, lingua_fim[1]),
                        2
                    )

        else:
            pygame.draw.rect(
                tela,
                ROXO_PRINCIPAL,
                (x, y, TAMANHO_BLOCO, TAMANHO_BLOCO),
                border_radius=4
            )


cobra, direcao, proxima_direcao, comida, score = reiniciar_jogo()
tempo_movimento = 0

while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN:
            if estado_jogo == MENU:
                if evento.key == pygame.K_RETURN:
                    cobra, direcao, proxima_direcao, comida, score = reiniciar_jogo()
                    estado_jogo = JOGANDO
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            elif estado_jogo == JOGANDO:
                if evento.key == pygame.K_UP and direcao != "DOWN":
                    proxima_direcao = "UP"
                elif evento.key == pygame.K_DOWN and direcao != "UP":
                    proxima_direcao = "DOWN"
                elif evento.key == pygame.K_LEFT and direcao != "RIGHT":
                    proxima_direcao = "LEFT"
                elif evento.key == pygame.K_RIGHT and direcao != "LEFT":
                    proxima_direcao = "RIGHT"
                elif evento.key == pygame.K_p:
                    estado_jogo = PAUSADO
                elif evento.key == pygame.K_ESCAPE:
                    estado_jogo = MENU

            elif estado_jogo == PAUSADO:
                if evento.key == pygame.K_p:
                    estado_jogo = JOGANDO
                elif evento.key == pygame.K_ESCAPE:
                    estado_jogo = MENU

                    

            elif estado_jogo == GAME_OVER:
                if evento.key == pygame.K_r:
                    cobra, direcao, proxima_direcao, comida, score = reiniciar_jogo()
                    estado_jogo = JOGANDO
                elif evento.key == pygame.K_m:
                    estado_jogo = MENU
                elif evento.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


    if estado_jogo == MENU:
        tocar_musica("assets/sounds/menu_song.mp3")
        tela_menu()

    elif estado_jogo == JOGANDO:
        tocar_musica("assets/sounds/game_song.mp3")
        tempo_movimento += clock.get_time()

        velocidade = 10 + (score // 5)

        if tempo_movimento >= 1000 // velocidade:
            tempo_movimento = 0
            direcao = proxima_direcao
            cobra, comida, score = atualizar_cobra(cobra, direcao, comida, score)

        if verificar_colisao(cobra):
            if score > high_score:
                high_score = score
            som_game_over.play()
            estado_jogo = GAME_OVER

        tela_jogo(cobra, comida, score, direcao)

    elif estado_jogo == GAME_OVER:
        tocar_musica("assets/sounds/menu_song.mp3")
        tela_game_over(score)
    elif estado_jogo == PAUSADO:
        tela_pausa()

    clock.tick(60)