# Daisys official MCP server

Daisys-mcp is a beta version and doesn't have a stable release yet. But you can try it out by doing the following:

1. Get an account on [Daisys](https://www.daisys.ai/) and create an username and password.

2. clone the repository: `git clone https://github.com/daisys-ai/daisys-mcp.git`

3. cd into the repository: `cd daisys-mcp`

4. Install `uv` (Python package manager), install with `curl -LsSf https://astral.sh/uv/install.sh | sh` or see the `uv` [repo](https://github.com/astral-sh/uv) for additional install methods.

5. Create a virtual environment and install dependencies [using uv](https://github.com/astral-sh/uv):

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

6. Add the following to your config file in your MCP client ([Claude Desktop](https://claude.ai/download), [Cursor](https://www.cursor.com/), [mcp-cli](https://github.com/chrishayuk/mcp-cli), [mcp-vscode](https://code.visualstudio.com/docs/copilot/chat/mcp-servers), etc.):
```json
{
    "mcpServers": {
        "daisys-mcp": {
            "command": "uv",
            "args": [
                "--directory",
                "{installation_path}/daisys-mcp",
                "run",
                "-m",
                "daisys_mcp.server"
            ],
            "env": {
                "DAISYS_EMAIL": "{Your Daisys Email}",
                "DAISYS_PASSWORD": "{Your Daisys Password}"
            }
        }
    }
}
```

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

4. Test the server by running the tests:

```bash
uv pytest
```

you can also run a full integration test with:

```bash
uv pytest -m 'requires_credentials' # ⚠️ Running full integration tests does costs tokens on the Daisys platform 
```

5. Debug and test locally with MCP Inspector: `mcp dev daisys_mcp/server.py`
