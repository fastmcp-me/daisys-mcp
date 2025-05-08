import os
import time
import numpy as np  # type: ignore
import sounddevice as sd  # type: ignore
import wave
from typing import Optional

from daisys import DaisysAPI  # type: ignore
from daisys.v1.speak import (  # type: ignore
    DaisysWebsocketGenerateError,
    Status,
    StreamOptions,
    StreamMode,
)

from daisys_mcp.utils import throw_mcp_error
import io

from dotenv import load_dotenv  # type: ignore

load_dotenv()

disable_audio_playback = os.getenv("DISABLE_AUDIO_PLAYBACK", "false").lower() == "true"
email = os.environ.get("DAISYS_EMAIL")
password = os.environ.get("DAISYS_PASSWORD")
storage_path = os.environ.get("DAISYS_BASE_STORAGE_PATH")


def text_to_speech_websocket(text: str, voice_id: Optional[str] = None):
    """
    Generate and return WAV audio from text using DaisysAPI's WebSocket protocol.
    """

    if not email or not password:
        raise throw_mcp_error("DAISYS_EMAIL and DAISYS_PASSWORD must be set.")

    wav_buffer = io.BytesIO()
    audio_chunks = []
    stream = None

    if not disable_audio_playback:
        stream = sd.OutputStream(
            samplerate=22050,  # or check from the actual stream
            channels=1,
            dtype="int16",
        )
        stream.start()

    with DaisysAPI("speak", email=email, password=password) as speak:
        with speak.websocket(voice_id=voice_id) as ws:
            done = False
            ready = False
            generated_take = None
            t0 = time.time()

            def audio_cb(request_id, take_id, part_id, chunk_id, audio):
                nonlocal done

                if audio:
                    audio_np = np.frombuffer(audio, dtype=np.int16)
                    if not disable_audio_playback:
                        stream.write(audio_np) if stream else None
                    audio_chunks.append(audio)

                else:
                    if chunk_id in [0, None]:
                        done = True

            def status_cb(request_id, take):
                nonlocal ready, generated_take
                generated_take = take
                if take.status == Status.READY:
                    ready = True

            ws.generate_take(
                voice_id=voice_id,
                text=text,
                status_callback=status_cb,
                audio_callback=audio_cb,
                stream_options=StreamOptions(mode=StreamMode.CHUNKS),
            )

            while not (ready and done) and (time.time() - t0) < 60:
                try:
                    ws.update(timeout=5)
                except DaisysWebsocketGenerateError as e:
                    throw_mcp_error(e)
                    break

    # Combine audio chunks and write to wav buffer
    combined_audio = b"".join(audio_chunks)
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(22050)
        wav_file.writeframes(combined_audio)

    if not disable_audio_playback:
        stream.stop() if stream else None
        stream.close() if stream else None

    return wav_buffer.getvalue()
