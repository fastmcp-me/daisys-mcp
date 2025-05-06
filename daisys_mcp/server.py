import os
from daisys import DaisysAPI
from mcp.server.fastmcp import FastMCP
from typing import Optional, Literal

from daisys_mcp.model import McpVoice
from daisys_mcp.websocket_tts import text_to_speech_websocket
from daisys_mcp.http_tts import text_to_speech_http
from daisys_mcp.utils import throw_mcp_error

from dotenv import load_dotenv

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Daisys-mcp-server")
email = os.environ.get("DAISYS_EMAIL")
password = os.environ.get("DAISYS_PASSWORD")

if not email or not password:
    throw_mcp_error("DAISYS_EMAIL, DAISYS_PASSWORD environment variable is required")

storage_path = os.environ.get("STORAGE_PATH")


@mcp.tool(
    "text_to_speech",
    description="Converts text to speech using a selected voice. Streams audio using the WebSocket API for low latency and falls back to HTTP if needed. Optionally, specify a voice ID to control the voice used for generation.",
)
def text_to_speech(text: str, voice_id: Optional[str] = None):
    # LLM sometimes send null as a string
    if voice_id.lower() == "null":
        voice_id = None
    try:
        return text_to_speech_websocket(text, voice_id)
    except Exception as e:
        return text_to_speech_http(text, voice_id)


@mcp.tool(
    "get_voices",
    description="Get available voices can be filtered by model and gender, and sorted by name or timestamp in ascending or descending order.",
)
def get_voices(
    model: str | None = None,
    gender: str | None = None,
    sort: Literal["timestamp", "name"] = "name",
    sort_direction: Literal["asc", "desc"] = "asc",
):
    with DaisysAPI("speak", email=email, password=password) as speak:
        # print("Found Daisys Speak API", speak.version())

        filtered_voices = [
            voice
            for voice in speak.get_voices()
            if (model is None or voice.model == model)
            and (gender is None or voice.gender == gender)
        ]
        voice_list = [
            McpVoice(
                voice_id=voice.voice_id,
                name=voice.name,
                gender=voice.gender,
                model=voice.model,
                description=voice.description,
            )
            for voice in filtered_voices
        ]
        if sort_direction == "asc":
            voice_list.sort(key=lambda x: getattr(x, sort))

        else:
            voice_list.sort(key=lambda x: getattr(x, sort), reverse=True)

        return voice_list


@mcp.tool(
    "get_models",
    description="Get available models.",
)
def get_models():
    pass


@mcp.tool(
    "create_voice",
    description="Create a new voice.",
)
def create_voice():
    pass


def main():
    print("Starting Daisys-mcp server.")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
