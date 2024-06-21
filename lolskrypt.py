import requests
from datetime import datetime, timedelta, timezone
import time
import os
from api_key import API_KEY
import sys

def get_match_history(puuid, api_key):
    url = f'https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
    params = {'start': 0, 'count': 20}
    headers = {'X-Riot-Token': api_key}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Błąd: {response.status_code}')
        return None

def get_match_results(match_ids, puuid, api_key):
    url = 'https://europe.api.riotgames.com/lol/match/v5/matches/{}'
    headers = {'X-Riot-Token': api_key}
    results = {'win': 0, 'loss': 0}
    for match_id in match_ids:
        response = requests.get(url.format(match_id), headers=headers)
        if response.status_code == 200:
            match_data = response.json()
            game_creation = datetime.fromtimestamp(match_data['info']['gameCreation'] // 1000, tz=timezone.utc)
            if datetime.now(timezone.utc) - game_creation < timedelta(hours=10):
                for participant in match_data['info']['participants']:
                    if participant['puuid'] == puuid:
                        if participant['win']:
                            results['win'] += 1
                        else:
                            results['loss'] += 1
                        break
    return results

def save_results_to_file(results):
    with open('obs.txt', 'w') as file:
        file.write(f"{results['win']} {results['loss']}\n")

if __name__ == '__main__':
    puuid = 'your puuid'
    refresh_interval = 60
    while True:
        match_history = get_match_history(puuid, API_KEY)
        if match_history:
            results = get_match_results(match_history, puuid, API_KEY)
            sys.stdout.write(f"\rLiczba wygranych: {results['win']}, Liczba przegranych: {results['loss']}")
            sys.stdout.flush()
            save_results_to_file(results)
        
        time.sleep(refresh_interval)
