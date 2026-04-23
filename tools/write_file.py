'''
Defines a function that writes one file by calling write_files.
'''
from tools.write_files import write_files


def write_file(path, contents, commit_message):
    """
    Writes contents to a file and commits it to git.

    >>> write_file("doctest_examples/file.txt", "hello world", "add file")
    "Wrote 1 file(s) and committed with message '[docchat] add file'"

    >>> write_file("nonexistent_dir/file.txt", "data", "msg")
    'No such file or directory.'

    >>> write_file("/etc/passwd", "data", "msg")
    'Invalid path.'

    >>> write_file("../secret.txt", "data", "msg")
    'Invalid path.'
    """
    return write_files(
        [{"path": path, "contents": contents}],
        commit_message,
    )


tool_schema = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Write contents to a single file and commit it using git.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative file path to write."
                },
                "contents": {
                    "type": "string",
                    "description": "Contents to write into the file."
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message describing the change."
                }
            },
            "required": ["path", "contents", "commit_message"]
        }
    }
}
