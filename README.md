# llm-project

<img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/test.yaml/badge.svg" /> <img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/integration.yaml/badge.svg" /> <img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/flake8.yaml/badge.svg" />
[![PyPI version](https://img.shields.io/pypi/v/cmc-csci040-JiyeonKim)](https://pypi.org/project/cmc-csci040-JiyeonKim/)

This is a command-line chatbot that maintains simple conversational context. This project uses GROQ to create a text-based AI assistant. 

Here is a link to the PyPI package: https://pypi.org/project/cmc-csci040-JiyeonKim/. 
### To install the package:
```
$ pip install cmc-csci040-JiyeonKim
$ chat
chat>
```

### Animated GIF example of the chat program:
![chat demo](demo.gif)

### Personal Webpage Example:
```
$ cd test_projects/jiyeonkim26.github.io
$ chat
chat> what files are in this project?
The project contains the following files: README.md, about.html, index.html, projects.html, and styles.css.
```

### Markdown Compiler Example:
```
$ cd test_projects/markdown_compiler
$ chat
chat> does this project use regex?
The codebase does not import or use the `re` module; all markdown parsing is done with plain string operations rather than regular expressions.
```

### Webscraping eBay Example:
```
$ cd test_projects/webscraping-ebay
$ chat
chat> what does this project do?
The project provides a Python script (`ebay-dl.py`) that scrapes eBay listings for a given search term and outputs the results as JSON (and optionally CSV), including item name, condition, price, number sold, free‑returns flag, and shipping cost. It includes sample data files for Apple Watch, KitchenAid mixers, and teddy bears.
chat> is this legal?
Web scraping is generally legal in the United States as long as you respect the site’s terms of service, do not bypass technical barriers, and use the data only for permissible purposes; however, eBay’s terms may restrict automated data collection, so you should review their policies and possibly obtain permission before running the script at scale.
```

### To check code coverage for the tools and `chat.py`:
```
$ coverage run -m doctest -v tools/*.py chat.py
$ coverage report -m
$ coverage html  # if you want a line-by-line look at which lines are covered/uncovered.
```
