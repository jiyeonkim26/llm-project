# LLM Agent

<img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/doctest.yaml/badge.svg?branch=agent" /> <img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/integration.yaml/badge.svg?branch=agent" /> <img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/flake8.yaml/badge.svg?branch=agent" />
[![PyPI version](https://img.shields.io/pypi/v/cmc-csci040-JiyeonKim)](https://pypi.org/project/cmc-csci040-JiyeonKim/)
[![codecov](https://codecov.io/github/jiyeonkim26/llm-project/branch/agent/graph/badge.svg?token=B5QEXH1O6I)](https://codecov.io/github/jiyeonkim26/llm-project)

This is a command-line chatbot that maintains simple conversational context. This project uses GROQ to create a text-based AI assistant. 

![chat demo](demo.gif)

## Install / Usage Examples
This example shows how the package can be installed and used to list the files in a project folder.
```
$ pip install cmc-csci040-JiyeonKim
$ cd test_projects/jiyeonkim26.github.io
$ chat
chat> what files are in this project?
The project contains the following files: README.md, about.html, index.html, projects.html, and styles.css.
```

This example shows how the chatbot can scan project files for certain text or keywords using the grep tool.
```
$ cd test_projects/markdown_compiler
$ chat
chat> does this project use regex?
The codebase does not import or use the `re` module; all markdown parsing is done with plain string operations rather than regular expressions.
```

This example shows the chatbot describing a project, its function, and its outputs. 
```
$ cd test_projects/webscraping-ebay
$ chat
chat> what does this project do?
The project provides a Python script (`ebay-dl.py`) that scrapes eBay listings for a given search term and outputs the results as JSON (and optionally CSV), including item name, condition, price, number sold, free‑returns flag, and shipping cost. It includes sample data files for Apple Watch, KitchenAid mixers, and teddy bears.
chat> is this legal?
Web scraping is generally legal in the United States as long as you respect the site’s terms of service, do not bypass technical barriers, and use the data only for permissible purposes; however, eBay’s terms may restrict automated data collection, so you should review their policies and possibly obtain permission before running the script at scale.
```

This example demonstrates that the chatbot can create and remove files when asked with changes automatically committed to the git repo.
```
$ ls doctest_examples 
__pycache__             example_utf16.txt       example.txt             file.txt                rm_test.txt             test.pychat
$ chat
chat> what files are in the doctest_examples folder?
The folder contains `__pycache__/`, `example.txt`, `example_utf16.txt`, `file.txt`, `rm_test.txt`, and `test.py`.
chat> add a file titled hello_world.txt with 'hello world' as the file's contents into the folder.
Added `hello_world.txt` containing “hello world” to the `doctest_examples` folder.
chat> ^c
$ git log --oneline
5fcc5f0 (HEAD -> agent) [docchat] Add hello_world.txt with greeting
$ chat
chat> what files are now in the doctest_examples folder?
The folder now contains `__pycache__/`, `example.txt`, `example_utf16.txt`, `file.txt`, `hello_world.txt`, `rm_test.txt`, and `test.py`.
chat> thanks, now remove the hello_world.txt file from the folder.
The hello_world.txt file has been removed. The folder now contains __pycache__, example.txt, example_utf16.txt, file.txt, rm_test.txt, and test.py.
chat> ^c
$ ls doctest_examples
__pycache__             example_utf16.txt       example.txt             file.txt                rm_test.txt             test.py
$ git log --oneline
372eec8 (HEAD -> agent) [docchat] rm doctest_examples/hello_world.txt
```