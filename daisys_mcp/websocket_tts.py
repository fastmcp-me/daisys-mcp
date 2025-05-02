import os
import time
import numpy as np
import sounddevice as sd
from typing import Optional

from daisys import DaisysAPI
from daisys.v1.speak import (
    DaisysWebsocketGenerateError,
    Status,
    StreamOptions,
    StreamMode,
)

from daisys_mcp.utils import throw_mcp_error

disable_audio_playback = os.getenv("DISABLE_AUDIO_PLAYBACK", "false").lower() == "true"
email = os.environ.get("DAISYS_EMAIL")
password = os.environ.get("DAISYS_PASSWORD")


def text_to_speech_websocket(text: str, voice_id: Optional[str] = None):
    if not email or not password:
        raise ValueError("DAISYS_EMAIL and DAISYS_PASSWORD must be set.")
    stream = None
    if not disable_audio_playback:
        stream = sd.OutputStream(
            samplerate=22050,  # or check from the actual stream
            channels=1,
            dtype="int16",
        )
        stream.start()

    with DaisysAPI("speak", email=email, password=password) as speak:
        print("Found Daisys Speak API", speak.version())

        if not voice_id:
            try:
                voice_id = speak.get_voices()[-1].voice_id
            except IndexError:
                throw_mcp_error("No voices available")

        with speak.websocket(voice_id=voice_id) as ws:
            done = False
            ready = False
            generated_take = None
            t0 = time.time()

            def audio_cb(request_id, take_id, part_id, chunk_id, audio):
                nonlocal done

                print(
                    f"[{time.time() - t0:.2f}s] Received chunk {chunk_id} of part {part_id}"
                )
                if audio:
                    audio_np = np.frombuffer(audio, dtype=np.int16)
                    if not disable_audio_playback:
                        stream.write(audio_np) if stream else None
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

        if generated_take:
            print(
                f"Deleting take {generated_take.take_id}:",
                speak.delete_take(generated_take.take_id),
            )

    if not disable_audio_playback:
        stream.stop() if stream else None
        stream.close() if stream else None

    return {"status": Status.READY}
