import os
import io
from typing import Optional


from daisys import DaisysAPI  # type: ignore
from daisys.v1.speak import SimpleProsody, DaisysTakeGenerateError  # type: ignore

from daisys_mcp.utils import throw_mcp_error
from daisys_mcp.model import Status

disable_audio_playback = os.getenv("DISABLE_AUDIO_PLAYBACK", "false").lower() == "true"

email = os.environ.get("DAISYS_EMAIL")
password = os.environ.get("DAISYS_PASSWORD")


def text_to_speech_http(text: str, voice_id: Optional[str] = None):
    """
    Generate and play audio from text using DaisysAPI's HTTP protocol with sounddevice.
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
                throw_mcp_error("No voices available. Try to generate a voice first.")

        try:
            take = speak.generate_take(
                voice_id=voice_id,
                text=text,
                prosody=SimpleProsody(pace=0, pitch=0, expression=5),
            )
        except DaisysTakeGenerateError as e:
            raise RuntimeError(f"Error generating take: {str(e)}")

        audio_mp3 = speak.get_take_audio(take.take_id, format="mp3")

        if not disable_audio_playback:
            try:
                import sounddevice as sd  # type: ignore
                import soundfile as sf  # type: ignore
            except ModuleNotFoundError:
                message = (
                    "`uv pip install sounddevice soundfile` to enable audio playback."
                )
                raise ValueError(message)
            sd.play(*sf.read(io.BytesIO(audio_mp3)))
            sd.wait()

        return {"status": Status.READY}
