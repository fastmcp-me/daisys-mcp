import os
from daisys import DaisysAPI  # type: ignore
from mcp.server.fastmcp import FastMCP  # type: ignore
from typing import Optional, Literal

from daisys_mcp.model import McpVoice, McpModel, VoiceGender
from daisys_mcp.websocket_tts import text_to_speech_websocket
from daisys_mcp.http_tts import text_to_speech_http
from daisys_mcp.utils import throw_mcp_error

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
        "Converts input text to speech using a selected voice. Supports SSML (Speech Synthesis Markup Language) "
        "for advanced speech customization. You can:\n\n"
        '- **Spell out text**: `<say-as interpret-as="spell-out">Fred</say-as>`\n'
        '- **Specify dates and times**: `<say-as interpret-as="date">11.4.1984</say-as>`\n'
        '- **Switch languages**: `<voice language="nl">t/m 09-01-2010</voice>`\n'
        '- **Emphasize words**: `<emphasis level="strong">Important</emphasis>`\n'
        '- **Insert pauses**: `<break strength="medium"/>`\n'
        '- **Define pronunciation**: `<phoneme ph="ɣ ə k l øː r d ə">gekleurde</phoneme>`\n'
        '- **Disambiguate parts of speech**: `<w role="daisys:NN">bass</w>`\n\n'
        "**Example Input**:\n"
        "```xml\n"
        "<speak>\n"
        '  Mijn naam spel je als <say-as interpret-as="spell-out">Fred</say-as>.\n'
        '  Het was <say-as interpret-as="year">1944</say-as>.\n'
        '  Ik vertrek om <say-as interpret-as="time">13.10</say-as>.\n'
        '  Ik ben geboren op <say-as interpret-as="date">11.4.1984</say-as>.\n'
        "</speak>\n"
        "```\n\n"
        "**Tips**:\n"
        "- Put break tags where you want pauses.\n"
        "- Wrap your SSML content within `<speak>...</speak>` tags.\n"
        "- Ensure all tags are properly closed.\n"
        "- Use double quotes for attribute values.\n"
        "- Validate your SSML to prevent parsing errors.\n\n"
        "By utilizing SSML, you can fine-tune the speech output to better match your desired pronunciation, emphasis, and pacing."
        "Also give a notification that using text_to_speech uses daisys tokens"
    ),
)
def text_to_speech(text: str, voice_id: Optional[str] = None):
    # LLM sometimes send null as a string
    if isinstance(voice_id, str) and voice_id.lower() in ["null", "undefined"]:
        voice_id = None
    try:
        return text_to_speech_websocket(text, voice_id)
    except Exception:
        return text_to_speech_http(text, voice_id)


@mcp.tool(
    "get_voices",
    description="Get available voices can be filtered by model and gender, and sorted by name or timestamp in ascending or descending order.",
)
def get_voices(
    model: str | None = None,
    gender: str | None = None,
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
def get_models(
    language: str | None = None,
    sort_by: Literal["name", "displayname"] = "displayname",
    sort_direction: Literal["asc", "desc"] = "asc",
):
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
    name: Optional[str] = "Daisy",
    gender: Optional[VoiceGender] = VoiceGender.FEMALE,
    model: Optional[str] = "english-v3.0",
):
    if gender not in VoiceGender:
        raise ValueError(
            f"Invalid gender: {gender}. Must be one of {list(VoiceGender)}."
        )

    with DaisysAPI("speak", email=email, password=password) as speak:
        voice = speak.generate_voice(name=name, gender=gender, model=model)
    return voice.voice_id


def main():
    print("Starting Daisys-mcp server.")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
