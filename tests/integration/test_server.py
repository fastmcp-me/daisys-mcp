import pytest
import json

from mcp import ClientSession


@pytest.mark.asyncio
@pytest.mark.requires_credentials
async def test_text_to_speech(mcp_session_factory):
    async with await mcp_session_factory() as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            result = await session.call_tool(
                "text_to_speech", arguments={"text": "MCP Integration Test!"}
            )
            assert json.loads(result.content[0].text) == {"status": "ready"}


@pytest.mark.asyncio
@pytest.mark.requires_credentials
async def test_get_voices(mcp_session_factory):
    async with await mcp_session_factory() as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool("get_voices")
            voice_list = result.content
            assert isinstance(voice_list, list)

@pytest.mark.asyncio
@pytest.mark.requires_credentials
async def test_get_models(mcp_session_factory):
    async with await mcp_session_factory() as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool("get_models")
            model_list = result.content
            assert isinstance(model_list, list)