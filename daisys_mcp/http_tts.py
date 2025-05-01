import os
from io import BytesIO
from typing import Optional

from daisys import DaisysAPI
from daisys.v1.speak import SimpleProsody, DaisysTakeGenerateError

from pydub import AudioSegment
from pydub.playback import play

from utils import throw_mcp_error


email = os.environ.get("DAISYS_EMAIL")
password = os.environ.get("DAISYS_PASSWORD")


def text_to_speech_http(text: str, voice_id: Optional[str] = None):
    """
    Generate and play audio from text using DaisysAPI's http protocol.
    """
    if not email or not password:
        throw_mcp_error(
            "DAISYS_EMAIL and DAISYS_PASSWORD environment variables must be set."
        )

    if text in ["None", "", None]:
        throw_mcp_error("Text for TTS cannot be empty.")

    with DaisysAPI("speak", email=email, password=password) as speak:
        if not voice_id:
            try:
                voice_id = speak.get_voices()[-1].voice_id
            except IndexError:
                throw_mcp_error(
                    "No voices available try to generate a voice with the voice_generate."
                )

        try:
            take = speak.generate_take(
                voice_id=voice_id,
                text=text,
                prosody=SimpleProsody(pace=0, pitch=0, expression=5),
            )
        except DaisysTakeGenerateError as e:
            raise RuntimeError(f"Error generating take: {str(e)}")

        audio_mp3 = speak.get_take_audio(take.take_id, format="mp3")
        audio = AudioSegment.from_file(BytesIO(audio_mp3), format="mp3")
        play(audio)
        return {"status": "Audio played successfully through."}
