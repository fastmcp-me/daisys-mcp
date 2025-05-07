import shutil
import os
from pathlib import Path
from datetime import datetime


class DaisysMcpError(Exception):
    pass


def throw_mcp_error(message: str):
    raise DaisysMcpError(message)


def is_installed(lib_name: str) -> bool:
    lib = shutil.which(lib_name)
    if lib is None:
        return False
    return True


def is_file_writeable(path: Path) -> bool:
    if path.exists():
        return os.access(path, os.W_OK)
    parent_dir = path.parent
    return os.access(parent_dir, os.W_OK) and parent_dir.exists()


def make_output_file(take_id: str, output_path: Path, extension: str = "wav") -> Path:
    output_file_name = (
        f"{take_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    )
    return output_path / output_file_name


def make_output_path(
    output_directory: str | None, base_path: str | None = None
) -> Path:
    output_path = None
    if output_directory is None:
        output_path = Path.home() / "Desktop"
    elif not os.path.isabs(output_directory) and base_path:
        output_path = Path(os.path.expanduser(base_path)) / Path(output_directory)
    else:
        output_path = Path(os.path.expanduser(output_directory))

    output_path.mkdir(parents=True, exist_ok=True)

    if not is_file_writeable(output_path):
        throw_mcp_error(f"Directory ({output_path}) is not writeable")
    return output_path
