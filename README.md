# 🐍 Snake Game - Cyberpunk Edition

Jogo 2D desenvolvido em Python com **Pygame**, visual cyberpunk neon, power-ups, obstáculos e high score persistido.

---

## 🎮 Funcionalidades

- Menu com legenda visual dos itens do jogo
- Power-ups com formas e cores distintas
- Obstáculos que aumentam a cada nível
- High score salvo em arquivo (persiste entre sessões)
- Dificuldade progressiva (velocidade e obstáculos por nível)
- Sistema de pausa com legenda
- HUD com score, recorde, nível e barra de escudo
- Animação da cobra (olhos e língua dinâmica)
- Efeitos sonoros e música dinâmica (menu / gameplay)

---

## ⚡ Power-ups

| Visual | Nome | Efeito |
|---|---|---|
| Círculo amarelo | Velocidade | Sobe um nível imediatamente |
| Círculo verde | +5 Pontos | Bônus direto de pontuação |
| Círculo azul | Escudo | Protege 1 batida em obstáculo |

---

## 🔴 Obstáculos

Blocos vermelhos fixos no mapa. Aparecem a partir do nível 1 e aumentam a cada nível (máx 20). Bater neles sem escudo = game over.

---

## 🕹️ Controles

- **Enter** → Iniciar o jogo
- **Setas (↑ ↓ ← →)** → Movimentar a cobra
- **P** → Pausar / Despausar
- **ESC** → Voltar ao menu / sair
- **R** → Reiniciar após Game Over
- **M** → Voltar ao menu após Game Over

---

## ⚙️ Tecnologias

- Python 3
- Pygame

---

## 📦 Como executar

```bash
pip install pygame
python main.py
```

---

## 📌 Observações

Mantenha a pasta `assets` junto do executável para funcionamento correto dos sons e músicas.

---

Desenvolvido por WRyan  
🔗 [LinkedIn](https://www.linkedin.com/in/wryan-lopes)  
🌐 [Portfólio](https://ryan-wes.github.io/portfolio/)
