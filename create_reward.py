from credentials import *
from helpers import pathing
import requests
import os
import json

users_oauth_token = os.environ['CHANNEL_TOKEN']

channel = 'shakerz_92'

headers = {'Authorization': API_ACCESS_TOKEN,
           'Client-Id': CLIENT_ID}

users_channel_id = int(requests.get(
    'https://api.twitch.tv/helix/users?login=' + channel, headers=headers).json()['data'][0]['id'])

headers_2 = {'Client-Id': CLIENT_ID, 
           'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}', 
           'Content-type': 'application/json'
        }

raw_data = '{"title":"سحب على 10 دولار", "cost": 3000}'
# raw_data = '{"title": "براااااااااع", "cost": 30000}'
broadcaster_id = users_channel_id

response = requests.post(
    f'https://api.twitch.tv/helix/channel_points/custom_rewards?broadcaster_id={broadcaster_id}',
    headers=headers_2, data=raw_data.encode('utf-8'))
print(response.content)
with open(pathing(f'static/{channel}', 'reward.json'), "w") as data:
    reward_file = response.json()['data']
    reward_file['reward_id'] = reward_file.pop('id')
    json.dump(reward_file, data, indent=4)
