from datetime import datetime, timedelta
from errors import EmptyCommand
from calculate import calculate, calculation
from pytimeparse.timeparse import timeparse
from credentials import *
import json, pytz, requests, re, ast, os, time

DIRNAME = '\\'.join(os.path.dirname(__file__).split("/"))

allowed_users = ['everyone', 'vips', 'mods']

headers = {
    'Authorization': f"Bearer {API_ACCESS_TOKEN}",
    'Client-Id': CLIENT_ID
}

headers_2 = {
    'Authorization': f"Bearer {CHANNEL_ACCESS_TOKEN}",
    'Client-Id': CLIENT_ID,
    'Content-Type': 'application/json'
}

def pathing(dir, file):
    return os.path.join(f"{DIRNAME}/{dir}", file)


def get_user(user):
    params = {'login': user}
    return requests.get('https://api.twitch.tv/helix/users',
                        headers=headers,
                        params=params).json()['data'][0]


def get_user_follows(from_id=None, to_id=None, after=None, first=None):
    if not (from_id or to_id): return 'check your ids'
    params = {
        'from_id': from_id,
        'to_id': to_id,
        'after': after,
        'first': first
    }
    return requests.get('https://api.twitch.tv/helix/users/follows',
                        headers=headers,
                        params=params).json()


def get_chat_color(user_id):
    params = {'user_id': user_id}
    return requests.get('https://api.twitch.tv/helix/chat/color',
                        headers=headers,
                        params=params).json()['data'][0]


def change_reward_status(client_id, channel_token, broadcaster_id, reward_id, id,status):
    headers = {'Client-Id': client_id, 
           'Authorization': 'Bearer ' + channel_token, 
           'Content-type': 'application/json'}
    params = {'broadcaster_id': broadcaster_id, 
              'reward_id': reward_id, 
              'id': id}
    raw_data = json.dumps({"status": status})
    r = requests.patch('https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions', headers=headers, params=params, data=raw_data)
    return r.status_code


def create_prediction(channel, channel_name, mention, queries=None):
    if not queries:
        return channel.send(
            f"{mention} you didn't precise any queries, please try again!")
    if len(queries) < 4:
        return channel.send(
            f"{mention} you need at least 4 queries to start a prediction!")
    if len(queries) > 12:
        return channel.send(f"{mention} too many queries (max of 12)!")
    if not queries[-1].isdigit():
        return channel.send(
            f"{mention} make sure you well precise the duration (in seconds)!")
    queries = [
        x.strip("( )")
        for x in re.split(r" \s*(?![^()]*\))", ' '.join(queries))
    ]
    
    if channel_name == '0us5ama':
        channel_name = 'shakerz_92'
    channel_id = get_user(channel_name)['id']
    title = queries[0]
    outcomes = [{"title": query} for query in queries[1:-1]]
    prediction_window = int(queries[-1])
    print(channel_id, title, outcomes, prediction_window)
    body_params = json.dumps({
        'broadcaster_id': channel_id,
        'title': title,
        'outcomes': outcomes,
        'prediction_window': prediction_window
    })
    response = requests.post('https://api.twitch.tv/helix/predictions',
                             headers=headers_2,
                             data=body_params).json()
    try:
        data = response['data']
        return channel.send(f'Prediction "{title}" was created successfully!')
    except KeyError:
        return channel.send(
            f'{mention} check your syntax (title outcomes duration [in secs])')


def get_stream(channel_id):
    params = {'user_id': channel_id}
    try:
        return requests.get('https://api.twitch.tv/helix/streams',
                            headers=headers,
                            params=params).json()['data'][0]
    except IndexError:
        return None


def make_timer(element, element_name, short_form=False):
    # return f'{str(element)} {element_name}s' if (element > 1 and not skip) else (
    #     f'{str(element)} {element_name}' if (element == 1 or (element > 0 and skip)) else '')
    if short_form:
        return f'{str(element)}{element_name}' if abs(element) > 0 else ''
    else:
        return f'{str(element)} {element_name}s' if abs(element) > 1 else (
            f'{str(element)} {element_name}' if abs(element) == 1 else '')


def to_time(mention, s, per_unit, unit):
    try:
        value = int(s[1])
        t = value * per_unit
        seconds = int(t % 60)
        minutes = int((t // 60) % 60)
        hours = int((t // 3600) % 24)
        days = int(t // (24 * 3600))

        days_str = make_timer(days, 'day')
        hours_str = make_timer(hours, 'hour')
        minutes_str = make_timer(minutes, 'minute')
        seconds_str = make_timer(seconds, 'second')
        return f'/me {mention}, if {unit} is {value}, ' + ' '.join(
            [days_str, hours_str, minutes_str, seconds_str]).strip()
    except ValueError:
        return f'{mention}, Check your input and try again'


def get_elapsed(duration, display=False):
    total = int(duration.total_seconds())
    hours = total // 3600
    minutes = (total - hours * 3600) // 60
    seconds = total % 60
    if display:
        hours_str = make_timer(hours, 'h', True)
        minutes_str = make_timer(minutes, 'm', True)
        seconds_str = make_timer(seconds, 's', True)
        return ''.join([hours_str, minutes_str, seconds_str]).strip('')
    else:
        return ':'.join([
            str(hours).zfill(2),
            str(minutes).zfill(2),
            str(seconds).zfill(2)
        ])


async def get_uptime(channel, short, channel_name=None):
    with open(pathing('json', 'timer.json'), "r") as data:
        live = json.load(data)
    started_at = datetime.strptime(live['started-at'], '%Y-%m-%d %H:%M:%S')
    # break_duration = live['break']
    old_viewer_count = live['viewer_count']
    now_zone = pytz.timezone('Asia/Riyadh')
    now = datetime.now(now_zone).replace(tzinfo=None)
    # break_seconds = timeparse(break_duration)
    # duration = now - started_at - timedelta(seconds=break_seconds if break_seconds else 0)
    duration = now - started_at
    # break_days, break_hours, break_minutes, break_seconds = [int(x) for x in break_duration.split(':')]
    # days_str = make_timer(break_days, 'D', True)
    # hours_str = make_timer(break_hours, 'h', True)
    # minutes_str = make_timer(break_minutes, 'm', True)
    # seconds_str = make_timer(break_seconds, 's', True)
    # break_time = ' '.join([days_str, hours_str, minutes_str, seconds_str]).strip()

    days = duration.days
    hours = duration.seconds // 3600
    minutes = (duration.seconds - hours * 3600) // 60
    seconds = duration.seconds % 60
    days_str = make_timer(days, 'D', True)
    hours_str = make_timer(hours, 'h', True)
    minutes_str = make_timer(minutes, 'm', True)
    seconds_str = make_timer(seconds, 's', True)
    time = ' '.join([days_str, hours_str, minutes_str, seconds_str]).strip()
    if not short:
        output = f'/me ⏰ LIVE started since {live["started-at"]} ◆ {time} 💬 {live["messages"]} message(s).'
        # if break_time:
        #     output += f' Live was offline for {break_time}.'

        return await channel.send(output)
    else:
        try:
            viewer_count = get_stream(
                get_user(channel_name)['id'])['viewer_count']
        except TypeError:
            viewer_count = 0
        viewer_diff = viewer_count - old_viewer_count
        if viewer_diff:
            live['viewer_count'] = viewer_count
            with open(pathing('json', 'timer.json'), "w") as data:
                json.dump(live, data, indent=4)
        viewer_diff_str = f'{viewer_diff:+}' if viewer_diff else '-'
        # return f'/me 【{viewer_count} viewers ({viewer_diff_str}) ⏰ {time} 】'
        return f'/me 【⏰ {time} 】'


async def get_remaining(channel, mention, message):
    try:
        costum_time = message[1].startswith('if_')
    except IndexError:
        costum_time = False
    if not costum_time:
        output = ''
        with open(pathing('json', 'url.json'), "r") as data:
            data = json.load(data)
        url = data['url']
        response = requests.get(url)
        p = re.compile("var deadline = (.*);")
        try:
            unix = int(p.search(str(response.content)).group(1).split(';')[0])
            seconds_raw = unix // 1000 - round(time.time())
            seconds = seconds_raw % 60
            minutes = seconds_raw % (60 * 60) // 60
            hours = seconds_raw % (60 * 60 * 24) // (60 * 60)
            days = seconds_raw // (60 * 60 * 24)

            days_str = make_timer(days, 'day')
            hours_str = make_timer(hours, 'hour')
            minutes_str = make_timer(minutes, 'minute')
            seconds_str = make_timer(seconds, 'second')

            output = '/me ' + ' '.join(
                [days_str, hours_str, minutes_str, seconds_str]).strip()
        except AttributeError:
            output = f'{mention} Widget Link not accessible, please try again later!'
    else:
        try:
            timer = message[1][3:]
            timer_hyp = timer.split(':')
            hours, minutes, seconds = [int(i) for i in timer_hyp]

            days = hours // 24
            hours -= days * 24

            days_str = make_timer(days, 'day')
            hours_str = make_timer(hours, 'hour')
            minutes_str = make_timer(minutes, 'minute')
            seconds_str = make_timer(seconds, 'second')
            output = (f'/me {mention}, if timer is {timer}, ' + ' '.join(
                [days_str, hours_str, minutes_str, seconds_str]).strip())
        except ValueError:
            output = f'{mention} Check your input and try again'
    return await channel.send(output)


def last_senders(author, senders):
    if (not author in senders):
        try:
            index = senders.index(None)
            senders[index] = author
        except ValueError:
            senders = senders[1:]
            senders.append(author)
    elif not author == senders[-1]:
        senders.remove(author)
        try:
            index = senders.index(None)
            senders.insert(index, author)
        except ValueError:
            senders.append(author)
    # print(senders)
    with open(pathing('json', 'last_senders.json'), "w") as data:
        last_senders = {"senders": senders}
        json.dump(last_senders, data, indent=4)
    return senders


async def get_entered(channel, mention, channel_name, queries):
    user = mention
    if queries:
        user = queries[0]
    try:
        resp = get_user(user)
        user_id = resp['id']
        user = resp['display_name']
    except (AttributeError, IndexError):
        return await channel.send(f' {user} مين ذا؟')
    
    if channel_name == '0us5ama':
        channel_name = 'shakerz_92'
    with open(pathing(f'static/{channel_name.lower()}', 'last.txt'), "r") as f:
        participants = f.read().lower().splitlines()
    
    if user.lower() in participants:
        return await channel.send(f'{user}, yes')
    else:
        return await channel.send(f'{user}, no')


async def switch(channel, mention, channel_name,
                 lasts, last_jsons, currents, current_jsons,
                 todays, day_jsons, nexts, users_oauth_tokens,
                 users_channel_ids):
    day_json = day_jsons[channel_name]
    last = lasts[channel_name]
    last_json = last_jsons[channel_name]
    current = currents[channel_name]
    current_json = current_jsons[channel_name]
    today = todays[channel_name]
    with open(day_json, "r") as data:
        day = json.load(data)
    day['today'] = (datetime.strptime(day['today'], '%d/%m/%Y') +
                    timedelta(days=1)).strftime("%d/%m/%Y")
    next = nexts[channel_name] = day['today']
    today = todays[channel_name] = datetime.strptime(
        next, '%d/%m/%Y').strftime("%d_%m_%Y")
    current = currents[channel_name] = pathing(
        f"static/{channel_name}", f"spin_{today}.txt")
    current_json = current_jsons[channel_name] = pathing(
        f"static/{channel_name}", f"spin_{today}.json")

    with open(day_json, "w") as data:
        json.dump(day, data)

    with open(last, "w") as f:
        pass
    with open(current, "a") as f:
        pass
    with open(current_json, "w") as f:
        f.write(json.dumps({}))

    await channel.send(f'{mention}, switched to tomorrow')

    with open(pathing(f"static/{channel_name}", 'reward.json'), "r") as data:
        data = json.load(data)
    reward_id = data['reward_id']

    with open(last_json, "r") as data:
        rewards = json.load(data)
    with open(last_json, "w") as f:
        f.write(json.dumps({}))
    rewards = rewards.values()
    # ids = [ reward['reward_id'] for reward in rewards if reward['reward_id']]
    users_oauth_token = users_oauth_tokens[channel_name]
    users_channel_id = users_channel_ids[channel_name]
    for reward in rewards:
        id = reward['reward_id']
        user = reward['user']
        change_reward_status(CLIENT_ID, users_oauth_token,
                                users_channel_id, reward_id, id,
                                "FULFILLED")


async def add_command(channel, user_id, mention, channel_name, message):
    output = ''
    try:
        aliases = None
        com_name = message[1]
        comm = ' '.join(message[2:])
        lst = message[1:]
        users = ["everyone"]
        excpt = []
        except_users = []
        for sub in lst:
            if 'aliases=' in sub:
                com_name = sub.replace('aliases=', '').replace('!', '')
                lst.remove(sub)
                aliases = lst[0]
                break
            elif 'users=' in sub:
                users = sub.replace('users=', '')
                lst.remove(sub)
                try:
                    users = ast.literal_eval(users)
                except (ValueError, IndentationError, SyntaxError):
                    users = [users]
            elif 'except=' in sub:
                except_users = sub.replace('except=', '')
                lst.remove(sub)
                try:
                    except_users = ast.literal_eval(except_users)
                except (ValueError, IndentationError, SyntaxError):
                    except_users = [except_users]
                for user in except_users:
                    try:
                        resp = get_user(user.replace('@', ''))
                        user_id = resp['id']
                        user = resp['display_name']
                        excpt.append(user_id)
                    except (AttributeError, IndexError):
                        return await channel.send(
                            f'{mention} check the users and try again')
        if not aliases:
            com_name = lst[0].replace('!', '')
            comm = ' '.join(lst[1:])
        print(users, excpt, com_name, comm, aliases)
        if not set(users) <= set(allowed_users) and not ('none' in users):
            print('r')
        if (comm == '' or com_name == '') and not excpt:
            raise EmptyCommand
        with open(pathing('json', 'commands.json'), 'r') as file:
            channels = json.load(file)
        if channel_name in channels.keys():
            comms = channels[channel_name]
        else:
            comms = {}
        if aliases:
            if com_name in comms.keys():
                comms[com_name]['aliases'].append(aliases)
                output = f'{mention} Alias "{aliases}" to "{com_name}" was added.'
            else:
                output = f'{mention} Command "{com_name}" does not exists!'
        elif excpt and com_name in comms.keys():
            if mention.lower() in ["0us5ama", "shakerz_92"]:
                prev_excpt = comms[com_name]['users']['except']
                if not set(excpt) <= set(prev_excpt):
                    comms[com_name]['users']['except'] = list(set(excpt + prev_excpt))
                    output = f'{mention} Exception User(s) {except_users} added to "{com_name}"'
                else:
                    output = f'{mention} User(s) {except_users} are already excepted from "{com_name}"!'
            else:
                output = f'{mention} Sorry you can not edit the exception users'
        elif not comm:
            raise EmptyCommand
        else:
            if not com_name in comms.keys():
                comms[com_name] = {
                    "built-in": False,
                    "content": comm,
                    "maker": user_id,
                    "editor": None,
                    "aliases": [],
                    "users": {
                        "level": users,
                        "except": excpt,
                    }
                }
                output = f'{mention} Command "{com_name}" was added.'
            else:
                output = f'{mention} Command "{com_name}" already exists!'
        channels[channel_name] = comms
        with open(pathing('json', 'commands.json'), 'w') as file:
            json.dump(channels, file, indent=4)
    except (IndexError, EmptyCommand) as e:
        if type(e).__name__ == EmptyCommand.__name__:
            output = f'{mention} Your command is empty, try again'
        else:
            output = f'{mention} check your Syntax and try again'
    return await channel.send(output)


async def edit_command(channel, user_id, mention, channel_name, message):
    output = ''
    try:
        com_name, comm = message[1], ' '.join(message[2:])
        if comm == '':
            raise EmptyCommand
        with open(pathing('json', 'commands.json'), 'r') as file:
            channels = json.load(file)
        if channel_name in channels.keys():
            comms = channels[channel_name]
        else:
            comms = {}
        if com_name in comms.keys():
            comms[com_name]["content"] = comm
            comms[com_name]["editor"] = user_id
            output = f'{mention} Command "{com_name}" was edited successfully.'
        else:
            output = f"{mention} Command '{com_name}' doesn't exists!"
        channels[channel_name] = comms
        with open(pathing('json', 'commands.json'), 'w') as file:
            json.dump(channels, file, indent=4)
    except (IndexError, EmptyCommand):
        output = f'{mention} check your Syntax and try again'
    return await channel.send(output)


async def delete_command(channel, mention, channel_name, message):
    output = ''
    try:
        com_name = message[1]
        with open(pathing('json', 'commands.json'), 'r') as file:
            channels = json.load(file)
        comms = channels[channel_name] if channel_name in channels.keys(
        ) else {}
        if not comms:
            channels[channel_name] = comms
            with open(pathing('json', 'commands.json'), 'w') as file:
                json.dump(channels, file, indent=4)
            output = f"{mention} There's no commands for this channel!"
            return await channel.send(output)
        aliases_dict = {comm: comms[comm]['aliases'] for comm in comms}
        aliases = set().union(*list(aliases_dict.values()))
        print(aliases)
        aliased = com_name in aliases
        if aliased:
            com_aliases = {
                aliase: comm
                for comm, aliases in aliases_dict.items() for aliase in aliases
            }
            comms[com_aliases[com_name]]['aliases'].remove(com_name)
            output = f'{mention} Aliase "{com_name}" was deleted successfully.'
        else:
            com_name = com_name.lstrip('!')
            if not com_name in comms.keys():
                output = f"{mention} Command '{com_name}' doesn't exists!"
                return await channel.send(output)
            if comms[com_name]['built-in']:
                output = f"{mention} Can't delete built-in commands"
                return await channel.send(output)
            del comms[com_name]
            output = f'{mention} Command "{com_name}" was deleted successfully.'
        channels[channel_name] = comms
        with open(pathing('json', 'commands.json'), 'w') as file:
            json.dump(channels, file, indent=4)
    except IndexError:
        output = f'{mention} check your Syntax and try again'
    return await channel.send(output)


async def say(channel, mention, message):
    try:
        output = ' '.join(message[1:])
        if not output.startswith('/'):
            return await channel.send(output)
        else:
            return await channel.send(
                f"{mention} Can't execute / commands PepeLaugh ")
    except NameError:
        pass


async def went(channel, message):
    output = ''
    now_zone = pytz.timezone('Asia/Riyadh')
    now = datetime.now(now_zone).replace(tzinfo=None)
    with open(pathing('json', 'afk.json'), "r") as data:
        times = json.load(data)
    is_went = times['went']
    went_at = times['went_at']
    is_back = times['back']
    came_back_at = times['came_back_at']
    uncount = times['uncount']
    try:
        if message[1] in ['كمل'] and is_back:
            times['went'] = True
            times['back'] = False
            sec = timeparse(uncount)
            duration = timedelta(
                seconds=sec if sec else 0) + now - datetime.strptime(
                    came_back_at, '%m/%d/%Y, %H:%M:%S')
            times['uncount'] = get_elapsed(duration)
            with open(pathing('json', 'afk.json'), "w") as data:
                json.dump(times, data, indent=4)
            output = "/me Afk time continues!"
    except IndexError:
        if not is_went:
            times['went_at'] = now.strftime('%m/%d/%Y, %H:%M:%S')
            times['came_back_at'] = ""
            times['went'] = True
            times['back'] = False
            times['uncount'] = "0:00:00"
            with open(pathing('json', 'afk.json'), "w") as data:
                json.dump(times, data, indent=4)
            # output = f"راح الساعة {now.strftime('%H:%M:%S')}"
            output = f"/me Streamer went at {now.strftime('%H:%M:%S')}"
        else:
            output = f"/me Streamer went before at {went_at}"
    return await channel.send(output)


async def came_back(channel, mention, message):
    output = ''
    now_zone = pytz.timezone('Asia/Riyadh')
    now = datetime.now(now_zone).replace(tzinfo=None)
    with open(pathing('json', 'afk.json'), "r") as data:
        times = json.load(data)
    is_went = times['went']
    went_at = times['went_at']
    is_back = times['back']
    came_back_at = times['came_back_at']
    uncount = times['uncount']
    if is_went:
        times['came_back_at'] = now.strftime('%m/%d/%Y, %H:%M:%S')
        times['went'] = False
        times['back'] = True
        with open(pathing('json', 'afk.json'), "w") as data:
            json.dump(times, data, indent=4)
        sec = timeparse(uncount)
        duration = now - datetime.strptime(
            went_at,
            '%m/%d/%Y, %H:%M:%S') - timedelta(seconds=sec if sec else 0)

        elapsed_time = get_elapsed(duration, display=True)
        output = f"/me Streamer was afk for {elapsed_time}"
    else:
        output = f"البثاث ما راح عشان يرجع {mention}"
    return await channel.send(output)


async def wastah(channel, channel_name, mention, lasts, last_jsons, currents, current_jsons):
    print(mention)
    user = mention
    try:
        resp = get_user(user)
        user_id = resp['id']
        user = resp['display_name']
    except (AttributeError, IndexError):
        return await channel.send('مين ذا؟')
    last = lasts[channel_name]
    last_json = last_jsons[channel_name]
    current = currents[channel_name]
    current_json = current_jsons[channel_name]
    with open(last_json, "r") as participants:
        users = json.load(participants)
    if not user_id in users.keys():
        with open(last, "a") as f:
            f.write(user + '\n')
        with open(current, "a") as f:
            f.write(user + '\n')
        participant = {
            "user": user,
            "reward_id": 0,
            "time": 0,
            "mode": 'cheat'
        }
        with open(current_json, 'r+') as data:
            # First we load existing data into a dict.
            try:
                file_data = json.load(data)
            except ValueError:
                file_data = {}
            # Join new_data with file_data inside emp_details
            file_data[user_id] = participant
            # Sets file's current position at offset.
            data.seek(0)
            # convert back to json.
            json.dump(file_data, data, indent=4)
        with open(last_json, "w") as data:
            json.dump(file_data, data, indent=4)
        await channel.send(f"{user} entered wastah!")
    else:
        await channel.send(f"{user} is already in, mayhtaj!")


async def unix_time(channel):
    return await channel.send(str(time.time()))


async def calc_deadline(channel, mention, queries):
    dhms = {f'{name}': 0 for name in ['d', 'h', 'm', 's']}
    dhms_checked = {f'{name}': False for name in ['d', 'h', 'm', 's']}
    dhms_lst = {'d' : ['days=', 'day=', 'd='], \
                    'h' : ['hours=', 'hour=', 'h='], \
                    'm' : ['minutes=', 'minute=', 'm='], \
                    's' : ['seconds=', 'second=', 'secs=', 'sec=']}
    for query in queries:
        for (name, lst) in dhms_lst.items():
            if not dhms_checked[f'{name}']:
                for sub in lst:
                    if sub in query:
                        try:
                            dhms[f'{name}'] = int(calculation(['', query.replace(sub, '')], internal = True))
                        except (ValueError, SyntaxError, TypeError, NameError):
                            return await channel.send(f"{mention}, Invalid time value for '{dhms_lst[name][0].replace('=', '').upper()}'")
                        dhms_checked[f'{name}'] = True
                        break
                if dhms_checked[f'{name}']:
                    break
    return dhms


def str_calc_time(d, h, m, s, subathon_timer):
    with open(pathing('json', 'subathon_timer.json'), "w") as data:
        json.dump(subathon_timer, data, indent=4)
    days_str = make_timer(d, 'D', short_form=True)
    hours_str = make_timer(h, 'h', short_form=True)
    minutes_str = make_timer(m, 'm', short_form=True)
    seconds_str = make_timer(s, 's', short_form=True)
    return ' '.join([days_str, hours_str, minutes_str, seconds_str]).strip()


async def add_time(channel, mention, queries):
    
    with open(pathing('json', 'subathon_timer.json'), "r") as data:
        subathon_timer = json.load(data)
    deadline = subathon_timer['deadline']
    dhms = await calc_deadline(channel, mention, queries)
    try:
        d, h, m, s = dhms.values()
    except AttributeError:
        return
    print(f"{dhms=}")
    # print(f"{dhms_checked=}")
    deadline = deadline if deadline else int(time.time())
    deadline += (((d*24)+h)*60+m)*60+s
    subathon_timer['deadline'] = deadline
    full_time = str_calc_time(d, h, m, s, subathon_timer)
    print(f"\"{full_time}\"")
    output = f"/me {mention}, you have successfully added {full_time}" if full_time else f"/me {mention}, you didn't input any time, try again"
    return await channel.send(output)


async def sub_time(channel, mention, queries):
    
    with open(pathing('json', 'subathon_timer.json'), "r") as data:
        subathon_timer = json.load(data)
    deadline = subathon_timer['deadline']
    dhms = await calc_deadline(channel, mention, queries)
    try:
        d, h, m, s = dhms.values()
    except AttributeError:
        return
    print(f"{dhms=}")
    # print(f"{dhms_checked=}")
    deadline = deadline if deadline else int(time.time())
    deadline -= (((d*24)+h)*60+m)*60+s
    subathon_timer['deadline'] = deadline
    full_time = str_calc_time(d, h, m, s, subathon_timer)
    print(f"\"{full_time}\"")
    output = f"/me {mention}, you have successfully subtracted {full_time}" if full_time else f"/me {mention}, you didn't input any time, try again"
    return await channel.send(output)


async def set_time(channel, mention, queries):
    
    with open(pathing('json', 'subathon_timer.json'), "r") as data:
        subathon_timer = json.load(data)
    deadline = subathon_timer['deadline']
    dhms = await calc_deadline(channel, mention, queries)
    try:
        d, h, m, s = dhms.values()
    except AttributeError:
        return
    print(f"{dhms=}")
    # print(f"{dhms_checked=}")
    deadline = int(time.time())
    deadline += (((d*24)+h)*60+m)*60+s
    subathon_timer['deadline'] = deadline
    full_time = str_calc_time(d, h, m, s, subathon_timer)
    print(f"\"{full_time}\"")
    output = f"/me {mention}, you have successfully set the timer to {full_time}" if full_time else f"/me {mention}, you didn't input any time, try again"
    return await channel.send(output)


async def get_price(channel, mention, queries):
    queries = ' '.join(queries)
    with open(pathing('json', 'subathon_timer.json'), "r") as data:
        subathon_timer = json.load(data)
    dict_in = {'donations': 'dono' in queries or 'donation' in queries,
               'bits': 'bit' in queries, 'subs': 'gift' in queries or 'sub' in queries}
    any_in = any(dict_in.values())
    
    output_dict = {}
    if dict_in['donations'] or not any_in:
        output_dict['1$'] = subathon_timer['donations']['multiplier']
    if dict_in['bits'] or not any_in:
        output_dict['100 bits'] = subathon_timer['bits']['multiplier']
    if dict_in['subs'] or not any_in:
        output_dict['subs-1'] = subathon_timer['subs']['1']
        output_dict['subs-2'] = subathon_timer['subs']['2']
        output_dict['subs-3'] = subathon_timer['subs']['3']
    output = ', '.join([f"{key}={value}s" for key, value in output_dict.items()])
    output = f"/me {mention}, {output}"
    return await channel.send(output)


async def set_price(channel, mention, queries):
    
    with open(pathing('json', 'subathon_timer.json'), "r") as data:
        subathon_timer = json.load(data)
    
    dbs = {f'{name}': None for name in ['donations', 'bits', 'subs-1', 'subs-2', 'subs-3']}
    dbs_checked = {f'{name}': False for name in ['donations', 'bits', 'subs']}
    dbs_lst = {'donations' : ['dono=', 'donations=', 'donation='],
                    'bits' : ['bits=', 'bit=', 'cheers=', 'cheer='],
                    'subs' : ['subs=', 'sub=', 'gifts=', 'gift=']}
    sub_checks = {f'subs-{i}': False for i in range(1, 4)}
    for query in queries:
            prev_check = False
            for (name, lst) in dbs_lst.items():
                checker = dbs_checked[f'{name}']
                if name == 'subs':
                    checker = all(sub_checks.values())
                if not checker:
                    for sub in lst:
                        if sub in query:
                            try:
                                inpt = query.replace(sub, '')
                                if name == 'subs':
                                    params = re.split(r'-|=', inpt)
                                    if params[0] in ['1', '2', '3']:
                                        if sub_checks[f'{name}-{params[0]}'] == False:
                                            dbs[f'subs-{params[0]}'] = int(params[1])
                                    else:
                                        return await channel.send(f"/me {mention}, you didn't input a valid sub tier, try again")
                                    
                                else:
                                    dbs[f'{name}'] = int(inpt)
                            except ValueError:
                                return await channel.send(f"{mention}, Invalid time value for '{name.upper()}'")
                            if name == 'subs':
                                sub_checks[f'{name}-{params[0]}'] = True
                            else:
                                dbs_checked[f'{name}'] = True
                            prev_check = True
                            break
                    if prev_check:
                        prev_check = True
                        break
    if any(dbs.values()):
        for element in dbs:
            if dbs[element] is not None:
                if 'subs' in element:
                    subathon_timer['subs'][element[-1]] = dbs[element]
                else:
                    subathon_timer[element]['multiplier'] = dbs[element]
        with open(pathing('json', 'subathon_timer.json'), "w") as data:
            json.dump(subathon_timer, data, indent=4)
    output = ' | '.join([f"'{key}' time was set to {value}s" for key, value in dbs.items() if value])
    output = f"/me {mention}, {output}" if output else f'/me {mention}, you didn\'t input any time, try again'
    return await channel.send(output)


async def kaf(channel, mention, channel_name):
    user = requests.get(f'https://2g.be/twitch/randomviewer.php?channel={channel_name}').text
    return await channel.send(f'ابلع كف {user}')
