import json


def calculate(expression):
    '''
    This tool evaluates a mathematical expression.

    >>> calculate("3 + 2")
    '{"result": 5}'

    '''
    result = eval(expression)  # Use safe evaluation in production
    return json.dumps({"result": result})
