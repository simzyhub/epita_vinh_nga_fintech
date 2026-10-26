## 1.3 Deliverable for Part 1 (Question 3)

### Comparing the two runs

I ran `scripts/inspect_env.py` two ways and compared the output.

**Without uv (normal python):**
- `sys.executable` = `/opt/homebrew/opt/python@3.14/bin/python3.14`
- `sys.prefix` = `/opt/homebrew/opt/python@3.14/Frameworks/Python.framework/Versions/3.14`
- It is NOT using a venv, because `sys.prefix` and `sys.base_prefix` are the same.

**With `uv run python scripts/inspect_env.py`:**
- `sys.executable` = `.../epita_vinh_nga_fintech/.venv/bin/python`
- `sys.prefix` = `.../epita_vinh_nga_fintech/.venv`
- Here it IS a venv (`sys.prefix` is different from `sys.base_prefix`).

So basically the first command uses my Homebrew Python on the Mac, and the second one uses the project `.venv`. PATH also changes: Homebrew stuff first in the global run, `.venv/bin` first when I use `uv run`.

### How `uv run` works without activate

Normally if I want a venv I do `source .venv/bin/activate`, then my shell stays in that env until I deactivate.

With `uv run` I don't need that. It just runs that one command inside the `.venv` (uses the venv python and puts `.venv/bin` first in PATH for that process only). When the command finishes, my shell is still on the normal global Python. That's why the inspect script shows a real venv even though I never activated it.

---

## 2.5 Deliverable for Part 2

### git status

```
On branch vinh-nga-le
Ignored files:
  (use "git add -f <file>..." to include in what will be committed)
	.env
	.venv/
	global_env_output.txt
	src/epita_vinh_nga_fintech/__pycache__/
	uv_env_output.txt

nothing to commit, working tree clean
```

`.env` shows up under Ignored files, so git is not tracking it (because of `.gitignore`).  
`.env.template` is tracked (I can see it with `git ls-files`, and it does not appear as untracked in `git status`).

### Live API call (redacted)

```
uv run python -c "from epita_vinh_nga_fintech.client import fetch_live_data; print(fetch_live_data())"
      Built epita-vinh-nga-fintech @ file:///Users/lenga/Documents/epita/ep
Uninstalled 1 package in 1.17s
Installed 1 package in 4ms
{'status': 'LIVE_SUCCESS', 'currency': 'EUR', 'available_balance': 0.0, 'livemode': False}
```

There is no API key in this output, just some balance info.

### Why env vars are better than putting secrets in config.json / settings.yaml

1. If the secret is in a file inside the project, it's easy to accidentally `git add` / push it. Then the key is in git history forever. With env vars + `.gitignore` on `.env`, the real secret stays on my machine.
2. Env vars are easier to change per environment (local, CI, server) without editing and sharing config files. Config files with secrets get copied around and left on disk more easily.

---

## Dependency tree and uv.lock

### uv tree output

```
epita-vinh-nga-fintech v0.1.0
├── python-dotenv v1.2.4
├── requests v2.34.2
│   ├── certifi v2026.10.23
│   ├── charset-normalizer v3.5.2
│   ├── idna v3.20
│   └── urllib3 v2.8.0
├── rich v15.0.0
│   ├── markdown-it-py v4.2.0
│   │   └── mdurl v0.1.2
│   └── pygments v2.21.0
└── pytest v9.1.1 (group: dev)
    ├── iniconfig v2.3.1
    ├── packaging v26.3
    ├── pluggy v1.7.0
    └── pygments v2.21.0
```

### Direct dependencies

These are the ones I put in `pyproject.toml`:
- python-dotenv
- requests
- rich
- pytest (dev group)

### Transitive dependencies

These come automatically because other packages need them.

From **requests**:
- certifi
- charset-normalizer
- idna
- urllib3

From **rich**:
- markdown-it-py (and that one also needs mdurl)
- pygments

### How SHA-256 hashes in uv.lock help against supply-chain attacks

In `uv.lock`, each package file (wheel / sdist) has something like `hash = "sha256:...."`.

When uv installs, it downloads the file and checks the hash again. If someone replaced the file on PyPI or on a mirror with malware (same version name but different bytes), the hash would not match and the install fails. Just locking the version number is not enough, because the attacker can keep the same version string. The hash is what checks the actual file content.

---

## 3.3 Semantic Versioning (SemVer) Analysis

### What each range means

- `requests = "^2.31.0"`  
  Means versions `>= 2.31.0` and `< 3.0.0`. So any newer 2.x is ok, but not 3.0.0.

- `urllib3 = "~=2.2.1"`  
  This is the PEP 440 compatible release operator. It means `>= 2.2.1` and `< 2.3.0` (only patch updates in 2.2.x).

- `rich = "==13.7.1"`  
  Exactly version 13.7.1, nothing else.

### If upstream releases 3.0.0 with breaking changes, will `uv lock --upgrade` install it with `^2.31.0`?

No. `^2.31.0` stops before 3.0.0 (`<3.0.0`), so even with `--upgrade` uv will not pick 3.0.0. I would have to change the range in `pyproject.toml` first (for example to `^3.0.0`).

### Difference between pyproject.toml and uv.lock

- `pyproject.toml` = what I declare (allowed version ranges, like `^` or `>=`).
- `uv.lock` = the exact versions (and hashes) that were actually resolved, so installs stay reproducible until I update the lock.

---

## 4.6 Deliverable for Part 4

### Public URL

https://test.pypi.org/project/epita-vinh-nga-fintech/

### Why wheels (.whl) are faster / safer than source distributions (.tar.gz)

1. Faster: a wheel is already built. The client mostly unpacks it into site-packages. With a `.tar.gz` sdist, the machine has to build the package first (download build tools, maybe compile stuff), which takes longer.
2. Safer: installing from sdist can run build code on the client (`setup.py` etc.), so there is more that can go wrong or be abused. A wheel is a finished artifact from the publisher, so the client does not need to run that build step.

---

## 5.3 Deliverable for Part 5

### Diagnosis

`volume` and `weight` were both **strings**, because they come from `split(",")`.

Example:
- `record["volume"]` = `"450"` (str)
- `record["weight"]` = `"3"` (str)

The crash happens in `compute_weighted_metric` with `volume * weight`. You can't multiply two strings like that, so I got:

`TypeError: can't multiply sequence by non-int of type 'str'`

Also if we only fixed the multiply somehow, adding `record["volume"]` to `total_volume` would concatenate strings instead of doing real math.

### Call Stack at the breakpoint (idx == 2)

I put a conditional breakpoint on the `impact = compute_weighted_metric(...)` line when `idx == 2` (REC_003).

In the Call Stack I saw:
1. `aggregate_telemetry` in `scripts/debug_challenge.py` (this is where I was paused, inside the loop)
2. `<module>` in `scripts/debug_challenge.py` (the main part that calls `aggregate_telemetry(api_payload)`)

`parse_api_record` was not in the stack anymore because it already finished. If I step into `compute_weighted_metric`, that function appears on top.

### The Fix

I converted volume and weight to float when parsing:

```python
return {
    "id": parts[0],
    "entity": parts[1],
    "volume": float(parts[2]),
    "status": parts[3],
    "weight": float(parts[4]),
}
```

### Validation

```bash
uv run python scripts/debug_challenge.py
```

Output:

```
Aggregate Result: {'successful_entries': 3, 'total_volume': 650.0, 'avg_volume': 216.66666666666666, 'high_impact_count': 1}
```

This matches what the comments in the script say (650 total, avg ~216.67, 1 high impact).
