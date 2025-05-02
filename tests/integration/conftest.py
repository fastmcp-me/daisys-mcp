import pytest
import pytest_asyncio
import os

from mcp.client.stdio import stdio_client
from mcp.client.stdio import StdioServerParameters
from dotenv import load_dotenv

load_dotenv()


def pytest_runtest_setup(item):
    if "requires_credentials" in item.keywords:
        if not os.getenv("DAISYS_EMAIL") or not os.getenv("DAISYS_PASSWORD"):
            pytest.skip("Skipping test that requires credentials")


@pytest.mark.requires_credentials
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
