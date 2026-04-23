"""
Defines a function that writes multiple files and commits them in a single git commit.
"""
from git import Repo
import os
from tools.valid_path import valid_path


def write_files(files, commit_message):
    """
    Writes multiple files and commits them in a single git commit.

    >>> write_files([{"path": "doctest_examples/file.txt", "contents": "data"}], "add data")
    "Wrote 1 file(s) and committed with message '[docchat] add data'"

    >>> write_files([], "add data")
    'No files provided.'

    >>> write_files([{"contents": "data"}], "add data")
    "Each file must have 'path' and 'contents'."

    >>> write_files([{"path": "/etc/passwd", "contents": "data"}], "msg")
    'Invalid path.'

    >>> write_files([{"path": "../secret.txt", "contents": "data"}], "msg")
    'Invalid path.'

    >>> write_files([{"path": "nonexistent_dir/file.txt", "contents": "data"}], "msg")
    'No such file or directory.'
    """
    if not files:
        return "No files provided."

    written_paths = []

    for file_info in files:
        if "path" not in file_info or "contents" not in file_info:
            return "Each file must have 'path' and 'contents'."

        path = file_info["path"]
        contents = file_info["contents"]

        if not valid_path(path):
            return "Invalid path."

        directory = os.path.dirname(path) or "."
        if not os.path.exists(directory):
            return "No such file or directory."

        with open(path, "w", encoding="utf-8") as f:
            f.write(contents)

        written_paths.append(path)

        repo = Repo(search_parent_directories=True)
        repo.index.add(written_paths)

        full_message = f"[docchat] {commit_message}"
        repo.index.commit(full_message)

        return f"Wrote {len(files)} file(s) and committed with message '{full_message}'"


tool_schema = {
    "type": "function",
    "function": {
        "name": "write_files",
        "description": "Write multiple files and commit them in a single git commit.",
        "parameters": {
            "type": "object",
            "properties": {
                "files": {
                    "type": "array",
                    "description": "List of files to write. Each file must include a path and contents.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Relative file path to write."
                            },
                            "contents": {
                                "type": "string",
                                "description": "Contents to write into the file."
                            }
                        },
                        "required": ["path", "contents"]
                    }
                },
                "commit_message": {
                    "type": "string",
                    "description": "Commit message describing the changes."
                }
            },
            "required": ["files", "commit_message"]
        }
    }
}
