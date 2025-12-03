import fastf1 #importa a biblioteca que vamos trabalhar
import os #importa ferramentas para trabalhar com windows e linux

cache_dir = 'cache' #define o nome da pasta

if not os.path.exists(cache_dir): #se ela não existe, ela é criada
    os.makedirs(cache_dir)

fastf1.Cache.enable_cache('cache')

session = fastf1.get_session(2023, 'Brazil', 'R') #carrega os dados da corrida do Brasil de 2023

print("Carregando dados...")
session.load()

ver_laps = session.laps.pick_driver('VER') #seleciona as primeiras 5 voltas do Max
print(ver_laps) #printa as voltas

