from quart import Quart, request, abort, make_response
from dataclasses import dataclass
from helpers import pathing

channel_name = "shakerz_92"

with open(pathing(f'static/{channel_name.lower()}', 'last.txt'), "r") as f:
    participants = f.read().lower().splitlines()
print(participants)