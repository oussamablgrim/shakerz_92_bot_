import asyncio
import sys
import socketio
import json
from helpers import pathing

sio = socketio.Client()

socketToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkVFNTdDMEFBRjE5M0VFOUI2NDFBIiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiNTE1NjU4MzYifQ.CZRaxsLsdZ-WkUK3mpKr8JMmzNeA5HCOGegIK2ubKSU'
socketToken_1 = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkM2RjJGN0NEM0IwNkZGQzFFNTVFMkU4QjAxNTdDRkRDMTY3NUM3Mzc4MzY1RjFCMDJCMUE0QjA2MkI4Q0E0ODVBRTJEMEFEREVDQzA1MTRGNUM5NzE4NUIzNzlBODI5NDRENzlEOEQxODY5MTM0QzdGQkU0RjQ4RkQ2Q0Y5Q0E3QTZCRUY4NzI3QUU2REYwMkE3RDQ5QkEyOTA1QUNGNTM1MjNFQzBGQ0YyNUQ4OTJCRjNBQUMxRTREOUE3QjVBMzQ4OEE3NDI2RUM1ODZBOTVERDM4NTU4N0Q2MDM1NTc4MDI3QzQ4QTY2N0RCNTFFNzk5RjcyM0RDNTQiLCJyZWFkX29ubHkiOnRydWUsInByZXZlbnRfbWFzdGVyIjp0cnVlLCJ0d2l0Y2hfaWQiOiI0MzY1MTY5NjMifQ.8zXcucabzhiylst-r998a8PhDQ1lm4yDxXOmYk5oyME'

@sio.event
def connect():
    print('connected')
    # result = sio.call('sum', {'numbers': [1, 2]})
    # print(result)


@sio.event
def connect_error(e):
    print(e)


@sio.event
def disconnect():
    print('disconnected')


@sio.event
def event(data):
    with open(pathing('json', 'all.json'), "a", encoding='utf-8') as al:
        al.write(f"{data}")
    if 'for' in data.keys():
        print('for in')
        if not data['for'] and data['type'] == 'donation':
            with open(pathing('json', 'donations.json'), "r", encoding='utf-8') as dt:
                donations = json.load(dt)
            with open(pathing('json', 'donations.json'), "w", encoding='utf-8') as dt:
                donations += data['message']
                json.dump(donations, dt, indent=4)
            with open(pathing('json', 'subathon_timer.json'), "r", encoding='utf-8') as dt:
                timer = json.load(dt)
            with open(pathing('json', 'subathon_timer.json'), "w", encoding='utf-8') as dt:
                timer['deadline'] += round(float(donations['amount'])*120)
                json.dump(timer, dt, indent=4)
        elif data['for'] == 'twitch_account':
            if data['type'] == 'follow':
                with open(pathing('json', 'follows.json'), "r", encoding='utf-8') as dt:
                    follows = json.load(dt)
                with open(pathing('json', 'follows.json'), "w", encoding='utf-8') as dt:
                    follows += data['message']
                    json.dump(follows, dt, indent=4)
                with open(pathing('json', 'subathon_timer.json'), "r", encoding='utf-8') as dt:
                    timer = json.load(dt)
                with open(pathing('json', 'subathon_timer.json'), "w", encoding='utf-8') as dt:
                    timer['deadline'] += round(float(1)*10)
                    json.dump(timer, dt, indent=4)
            elif data['type'] == 'subscription':
                with open(pathing('json', 'subscriptions.json'), "r", encoding='utf-8') as dt:
                    subscriptions = json.load(dt)
                with open(pathing('json', 'subscriptions.json'), "w", encoding='utf-8') as dt:
                    subscriptions += data['message']
                    json.dump(subscriptions, dt, indent=4)
                with open(pathing('json', 'subathon_timer.json'), "r", encoding='utf-8') as dt:
                    timer = json.load(dt)
                with open(pathing('json', 'subathon_timer.json'), "w", encoding='utf-8') as dt:
                    timer['deadline'] += round(float(1)*250)
                    json.dump(timer, dt, indent=4)
            elif data['type'] == 'bits':
                with open(pathing('json', 'bits.json'), "r", encoding='utf-8') as dt:
                    bits = json.load(dt)
                with open(pathing('json', 'bits.json'), "w", encoding='utf-8') as dt:
                    bits += data['message']
                    json.dump(bits, dt, indent=4)
                with open(pathing('json', 'subathon_timer.json'), "r", encoding='utf-8') as dt:
                    timer = json.load(dt)
                with open(pathing('json', 'subathon_timer.json'), "w", encoding='utf-8') as dt:
                    timer['deadline'] += round(float(bits['amount'])*140)
                    json.dump(timer, dt, indent=4)
            else:
                with open(pathing('json', 'other.json'), "r", encoding='utf-8') as dt:
                    other = json.load(dt)
                with open(pathing('json', 'other.json'), "w", encoding='utf-8') as dt:
                    other += data['message']
                    json.dump(other, dt, indent=4)
    print(data['type'])


def main_1(holder = None):
    sio.connect(f"https://sockets.streamlabs.com?token={socketToken}")
    sio.wait()

if __name__ == '__main__':
    main_1(sys.argv[1] if len(sys.argv) > 1 else None)