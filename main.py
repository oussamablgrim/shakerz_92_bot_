# from hypercorn.config import Config
# from hypercorn.asyncio import serve
# from app import app
from bot import Bot, client, main
from my_socket import sio
import asyncio

socketToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkVFNTdDMEFBRjE5M0VFOUI2NDFBIiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiNTE1NjU4MzYifQ.CZRaxsLsdZ-WkUK3mpKr8JMmzNeA5HCOGegIK2ubKSU'

client.loop.create_task(main())

loop = asyncio.get_event_loop()
# config = Config()
# config.port = 5000
# loop.create_task(serve(app, config))
sio.connect(f"https://sockets.streamlabs.com?token={socketToken}")
# loop.create_task(main_1())
bot = Bot(['0us5ama'])
bot.pubsub_client = client
bot.run()
