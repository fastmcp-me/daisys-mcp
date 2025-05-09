import os
from daisys import DaisysAPI  # type: ignore

# from daisys.v1.speak.models import ProsodyFeaturesUnion, ProsodyType
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
        Convert text to speech with a given voice and play the audio buffer.
        Voice_id can be provided. If not provided, the latest voice will be used.

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
    description=(
        """
        Get all available models from Daisys API.

        Args:
            language (str, optional): needs to be "de" for german, "en" for english and "nl" for dutch. Defaults to None.
            sort_by (str, optional): can be "name" or "displayname". Defaults to "displayname".
            sort_direction (str, optional): can be "asc" or "desc". Defaults to "asc".

        Returns:
            model_list: An object containing details of all models

        """
    ),
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
    description=(
        """
        Convert text to speech with a given voice and play the audio buffer.
        Voice_id can be provided. If not provided, the latest voice will be used.

        before calling also call get models so it always inputs a valid model

        ⚠️ TOKEN WARNING: This tool makes an API call to Daisys API which may incur costs. 

        Args:
            name (str, optional): The name of the voice to create. Defaults to "Daisy".
            gender (str, optional): The gender of the voice can be "male" or "female". Defaults to "female".
            model (str, optional): The model of the voice. Defaults to "english-v3.0".
            pitch (int, optional): Adjusts the pitch level; -10 for very low pitch, 10 for very high pitch.
            pace (int, optional): Controls the speech rate; -10 for very slow, 10 for very fast.
            expression (int, optional): Modulates expressiveness; -10 for monotone, 10 for highly expressive.

        Returns:
            McpVoice: An object containing details of the created voice, including voice_id, name, gender, model, and description.

        """
    ),
)
def create_voice(
    name: str = "Daisy",
    gender: str = "female",
    model: str = "english-v3.0",
    pitch: int = 0,
    pace: int = 0,
    expression: int = 0,
):
    # Using SimpleProsody
    prosody_params = {
        "pitch": pitch,
        "pace": pace,
        "expression": expression,
    }
    # Validate that all prosody parameters are within the range -10 to 10
    for param_name, value in prosody_params.items():
        if not -10 <= value <= 10:
            throw_mcp_error(f"{param_name} must be between -10 and 10, got {value}.")

    if gender not in VoiceGender:
        throw_mcp_error(
            f"Invalid gender: {gender}. Must be one of {list(VoiceGender)}."
        )

    with DaisysAPI("speak", email=email, password=password) as speak:
        voice = speak.generate_voice(
            name=name, gender=gender, model=model, default_prosody=prosody_params
        )
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
