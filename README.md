## NOTE

Daisys-mcp is a beta version and is not yet official available on the Claude Desktop or any other mcp clients.

## TODO 

Still need to add installation instructions for uvx

## Contributing

If you want to contribute or run from source:

1. Clone the repository:

```bash
git clone {this repo}
cd daisys_mcp
```

2. Create a virtual environment and install dependencies [using uv](https://github.com/astral-sh/uv):

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

3. Copy `.env.example` to `.env` and add your DAISYS username and password:

```bash
cp .env.example .env
# Edit .env and add your DAISYS username and password
```

5. Install the server in Claude Desktop: `mcp install daisys_mcp/server.py`

6. Debug and test locally with MCP Inspector: `mcp dev daisys_mcp/server.py`
