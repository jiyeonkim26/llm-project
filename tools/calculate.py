import json

def calculate(expression):
    """Evaluate a mathematical expression"""
    try:
        result = eval(expression)  # Use safe evaluation in production
        return json.dumps({"result": result})
    except:
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
          "description": "The mathematical expression to evaluate"
        }
      },
      "required": ["expression"]
    }
  }
}


# tool file is always going to have one python function and tool schema