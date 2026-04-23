import json


def calculate(expression):
    '''
    Evaluates a mathematical expression.

    >>> calculate("3 + 2")
    '{"result": 5}'

    >>> calculate("10 / 2")
    '{"result": 5.0}'

    >>> calculate("j")
    '{"error": "Invalid expression"}'
    '''
    try:
        result = eval(expression)  # Use safe evaluation in production
        return json.dumps({"result": result})
    except Exception:
        return json.dumps({"error": "Invalid expression"})
