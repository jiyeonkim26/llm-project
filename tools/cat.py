'''
cat.py defines the function that allows the cat tool to be called and used by chat.py.
'''


def cat(filename):
    """
    This tool returns the contents of a file.

    >>> cat("does_not_exist.txt")
    "Error: [Errno 2] No such file or directory: 'does_not_exist.txt'"

    # these are all excellent test cases that you have;
    # good job writing them;
    # it is unfortunate that your doctests don't actually run them :(
    # (I do believe they at least mostly work though)
    >>> print(cat("doctest_examples/example_utf16.txt"))
    hello world

    >>> print(cat("doctest_examples/example.txt"))
    hello world
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
