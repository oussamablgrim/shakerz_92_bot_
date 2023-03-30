import socketio
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


def lower_equal(a: str, b: str):
    return a.lower() == b.lower()


def payload(data):
    data = data['message'][0]
    try:
        return data['payload'] if 'payload' in data.keys() else data
    except AttributeError:
        print('exception')
        return data


def add_time(_type: str, amount: int, base_amount: int = 1, sub_plan: int = None):
    with open(pathing('json', 'subathon_timer.json'), "r", encoding='utf-8') as dt:
        timer = json.load(dt)
    if not sub_plan or not _type in ['subs', 'submysterygift']:
        multiplier = timer[_type]['multiplier']
    elif _type in ['subs', 'submysterygift']:
        multiplier = timer[_type][str(sub_plan)[0]]
    timer['deadline'] += round(float(amount/base_amount)*multiplier)
    with open(pathing('json', 'subathon_timer.json'), "w", encoding='utf-8') as dt:
        json.dump(timer, dt, indent=4)
    output = f'Added {round(float(amount/base_amount)*multiplier)}s from {amount} of {_type+str(sub_plan) if sub_plan else _type}'
    logging.info(f'Timer: {output}')
    print(f'Timer: {output}')
    return 0


prev_donation_id, prev_bits_id, prev_subs_id, prev_mysterygift_id = [None]*4
not_count = 0


@sio.event
def event(data):
    global prev_donation_id, prev_bits_id, prev_subs_id, prev_mysterygift_id
    global not_count
    with open(pathing('json', 'all.json'), "a", encoding='utf-8') as al:
        al.write(f"{data}")
    if lower_equal(data['type'], 'donation'):
        donation = payload(data)
        if not prev_donation_id or prev_donation_id != str(donation['id']):
            add_time(_type = 'donations', amount = int(donation['amount']))
            prev_donation_id = str(donation['id'])
    elif 'for' in data.keys():
        if lower_equal(data['for'], 'twitch_account'):
            if lower_equal(data['type'], 'bits'):
                bits = payload(data)
                if not prev_bits_id or prev_bits_id != bits['event_id']:
                    add_time(_type = 'bits', amount = int(bits['amount']), base_amount = 100)
                    prev_bits_id = bits['event_id']
            elif lower_equal(data['type'], 'submysterygift'):
                subscriptions = payload(data)
                if not prev_mysterygift_id or prev_mysterygift_id != subscriptions['event_id']:
                    not_count += subscriptions['amount']
                    add_time(_type = 'subs', amount = int(subscriptions['amount']), sub_plan = int(subscriptions['sub_plan']))
                    prev_mysterygift_id = subscriptions['event_id']
            elif lower_equal(data['type'], 'subscription'):
                subscription = payload(data)
                if not prev_subs_id or prev_subs_id != subscription['event_id']:
                    if not not_count:
                        add_time(_type = 'subs', amount = 1, sub_plan = int(subscription['sub_plan']))
                    else:
                        not_count -= 1
                    prev_subs_id = subscription['event_id']
            else:
                with open(pathing('json', 'other.json'), "r", encoding='utf-8') as dt:
                    other = json.load(dt)
                with open(pathing('json', 'other.json'), "w", encoding='utf-8') as dt:
                    other += data['message']
                    json.dump(other, dt, indent=4)
    print(data['type'])


# def main_1(holder = None):
#     sio.connect(f"https://sockets.streamlabs.com?token={socketToken}")
    # sio.wait()

# if __name__ == '__main__':
#     main_1(sys.argv[1] if len(sys.argv) > 1 else None)
