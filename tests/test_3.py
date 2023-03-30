import socketio
import asyncio
import json
from aiohttp import web
from helpers import pathing

class MyCustomNamespace(socketio.AsyncClientNamespace):
    async def on_connect(self):
        print("I'm connected!")

    async def on_disconnect(self):
        print("I'm disconnected!")

    async def on_event(self, data):
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
            elif data['for'] == 'twitch_account':
                if data['type'] == 'follow':
                    with open(pathing('json', 'follows.json'), "r", encoding='utf-8') as dt:
                        follows = json.load(dt)
                    with open(pathing('json', 'follows.json'), "w", encoding='utf-8') as dt:
                        follows += data['message']
                        json.dump(follows, dt, indent=4)
                elif data['type'] == 'subscription':
                    with open(pathing('json', 'subscriptions.json'), "r", encoding='utf-8') as dt:
                        subscriptions = json.load(dt)
                    with open(pathing('json', 'subscriptions.json'), "w", encoding='utf-8') as dt:
                        subscriptions += data['message']
                        json.dump(subscriptions, dt, indent=4)
                elif data['type'] == 'bits':
                    with open(pathing('json', 'bits.json'), "r", encoding='utf-8') as dt:
                        bits = json.load(dt)
                    with open(pathing('json', 'bits.json'), "w", encoding='utf-8') as dt:
                        bits += data['message']
                        json.dump(bits, dt, indent=4)
                else:
                    with open(pathing('json', 'other.json'), "r", encoding='utf-8') as dt:
                        other = json.load(dt)
                    with open(pathing('json', 'other.json'), "w", encoding='utf-8') as dt:
                        other += data['message']
                        json.dump(other, dt, indent=4)
        print(data['type'])
        # await self.emit('my_response', data)

    async def on_message(self, data):
        print("[echo]:", data)

class mysio:
    
    def __init__(self) -> None:
        global sio
        self.sio = socketio.AsyncClient(logger=False, engineio_logger=False)
        self.sio.register_namespace(MyCustomNamespace('/')) # bind

async def main_1():

    async def fun1():
        sio1 = mysio().sio
        socketToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkVFNTdDMEFBRjE5M0VFOUI2NDFBIiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiNTE1NjU4MzYifQ.CZRaxsLsdZ-WkUK3mpKr8JMmzNeA5HCOGegIK2ubKSU'
        await sio1.connect(f"https://sockets.streamlabs.com?token={socketToken}")
        await sio1.emit('message', b'11111110001')
        await sio1.wait()

    # async def fun2():
    #     sio2 = mysio().sio
    #     await sio2.connect('http://localhost:8080')
    #     await sio2.emit('message', 'from sio2')
    #     await sio2.wait()
    
    # async def fun2():
    #     sios = socketio.AsyncServer()
    #     app = socketio.ASGIApp(sios)
    #     await app.run()

    # tasks_ = [asyncio.create_task(fun1()),asyncio.create_task(fun2()) ]
    tasks = [asyncio.create_task(fun1())]
    
    await asyncio.wait(tasks)

asyncio.run(main_1())