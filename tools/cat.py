def cat(filename):
    """
    This tool returns the contents of a file.

    >>> print(cat("example.txt"))
    hello world

    >>> print(cat("README.md"))
    # llm-project
    <BLANKLINE>
    <img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/test.yaml/badge.svg" /> <img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/integration.yaml/badge.svg" /> <img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/flake8/badge.svg" />
    <BLANKLINE>
    <BLANKLINE>
    A command-line chatbot that maintains simple conversational context. This project uses GROQ to create a text-based AI assistant.
    <BLANKLINE>
    Here is a link to the PyPI package: https://pypi.org/project/cmc-csci040-JiyeonKim/.
    <BLANKLINE>
    To check code coverage for the tools:
    '''
    $ coverage run -m doctest -v tools/*.py
    $ coverage report -m
    '''

    >>> cat("does_not_exist.txt")
    "Error: [Errno 2] No such file or directory: 'does_not_exist.txt'"

    >>> print(cat("example_utf16.txt"))
    hello world
    >>>
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(filename, "r", encoding="utf-16") as f:
            return f.read()
    except (FileNotFoundError, OSError) as e:
        return f"Error: {e}"


tool_schema = {
    "type": "function",
    "function": {
        "name": "cat",
        "description": "Open a file and return its contents",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The path of the file to read"
                }
            },
            "required": ["filename"]
        }
    }
}
