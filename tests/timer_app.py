from quart import Quart, render_template, request, abort, make_response
from quart_cors import cors
from dataclasses import dataclass
from helpers import pathing
import os
import json
import time

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

@app.route("/")
async def index():
    return await render_template("test.html")

old_data = None

@app.get("/sse")
async def sse():
    if "text/event-stream" not in request.accept_mimetypes:
        abort(400)

    async def send_events():
        global old_data
        
        while True:
            with open(pathing('json', 'subathon_timer.json'), "r", encoding='utf-8') as data:
                timer = dict(json.load(data))
            
            data = json.dumps(timer)
            if old_data is None or old_data != data:
                print(timer)
                print(data)
                old_data = data
                _event = 'message'
                event = ServerSentEvent(data, _event)
                yield event.encode()
            time.sleep(0.5)
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)