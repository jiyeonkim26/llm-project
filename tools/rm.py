"""
Removes one or more files using glob pattern and commits the deletion to git.
"""
import os
import glob
from git import Repo, GitCommandError
from tools.valid_path import valid_path


def rm(path):
    """
    Removes one or more files matching path and commits the deletion.

    >>> rm("doctest_examples/rm_test.txt")
    "Removed 1 file(s) and committed with message '[docchat] rm doctest_examples/rm_test.txt'"
    >>> rm("doctest_examples/*.does_not_exist")
    'No files matched.'
    >>> rm("/etc/passwd")
    'Invalid path.'
    >>> rm("../secret.txt")
    'Invalid path.'
    >>> rm("doctest_examples")
    'Refusing to remove directories.'
    """
    if not valid_path(path):
        return "Invalid path."

    matches = sorted(glob.glob(path))
    if not matches:
        return "No files matched."

    for match in matches:
        if os.path.isdir(match):
            return "Refusing to remove directories."
        
        else:
            repo = Repo(search_parent_directories=True)
            repo_root = repo.working_tree_dir

            abs_matches = [os.path.abspath(match) for match in matches]
            rel_matches = [os.path.relpath(match, repo_root) for match in abs_matches]

            for match in abs_matches:
                os.remove(match)

            # Stage deletions for tracked files
            repo.git.add("--update", *rel_matches)

            commit_message = f"[docchat] rm {path}"
            repo.index.commit(commit_message)

            return f"Removed {len(matches)} file(s) and committed with message '{commit_message}'"


tool_schema = {
    "type": "function",
    "function": {
        "name": "rm",
        "description": "Remove one or more files using a glob pattern and commit the deletion to git.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "A relative file path or glob pattern to remove.",
                }
            },
            "required": ["path"],
        },
    },
}
