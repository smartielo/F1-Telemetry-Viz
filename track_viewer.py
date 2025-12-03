import arcade
import fastf1
import pandas as pd
import numpy as np


# Configurações da Janela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "F1 Telemetry Viewer - Interlagos"

# Cores
BG_COLOR = arcade.color.BLACK #background color
TRACK_COLOR = arcade.color.WHITE #track color
CAR_COLOR = arcade.color.RED #car color

class F1Window(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BG_COLOR)

        # Onde vamos guardar as coordenadas processadas
        self.track_points = []
        self.map_scale = 1.0  # Inicializamos com um valor padrão
        self.offsets = (0, 0)  # x_offset, y_offset

        # Variáveis de Animação
        self.telemetry_data = None  # Vai guardar o DataFrame com os dados
        self.time_elapsed = 0.0  # Relógio interno da nossa simulação (em segundos)
        self.car_position = (0, 0)  # Posição X,Y atual do carro na tela

    def setup(self):
        """ Aqui carregamos os dados e fazemos a matemática pesada """
        print("Baixando dados...")
        fastf1.Cache.enable_cache('cache')
        session = fastf1.get_session(2023, 'Brazil', 'R')
        session.load()

        # Pegamos a volta mais rápida
        lap = session.laps.pick_fastest()
        self.telemetry_data = lap.get_telemetry()
        self.telemetry_data['TimeSeconds'] = self.telemetry_data['Time'].dt.total_seconds()

        # Dados brutos (Mundo)
        x_series = self.telemetry_data['X'].values
        y_series = self.telemetry_data['Y'].values

        # --- MATEMÁTICA DE ESCALA ---
        # 1. Encontrar os limites do mapa
        min_x, max_x = x_series.min(), x_series.max()
        min_y, max_y = y_series.min(), y_series.max()

        track_width_m = max_x - min_x
        track_height_m = max_y - min_y

        # 2. Definir a escala (Renomeado para map_scale)
        scale_x = (SCREEN_WIDTH - 100) / track_width_m
        scale_y = (SCREEN_HEIGHT - 100) / track_height_m

        self.map_scale = min(scale_x, scale_y)

        # 3. Centralizar a pista
        # Usamos self.map_scale aqui
        x_center_offset = (SCREEN_WIDTH - (track_width_m * self.map_scale)) / 2
        y_center_offset = (SCREEN_HEIGHT - (track_height_m * self.map_scale)) / 2
        self.offsets = (x_center_offset, y_center_offset)  # Guardamos para usar na animação

        # 4. Transformar todos os pontos
        print("Processando coordenadas...")
        self.track_points = []
        for x, y in zip(x_series, y_series):
            sx, sy = self.world_to_screen(x, y, min_x, min_y)
            self.track_points.append((sx, sy))
        self.min_x = min_x
        self.min_y = min_y

    def world_to_screen(self, x, y, min_x, min_y):
        """ Função auxiliar para converter coordenadas """
        sx = (x - min_x) * self.map_scale + self.offsets[0]
        sy = (y - min_y) * self.map_scale + self.offsets[1]
        return sx, sy

    def on_update(self, delta_time):
        """ Lógica do jogo: chamada a cada frame (aprox 1/60s) """
        if self.telemetry_data is None:
            return

        # 1. Avança o relógio da simulação
        # Multiplique por 2 ou 4 se quiser acelerar (ex: delta_time * 2)
        self.time_elapsed += delta_time

        # 2. Encontra a linha de dados mais próxima do tempo atual
        # Usamos busca binária (searchsorted) do Numpy que é MUITO rápida
        times = self.telemetry_data['TimeSeconds'].values

        # Se o tempo passou do final da volta, reseta (loop)
        if self.time_elapsed > times[-1]:
            self.time_elapsed = 0

        # Acha o índice do dado mais próximo
        idx = np.searchsorted(times, self.time_elapsed)

        # Evita erro de índice no final do array
        if idx >= len(self.telemetry_data):
            idx = len(self.telemetry_data) - 1

        # 3. Pega as coordenadas X, Y daquele momento
        row = self.telemetry_data.iloc[idx]
        world_x = row['X']
        world_y = row['Y']

        # 4. Converte para tela e atualiza a posição do carro
        self.car_position = self.world_to_screen(world_x, world_y, self.min_x, self.min_y)

    def on_draw(self):
        self.clear()

        # Desenha a pista
        if self.track_points:
            arcade.draw_line_strip(self.track_points, TRACK_COLOR, 3)

        # Desenha o carro (Círculo Vermelho)
        cx, cy = self.car_position
        # O carro só aparece se tivermos coordenadas válidas
        if cx > 0 and cy > 0:
            arcade.draw_circle_filled(cx, cy, 5, CAR_COLOR)  # Raio 5

if __name__ == "__main__":
    app = F1Window()
    app.setup()
    arcade.run()