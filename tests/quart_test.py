from quart import Quart, render_template, abort, make_response, request
from dataclasses import dataclass
from quart_cors import cors
from helpers import pathing
import json
import asyncio

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

@app.route("/")
async def hello():
    return "Welcome!"

# @app.route("/api")
# async def json():
#     return {"hello": "world"}

@app.route('/timer')
async def timer():
    return await render_template('test.html')

old_data = None

@app.get("/sse")
async def sse():
    if "text/event-stream" not in request.accept_mimetypes:
        abort(400)

    async def send_events():
        global old_data
        
        while True:
            with open(pathing('json', 'subathon_timer.json'), "r", encoding='utf-8') as data:
                timer = json.load(data)
            
            data = json.dumps(timer)
            if old_data is None or old_data != data:
                print(timer)
                print(data)
                old_data = data
                _event = 'message'
                event = ServerSentEvent(data, _event)
                yield event.encode()
            await asyncio.sleep(0.5)
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

if __name__ == "__main__":
    app.run()