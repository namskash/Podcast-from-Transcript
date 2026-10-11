# Python venv

- `venv` is a Python virtual environment.
- It keeps project packages separate from system Python packages.
- It helps avoid system package manager errors.
- It helps avoid dependency conflicts between projects.

## How We Use It

- We create a local environment in `.venv/`.
- We activate it before we install packages.
- We install this project inside the environment.
- We run the CLI from the same environment.

## Commands

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
podcast-from-transcript --input /path/to/transcript.md
```

## API Key

- The virtual environment does not store the API key.
- It reads `GEMINI_API_KEY` from the shell environment.
- If the key is exported before activation, the venv can use it.
