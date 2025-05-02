import shutil
import subprocess
from typing import Iterator, Union


class DaisysMcpError(Exception):
    pass


def throw_mcp_error(message: str):
    raise DaisysMcpError(message)


def is_installed(lib_name: str) -> bool:
    lib = shutil.which(lib_name)
    if lib is None:
        return False
    return True


def play_audio_cross_os(
    audio: Union[bytes, Iterator[bytes]],
    notebook: bool = False,
    use_ffmpeg: bool = True,
) -> None:
    if isinstance(audio, Iterator):
        audio = b"".join(audio)
    if notebook:
        try:
            from IPython.display import Audio, display  # type: ignore
        except ModuleNotFoundError:
            message = "`pip install ipython` required when `notebook=False` "
            raise ValueError(message)

        display(Audio(audio, rate=44100, autoplay=True))
    elif use_ffmpeg:
        if not is_installed("ffplay"):
            message = (
                "ffplay from ffmpeg not found, necessary to play audio. "
                "On mac you can install it with 'brew install ffmpeg'. "
                "On linux and windows you can install it from https://ffmpeg.org/"
            )
            raise ValueError(message)
        args = ["ffplay", "-autoexit", "-", "-nodisp"]
        proc = subprocess.Popen(
            args=args,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        out, err = proc.communicate(input=audio)
        proc.poll()
    else:
        try:
            import io

            import sounddevice as sd  # type: ignore
            import soundfile as sf  # type: ignore
        except ModuleNotFoundError:
            message = (
                "`pip install sounddevice soundfile` required when `use_ffmpeg=False` "
            )
            raise ValueError(message)
        sd.play(*sf.read(io.BytesIO(audio)))
        sd.wait()
