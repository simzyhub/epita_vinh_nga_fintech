# Comparing the two runs

## sys.executable and sys.prefix

With a normal `python scripts/inspect_env.py`:

- `sys.executable` = `/opt/homebrew/opt/python@3.14/bin/python3.14`
- `sys.prefix` = `/opt/homebrew/opt/python@3.14/Frameworks/Python.framework/Versions/3.14`
- not in a venv (`sys.prefix` and `sys.base_prefix` are the same)

With `uv run python scripts/inspect_env.py`:

- `sys.executable` = `.../epita_vinh_nga_fintech/.venv/bin/python`
- `sys.prefix` = `.../epita_vinh_nga_fintech/.venv`
- in a venv (`sys.prefix` != `sys.base_prefix`)

So the first run uses the Homebrew Python on the machine. The second one uses the project's `.venv` instead. PATH also changes: Homebrew first in the global run, `.venv/bin` first with `uv run`.

## How uv run works without activate

Normally you run `source .venv/bin/activate` so your shell switches to the venv (it changes PATH). You stay in that env until you deactivate.

`uv run` does not change your shell. It just starts the command inside the `.venv` for that one process: it uses the venv's python and puts `.venv/bin` at the front of PATH for that command only. After it finishes, your shell is still on the global Python. That's why we see a real venv in the output without ever calling activate.
