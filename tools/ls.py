'''
ls.py defines the function that allows the ls tool to be called and used by chat.py.
'''
import glob


def ls(folder=None):
    """
    Behaves just like the ls program in the shell.

    >>> ls('doesnotexist')
    ''

    >>> output = ls()
    >>> "chat.py" in output
    True

    >>> ls('.github')
    '.github/workflows '
    """
    if folder:
        result = ""
        # glob is nondeterministic; sort for consistent output
        for path in sorted(glob.glob(folder + "/*")):
            result += path + " "
        return result
    else:
        result = ""
        for path in sorted(glob.glob("*")):
            result += path + " "
        return result.strip()
        # it is much better to balance the if/else statements;
        # much easier to read this way;
        # even better would be to factor out the common code between them


tool_schema = {
    "type": "function",
    "function": {
        "name": "ls",
        "description": (
            "List the files in the current folder or in the specified folder"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "folder": {
                    "type": "string",
                    "description": "The folder to list files",
                }
            },
            "required": ["folder"],
        },
    },
}
