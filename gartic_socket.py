import socketio
import sys
import json
import logging
from helpers import pathing

sio = socketio.Client()

socketToken = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkVFNTdDMEFBRjE5M0VFOUI2NDFBIiwicmVhZF9vbmx5Ijp0cnVlLCJwcmV2ZW50X21hc3RlciI6dHJ1ZSwidHdpdGNoX2lkIjoiNTE1NjU4MzYifQ.CZRaxsLsdZ-WkUK3mpKr8JMmzNeA5HCOGegIK2ubKSU'
socketToken_1 = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbiI6IkM2RjJGN0NEM0IwNkZGQzFFNTVFMkU4QjAxNTdDRkRDMTY3NUM3Mzc4MzY1RjFCMDJCMUE0QjA2MkI4Q0E0ODVBRTJEMEFEREVDQzA1MTRGNUM5NzE4NUIzNzlBODI5NDRENzlEOEQxODY5MTM0QzdGQkU0RjQ4RkQ2Q0Y5Q0E3QTZCRUY4NzI3QUU2REYwMkE3RDQ5QkEyOTA1QUNGNTM1MjNFQzBGQ0YyNUQ4OTJCRjNBQUMxRTREOUE3QjVBMzQ4OEE3NDI2RUM1ODZBOTVERDM4NTU4N0Q2MDM1NTc4MDI3QzQ4QTY2N0RCNTFFNzk5RjcyM0RDNTQiLCJyZWFkX29ubHkiOnRydWUsInByZXZlbnRfbWFzdGVyIjp0cnVlLCJ0d2l0Y2hfaWQiOiI0MzY1MTY5NjMifQ.8zXcucabzhiylst-r998a8PhDQ1lm4yDxXOmYk5oyME'

logging.basicConfig(filename="timer.log",
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

@sio.event
def connect():
    logging.info('Timer: Connection to Streamlabs socket established')
    print('Timer: Connection to Streamlabs socket established')


@sio.event
def connect_error(e):
    logging.error(e)
    print(e)


@sio.event
def disconnect():
    logging.info('Timer: Connection to Streamlabs socket was closed')
    print('Timer: Disconnected from Streamlabs socket!')

answers = {}

@sio.on(3)
def event(index, data):
    global answers
    for pair in data:
        if pair['figure'] not in answers.keys():
            answers[pair['figure']] = {0: int(pair['ind'])}
        elif int(pair['ind']) != answers[pair['figure']][0]:
            answers[pair['figure']][1] = int(pair['ind'])
    for answer in answers:
        if len(answers[answer]) == 2:
            with open('answers.txt', 'a') as f:
                f.write(f'{answer}: {answers[answer][0]} {answers[answer][1]}')



def main_1(url = None):
    import re
    if not url:
        url = input('Enter the URL: ')
    url = re.sub('.+#', '', url)
    print(url)
    sio.connect(f"https://memory.gartic.es/socket.io/?uid={url}")
    sio.wait()

if __name__ == '__main__':
    main_1(sys.argv[1] if len(sys.argv) > 1 else None)
