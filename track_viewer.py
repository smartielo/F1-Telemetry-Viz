import arcade
import fastf1
import pandas as pd
import numpy as np

# Configurações Visuais
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
BG_COLOR = arcade.color.BLACK
TRACK_COLOR = arcade.color.WHITE_SMOKE
UI_BG_COLOR = arcade.color.CHARCOAL

# Cores genéricas para pilotos (pode expandir depois)
COLORS = [
    arcade.color.RED, arcade.color.BLUE, arcade.color.GREEN, arcade.color.YELLOW,
    arcade.color.ORANGE, arcade.color.PURPLE, arcade.color.CYAN, arcade.color.MAGENTA,
    arcade.color.LIME, arcade.color.PINK, arcade.color.TEAL, arcade.color.GOLD
]


class Car:
    def __init__(self, driver_code, team_name, telemetry_data, color_index):
        self.driver_code = driver_code
        self.team_name = team_name
        self.color = COLORS[color_index % len(COLORS)]  # Escolhe cor ciclicamente

        self.telemetry = telemetry_data
        if 'TimeSeconds' not in self.telemetry.columns:
            self.telemetry['TimeSeconds'] = self.telemetry['Time'].dt.total_seconds()

        self.times = self.telemetry['TimeSeconds'].values
        self.x = -1000
        self.y = -1000
        self.max_time = self.times[-1]

    def update_position(self, current_time, map_scale, offsets, min_x, min_y):
        loop_time = current_time % self.max_time
        idx = np.searchsorted(self.times, loop_time)
        if idx >= len(self.telemetry): idx = len(self.telemetry) - 1

        row = self.telemetry.iloc[idx]
        self.x = (row['X'] - min_x) * map_scale + offsets[0]
        self.y = (row['Y'] - min_y) * map_scale + offsets[1]

    def draw(self):
        if self.x > -900:
            arcade.draw_circle_filled(self.x, self.y, 6, self.color)
            arcade.draw_text(self.driver_code, self.x + 8, self.y + 8, self.color, 10, bold=True)


class F1Window(arcade.Window):
    def __init__(self, year, race, session_type, selected_drivers):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, f"F1 Replay: {year} {race}")
        arcade.set_background_color(BG_COLOR)

        # Parâmetros recebidos do Launcher
        self.year = year
        self.race = race.split(" - ")[1] if " - " in race else race
        self.session_type = session_type
        self.selected_drivers = selected_drivers

        self.cars = []
        self.track_points = []
        self.time_elapsed = 0.0
        self.speed_multiplier = 1.0
        self.paused = False

    def setup(self):
        # Carrega a sessão completa com telemetria
        fastf1.Cache.enable_cache('cache')
        session = fastf1.get_session(self.year, self.race, self.session_type)
        session.load()

        # 1. Desenha Pista (Usa volta mais rapida geral como referencia)
        fastest = session.laps.pick_fastest()
        ref_tel = fastest.get_telemetry()
        x_s, y_s = ref_tel['X'].values, ref_tel['Y'].values

        self.min_x, max_x = x_s.min(), x_s.max()
        self.min_y, max_y = y_s.min(), y_s.max()

        # Area de desenho (deixa 250px para UI lateral)
        draw_w = SCREEN_WIDTH - 250
        scale_x = (draw_w - 100) / (max_x - self.min_x)
        scale_y = (SCREEN_HEIGHT - 100) / (max_y - self.min_y)
        self.map_scale = min(scale_x, scale_y)

        self.ox = (draw_w - (max_x - self.min_x) * self.map_scale) / 2
        self.oy = (SCREEN_HEIGHT - (max_y - self.min_y) * self.map_scale) / 2

        self.track_points = []
        for x, y in zip(x_s, y_s):
            self.track_points.append(
                ((x - self.min_x) * self.map_scale + self.ox, (y - self.min_y) * self.map_scale + self.oy))

        # 2. Carrega Pilotos Selecionados
        print(f"Carregando {len(self.selected_drivers)} pilotos...")
        for i, drv in enumerate(self.selected_drivers):
            try:
                # Se for corrida, pega todas as voltas ou a mais rapida?
                # Vamos pegar a volta mais rápida de cada um para comparar performance pura
                d_laps = session.laps.pick_drivers(drv).pick_fastest()
                tel = d_laps.get_telemetry()
                team = d_laps['Team']
                self.cars.append(Car(drv, team, tel, i))
            except:
                pass

    def on_update(self, delta_time):
        if not self.paused:
            self.time_elapsed += delta_time * self.speed_multiplier
            for car in self.cars:
                car.update_position(self.time_elapsed, self.map_scale, (self.ox, self.oy), self.min_x, self.min_y)

    def on_draw(self):
        self.clear()
        if self.track_points:
            arcade.draw_line_strip(self.track_points, TRACK_COLOR, 2)
        for car in self.cars:
            car.draw()

        # UI Lateral
        arcade.draw_lrbt_rectangle_filled(SCREEN_WIDTH - 250, SCREEN_WIDTH, 0, SCREEN_HEIGHT, UI_BG_COLOR)
        arcade.draw_text("Leaderboard", SCREEN_WIDTH - 230, SCREEN_HEIGHT - 40, arcade.color.WHITE, 14, bold=True)

        y = SCREEN_HEIGHT - 80
        for car in self.cars:
            arcade.draw_text(f"{car.driver_code}", SCREEN_WIDTH - 230, y, car.color, 12, bold=True)
            y -= 25

        arcade.draw_text(f"Time: {self.time_elapsed:.1f}s", SCREEN_WIDTH - 230, 100, arcade.color.WHITE, 12)
        arcade.draw_text(f"Speed: {self.speed_multiplier:.1f}x", SCREEN_WIDTH - 230, 80, arcade.color.GREEN, 12)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.SPACE:
            self.paused = not self.paused
        elif key == arcade.key.UP:
            self.speed_multiplier += 0.5
        elif key == arcade.key.DOWN:
            self.speed_multiplier = max(0.5, self.speed_multiplier - 0.5)


def start_visualization(year, race, session, drivers):
    window = F1Window(year, race, session, drivers)
    window.setup()
    arcade.run()