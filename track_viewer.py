import arcade
import fastf1
import pandas as pd
import numpy as np

# --- CONFIGURAÇÕES VISUAIS ---
SCREEN_WIDTH = 1000  # Aumentei para caber o menu lateral
SCREEN_HEIGHT = 600
SCREEN_TITLE = "F1 Telemetry: Brazil 2023 Analysis"
BG_COLOR = arcade.color.BLACK
TRACK_COLOR = arcade.color.WHITE_SMOKE
UI_BG_COLOR = arcade.color.CHARCOAL

# Cores das Equipes
TEAM_COLORS = {
    'Red Bull Racing': arcade.color.RED_DEVIL,
    'McLaren': arcade.color.ORANGE_PEEL,
    'Ferrari': arcade.color.YELLOW,
    'Mercedes': arcade.color.CYAN,
    'Aston Martin': arcade.color.BRITISH_RACING_GREEN,
}


class Car:
    def __init__(self, driver_code, team_name, telemetry_data):
        self.driver_code = driver_code
        self.team_name = team_name
        self.color = TEAM_COLORS.get(team_name, arcade.color.GRAY)

        # Dados
        self.telemetry = telemetry_data
        if 'TimeSeconds' not in self.telemetry.columns:
            self.telemetry['TimeSeconds'] = self.telemetry['Time'].dt.total_seconds()

        self.times = self.telemetry['TimeSeconds'].values
        self.x = -100
        self.y = -100

        # Para suavizar o movimento (lerp)
        self.max_time = self.times[-1]

    def update_position(self, current_time, map_scale, offsets, min_x, min_y):
        # Loop infinito da volta
        loop_time = current_time % self.max_time

        # Busca binária
        idx = np.searchsorted(self.times, loop_time)
        if idx >= len(self.telemetry):
            idx = len(self.telemetry) - 1

        row = self.telemetry.iloc[idx]

        # Conversão Mundo -> Tela
        world_x = row['X']
        world_y = row['Y']

        target_x = (world_x - min_x) * map_scale + offsets[0]
        target_y = (world_y - min_y) * map_scale + offsets[1]

        # Atualização direta (sem interpolação complexa por enquanto)
        self.x = target_x
        self.y = target_y

    def draw(self):
        if self.x > 0:
            arcade.draw_circle_filled(self.x, self.y, 8, self.color)
            # Texto pequeno com nome
            arcade.draw_text(self.driver_code, self.x + 10, self.y + 10, self.color, 9, bold=True)


class F1Window(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(BG_COLOR)

        self.track_points = []
        self.cars = []

        # Estado da Simulação
        self.time_elapsed = 0.0
        self.speed_multiplier = 1.0  # 1x velocidade normal
        self.paused = False

        # Variáveis de escala
        self.map_scale = 1.0
        self.offsets = (0, 0)
        self.min_x = 0
        self.min_y = 0

    def setup(self):
        print("--- INICIANDO TELEMETRIA F1 ---")
        fastf1.Cache.enable_cache('cache')
        session = fastf1.get_session(2023, 'Brazil', 'R')
        session.load()

        # 1. Configurar Pista (Baseado no Verstappen)
        print("Calculando geometria da pista...")
        fastest_lap = session.laps.pick_fastest()
        ref_tel = fastest_lap.get_telemetry()

        x_series = ref_tel['X'].values
        y_series = ref_tel['Y'].values

        self.min_x, max_x = x_series.min(), x_series.max()
        self.min_y, max_y = y_series.min(), y_series.max()

        # Deixa espaço para o menu lateral (800px para pista, 200px para menu)
        track_area_width = 800

        track_width = max_x - self.min_x
        track_height = max_y - self.min_y

        scale_x = (track_area_width - 100) / track_width
        scale_y = (SCREEN_HEIGHT - 100) / track_height
        self.map_scale = min(scale_x, scale_y)

        ox = (track_area_width - track_width * self.map_scale) / 2
        oy = (SCREEN_HEIGHT - track_height * self.map_scale) / 2
        self.offsets = (ox, oy)

        # Gera o desenho da pista
        self.track_points = []
        for x, y in zip(x_series, y_series):
            sx = (x - self.min_x) * self.map_scale + ox
            sy = (y - self.min_y) * self.map_scale + oy
            self.track_points.append((sx, sy))

        # 2. Carregar Pilotos (Top 5)
        drivers = ['NOR', 'VER', 'ALO', 'STR', 'HAM']
        print(f"Carregando pilotos: {drivers}")

        for driver in drivers:
            try:
                d_lap = session.laps.pick_driver(driver).pick_fastest()
                d_tel = d_lap.get_telemetry()
                team = d_lap['Team']
                self.cars.append(Car(driver, team, d_tel))
            except:
                print(f"Erro ao carregar {driver}")

    def on_update(self, delta_time):
        if self.paused:
            return

        # Aplica o multiplicador de velocidade
        self.time_elapsed += delta_time * self.speed_multiplier

        for car in self.cars:
            car.update_position(self.time_elapsed, self.map_scale, self.offsets, self.min_x, self.min_y)

    def on_draw(self):
        self.clear()

        # 1. Desenha a Pista
        if self.track_points:
            arcade.draw_line_strip(self.track_points, TRACK_COLOR, 2)

        # 2. Desenha os Carros
        for car in self.cars:
            car.draw()

        # 3. Desenha a Interface (UI) - Menu Lateral
        # Fundo do menu
        arcade.draw_lrbt_rectangle_filled(800, SCREEN_WIDTH, 0, SCREEN_HEIGHT, UI_BG_COLOR)

        # Título do Menu
        arcade.draw_text("LEADERBOARD", 820, SCREEN_HEIGHT - 40, arcade.color.WHITE, 14, bold=True)

        # Lista de Pilotos (Manual por enquanto)
        y_pos = SCREEN_HEIGHT - 80
        for car in self.cars:
            # Nome e Equipe
            arcade.draw_text(f"{car.driver_code}", 820, y_pos, arcade.color.WHITE, 12, bold=True)
            arcade.draw_text(f"{car.team_name}", 860, y_pos, car.color, 10)
            y_pos -= 30

        # --- CONTROLES E STATUS ---
        y_bottom = 100
        arcade.draw_text(f"Tempo: {self.time_elapsed:.2f}s", 820, y_bottom, arcade.color.WHITE, 12)
        arcade.draw_text(f"Velocidade: {self.speed_multiplier:.1f}x", 820, y_bottom - 20, arcade.color.GREEN, 12)

        status = "PAUSADO" if self.paused else "RODANDO"
        arcade.draw_text(f"Status: {status}", 820, y_bottom - 40,
                         arcade.color.YELLOW if self.paused else arcade.color.GREEN, 12)

        # Instruções
        arcade.draw_text("[ESPAÇO] Pausar", 820, 40, arcade.color.GRAY, 10)
        arcade.draw_text("[CIMA/BAIXO] Velocidade", 820, 20, arcade.color.GRAY, 10)

    def on_key_press(self, key, modifiers):
        """ Controle de Teclado """

        if key == arcade.key.SPACE:
            self.paused = not self.paused

        elif key == arcade.key.UP:
            self.speed_multiplier += 0.5

        elif key == arcade.key.DOWN:
            self.speed_multiplier -= 0.5
            if self.speed_multiplier < 0.5: self.speed_multiplier = 0.5


if __name__ == "__main__":
    app = F1Window()
    app.setup()
    arcade.run()