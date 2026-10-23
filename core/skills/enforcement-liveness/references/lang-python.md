# Language reference — Python

Load this only when the diff contains Python (`*.py`, `pyproject.toml`, `requirements*.txt`). Use it as a review lens: each item says what fails and how to check it.

## Checks (run by whoever holds Bash; a read-only reviewer cites the completion audit's run)

| Tool | Command | What it catches |
|---|---|---|
| linter | `ruff check .` | bugs, unused code, risky patterns |
| types | `mypy .` (with the project's config) | type errors the tests miss |
| security | `bandit -r <package>` | shell injection, unsafe deserialization, weak crypto |
| tests | the project's test command (for example `pytest -q`) | behaviour |
| dependencies | `pip-audit` | dependencies with published vulnerabilities |

Quote each command's output in the evidence. A tool the project does not have installed is a gap to state, not a pass.

Test helpers that create a Git repository, and asserting on full output lines: `test-isolation.md` (shared by every language).

## Blocking
- SQL built by string formatting or concatenation with any input; use parameters.
- `subprocess` with `shell=True` on input, `eval`/`exec` on input, or `pickle`/`yaml.load` (without a safe loader) on data the program did not create.
- A bare `except:` or `except Exception: pass` on a path that writes, deletes, pays, or authorizes: failures disappear.
- Network calls (`requests`, `httpx`, clients) with no timeout.
- Money held in `float`; use `Decimal` or integer minor units.

## Should fix
- Mutable default arguments (`def f(x=[])`).
- Naive `datetime` values mixed with aware ones, or local time stored where UTC is meant.
- Blocking calls inside `async def` functions.
- `assert` used for input validation (it is removed under `-O`).

## Nit
- Missing type hints on public functions; imports not sorted per the project's tool.
