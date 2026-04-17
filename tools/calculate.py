'''
calculate.py defines the function that allows the calculate tool to be called and used by chat.py.
'''
import json


def calculate(expression):
    '''
    This tool evaluates a mathematical expression.

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


tool_schema = {
    "type": "function",
    "function": {
        "name": "calculate",
        "description": "Evaluate a mathematical expression",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The mathematical expression to evaluate",
                }
            },
            "required": ["expression"],
        },
    },
}
