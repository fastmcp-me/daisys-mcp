import os

import pytest  # type: ignore
import pytest_asyncio  # type: ignore
from mcp.client.stdio import stdio_client  # type: ignore
from mcp.client.stdio import StdioServerParameters  # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv()


def pytest_runtest_setup(item):
    if "requires_credentials" in item.keywords:
        if not os.getenv("DAISYS_EMAIL") or not os.getenv("DAISYS_PASSWORD"):
            pytest.skip("Skipping test that requires credentials")


@pytest_asyncio.fixture
async def mcp_session_factory():
    async def _create():
        server_params = StdioServerParameters(
            command="uv",
            args=["--directory", ".", "run", "-m", "daisys_mcp.server"],
            env={
                "DAISYS_EMAIL": os.getenv("DAISYS_EMAIL"),
                "DAISYS_PASSWORD": os.getenv("DAISYS_PASSWORD"),
                "DISABLE_AUDIO_PLAYBACK": "True",
            },
        )
        return stdio_client(server_params)

    return _create
