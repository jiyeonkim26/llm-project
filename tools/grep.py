'''
cat.py defines the function that allows the grep tool to be called and used by chat.py.
'''
import glob
import os
import re


def grep(regex, path):
    '''
    This tool searches every file matching a glob path and return lines that match regex.

    >>> print(grep("append", "chat.py"))
           self.messages.append(
                self.messages.append(response_message)
                        self.messages.append({
                    self.messages.append({
                self.messages.append({
                self.messages.append({
                        chat.messages.append({
                        chat.messages.append({

    >>> print(grep("hello", "doctest_examples/example_utf16.txt"))
    hello world

    >>> print(grep("hello", "filenotfound.txt"))
    <BLANKLINE>

    >>> grep("mike izbicki", "chat.py")
    ''

    >>> grep("hello", "/tools")
    ''

    >>> grep("hello", "..")
    ''

    >>> grep("(", "chat.py")
    ''

    >>> grep("hello", "*")
    ''

    >>> grep("hello", "tools")
    ''
    '''
    try:
        # Block absolute paths
        if os.path.isabs(path):
            return ""

        # Block directory traversal
        normalized = os.path.normpath(path)
        if normalized.startswith("..") or "/.." in normalized or "\\.." in normalized:
            return ""

        if any(char in path for char in "*?[]"):
            return ""

        matched_files = sorted(glob.glob(path))

        results = []

        pattern = re.compile(regex, re.IGNORECASE)

        for filename in matched_files:
            # Only read regular files
            if not os.path.isfile(filename):
                continue

            try:
                with open(filename, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(filename, "r", encoding="utf-16") as f:
                    lines = f.readlines()

            for line in lines:
                if pattern.search(line):
                    results.append(line.rstrip("\n"))

        return "\n".join(results)

    except re.error:
        return ""


tool_schema = {
    "type": "function",
    "function": {
        "name": "grep",
        "description": "Returns lines in a file that match the regex",
        "parameters": {
            "type": "object",
            "properties": {
                "regex": {
                    "type": "string",
                    "description": "The regular expression to search for."
                },
                "path": {
                    "type": "string",
                    "description": "The path of the file to read."
                }
            },
            "required": ["regex", "path"]
        }
    }
}
