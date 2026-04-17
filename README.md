# Building an LLM

<img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/doctest.yaml/badge.svg" /> <img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/integration.yaml/badge.svg" /> <img src="https://github.com/jiyeonkim26/llm-project/actions/workflows/flake8.yaml/badge.svg" />
[![PyPI version](https://img.shields.io/pypi/v/cmc-csci040-JiyeonKim)](https://pypi.org/project/cmc-csci040-JiyeonKim/)
[![codecov](https://codecov.io/github/jiyeonkim26/llm-project/graph/badge.svg?token=B5QEXH1O6I)](https://codecov.io/github/jiyeonkim26/llm-project)

This is a command-line chatbot that maintains simple conversational context. This project uses GROQ to create a text-based AI assistant. 

<!-- pictures/demos should generally be "above the fold" so that readers see them quickly -->
![chat demo](demo.gif)

<!--
Here is a link to the PyPI package: https://pypi.org/project/cmc-csci040-JiyeonKim/. 
the link in the badge is enough
-->

<!-- single word / very short titles are better; enables skimming -->
## Install / Usage

Anytime you have a codeblock/figure, you need a sentence introducing it and explaining why the reader should care.
Do not introduce codeblocks/figures with ### headers.
```
$ pip install cmc-csci040-JiyeonKim
$ cd test_projects/jiyeonkim26.github.io
$ chat
chat> what files are in this project?
The project contains the following files: README.md, about.html, index.html, projects.html, and styles.css.
```
Notice how I edited the code block above to contain both the install and usage commands.
Now this code block has everything a potential user of your application might need in order to know if they want to use your tool and how to use it.

```
$ cd test_projects/markdown_compiler
$ chat
chat> does this project use regex?
The codebase does not import or use the `re` module; all markdown parsing is done with plain string operations rather than regular expressions.
```

```
$ cd test_projects/webscraping-ebay
$ chat
chat> what does this project do?
The project provides a Python script (`ebay-dl.py`) that scrapes eBay listings for a given search term and outputs the results as JSON (and optionally CSV), including item name, condition, price, number sold, free‑returns flag, and shipping cost. It includes sample data files for Apple Watch, KitchenAid mixers, and teddy bears.
chat> is this legal?
Web scraping is generally legal in the United States as long as you respect the site’s terms of service, do not bypass technical barriers, and use the data only for permissible purposes; however, eBay’s terms may restrict automated data collection, so you should review their policies and possibly obtain permission before running the script at scale.
```

<!--
I think you're aware that this was supposed to be in the github action,
but you couldn't figure out how to get it to work?

### To check code coverage for the tools and `chat.py`:
```
$ coverage run -m doctest -v tools/*.py chat.py
$ coverage report -m
$ coverage html  # if you want a line-by-line look at which lines are covered/uncovered.
```
-->
