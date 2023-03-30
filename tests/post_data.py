import requests
import json
from helpers import pathing

with open(pathing('json', 'subathon_timer.json'), "r", encoding='utf-8') as data:
    timer = json.load(data)
    print(data)
    r = requests.post('http://127.0.0.1:8000/timer', json={"deadline": 0})