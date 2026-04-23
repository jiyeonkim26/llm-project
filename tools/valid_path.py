'''
Helper function that checks whether a path is an absolute path or '..'.
'''
import os


def valid_path(path):
    """
    Returns True if path is safe to use.

    A safe path:
    - is not absolute
    - does not contain '..'

    >>> valid_path("doctest_examples/file.txt")
    True
    >>> valid_path("/etc/passwd")
    False
    >>> valid_path("../secret.txt")
    False
    >>> valid_path("foo/../bar.txt")
    False
    >>> valid_path(None)
    False
    >>> valid_path(123)
    False
    >>> valid_path("")
    False
    """
    if not isinstance(path, str) or not path:
        return False

    # Reject absolute paths
    if os.path.isabs(path):
        return False

    # Check raw path for traversal BEFORE normalization
    if ".." in path.split(os.sep):
        return False

    return True


tool_schema = {
    "type": "function",
    "function": {
        "name": "valid_path",
        "description": "Check whether a given file path is safe to use. A valid path is not absolute and does not contain directory traversal like '..'.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The file path to validate."
                }
            },
            "required": ["path"]
        }
    }
}
