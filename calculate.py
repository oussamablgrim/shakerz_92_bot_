from math import *
import os
import json

DIRNAME = '//'.join(os.path.dirname(__file__).split("/"))

env = {}
env["locals"]   = None
env["globals"]  = None
env["__name__"] = None
env["__file__"] = None
env["__builtins__"] = {
    'pi': pi,
    'e': e,
    'ceil': ceil,
    'floor': floor,
    'cos': cos,
    'sin': sin,
    'tan': tan,
    'sqrt': sqrt,
    'pow': pow,
    'exp': exp,
    'log': log
}
with open(os.path.join(f'{DIRNAME}/json', 'invalid_characters.json'), "r") as data:
    invalid_calc = json.load(data)


def calculation(message, internal):
    expression = ''.join(message[1:])
    for ele in expression:
        if ele in invalid_calc.keys():
            expression = expression.replace(ele, invalid_calc[ele])
    expression = expression.replace("mod", invalid_calc["mod"])
    value = round(eval(expression, env), 3)
    value_str = str(value)
    value_str = value_str[:-2] if value_str.endswith('.0') else value_str
    return value if internal else value_str


async def calculate(channel, mention, message, internal = False):
    output = ''
    try:
        output = calculation(message, internal)
    except (SyntaxError, TypeError, NameError):
        output = f'{mention}, check your input and try again'
    except ZeroDivisionError:
        output = f"{mention}, can't devide by zero!"
    return await channel.send(output) if not internal else output