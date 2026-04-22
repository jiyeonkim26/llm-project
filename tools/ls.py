'''
ls.py defines the function that allows the ls tool to be called and used by chat.py.
'''
# step 1: create function wiht the right number of args; write the docstring
# step 2: create the doctests for that function
# step 3: get the function to pass doctest
# step 3b: may have to modify doctests to get them to pass
# step 4: you know you have enough doctests if you have 100% code coverage
import glob


def ls(folder=None):
    """
    This tool behaves just like the ls program in the shell.

    >>> ls('doesnotexist')
    ''

    >>> output = ls()
    >>> "chat.py" in output
    True

    >>> ls('doctest_examples')
    'doctest_examples/__pycache__ doctest_examples/example.txt doctest_examples/example_utf16.txt doctest_examples/test.py '
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
