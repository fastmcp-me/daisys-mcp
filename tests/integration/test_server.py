import json

import pytest  # type: ignore
from mcp import ClientSession  # type: ignore


@pytest.mark.asyncio
@pytest.mark.requires_credentials
async def test_text_to_speech(mcp_session_factory):
    async with await mcp_session_factory() as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            result = await session.call_tool(
                "text_to_speech", arguments={"text": "MCP Integration Test!"}
            )
            assert result.content[0].text.startswith("Success")


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


@pytest.mark.asyncio
@pytest.mark.requires_credentials
async def test_create_remove_voice(mcp_session_factory):
    async with await mcp_session_factory() as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            result = await session.call_tool(
                "create_voice",
                arguments={
                    "name": "Test_Voice",
                    "gender": "male",
                    "model": "english-v3.0",
                },
            )
            voice_id = json.loads(result.content[0].text)["voice_id"]
            assert voice_id
            result = await session.call_tool(
                "remove_voice", arguments={"voice_id": voice_id}
            )
            assert result.content[0].text.startswith("Success")
