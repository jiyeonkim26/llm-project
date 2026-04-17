"""CLI chat interface with Groq-backed chat and local tool execution."""

import json
import os
import readline

from dotenv import load_dotenv
from groq import Groq

from tools.calculate import calculate, tool_schema as calculate_schema
from tools.cat import cat, tool_schema as cat_schema
from tools.grep import grep, tool_schema as grep_schema
from tools.ls import ls, tool_schema as ls_schema

load_dotenv()


def get_available_functions():
    """Return the local tools available to the chat agent.

    >>> funcs = get_available_functions()
    >>> sorted(funcs.keys())
    ['calculate', 'cat', 'grep', 'ls']
    """
    return {
        "calculate": calculate,
        "ls": ls,
        "cat": cat,
        "grep": grep,
    }


def get_tool_schemas():
    """Return the schemas for Groq tool calling.

    >>> len(get_tool_schemas())
    4
    """
    return [calculate_schema, ls_schema, cat_schema, grep_schema]


def run_local_command(command_line, available_functions=None):
    """Run a slash command locally.

    Returns the tool output as a string.

    >>> funcs = get_available_functions()
    >>> run_local_command("/unknown", funcs)
    'Unknown command: unknown'
    >>> run_local_command("/", funcs)
    'Unknown command'
    >>> run_local_command("/calculate 2 + 2", funcs)
    '{"result": 4}'
    >>> run_local_command("/cat definitely_missing.txt", funcs)
    'File not found: definitely_missing.txt'
    >>> run_local_command("/grep hello definitely_missing.txt", funcs)
    ''
    """
    if available_functions is None:
        available_functions = get_available_functions()

    parts = command_line[1:].strip().split()
    if not parts:
        return "Unknown command"

    command = parts[0]
    args = parts[1:]

    if command not in available_functions:
        return f"Unknown command: {command}"

    if command == "calculate":
        if not args:
            return "Error: calculate requires an expression"
        expression = " ".join(args)
        return available_functions["calculate"](expression)

    if command == "ls":
        folder = args[0] if args else None
        return available_functions["ls"](folder)

    if command == "cat":
        if len(args) != 1:
            return "Error: cat requires exactly one filename"
        return available_functions["cat"](args[0])

    if command == "grep":
        if len(args) < 2:
            return "Error: grep requires a regex and a path"
        regex = args[0]
        path = " ".join(args[1:])
        return available_functions["grep"](regex, path)

    return f"Unknown command: {command}"


def execute_tool_call(tool_call, available_functions):
    """Execute a single Groq tool call.

    >>> class FakeFunction:
    ...     def __init__(self, name, arguments):
    ...         self.name = name
    ...         self.arguments = arguments
    >>> class FakeToolCall:
    ...     def __init__(self, name, arguments, call_id="abc123"):
    ...         self.function = FakeFunction(name, arguments)
    ...         self.id = call_id
    >>> funcs = get_available_functions()
    >>> call = FakeToolCall("calculate", '{"expression": "2 + 3"}')
    >>> execute_tool_call(call, funcs)
    ('calculate', '{"result": 5}')
    >>> call = FakeToolCall("ls", '{}')
    >>> name, output = execute_tool_call(call, funcs)
    >>> name
    'ls'
    >>> isinstance(output, str)
    True
    """
    function_name = tool_call.function.name
    function_to_call = available_functions[function_name]
    function_args = json.loads(tool_call.function.arguments)

    if function_name == "calculate":
        return function_name, function_to_call(function_args["expression"])

    if function_name == "ls":
        return function_name, function_to_call(function_args.get("folder"))

    if function_name == "cat":
        return function_name, function_to_call(function_args["filename"])

    if function_name == "grep":
        return function_name, function_to_call(
            function_args["regex"],
            function_args["path"],
        )

    raise ValueError(f"Unsupported tool: {function_name}")


class Chat:
    """Conversational agent with message history and Groq tool support.

    The client is injectable so that tests can use a fake client instead of
    making live API calls.

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
    >>> class FakeFunction:
    ...     def __init__(self, name, arguments):
    ...         self.name = name
    ...         self.arguments = arguments
    >>> class FakeToolCall:
    ...     def __init__(self, name, arguments, call_id="tool1"):
    ...         self.function = FakeFunction(name, arguments)
    ...         self.id = call_id
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

    Non-tool path:

    >>> fake_client = FakeClient([
    ...     FakeResponse(FakeMessage(content="Hello there.", tool_calls=None))
    ... ])
    >>> chat = Chat(client=fake_client)
    >>> chat.send_message("Hi", temperature=0.0)
    'Hello there.'

    Tool path:

    >>> tool_call = FakeToolCall("calculate", '{"expression": "2 + 2"}')
    >>> fake_client = FakeClient([
    ...     FakeResponse(FakeMessage(content=None, tool_calls=[tool_call])),
    ...     FakeResponse(FakeMessage(content="The answer is 4.", tool_calls=None)),
    ... ])
    >>> chat = Chat(client=fake_client)
    >>> chat.send_message("What is 2 + 2?", temperature=0.0)
    'The answer is 4.'
    """

    MODEL = "openai/gpt-oss-120b"

    def __init__(self, client=None):
        self.client = client or Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Write the output in 1-2 sentences. "
                    "Always use tools to complete tasks when appropriate. "
                    "Don't bold the answer."
                ),
            },
        ]

    def send_message(self, message, temperature=0.8):
        """Send a user message to the model and return the assistant response."""
        self.messages.append({"role": "user", "content": message})

        tools = get_tool_schemas()
        available_functions = get_available_functions()

        chat_completion = self.client.chat.completions.create(
            messages=self.messages,
            model=self.MODEL,
            temperature=temperature,
            seed=0,
            tools=tools,
            tool_choice="auto",
        )

        response_message = chat_completion.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            self.messages.append(response_message)

            for tool_call in tool_calls:
                function_name, function_response = execute_tool_call(
                    tool_call,
                    available_functions,
                )
                self.messages.append(
                    {
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": function_response,
                    }
                )

            second_response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=self.messages,
                tools=tools,
                tool_choice="auto",
            )
            result = second_response.choices[0].message.content
        else:
            result = response_message.content

        self.messages.append({"role": "assistant", "content": result})
        return result


def repl(temperature=0.0):
    """Run the interactive chat loop.

    Slash commands are handled locally.

    >>> class FakeChat:
    ...     def __init__(self):
    ...         self.messages = []
    ...     def send_message(self, message, temperature=0.0):
    ...         return f"echo: {message}"
    >>> inputs = iter(["/calculate 2 + 2", "/unknown", "hello"])
    >>> def fake_input(prompt):
    ...     value = next(inputs)
    ...     print(f"{prompt}{value}")
    ...     return value
    >>> import builtins
    >>> old_input = builtins.input
    >>> old_chat = globals()["Chat"]
    >>> builtins.input = fake_input
    >>> globals()["Chat"] = FakeChat
    >>> try:
    ...     repl(temperature=0.0)
    ... except StopIteration:
    ...     print()
    chat> /calculate 2 + 2
    {"result": 4}
    chat> /unknown
    Unknown command: unknown
    chat> hello
    echo: hello
    <BLANKLINE>
    >>> builtins.input = old_input
    >>> globals()["Chat"] = old_chat
    """
    readline.parse_and_bind("tab: complete")
    chat = Chat()
    available_functions = get_available_functions()

    try:
        while True:
            user_input = input("chat> ")

            if user_input.startswith("/"):
                try:
                    result = run_local_command(user_input, available_functions)
                    print(result)
                    chat.messages.append({"role": "user", "content": user_input})
                    chat.messages.append({"role": "assistant", "content": result})
                except Exception as exc:
                    print(f"Unexpected error: {exc}")
                continue

            response = chat.send_message(user_input, temperature=temperature)
            print(response)

    except (KeyboardInterrupt, EOFError):
        print()
    except Exception as exc:
        print(f"Unexpected error: {exc}")


if __name__ == "__main__":
    repl(temperature=0.0)
