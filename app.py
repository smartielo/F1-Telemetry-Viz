import fastf1
import os

cache_dir = 'cache'
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
fastf1.Cache.enable_cache(cache_dir)

print("Carregando dados da pista...")
session = fastf1.get_session(2023, 'Brazil', 'R')
session.load()

# A lógica é: pegar a volta mais rápida da corrida inteira.
# O caminho que esse piloto fez será o desenho da pista.
print("Calculando traçado ideal...")
lap = session.laps.pick_fastest()
telemetry = lap.get_telemetry() # Aqui baixamos X, Y, Z, Velocidade, RPM, etc.


print(telemetry[['X', 'Y', 'Speed', 'nGear']].head()) # X e Y são as coordenadas em metros (sistema da FIA)