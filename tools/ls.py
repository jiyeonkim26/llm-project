# step 1: create function wiht the right number of args; write the docstring
# step 2: create the doctests for that function
# step 3: get the function to pass doctest
# step 3b: may have to modify doctests to get them to pass
# step 4: you know you have enough doctests if you have 100% code coverage


import glob


def ls(folder=None):
   '''
   This function behaves just like the ls program in the shell.
   >>> ls()
   'README.md __pycache__ build chat.py cmc_cs040_JiyeonKim.egg-info dist htmlcov pyproject.toml requirements.txt tools venv'
   >>> ls('tools')
   'tools/__pycache__ tools/ls.py '
   '''
   if folder:
       result = ''
       # folder + '/' ==> tools
       # glob is non deterministic; no guarantee about order of glob results
       # need to convert nondeterministic to deterministic
       for path in sorted(glob.glob(folder + '/*')):
           result += path + ' '
       return result
   else:
       result = ''
       for path in sorted(glob.glob('*')):
           result += path + ' '
       return result.strip()


tool_schema = {
  "type": "function",
  "function": {
    "name": "ls",
    "description": "List out the files in the current folder or the folder of the argument raised",
    "parameters": {
      "type": "object",
      "properties": {
        "expression": {
          "type": "string",
          "description": "The folder to list files"
        }
      },
      "required": ["expression"]
    }
  }
}