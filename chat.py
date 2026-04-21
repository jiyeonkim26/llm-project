"""
chat.py provides a CLI-based chat interface with a REPL loop that
interacts with the Groq API and supports both automatic and manual
tool execution.
"""

import json
import os
import readline
import shlex

from groq import Groq
from tools.calculate import calculate, tool_schema as calculate_schema
from tools.ls import ls, tool_schema as ls_schema
from tools.cat import cat, tool_schema as cat_schema
from tools.grep import grep, tool_schema as grep_schema

from dotenv import load_dotenv

load_dotenv()


class Chat:
    '''
    A conversational chat agent that maintains message history and
    interacts with a language model via the Groq API. The class supports
    automatic tool use (e.g., calculate, ls, cat, grep) by detecting and
    executing model-requested function calls, then incorporating their
    results into the final response. It enables multi-turn conversations
    with contextual memory and controllable response randomness via the
    temperature parameter.
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

    MODEL = "openai/gpt-oss-120b"

    def __init__(self): 
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        self.messages = [
            {
                "role": "system",
                "content": (
                    "Write the output in 1-2 sentences. Always use tools "
                    "to complete tasks when appropriate. Don't bold the answer."
                ),
            },
        ]

    def send_message(self, message, temperature=0.8):
        '''
        >>> from unittest.mock import MagicMock
        >>> chat = Chat()
        >>> chat.client = MagicMock()
        >>> chat.client.chat.completions.create.return_value = MagicMock(
        ...     choices=[MagicMock(message=MagicMock(content="Hello Bob, it's nice to meet you.", tool_calls=None))]
        ... )
        >>> chat.send_message('my name is Bob', temperature=0.0)
        "Hello Bob, it's nice to meet you."
        '''
        self.messages.append(
            {
                # system: never change; user: changes a lot
                # the message that you are sending to the AI
                'role': 'user',
                'content': message,
            }
        )

        # define tools
        tools = [calculate_schema, ls_schema, cat_schema, grep_schema]

        # higher temperature = more randomness/creativity
        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            # model="llama-3.1-8b-instant",
            model=self.MODEL,
            temperature=temperature,
            seed=0,
            tools=tools,
            tool_choice="auto",
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
                        function_args["path"],
                    )

                # Add tool response to conversation
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

            # Step 4: Get final response from model
            second_response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=self.messages,
                tools=tools,
                tool_choice="auto",
            )

            result = second_response.choices[0].message.content
            self.messages.append(
                {
                    'role': 'assistant',
                    'content': result,
                }
            )

        # tell LLM what we were previously talking about
        else:
            result = response_message.content
            self.messages.append(
                {
                    "role": "assistant",
                    "content": result,
                }
            )

        return result


def _parse_slash_command(user_input):
    '''
    Parse slash-command input into a command name and argument list.

    This parser uses shell-style splitting so quoted strings work.

    >>> _parse_slash_command('/calculate 2 + 2')
    ('calculate', ['2', '+', '2'])

    >>> _parse_slash_command('/cat "doctest_examples/example.txt"')
    ('cat', ['doctest_examples/example.txt'])

    >>> _parse_slash_command('/grep "hello world" doctest_examples/example.txt')
    ('grep', ['hello world', 'doctest_examples/example.txt'])

    >>> _parse_slash_command('/')
    (None, [])

    >>> _parse_slash_command('hello')
    (None, [])
    '''
    if not user_input.startswith("/"):
        return None, []

    raw = user_input[1:].strip()
    if not raw:
        return None, []

    try:
        parts = shlex.split(raw)
    except ValueError:
        parts = raw.split()

    if not parts:
        return None, []

    return parts[0], parts[1:]


def _run_slash_command(command, args, available_functions):
    '''
    Execute a validated slash command and return the resulting string.

    >>> funcs = {
    ...     "calculate": calculate,
    ...     "ls": ls,
    ...     "cat": cat,
    ...     "grep": grep,
    ... }

    >>> _run_slash_command('calculate', ['2', '+', '2'], funcs)
    '{"result": 4}'

    >>> _run_slash_command('calculate', [], funcs)
    'Error: calculate requires an expression'

    >>> _run_slash_command('cat', [], funcs)
    'Error: cat requires exactly one filename'

    >>> _run_slash_command('grep', ['hello'], funcs)
    'Error: grep requires a regex and a path'

    >>> _run_slash_command('not_command', ['hello'], funcs)
    'Unknown command: not_command'

    >>> _run_slash_command('grep', ['hello', 'doctest_examples/example.txt'], funcs)
    'hello world'
    '''
    if command not in available_functions:
        return f"Unknown command: {command}"

    function_to_call = available_functions[command]

    if command == "calculate":
        if not args:
            return "Error: calculate requires an expression"
        expression = " ".join(args)
        return function_to_call(expression)

    if command == "ls":
        folder = args[0] if args else None
        return function_to_call(folder)

    if command == "cat":
        if len(args) != 1:
            return "Error: cat requires exactly one filename"
        return function_to_call(args[0])

    if command == "grep":
        if len(args) < 2:
            return "Error: grep requires a regex and a path"
        regex = args[0]
        path = " ".join(args[1:])
        return function_to_call(regex, path)


def _record_slash_command(chat, user_input, result):
    '''
    Store a handled slash command and its result in chat history.

    >>> class DummyChat:
    ...     def __init__(self):
    ...         self.messages = []
    ...
    >>> chat = DummyChat()
    >>> _record_slash_command(chat, '/calculate 2 + 2', '{"result": 4}')
    >>> chat.messages
    [{'role': 'user', 'content': '/calculate 2 + 2'}, {'role': 'assistant', 'content': '{"result": 4}'}]
    '''
    chat.messages.append(
        {
            "role": "user",
            "content": user_input,
        }
    )
    chat.messages.append(
        {
            "role": "assistant",
            "content": result,
        }
    )


def slash_command(user_input, available_functions, chat):
    '''
    Handle local slash commands. Return True when handled locally and
    False when the input should be sent to the language model.

    >>> class DummyChat:
    ...     def __init__(self):
    ...         self.messages = []
    ...
    >>> funcs = {
    ...     "calculate": calculate,
    ...     "ls": ls,
    ...     "cat": cat,
    ...     "grep": grep,
    ... }
    >>> chat = DummyChat()

    >>> slash_command('/calculate 2 + 2', funcs, chat)
    {"result": 4}
    True

    >>> slash_command('/unknown', funcs, chat)
    Unknown command: unknown
    True

    >>> slash_command('/', funcs, chat)
    Unknown command
    True

    >>> slash_command('hello', funcs, chat)
    False
    '''
    if not user_input.startswith("/"):
        return False

    command, args = _parse_slash_command(user_input)

    if command is None:
        print("Unknown command")
        return True

    if command not in available_functions:
        print(f"Unknown command: {command}")
        return True

    try:
        result = _run_slash_command(command, args, available_functions)
        print(result)
        _record_slash_command(chat, user_input, result)
    except Exception as e:
        print(f"Unexpected error: {e}")

    return True


# repl: reads input and evaluates input
def repl(temperature=0.0):
    '''
    >>> def monkey_input(prompt, user_inputs=['/ls doctest_examples', '/calculate 2 + 2', '/cat doctest_examples/example.txt', '/unknown', '/grep hello doctest_examples/example.txt']):
    ...     try:
    ...         user_input = user_inputs.pop(0)
    ...         print(f'{prompt}{user_input}')
    ...         return user_input
    ...     except IndexError:
    ...         raise KeyboardInterrupt
    >>> import builtins
    >>> builtins.input = monkey_input
    >>> repl(temperature=0.0)
    chat> /ls doctest_examples
    doctest_examples/example.txt doctest_examples/example_utf16.txt 
    chat> /calculate 2 + 2
    {"result": 4}
    chat> /cat doctest_examples/example.txt
    hello world
    chat> /unknown
    Unknown command: unknown
    chat> /grep hello doctest_examples/example.txt
    hello world
    <BLANKLINE>
    '''
    readline.parse_and_bind("tab: complete")
    chat = Chat()

    available_functions = {
        "calculate": calculate,
        "ls": ls,
        "cat": cat,
        "grep": grep,
    }

    try:
        while True:
            # this makes the user interface nicer by saying 'chat>'
            user_input = input('chat> ')
            if slash_command(user_input, available_functions, chat):
                continue
            response = chat.send_message(user_input, temperature=temperature)
            print(response)
    except (KeyboardInterrupt, EOFError):
        print()


if __name__ == '__main__':
    repl(temperature=0.0)
