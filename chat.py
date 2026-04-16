import json
import os
from groq import Groq
from tools.calculate import calculate, tool_schema as calculate_schema
from tools.ls import ls, tool_schema as ls_schema
from tools.cat import cat, tool_schema as cat_schema
from tools.grep import grep, tool_schema as grep_schema

from dotenv import load_dotenv
load_dotenv()


class Chat:
    '''
    >>> def monkey_input(prompt, user_inputs=['Hello, I am monkey.', 'Goodbye.']):
    ...    try:
    ...        user_input = user_inputs.pop(0)
    ...        print(f'{prompt}{user_input}')
    ...        return user_input
    ...    except IndexError:
    ...        raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> Hello, I am monkey.
    Nice to meet you, monkey! How can I assist you today?
    chat> Goodbye.
    Goodbye! Feel free to return anytime you need assistance.
    <BLANKLINE>
    '''
    '''
    >>> chat = Chat()
    >>> chat.send_message('my name is Bob', temperature=0.0)
    "Hello Bob, it's nice to meet you."
    >>> chat.send_message('what is my name?', temperature=0.0)
    'Your name is Bob.'


    >>> chat2 = Chat()
    >>> chat2.send_message('what is my name?', temperature=0.0)
    "I don't have any information about your name. I'm a text-based AI assistant and our conversation just started, so I don't have any prior knowledge about you."
    '''
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    MODEL = "openai/gpt-oss-120b"

    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": "Write the output in 1-2 sentences. Always use tools to complete tasks when appropriate. Don't bold the answer."
            },
        ]

    def send_message(self, message, temperature=0.8):
        self.messages.append(
            {
                # system: never change; user: changes a lot
                # the message that you are sending to the AI
                'role': 'user',
                'content': message
            }
        )

        # define tools
        tools = [calculate_schema, ls_schema, cat_schema, grep_schema]

        # in order to make non deterministic code deterministic:
        # in this case, has a 'temperature' param that controls randomness:
        # the higher the value, the more randomness;
        # higher temperature = more creativity
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            # model="llama-3.1-8b-instant",
            model=self.MODEL,
            temperature=temperature,
            seed=0,
            tools=tools,
            tool_choice="auto"
        )

        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls
        # Step 2: Check if the model wants to call tools
        if tool_calls:
            available_functions = {
                "calculate": calculate,
                "ls": ls,
                "cat": cat,
                "grep": grep,
            }

            self.messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions[function_name]
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "calculate":
                    function_response = function_to_call(
                        function_args["expression"]
                    )

                elif function_name == "ls":
                    function_response = function_to_call(
                        function_args.get("folder")
                    )

                elif function_name == "cat":
                    function_response = function_to_call(
                        function_args["filename"]
                    )

                elif function_name == "grep":
                    function_response = function_to_call(
                        function_args["regex"],
                        function_args["path"]
                    )

                print(f"[tool] function_name={function_name}, function_args={function_args}")
                if function_name == "cat":
                    self.messages.append({
                        "role": "assistant",
                        "content": function_response
                    })
                    return function_response

                # Add tool response to conversation
                self.messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })

            # Step 4: Get final response from model
            second_response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=self.messages
            )
            result = second_response.choices[0].message.content
            self.messages.append({
                'role': 'assistant',
                'content': result
            })

        # tell LLM what we were previously talking about
        else:
            result = response_message.content
            self.messages.append({
                "role": "assistant",
                "content": result
            })

        return result


# this makes the user interface nicer by saying 'chat>'
# repl: reads input and evaluates input
'''
if __name__ == '__main__':
   chat = Chat()
   try:
       while True:
               user_input = input('chat>')
               response = chat.send_message(user_input)
               print(response)
   except KeyboardInterrupt:
       print()
'''


def repl(temperature=0.0):
    '''
    >>> def monkey_input(prompt, user_inputs=['/ls', '/calculate 2 + 2', '/cat example.txt', '/unknown', '/grep hello example.txt']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> /ls
    README.md __pycache__ chat.py chatdemo.gif cmc_csci040_JiyeonKim.egg-info demo.gif example.txt example_utf16.txt pyproject.toml requirements.txt test_projects tools
    chat> /calculate 2 + 2
    {"result": 4}
    chat> /cat example.txt
    hello world
    chat> /unknown
    Unknown command: unknown
    chat> /grep hello example.txt
    hello world
    <BLANKLINE>
    '''
    chat = Chat()

    available_functions = {
        "calculate": calculate,
        "ls": ls,
        "cat": cat,
        "grep": grep,
    }

    try:
        while True:
            user_input = input('chat> ')

            # Handle slash commands locally: /command param1 param2
            if user_input.startswith("/"):
                parts = user_input[1:].strip().split()

                if not parts:
                    print("Unknown command")
                    continue

                command = parts[0]
                args = parts[1:]

                if command not in available_functions:
                    print(f"Unknown command: {command}")
                    continue

                try:
                    if command == "calculate":
                        if len(args) < 1:
                            result = "Error: calculate requires an expression"
                        else:
                            expression = " ".join(args)
                            result = calculate(expression)

                    elif command == "ls":
                        folder = args[0] if args else None
                        result = ls(folder)

                    elif command == "cat":
                        if len(args) != 1:
                            result = "Error: cat requires exactly one filename"
                        else:
                            result = cat(args[0])

                    elif command == "grep":
                        if len(args) < 2:
                            result = "Error: grep requires a regex and a path"
                        else:
                            regex = args[0]
                            path = " ".join(args[1:])
                            result = grep(regex, path)

                    print(result)

                    # Store the slash command and result in conversation history
                    chat.messages.append({
                        "role": "user",
                        "content": user_input
                    })
                    chat.messages.append({
                        "role": "assistant",
                        "content": result
                    })

                except Exception:
                    print("")
                continue

            response = chat.send_message(user_input, temperature=temperature)
            print(response)

    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == '__main__':
    repl(temperature=0.0)
