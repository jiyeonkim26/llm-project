# AGENTS.md

## Dev environment tips
- Create and activate a virtual environment before working on the project.
- Install dependencies with `pip install -e .` or `pip install -r requirements.txt`.
- Run the chat tool with `chat` after installation, or `python chat.py` during development.
- Tool modules live in `tools/` and should expose both the tool function and `tool_schema`.
- Store `GROQ_API_KEY` in environment variables or `.env`, never in committed files.

## Testing instructions
- Run doctests with `pytest --doctest-modules`.
- Run coverage with `pytest --cov=chat --cov=tools --cov-branch --cov-report=term-missing`.
- If configured, run lint checks before committing.
- Add or update doctests/tests whenever you modify a tool or chat behavior.

## PR instructions
- Title format: [chat] <Title>
- Ensure tests and doctests pass before committing.
- Commit changes with clear messages, especially when updating tools or schemas.