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

    >>> ls()
    'README.md __pycache__ chat.py cmc_csci040_JiyeonKim.egg-info coverage.xml demo.gif dist doctest_examples htmlcov junit.xml ls.json pyproject.toml reader-whl requirements.txt test_projects tools venv'

    >>> ls('tools')
    'tools/__init__.py tools/__pycache__ tools/calculate.py tools/cat.py tools/grep.py tools/ls.py '
    """
    if folder:
        result = ""

        # glob is nondeterministic; sort for consistent output
        for path in sorted(glob.glob(folder + "/*")):
            result += path + " "

        return result

    result = ""

    for path in sorted(glob.glob("*")):
        result += path + " "

    return result.strip()


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
