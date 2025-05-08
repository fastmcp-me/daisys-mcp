import pytest  # type: ignore
import sys
from pathlib import Path
from daisys_mcp.utils import make_output_path, is_file_writeable


def test_make_output_path_default(monkeypatch, tmp_path):
    # Redirect Path.home() to a temp location
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    path = make_output_path(None)
    assert path.exists()
    assert path.name == "Desktop"


def test_make_output_path_relative(monkeypatch, tmp_path):
    relative_dir = "outputs"
    base_path = str(tmp_path)
    path = make_output_path(relative_dir, base_path)
    assert path.exists()
    assert path.name == "outputs"
    assert is_file_writeable(path)


def test_make_output_path_absolute(tmp_path):
    absolute_dir = str(tmp_path / "absolute_output")
    path = make_output_path(absolute_dir)
    assert path.exists()
    assert path.name == "absolute_output"
    assert is_file_writeable(path)


@pytest.mark.skipif(
    sys.platform == "win32", reason="Windows does not support file permissions"
)
def test_make_output_path_unwritable(tmp_path, monkeypatch):
    # Simulate unwritable directory
    unwritable_dir = tmp_path / "unwritable"
    unwritable_dir.mkdir()
    unwritable_dir.chmod(0o400)  # read-only

    monkeypatch.setattr(
        "daisys_mcp.utils.throw_mcp_error",
        lambda msg: (_ for _ in ()).throw(Exception(msg)),
    )

    with pytest.raises(Exception, match="is not writeable"):
        make_output_path(str(unwritable_dir))

    # Restore permissions to clean up
    unwritable_dir.chmod(0o700)
