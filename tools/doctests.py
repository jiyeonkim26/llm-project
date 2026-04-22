'''
doctests.py defines the function that allows the doctests tool to be called and used by chat.py.
'''
import sys
import doctest
import importlib.util
import os


def doctests(path):
    '''
    This tool runs the doctests (with the --verbose flag) and returns the output.

    >>> doctests("tools/cat.py")
    --- Running doctests for: tools/cat.py ---
    Trying:
        cat("does_not_exist.txt")
    Expecting:
        "Error: [Errno 2] No such file or directory: 'does_not_exist.txt'"
    ok
    Trying:
        print(cat("doctest_examples/example_utf16.txt"))
    Expecting:
        hello world
    ok
    Trying:
        print(cat("doctest_examples/example.txt"))
    Expecting:
        hello world
    ok
    1 item had no tests:
        cat
    1 item passed all tests:
       3 tests in cat.cat
    3 tests in 2 items.
    3 passed.
    Test passed.

    >>> doctests("doctest_examples/example.txt")
    Skipping doctest_examples/example.txt: Not a .py file

    >>> doctests("doctest_examples")
    Skipping doctest_examples: Not a .py file

    >>> doctests("doctest_examples/does_not_exist.txt")
    Skipping doctest_examples/does_not_exist.txt: Not a .py file

    >>> doctests("doctest_examples/example_utf16.txt")
    Skipping doctest_examples/example_utf16.txt: Not a .py file
    '''
    if path.endswith(".py") and os.path.isfile(path):
        print(f"--- Running doctests for: {path} ---")

        # Dynamically load the module from the path
        module_name = os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Run doctest on the imported module
        doctest.testmod(module, verbose=True)
    else:
        print(f"Skipping {path}: Not a .py file")


tool_schema = {
    "type": "function",
    "function": {
        "name": "doctests",
        "description": "Run a doctest on a file with the --verbose flag and return the output",
        "parameters": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The path and name of the file to test"
                }
            },
            "required": ["paths"]
        }
    }
}
