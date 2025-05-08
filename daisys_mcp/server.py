import os
from daisys import DaisysAPI  # type: ignore
from mcp.server.fastmcp import FastMCP  # type: ignore
from mcp.types import TextContent
from typing import Literal

from daisys_mcp.model import McpVoice, McpModel, VoiceGender
from daisys_mcp.websocket_tts import text_to_speech_websocket
from daisys_mcp.http_tts import text_to_speech_http
from daisys_mcp.utils import throw_mcp_error, make_output_file, make_output_path

from dotenv import load_dotenv  # type: ignore

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("Daisys-mcp-server")
email = os.environ.get("DAISYS_EMAIL")
password = os.environ.get("DAISYS_PASSWORD")

if not email or not password:
    throw_mcp_error("DAISYS_EMAIL, DAISYS_PASSWORD environment variable is required")

storage_path = os.environ.get("DAISYS_BASE_STORAGE_PATH")


@mcp.tool(
    "text_to_speech",
    description=(
        """
        Convert text to speech with a given voice and save the output audio file to a given directory.
        Directory is optional, if not provided, the output file will be saved to $HOME/Desktop.
        Only one of voice_id or voice_name can be provided. If none are provided, the default voice will be used.

        ⚠️ TOKEN WARNING: This tool makes an API call to Daisys API which may incur costs. 

        Args:
            text (str): The text to convert to speech.
            voice_id (str, optional): The voice_id of the voice to use. If no voice specified use latest created voice.
            audio_format (str, optional): Can be either "wav" or "mp3". Defaults to "wav".
            output_dir (str, optional): Directory where files should be saved. Defaults to $HOME/Desktop if not provided.
            streaming (bool, optional): Whether to use streaming or not. Defaults to True. (streaming makes use of the websocket protocol which send and play audio in chunks)
            Defaults don't store if not provided.

        Returns:
            Text content with the path to the output file and name of the voice used.
        """
    ),
)
# Disabled optional typing since its not yet supported by cursor's mcp client
def text_to_speech(
    text: str,
    voice_id: str = None,  # type: ignore
    audio_format: str = "wav",
    output_dir: str = None,  # type: ignore
    streaming: bool = True,
):
    if text in ["None", "", None]:
        throw_mcp_error("Text for TTS cannot be empty.")

    # LLM sometimes send null as a string
    if isinstance(voice_id, str) and voice_id.lower() in ["null", "undefined"]:
        voice_id = None  # type: ignore

    with DaisysAPI("speak", email=email, password=password) as speak:  # type: ignore
        if not voice_id:
            try:
                voice_id = speak.get_voices()[-1].voice_id
            except IndexError:
                throw_mcp_error("No voices available. Try to generate a voice first.")

    try:
        # this can create only a wav file but has fast inference
        if audio_format == "wav" and streaming:
            audiobuffer = text_to_speech_websocket(text, voice_id)
        else:
            audiobuffer = text_to_speech_http(text, voice_id)
    except Exception:
        throw_mcp_error("Error generating audio")

    if not storage_path:
        return TextContent(
            type="text",
            text=f"Success. Voice used: {voice_id}",
        )
    # Create the output file
    output_path = make_output_path(output_dir, storage_path)
    output_file_name = make_output_file(text, output_path, audio_format)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path / output_file_name, "wb") as f:
        f.write(audiobuffer)  # type: ignore

    return TextContent(
        type="text",
        text=f"Success. File saved as: {output_path / output_file_name}. Voice used: {voice_id}",
    )


@mcp.tool(
    "get_voices",
    description="Get available voices can be filtered by model and gender, and sorted by name or timestamp in ascending or descending order.",
)
# Disabled optional typing since its not yet supported by cursor's mcp client
def get_voices(
    model: str = None,
    gender: str = None,
    sort_by: Literal["description", "name"] = "name",
    sort_direction: Literal["asc", "desc"] = "asc",
):
    with DaisysAPI("speak", email=email, password=password) as speak:
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
            voice_list.sort(key=lambda x: getattr(x, sort_by).lower())

        else:
            voice_list.sort(key=lambda x: getattr(x, sort_by).lower(), reverse=True)

        return voice_list


@mcp.tool(
    "get_models",
    description="Get available models.",
)
# Disabled optional typing since its not yet supported by cursor's mcp client
def get_models(
    language: str = None,
    sort_by: Literal["name", "displayname"] = "displayname",
    sort_direction: Literal["asc", "desc"] = "asc",
):
    # make sure to only use the first 2 letters of the language
    if language:
        language = language.lower()[:1]

    with DaisysAPI("speak", email=email, password=password) as speak:
        filtered_models = [
            model
            for model in speak.get_models()
            if language is None
            or any(lang.startswith(language) for lang in model.languages)
        ]
        model_list = [
            McpModel(
                name=model.name,
                displayname=model.displayname,
                flags=model.flags,
                languages=model.languages,
                genders=model.genders,
                styles=model.styles,
                prosody_types=model.prosody_types,
            )
            for model in filtered_models
        ]

        if sort_direction == "asc":
            model_list.sort(key=lambda x: getattr(x, sort_by).lower())

        else:
            model_list.sort(key=lambda x: getattr(x, sort_by).lower(), reverse=True)
        return model_list


@mcp.tool(
    "create_voice",
    description="Create a new voice.",
)
def create_voice(
    name: str = "Daisy",
    gender: VoiceGender = VoiceGender.FEMALE,
    model: str = "english-v3.0",
):
    if gender not in VoiceGender:
        raise ValueError(
            f"Invalid gender: {gender}. Must be one of {list(VoiceGender)}."
        )

    with DaisysAPI("speak", email=email, password=password) as speak:
        voice = speak.generate_voice(name=name, gender=gender, model=model)
    return McpVoice(
        voice_id=voice.voice_id,
        name=voice.name,
        gender=voice.gender,
        model=voice.model,
        description=voice.description,
    )


@mcp.tool(
    "remove_voice",
    description="Delete a voice.",
)
def remove_voice(
    voice_id: str,
):
    with DaisysAPI("speak", email=email, password=password) as speak:
        speak.delete_voice(voice_id)

    return TextContent(
        type="text",
        text=f"Success. voice {voice_id} deleted.",
    )


def main():
    print("Starting Daisys-mcp server.")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
