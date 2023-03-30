from quart import Quart, render_template, redirect, send_from_directory, request, abort, make_response
from quart_cors import cors
from dataclasses import dataclass
from helpers import pathing
from func import apology
import os
import json
import asyncio

DIRNAME = '\\'.join(os.path.dirname(__file__).split("/"))

app = Quart(__name__)
app = cors(app, allow_origin="*")


@dataclass
class ServerSentEvent:
    data: str
    event: str = None
    id: int = None
    retry: int = None
    # def __init__(self, data : str, event : str = None, id : int = None, retry : int = None):
    #     self.data = data
    #     self.event = event
    #     self.id = id
    #     self.retry = retry
        
    def encode(self) -> bytes:
        message = f"data: {self.data}"
        if self.event is not None:
            message = f"{message}\nevent: {self.event}"
        if self.id is not None:
            message = f"{message}\nid: {self.id}"
        if self.retry is not None:
            message = f"{message}\nretry: {self.retry}"
        message = f"{message}\r\n\r\n"
        return message.encode('utf-8')


@app.route("/data/<channel>/<path:path>")
async def get_txt(channel, path):
    try:
        if not path.endswith('.txt'):
            raise FileNotFoundError
        with open(os.path.join(f"{DIRNAME}/static/{channel}", path), "r") as f:
            content = f.read()
        return {"participants": content.strip().split('\n')}
    except FileNotFoundError:
        # raise ValueError('No such file')
        return await apology('FileNotFoundError', 500)


@app.route('/')
async def index():
    return 'What do you want here ?! 🙄'


@app.route("/static/<channel>/<path:path>")
async def static_dir(channel, path):
    return await send_from_directory(f"static/{channel}", path)


@app.route("/spin/<channel>/<path:path>")
async def spin(channel, path):
    data = await get_txt(channel, path)
    # print(data['participants'].strip().split('\n'))
    if not isinstance(data, tuple):
        return await render_template('last.html',
                                     title=path.replace('.txt', ''),
                                     data=data['participants'],
                                     channel=channel)
    else:
        return await apology('FileNotFoundError', 500)


@app.route("/spins/<channel>/<path:path>")
async def spins(channel, path):
    data = await get_txt(channel, path)
    # print(data['participants'].strip().split('\n'))
    if not isinstance(data, tuple):
        return await render_template('spin.html',
                                     title=path.replace('.txt', ''),
                                     data=data['participants'])
    else:
        return redirect(f"/{path}", code=302)


@app.route("/test/<channel>/<path:path>")
async def test(channel, path):
    data = await get_txt(channel, path)
    # print(data['participants'].strip().split('\n'))
    if not isinstance(data, tuple):
        return await render_template('last_2.html',
                                     title=path.replace('.txt', ''),
                                     data=data['participants'])
    else:
        return redirect(f"/{path}", code=302)


@app.get("/sse")
async def sse():
    if "text/event-stream" not in request.accept_mimetypes:
        abort(400)
    old_timer = None

    async def send_events():
        nonlocal old_timer
        
        while True:
            with open(pathing('json', 'subathon_timer.json'), "r", encoding='utf-8') as data:
                timer = json.load(data)
            
            if old_timer is None or old_timer['deadline'] != timer['deadline']:
                old_timer = timer
                print(timer)
                data = json.dumps(timer)
                _event = 'deadline'
                event = ServerSentEvent(data, _event)
                yield event.encode()
            await asyncio.sleep(0.1)
    response = await make_response(
        send_events(),
        {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Transfer-Encoding': 'chunked',
        },
    )
    response.timeout = None
    return response


@app.route('/timer')
async def timer():
    return await render_template('timer.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0")