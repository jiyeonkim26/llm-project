"""CLI chat interface using the Groq API and local tools."""

import json
import os
import readline

from groq import Groq
from tools.calculate import calculate, tool_schema as calculate_schema
from tools.ls import ls, tool_schema as ls_schema
from tools.cat import cat, tool_schema as cat_schema
from tools.grep import grep, tool_schema as grep_schema
from dotenv import load_dotenv

load_dotenv()


class Chat:
    """
    A conversational chat agent that maintains message history and interacts
    with the Groq API.

    The class supports automatic tool use, such as calculate, ls, cat, and
    grep, by detecting and executing model-requested function calls and then
    incorporating their results into the final response.
    """

    MODEL = "openai/gpt-oss-120b"

    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))

        self.messages = [
            {
                "role": "system",
                "content": (
                    "Write the output in 1-2 sentences. Always use tools to "
                    "complete tasks when appropriate. Don't bold the answer."
                ),
            },
        ]

    def send_message(self, message, temperature=0.8):
        """
        >>> class FakeMessage:
        ...     def __init__(self, content=None, tool_calls=None):
        ...         self.content = content
        ...         self.tool_calls = tool_calls
        >>> class FakeChoice:
        ...     def __init__(self, message):
        ...         self.message = message
        >>> class FakeResponse:
        ...     def __init__(self, message):
        ...         self.choices = [FakeChoice(message)]
        >>> class FakeCompletions:
        ...     def __init__(self, responses):
        ...         self.responses = responses
        ...         self.index = 0
        ...     def create(self, **kwargs):
        ...         response = self.responses[self.index]
        ...         self.index += 1
        ...         return response
        >>> class FakeChatAPI:
        ...     def __init__(self, responses):
        ...         self.completions = FakeCompletions(responses)
        >>> class FakeClient:
        ...     def __init__(self, responses):
        ...         self.chat = FakeChatAPI(responses)

        >>> chat = Chat()
        >>> chat.client = FakeClient([
        ...     FakeResponse(FakeMessage(content="Hello there.", tool_calls=None))
        ... ])
        >>> chat.send_message("Hi", temperature=0.0)
        'Hello there.'
        """
        self.messages.append(
            {
                # system: never change; user: changes a lot
                # the message that you are sending to the AI
                "role": "user",
                "content": message,
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
                        function_args["path"]
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
                    "role": "assistant",
                    "content": result,
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


def run_local_command(user_input, available_functions):
    """
    Run a slash command locally.

    >>> funcs = {
    ...     "calculate": calculate,
    ...     "ls": ls,
    ...     "cat": cat,
    ...     "grep": grep,
    ... }
    >>> run_local_command("/unknown", funcs)
    'Unknown command: unknown'
    >>> run_local_command("/", funcs)
    'Unknown command'
    >>> run_local_command("/calculate 2 + 2", funcs)
    '{"result": 4}'
    >>> run_local_command("/cat definitely_missing.txt", funcs)
    "Error: [Errno 2] No such file or directory: 'definitely_missing.txt'"
    >>> run_local_command("/grep hello definitely_missing.txt", funcs)
    ''
    """
    parts = user_input[1:].strip().split()

    if not parts:
        return "Unknown command"

    command = parts[0]
    args = parts[1:]

    if command not in available_functions:
        return f"Unknown command: {command}"

    if command == "calculate":
        if len(args) < 1:
            return "Error: calculate requires an expression"
        expression = " ".join(args)
        return calculate(expression)

    if command == "ls":
        folder = args[0] if args else None
        return ls(folder)

    if command == "cat":
        if len(args) != 1:
            return "Error: cat requires exactly one filename"
        return cat(args[0])

    if command == "grep":
        if len(args) < 2:
            return "Error: grep requires a regex and a path"
        regex = args[0]
        path = " ".join(args[1:])
        return grep(regex, path)

    return f"Unknown command: {command}"


# this makes the user interface nicer by saying 'chat>'
# repl: reads input and evaluates input
"""
if __name__ == '__main__':
   chat = Chat()
   try:
       while True:
               user_input = input('chat>')
               response = chat.send_message(user_input)
               print(response)
   except KeyboardInterrupt:
       print()
"""


def repl(temperature=0.0):
    """
    >>> def monkey_input(
    ...     prompt,
    ...     user_inputs=[
    ...         '/ls',
    ...         '/calculate 2 + 2',
    ...         '/cat doctest_examples/example.txt',
    ...         '/unknown',
    ...         '/grep hello doctest_examples/example.txt'
    ...     ]
    ... ):
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
    README.md __pycache__ chat.py cmc_csci040_JiyeonKim.egg-info coverage.xml demo.gif doctest_examples pyproject.toml requirements.txt test_projects tools
    chat> /calculate 2 + 2
    {"result": 4}
    chat> /cat doctest_examples/example.txt
    hello world
    chat> /unknown
    Unknown command: unknown
    chat> /grep hello doctest_examples/example.txt
    hello world
    <BLANKLINE>
    """
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
            user_input = input("chat> ")

            # Handle slash commands locally: /command param1 param2
            if user_input.startswith("/"):
                result = run_local_command(user_input, available_functions)
                print(result)

                # Store the slash command and result in conversation history
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
                continue

            response = chat.send_message(user_input, temperature=temperature)
            print(response)

    except (KeyboardInterrupt, EOFError):
        print()

    except Exception as exc:
        print(f"Unexpected error: {exc}")


if __name__ == "__main__":
    repl(temperature=0.0)
