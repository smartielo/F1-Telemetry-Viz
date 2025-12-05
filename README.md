# 🏎️ F1 Telemetry Visualizer

Uma aplicação Desktop desenvolvida em Python que processa dados reais de telemetria da Fórmula 1 e gera simulações visuais ("Ghost Replays") de qualquer corrida da história recente.

![Status](https://img.shields.io/badge/Status-Completed-success)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)

## 🎯 Sobre o Projeto

Este projeto foi desenvolvido com o objetivo de aplicar conceitos de **Engenharia de Dados** e **Computação Gráfica**. A aplicação consome a API da biblioteca `FastF1`, processa gigabytes de dados de telemetria (velocidade, coordenadas GPS, tempo), e renderiza uma batalha visual entre pilotos em tempo real.

O sistema permite que o usuário compare traçados de diferentes pilotos, visualizando onde cada um ganha ou perde tempo na pista.

## ✨ Funcionalidades

- **Launcher GUI:** Interface gráfica (Tkinter) para seleção de Ano, Grande Prêmio e Sessão (Treino, Classificação ou Corrida).
- **Seleção Multi-Piloto:** Escolha e compare qualquer combinação de pilotos (ex: Hamilton vs Verstappen).
- **Renderização da Pista:** Mapeamento dinâmico de coordenadas GPS (Latitude/Longitude) para Coordenadas de Tela (Pixels) mantendo o Aspect Ratio real do circuito.
- **Playback Controls:** Pause, Acelere (até 4x) ou reduza a velocidade da simulação.
- **Leaderboard em Tempo Real:** Painel lateral com atualizações de status.

## 🛠️ Tecnologias Utilizadas

- **Python 3:** Linguagem base.
- **FastF1:** Extração e cache de dados oficiais da F1.
- **Pandas & NumPy:** Manipulação de DataFrames e cálculos vetoriais (Busca Binária para sincronização de tempo).
- **Arcade:** Engine gráfica para renderização 2D de alta performance (60 FPS).
- **Tkinter:** Interface nativa para o menu de configuração.

## 🚀 Como Rodar

1. Clone o repositório:
   ```bash
   git clone [https://github.com/smartielo/f1-telemetry-viz.git]
   (https://github.com/smartielo/f1-telemetry-viz.git)
   cd f1-telemetry-viz

2. Crie um ambiente virtual e instale as dependências:
  ```bash
  python -m venv .venv
  source .venv/bin/activate  # No Windows: .venv\Scripts\activate
  pip install fastf1 pandas numpy arcade
 ```

3. Execute o Launcher:
  ```bash
  python launcher.py
 ```

##  🧠 Desafios Técnicos Resolvidos
Mapeamento de Coordenadas (World to Screen)
Um dos maiores desafios foi converter as coordenadas geográficas (que variam em milhares de metros) para a janela de 1200x800 pixels sem distorcer o traçado. Foi implementada uma lógica de normalização linear com preservação de escala:

```bash
scale = min(screen_width / track_width, screen_height / track_height)
screen_x = (world_x - min_x) * scale + offset_x
 ```

## 📄 Licença
Este projeto é para fins educacionais. Os dados pertencem à Fórmula 1.
Feito com 🏁 por Gabriel Martielo
