---
title: Local Development
---

# Local Development

To localdev, 

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone https://github.com/arunpatro/declo
cd declo
uv venv --python 3.12
uv sync --dev
uv pip install -e .
```

Now you are all set to start developing the declo project.

## Running tests

```bash
uv run tests/cli.py test
```