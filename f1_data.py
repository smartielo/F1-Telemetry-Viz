import fastf1

# Configura cache globalmente
fastf1.Cache.enable_cache('cache')


def get_schedule(year):
    """ Retorna a lista de corridas de um ano """
    try:
        schedule = fastf1.get_event_schedule(year)
        # Filtra apenas corridas oficiais (exclui testes)
        # Retorna uma lista de tuplas: (Round, Nome da Corrida, Data)
        races = []
        for index, row in schedule.iterrows():
            races.append(f"{row['RoundNumber']} - {row['EventName']}")
        return races
    except Exception as e:
        return [f"Erro: {e}"]


def get_drivers_from_session(year, race_name, session_type):
    """ Carrega a sessão leve apenas para pegar a lista de pilotos """
    try:
        # Pega o número do round ou nome da string "1 - Bahrain GP"
        if " - " in race_name:
            race_name = race_name.split(" - ")[1]

        session = fastf1.get_session(year, race_name, session_type)
        session.load(telemetry=False, weather=False, messages=False)  # Carregamento leve

        # Retorna lista de tuplas (Numero, Abreviação)
        drivers = []
        for driver in session.drivers:
            abbreviation = session.get_driver(driver)['Abbreviation']
            drivers.append(abbreviation)
        return list(set(drivers))  # Remove duplicatas se houver
    except Exception as e:
        print(f"Erro ao buscar pilotos: {e}")
        return []